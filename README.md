# slack-publicity-app

Slack bot designed to automate publicity logging for EMs of UC Berkeley MCBcDNA.

### Slack Setup:

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
