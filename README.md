set-up:

1. Go to https://api.slack.com/. Navigate to "Your Apps".

2. Click on "Create an app". Select "From scratch".

3. Basic Information > App-Level Tokens > Generate Token and Scopes. Give it the three scopes. Copy the id for SLACK_APP_TOKEN.

4. Give bot info on same page.

5. Features > OAuth & Permissions. Go to Scopes. Give it the scopes.

6. Go to OAuth Tokens. Install to workspace and copy Bot User OAuth Token for SLACK_BOT_TOKEN.

7. Go to Settings > Socket Mode. Turn it on.

8. Make sure "Event Subscriptions" is enabled. If not, click on it. Then turn it on and go to Subscribe to bot events and fill it out.

9. Normal python stuff
