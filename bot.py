# Adapted from the templates found at https://pypi.org/project/slack-bolt/
"""
1. EM posts up a flyer, or does a classroom announcement, or Ed discussion, etc.
2. EM takes a photo / screenshot as proof
3. EM opens up Slack/Discord on their phone, and sends the proof to a channel #publicity-points-logging
4. The Discord/Slack bot receives the proof and saves the image to a folder (named after the EM) onto a computer/server. It also renames the image to the timestamp of the submission.
5. The Discord /Slack bot responds to the user with a message confirming receipt of the proof, and optionally tells them how many photos they’ve submitted for the current event.
6. When the deadline for the event publicity is met, the bot automatically zips up all the folders of EM publicity proof and somehow sends it to the publicity officer.
7. The publicity officer then looks through all the submissions and tallies up points for EMs / updates the MasterLog.
"""
import os #hide secrets
import time #for debugging and logging
import requests #to do file downloads
import re #for regex stuff
import json #to write dicts or jsons to files
import shutil #for zipping stuff up
import asyncio #for running stuff asynch or on timers
import pytz #for timezones
from dotenv import load_dotenv #so we can read .env files
from datetime import datetime #to manage dates
from pathlib import Path #i don't want to exclude the microsoft users
from slack_bolt.app.async_app import AsyncApp #slack-bolt app stuff
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler #and I don't want to run ngrok, so heres sockets

load_dotenv() #first load in our secrets
SLACK_BOT_TOKEN=os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN=os.getenv("SLACK_APP_TOKEN")
BOT_CHANNEL_ID=os.getenv("BOT_CHANNEL_ID")

slackapp = AsyncApp(token=SLACK_BOT_TOKEN) #then initialize slack app stuff
bot_timezone = pytz.timezone('America/Los_Angeles') #manually set bot checking to a specific timezone

# Define common functions
def load_json(filepath):
  """Function that loads a json to read, then returns the stuff inside."""
  try:
    with open(filepath, 'r') as f:
      return json.load(f)
  except:
    printlg(f"Failed to open {filepath}")

def write_json(filepath, content):
  """Function that writes CONTENT to a json at FILEPATH."""
  try:
    with open(filepath, 'w') as f:
      json.dump(content, f)
  except:
    printlg(f"Failed to open {filepath}")

def printlg(input_str, logfile="log.log"):
  """Function that takes in an INPUT_STR and both prints to console, as well as to a log.log.
  Automatically prepends a [DEBUG] and unix timestamp to the input."""
  format_str = f"[DEBUG] ({time.time()}): {input_str}"
  print(format_str)
  if not os.path.exists(logfile): #make sure we have one
    with open(logfile, 'w') as f:
      pass
  with open(logfile, 'a') as f: #append mode
    f.write(format_str + '\n')

async def get_member_info():
  """Function that gets member's names and slack IDs."""
  member_info = await slackapp.client.users_list() #and also get user info for easier tagging later on
  member_dict = {}
  for each in member_info["members"]:
    member_dict[each["id"]] = each["profile"]["real_name"]
  printlg(f"Member info generated. Dict contains {len(member_dict)} pairings.")
  write_json(Path("data") / 'member-map.json', member_dict) #if we actually need this, then someones going to have to do some data science tee hee
  return member_dict

async def zip_and_send():
  """Function that attempts to zip up the previous event details and send them to slack. Then deletes it.
  Importantly, we do NOT recreate an data folder here, that's what the other function calls have to do."""
  if os.path.isfile(Path("data") / 'config.json'):
    load_dict = load_json(Path("data") / 'config.json') #now we open up config.json
    prev_title = load_dict["title"]
    zip_time = int(time.time()) #so we can make each zip different
    member_info = await get_member_info() #we get the member info json, and stick it into the zip for good measure.
    #logic to rename all id folders to real name folders
    for each_dir in os.listdir("data"):
      this_dir = Path("data") / each_dir
      if os.path.isdir(this_dir) and each_dir in member_info:
        new_name = member_info[each_dir] #for the print message later, but this is technically not needed
        os.rename(this_dir, Path("data") / new_name)
        printlg(f"'{each_dir}' renamed to '{new_name}'")
    new_zip_name = f"{prev_title}-data-{zip_time}" #planned to make it modular, but realized there was no point
    shutil.make_archive(new_zip_name, 'zip', "data") #archive it
    shutil.rmtree("data") #then remove what we had
    os.makedirs("data", exist_ok=True) #restore it
    response = await slackapp.client.files_upload_v2(
      channel=BOT_CHANNEL_ID,
      file=f"{new_zip_name}.zip",
      title=f"{new_zip_name}.zip",
    )
    printlg(f"File uploaded:", response["file"]["id"])
    os.remove(f"{new_zip_name}.zip") #we don't need it now
    return True
  else:
    printlg(f"No config file found. -OR- No data to zip up. Skipping...")
    return False
  
