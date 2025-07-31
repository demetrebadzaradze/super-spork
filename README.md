# Super-Spork

This project provides a bot that forwards text messages from Mumble server (version 1.5.735) to a Discord server. The bot forwards messages sent in Mumble channels to a specified Discord channel.

# Features
- Mumble-to-Discord: Forwards messages from Mumble channels to a Discord channel, including the sender's name and channel name (e.g., **TG_3W3p** in **Minecraft**: Hello from Mumble!).
- Basic Discord Commands: Responds to simple commands like ?hello or hi with responses like yooooo or whats up (via the responce.py cog).

# Prerequisites
- System: Ubuntu 24.04.1 LTS (or compatible Linux distribution).
- Docker: Docker and Docker Compose installed (`sudo apt install docker.io docker-compose`).
- Mumble Server: Version 1.5.735 running in a Docker container.
- Python: Version 3.12 (included in the bot's Docker image).
- Dependencies: Listed in requirements.txt (e.g., `discord.py`, `PyNaCl` for voice support, `zeroc-ice` for Ice communication).
- Discord Bot Token: Obtain from the Discord Developer Portal.
- Mumble Ice Password: Set in the Mumble server configuration.
- Discord Channel ID: The ID of the Discord channel where Mumble messages are forwarded (e.g., `1349702376763818087`).

# Setup Instructions
Directory Structure
``` plain
├── .env
├── docker-compose.yml
├── data/
├── logs/
└── super-spork/
    ├── cogs/
    │   ├── mumble.py
    │   ├── responce.py
    ├── Dockerfile
    ├── MumbleServer_ice.py
    ├── main.py
    └── requirements.txt
```
1. clone the `super-spork` directory where  mumble server compose file is
  go to the corect direvctory(e.g `cd /mnt/silver-64/opt/mumble/`) and clone the repo
  ```bash
  git clone https://github.com/demetrebadzaradze/super-spork.git
  ```
1. configure `.env` file


1. Configure the Mumble Server





Ensure the Mumble server is running in a Docker container with Ice enabled:

# docker-compose.yml
services:
  mumble-server:
    image: mumblevoip/mumble-server:1.5.735
    ports:
      - "64738:64738"
      - "6502:6502"
    environment:
      - MUMBLE_ICE_SECRET=password
    volumes:
      - ./data:/data
    networks:
      - mumble-network
networks:
  mumble-network:



Start the Mumble server:

cd /mnt/silver-64/opt/mumble
sudo docker compose up -d

2. Configure the Bot





Create a Discord bot in the Discord Developer Portal:





Note the bot token.



Invite the bot to your server with permissions to read and send messages.



Set environment variables in docker-compose.yml:

services:
  super-spork-bot:
    build: ./super-spork
    environment:
      - DISCORD_TOKEN=your_discord_bot_token
      - DISCORD_CHANNEL_ID=1349702376763818087
      - MUMBLE_ICE_PASSWORD=password
    depends_on:
      - mumble-server
    volumes:
      - ./logs:/app/logs
    networks:
      - mumble-network
networks:
  mumble-network:

Replace your_discord_bot_token with your bot’s token.



Ensure the super-spork directory contains:





Dockerfile:

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python3", "main.py"]



requirements.txt:

discord.py
PyNaCl
zeroc-ice



MumbleServer_ice.py: Generated Ice interface file for Mumble 1.5.735.



main.py: The main bot script to load cogs (mumble.py, responce.py).



cogs/mumble.py: Handles Mumble-Discord bridging.



cogs/responce.py: Handles simple Discord commands (?hello, hi).



Build and start the bot:

cd /mnt/silver-64/opt/mumble
sudo docker compose up --build -d

3. Verify File Permissions

sudo chmod 644 /mnt/silver-64/opt/mumble/super-spork/cogs/*.py
sudo mkdir -p /mnt/silver-64/opt/mumble/logs
sudo chmod 777 /mnt/silver-64/opt/mumble/logs

Usage

Mumble-to-Discord





Connect to the Mumble server (host: your_server_ip, port: 64738, username: e.g., TG_3W3p).



Send a message in a Mumble channel (e.g., Minecraft).



Check the Discord channel (ID: 1349702376763818087) for the message, formatted as:

**TG_3W3p** in **Minecraft**: Hello from Mumble!

Discord-to-Mumble





In the Discord channel, send:

?mumble_send Test message from Discord



Check the Mumble server’s Root channel (ID 0) for the message.

Basic Commands





Send ?hello or hi in Discord to receive a response like yooooo or whats up.

Troubleshooting

Common Issues





Messages Not Appearing in Discord:





Check Logs:

sudo docker logs super-spork-bot

Look for errors in mumble.py (e.g., Error processing message).



Verify Discord Channel ID: Enable Discord Developer Mode and confirm the channel ID (1349702376763818087). Ensure the bot has permissions to send messages in the channel.



Check Mumble Ice Connection: Verify the Ice password (MUMBLE_ICE_PASSWORD) matches the server’s configuration (password). Confirm the server proxy identity is s/1:

sudo cat /mnt/silver-64/opt/mumble/super-spork/MumbleServer_ice.py | grep -A 20 "interface Server"



Mumble TextMessage Errors:





If errors occur with TextMessage attributes, verify the structure in MumbleServer_ice.py:

sudo cat /mnt/silver-64/opt/mumble/super-spork/MumbleServer_ice.py | grep -A 20 "class TextMessage"

Ensure message.channels is used (not channelId) and getChannels is called correctly.



Ice Proxy Errors:





If ObjectNotExistException occurs, confirm the server proxy identity is s/1 in mumble.py:

server = current.adapter.getCommunicator().stringToProxy("s/1:tcp -h mumble-server -p 6502 -t 60000")



Test the Ice connection manually:

sudo docker exec -it super-spork-bot python3
>>> import Ice, MumbleServer
>>> init_data = Ice.InitializationData()
>>> init_data.properties = Ice.createProperties()
>>> communicator = Ice.initialize(init_data)
>>> adapter = communicator.createObjectAdapterWithEndpoints("CallbackAdapter", "tcp -h 0.0.0.0")
>>> class ServerCallbackI(MumbleServer.ServerCallback):
...     def userTextMessage(self, state, message, current=None):
...         print(f"Message: {message.text}, User: {state.name}, Channels: {message.channels}")
...         server = current.adapter.getCommunicator().stringToProxy("s/1:tcp -h mumble-server -p 6502 -t 60000")
...         server = MumbleServer.ServerPrx.checkedCast(server)
...         channels = server.getChannels(current.ctx) if message.channels else {}
...         channel = channels.get(message.channels[0]) if message.channels and message.channels[0] in channels else None
...         print(f"Channel: {channel.name if channel else 'Unknown'}")
...     def textMessage(self, message, current=None): print(f"TextMessage: {message.text}")
...     def userConnected(self, state, current=None): print(f"Connected: {state.name}")
...     def userDisconnected(self, state, current=None): pass
...     def userStateChanged(self, state, current=None): pass
...     def channelCreated(self, state, current=None): pass
...     def channelRemoved(self, state, current=None): pass
...     def channelStateChanged(self, state, current=None): pass
>>> callback = ServerCallbackI()
>>> callback_obj = adapter.add(callback, communicator.stringToIdentity("ServerCallback"))
>>> callback_proxy = MumbleServer.ServerCallbackPrx.checkedCast(callback_obj)
>>> adapter.activate()
>>> base = communicator.stringToProxy("Meta:tcp -h mumble-server -p 6502 -t 60000")
>>> meta = MumbleServer.MetaPrx.checkedCast(base)
>>> server = meta.getServer(1, {"secret": "password"})
>>> server.addCallback(callback_proxy, {"secret": "password"})
>>> # Send a message in Mumble and check for output
>>> communicator.destroy()



File-Based Logging:





The bot logs to /app/logs/mumble_bot.log, but file-based logging may not work due to permissions. Check:

sudo docker exec super-spork-bot ls -l /app/logs
sudo ls -l /mnt/silver-64/opt/mumble/logs



Currently, logs are output to stderr (view with sudo docker logs super-spork-bot).

Known Limitations





File-Based Logging: Logs are written to stderr but may not persist in /app/logs/mumble_bot.log due to permission issues. Consider fixing by ensuring the container user has write access to /app/logs.



PyNaCl Warning: The bot logs PyNaCl is not installed, voice will NOT be supported. Voice features are not currently used, but installing PyNaCl may be required for future enhancements.



System Restart: The system may show *** System restart required ***. Reboot after confirming the bot works:

sudo reboot

Contributing





To add new features (e.g., additional Discord commands), create new cogs in the cogs/ directory and load them in main.py.



Report issues or suggest improvements by modifying the code in /mnt/silver-64/opt/mumble/super-spork.

License

This project is unlicensed and intended for private use. Modify and distribute as needed for your server.