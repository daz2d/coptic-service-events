# Google Calendar Setup Guide

This guide will help you set up Google Calendar integration for the Coptic Service Events Bot.

## Prerequisites

- A Google account
- Python 3.9 or higher installed

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select an existing project
3. Give your project a name (e.g., "Coptic Events Bot")
4. Click "Create"

## Step 2: Enable the Google Calendar API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in the required fields (App name, user support email, developer email)
   - Add your email to "Test users"
   - Save and continue through all steps
4. Back on the credentials page:
   - Choose "Desktop app" as the application type
   - Give it a name (e.g., "Coptic Events Bot Desktop")
   - Click "Create"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the project root directory

## Step 4: First Run Authorization

When you run the bot for the first time with Google Calendar enabled:

```bash
python main.py --once
```

1. A browser window will open asking you to authorize the application
2. Log in with your Google account
3. Grant the requested permissions (Calendar access)
4. The authorization will be saved in `token.json` for future use

## Security Notes

- **Never commit `credentials.json` or `token.json` to version control**
- These files are already listed in `.gitignore`
- Keep these files secure and private

## Troubleshooting

### "credentials.json not found" error
- Make sure you've downloaded the OAuth credentials from Google Cloud Console
- Ensure the file is named exactly `credentials.json`
- Place it in the project root directory

### Authorization page doesn't open
- The bot will print a URL in the console
- Copy and paste this URL into your browser manually
- Complete the authorization process

### "Access blocked: This app hasn't been verified"
- Click "Advanced" > "Go to [App Name] (unsafe)"
- This is safe for personal use applications
- Alternatively, you can publish your app and go through the verification process

## Configuration

In `config.json`, you can customize:

```json
{
  "google_calendar": {
    "enabled": true,
    "calendar_name": "Coptic Service Events",
    "auto_add_events": true,
    "reminder_minutes": [1440, 60]
  }
}
```

- `enabled`: Enable/disable Google Calendar integration
- `calendar_name`: Name of the calendar to create/use
- `auto_add_events`: Automatically add discovered events
- `reminder_minutes`: When to send reminders (1440 = 1 day, 60 = 1 hour)

## Multiple Calendars

If you want to use different calendars for different event types, you can modify the code to check `event.event_type` and route to different calendars.