async def seconds_check(x):
  """Function that checks the current date every X seconds. If the deadline is hit, then we
  return ZIP_AND_SEND, and alert the channel too."""
  while True:
    printlg(f"seconds_check({x}) has been triggered...")
    try:
      load_dict = load_json(Path("data") / 'config.json') #now we open up config.json
    except:
      load_dict = False
    if load_dict:
      end_date = datetime.strptime(load_dict["dates"][1], "%m/%d/%Y").replace(hour=23, minute=59) #we assume the date is in the correct format, because we had an earlier check
      curr_date = datetime.now(bot_timezone)
      if curr_date > end_date:
        printlg(f"Event end date has been passed. Zipping up the responses and sending to Slack...")
        await slackapp.client.chat_postMessage(
          channel=BOT_CHANNEL_ID,
          text=f"[Attention] Publicity logging for {load_dict['title']} has ended. A zip file of all submissions for this event is being generated. It will be sent shortly."
        )
        await zip_and_send()
      else:
        printlg(f"Event end date has NOT been passed. Skipping...")
    else:
      printlg(f"Event details were not found. Skipping...")
    await asyncio.sleep(x)

@slackapp.event("app_mention")
# Logic to deal with pinging. Use in place of slash commands or something. These commands will be received in any channel.
async def respond(body, context, say):
  """This function handles the logic meant to parse 'commands' sent as pings to the bot"""
  try:
    if "text" in body["event"]:
      printlg(f"{context['user_id']} pinged bot")
      full_text = body["event"]["text"] #get all the text with the ping itself
      ping_text = re.search(r'>\s*(.*)', full_text) #then regex match the > (end of ping)
      if ping_text: #i don't think we'll ever hit the else condition
        reg_result = ping_text.group(1) #get after the match
        #If its an empty ping:
        if reg_result == "":
          await say(f"Hello <@{context['user_id']}>! To begin setting up publicity logging for an event, please ping me the following:\n\n  - Please enter the EVENT NAME, START DATE, and END DATE, in that order, all separated by commas.\n\n  - The date format should be MM/DD/YYYY.\n\nAn example of a message is: FSN, 01/01/2025, 01/08/2025. This creates an event called 'FSN', that starts publicity on 01/01/2025, and ends on 01/08/2025.")
        else:
          reg_result = reg_result.split(",") #makes a list, then we have to parse through it
          #the first item can be anything, but the next two must be recognized by datetime
          #Make sure our syntax is good...
          if len(reg_result) != 3: #make sure we have corect # of args
            await say(f"Hello <@{context['user_id']}>, your event details were NOT set.\n\n  - Your message contains an incorrect amount of arguments. As a reminder, please enter the EVENT NAME, START DATE, and END DATE, all separated by commas.\n\n  - Date format should be MM/DD/YYYY.")
            return
          #...so that we can start parsing
          else:
            event_title = reg_result[0] #event title -> key of dict
            start_date = reg_result[1].strip() #first date -> publicity start
            end_date = reg_result[2].strip() #second date -> publicity end
            try: #we want to filter out bad syntax
              start_datetime = datetime.strptime(start_date, "%m/%d/%Y")
              end_datetime = datetime.strptime(end_date, "%m/%d/%Y")
            except:
              await say(f"Hello <@{context['user_id']}>, your event details were NOT set.\n\n  - Your message does not contain recognized date formats. As a reminder, please enter the EVENT NAME, START DATE, and END DATE, all separated by commas.\n\n  - Date format should be MM/DD/YYYY.")
              return
            if start_datetime.strftime("%m/%d/%Y") and end_datetime.strftime("%m/%d/%Y"): #make sure they both work
              if start_datetime > end_datetime or end_datetime < start_datetime: #this is redundant but so it goes
                await say(f"Hello <@{context['user_id']}>, your event details were NOT set.\n\n  - Your END DATE cannot be before the START DATE. Please try again.")
                return
              if await zip_and_send():
                await say(f"A zip file of all submissions for the past event is being generated. It will be sent shortly.") #and send out the zip
              else:
                printlg(f"File upload failed. This may or may not be a false alarm. Please check the Slack channel.") #sometimes, slack triggers the file logic twice, not too sure why
              os.makedirs("data", exist_ok=True) #just to make sure
              write_dict = {"title":event_title, "dates":[start_date, end_date]} #assemble the dict. Key 0 is title, Key 1 is dates. Value 0 is a string, Value 1 is a list with 2 items
              write_json(Path("data") / 'config.json', write_dict) #and write it to our new json
              await say(f"Hello <@{context['user_id']}>, your new event details have been set.\n\n  - Event Name: {event_title}\n  - Publicity Start Date: {reg_result[1]}\n  - Publicity End Date: {reg_result[2]}\n\nTo set new dates or make a new event, ping me again with the updated details.")
  except:
    printlg(f"Try-Except loop in async function 'respond' has failed. Please check the log messages.")
    await say(f"Hello, <@{context['user_id']}>. Your message has created an internal error in my code! Please notify an officer.\nTell them to look at 'respond'.")

