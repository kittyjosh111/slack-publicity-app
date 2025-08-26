# slack-publicity-app

Slack bot designed to automate publicity logging for EMs of UC Berkeley MCBcDNA. The general usage and setup guide are detailed below.

### General Usage:

These steps refer to terms specific to MCBcDNA's club structure. EMs stand for Executive Members, who are in charge of planning and publicizing events.

1. Officer creates an event by pinging the bot with a formatted message. The bot needs a name for the event, then the start and end dates for publicity logging. The message the bot expects are the NAME (string), START_DATE (MM/DD/YYYY), and END_DATE (MM/DD/YYYY), all separated by commas. An example of a succesful command would be: ```Test Event, 08/25/2025, 08/30/2025```.

2. EM then does their publicity by posting a flyer, classroom announcement, Ed discussion, etc.

3. EM then takes a photo or screenshot of their publicity as proof.

4. EM then opens up Slack and sends the proof to a dedicated publicity channel on the server.

5. This Slack bot receives the proof and saves the image locally to a folder named using the EM's Slack ID. It also renames the image to the timestamp of the submission.

6. This Slack bot responds to the user with a message confirming receipt of the proof and tells them how many photos they’ve submitted for the current event.

7. When the deadline for the event publicity is met, the bot automatically stops accepting responses. It then pulls a json from Slack matching all the local Slack IDs with their Slack usernames, and renames the folders to said Slack usernames.

8. This Slack bot then zips up all the folders of EM publicity proof and sends it back into the dedicated publicity channel on the Slack server.

9. The publicity officer then downloads the zip and looks through all the submissions, then tallies up points for each individual EM. Inside the zip is a ```config.json``` which holds the event details supplied in step 1, as well as a ```member-map.json```, which has pairing between Slack IDs and Slack usernames, in case something went wrong during the renaming.

10. The bot awaits a new event. Go to Step 1 and repeat the cycle.

The bot will usually send messages indicating receipt of a command, or hints as to how to format commands. It'll also send warning messages when something errors out so that the deployer of the bot can investigate. To whoever deploys the bot, there will also be a ```log.log``` file in the directory of the bot executable which contains logs of all interactions (and errors) the bot encounters.

### Python Bot Setup:

1. Clone or download this repository somewhere you have write privileges (the bot needs to make folders for submissions). If using git, use ```git clone https://github.com/kittyjosh111/slack-publicity-app.git```.

2. Move into the directory of this bot.

3. It is recommended to run this bot in a virtual environment, as it does require a number of dependencies. My favorite way to do so is ```python3 -m venv venv```. Also, this bot was only tested on Python 3.10, but I expect it would work on most other Python3 versions as well.

4. Activate your venv and use pip to install the requirements from requirements.txt. For example, ```pip install -r requirements.txt```.

The Python bot and environment have been set up. You can run it now but the bot probably won't work unless you finish the Slack Setup and ```.env``` setup.

### Slack Setup (and ```.env``` setup):

1. Go to https://api.slack.com/. Navigate to "Your Apps".

2. Click on "Create an app". Select "From scratch".

![alt text](/slack-bot-docs/step2.png)

3. On the resulting page, go to "Basic Information" > "App-Level Tokens" > "Generate Token and Scopes". Give it the three scopes listed in the picture. Copy the id you get and enter it in the ```SLACK_APP_TOKEN``` field into the ```.env``` file from this repository.

![alt text](/slack-bot-docs/step3.png)

4. On the same page, scroll down and fill in some basic information about your bot.

![alt text](/slack-bot-docs/step4.png)

5. Now on the sidebar, find the "Features" heading and go to "OAuth & Permissions" link. Go to "Scopes". Add the scopes listed in the following pictures.

![alt text](/slack-bot-docs/step5.png)

6. Scroll up to find "OAuth Tokens". Install the bot to your Slack workspace and copy the "Bot User OAuth Token" into the ```SLACK_BOT_TOKEN``` field on the ```.env``` file from this repository.

7. Go to the sidebar again and find "Settings" > "Socket Mode". When the toggle loads, turn it on.

![alt text](/slack-bot-docs/step78.png)

8. On the same page, scroll down and make sure "Event Subscriptions" is enabled. If not, click on it. Then turn it on and go to Subscribe to bot events and fill it out.

![alt text](/slack-bot-docs/step8.png)

You should be ready to start the python bot now.
