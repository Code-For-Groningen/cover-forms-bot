Cover bot go brr.

- [Installation](#installation)
  - [Necessary environment variables](#necessary-environment-variables)
  - [Example interaction with the script](#example-interaction-with-the-script)
- [Dockerized version](#dockerized-version)
- [Non-dockerized version](#non-dockerized-version)
  - [Set the enviornment variables](#set-the-enviornment-variables)
  - [Running the bot](#running-the-bot)
- [Usage](#usage)
  - [Commands](#commands)

## Installation

```bash
git clone https://github.com/Code-For-Groningen/cover-forms-bot.git
cd cover-forms-bot
```

### Necessary environment variables

- `DISCORD_BOT_TOKEN` - [Tutorial](https://www.writebots.com/discord-bot-token/)
- `COVER_EMAIL`
- `COVER_PASSWORD`
- `COVER_CHANNEL_ID` - [Tutorial](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-)
- `POLL_INTERVAL` (optional, default: 60s)
- `EMBED_IMAGE` (author of embeds, default is cover logo)

Set them in the environment. Use the startup script if you'd like.

> [!WARNING]
> The script produces another script which only works on Unix-like systems. You have to run the bot manually or use [docker](#dockerized-version) on Windows.
> If you're using it, check out [the example interaction](#example-interaction) below.

### Example interaction with the script

```bash
$ cd src
$ python initial.py
Discord bot token: # This is supposed to not be visible while typing
Email (svcover.nl): amo@ng.us
Password: # This too
Channel ID to post in:696969696969
Polling interval (seconds):5
Embed image URL:https://raw.githubusercontent.com/CircuitReeRUG/branding/refs/heads/main/mascot/circuitree_waving.png
```

## Dockerized version

Change the environment variables in the `docker-compose.yml` file.

```bash
docker compose up -d
```

## Non-dockerized version

### Set the enviornment variables

Using the script or set them manually.

### Running the bot

```bash
$ pip install -r requirements.txt
>> ...
$ python3 start.py # Requires Python 3.9+
```

## Usage

[Invite the bot to your server](https://discordpy.readthedocs.io/en/stable/discord.html).

### Commands

| Command                  | What do it do?                                                |
| ------------------------ | ------------------------------------------------------------- |
| !observe <name of event> | begins observing the event, pinging and showing new attendees |
| !stop_observe            | stops observing the event                                     |