@slackapp.event("message")
# Logic to follow upon receiving a message from a user. It only works in BOT_CHANNEL_ID.
async def handle_message_events(body, context, say):
  """This function handles all the logic for what to do when a message is passed in.
  Unfortunately, I can't seem to call other functions / return them, so all the logic has
  to be crammed into a single if loop. Boo..."""
  try:
    if body['event']['channel'] != BOT_CHANNEL_ID: #ignore messages from outside of the bot channel
      return
    else:
      # Logic for Files
      if "files" in body["event"]: #when we deal with files...
        user = context['user_id']
        printlg(f"File detected in message from {user}.")
        if not os.path.exists(Path("data") / "config.json"):
          await say(f"Hello <@{user}>. There is no current event set for publicity logging. Please contact an officer to ping me to set up an event.")
          return #ooh i missed typing that
        load_dict = load_json(Path("data") / 'config.json') #read the config file
        start_date = datetime.strptime(load_dict["dates"][0], "%m/%d/%Y") #conversion to the datetime formats
        end_date = datetime.strptime(load_dict["dates"][1], "%m/%d/%Y").replace(hour=23, minute=59) #important here, to allow for same-day submissions
        curr_date = datetime.now(bot_timezone)
        if curr_date < start_date:
          await say(f"Hello <@{user}>. Publicity logging for {load_dict['title']} has not yet started. If you think this is a mistake, contact an officer for help.")
          return
        elif curr_date > end_date:
          await say(f"Hello <@{user}>. Publicity logging for {load_dict['title']} has ended. If you have questions, please contact an officer for help.")
          return
        #if we're still here...
        os.makedirs(Path("data") / user, exist_ok=True) #first make a folder for this user should they not exist
        headers = {
          "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
        } #prepare the headers for file downloads, we use requests to do so
        message_toggle = True #we'll use this to determine which message to send to user later.
        files = body["event"]["files"] #this is a list of dicts! tricky sneaky
        files_length = len(files) #so, we have to know how many files...
        for i in range(files_length): #...in order to iterate through them all
          save_name = f"{int(time.time())}-{files[i]['title']}" #assemble the save filepath
          response = requests.get(files[i]["url_private_download"], headers=headers) #now we actually download the file
          if response.status_code == 200: #success!
            with open(Path("data") / user / save_name, "wb") as f: #pathlib stuff
              f.write(response.content) #write the file to the path above
            printlg(f"'{save_name}' downloaded to folder '{user}'.")
          else:
            message_toggle = False #i couldve made response.status_code the trigger, but i can think of a few edge cases
            printlg(f"'{save_name}' was NOT downloaded. Something went wrong...")
        if message_toggle:
          file_count = len(os.listdir(Path("data") / user)) #this is not very good honestly, but it works for our use case (doesn't check if its a file)
          await say(f"Files received, <@{user}>! You have submitted {file_count} files for {load_dict['title']}.")
        else: #even a single failed download should trigger this. i hope. i also hope this never happens
          await say(f"Unfortunately, your files were NOT received, <@{user}>. Contact an officer for help.")
  except:
    printlg(f"Try-Except loop in async function 'handle_message_events' has failed. Please check the log messages.")
    await say(f"Hello, <@{context['user_id']}>. Your message has created an internal error in my code! Please notify an officer.\nTell them to look at 'handle_message_events'.")

async def start_bot():
    """Async function that starts the bot"""
    handler = AsyncSocketModeHandler(slackapp, SLACK_APP_TOKEN)
    await handler.start_async()

async def main():
    """Async function that starts both the bot and the seconds_check."""
    await asyncio.gather(
        seconds_check(60 * 60 * 2), #can be anything, lets just set it to run every 2 hours
        start_bot()
    )

if __name__ == "__main__": #the actual call
  asyncio.run(main())
