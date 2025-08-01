# Super-Spork
This project provides a bot that forwards text messages from Mumble server running in the docker with compose (version 1.5.735) to a Discord server. it is not a plug and play like just adding the bot to Discord and be done. it is more of making your own discord bot and running this project as docker to use the bot as a one way bridge for now.

this is very bare bone project as you can tell and will improve lattes if gets any users.

  

# Features

- Mumble-to-Discord: Forwards messages from Mumble channels to a Discord channel, including the sender's name and channel name (e.g., **TG_3W3p** in **Minecraft**: Hello from Mumble!).

- Basic Discord Commands: Responds to simple commands like ?hello or hi with responses like `yooooo` or `whats` up (via the responce.py cog), and can gamble too.

# Prerequisites
- System: Ubuntu 24.04.1 LTS (or compatible Linux distribution), but since it runs in the docker you could make it work anywhere.
- Docker: Docker and Docker Compose installed (`sudo apt install docker.io docker-compose`).
- Mumble Server: Version 1.5.735 running in a Docker container.
- Python: Version 3.12 (included in the bot's Docker image).
- Dependencies: Listed in requirements.txt (e.g., `discord.py`, `zeroc-ice` for Ice communication).
- Discord Bot Token: create your own discord bot and Obtain its token from the Discord Developer Portal.
- Mumble Ice Password: this should be same as `MUMBLE_CONFIG_SERVERPASSWORD` from mumble server.
- Discord Channel ID: The ID of the Discord channel where Mumble messages are forwarded (e.g., `1349705376263418589`).

# Setup Instructions

Directory Structure should look like this
``` plain
├── .env (same file as in super-spork)
├── docker-compose.yml
├── data/
├── logs/
└── super-spork/
    ├── .env
    ├── cogs/
    │   ├── mumble.py
    │   ├── responce.py
    ├── Dockerfile
    ├── MumbleServer_ice.py
    ├── main.py
    └── requirements.txt
```
for that:
1. clone the `super-spork` directory where  mumble server compose file is. go to the correct directory(e.g. `cd /mnt/silver-64/opt/mumble/`) and clone the repo
```bash
	  git clone https://github.com/demetrebadzaradze/super-spork.git
```

2. **make a discord bot**
	  1. go to [discord developer portal](https://discord.com/developers/applications)
	  2. create new application and give it a name
	  3. configure it as you would like in general (e.g. add a picture, description, etc.)
	  4. go over in the `bot` section and note the bot token (reset if not present)
	  5. then add the bot to the server with a [generated link,](https://discordjs.guide/preparations/adding-your-bot-to-servers.html#creating-and-using-your-invite-link)   for permeations it should work with: 
		  `View Channels`, `Send Messages` , `Manage Messages`, `Read Message History`.
		  I checked `admin` witch is not recommended but it works if you cant get it working other way.  and also you can send this link to owner of another server and they could add it to server that you don't own.

3. **Configure the Mumble Server**
Ensure the Mumble server is running in a Docker container with Ice enabled:
**template `compose.yml` file for `mumbe` server and `super-spork` bot **
```yml
services:
    mumble-server:
        image: mumblevoip/mumble-server:latest
        container_name: mumble-server
        hostname: <replace this with your hostname>
        restart: on-failure
        ports:
            - 64738:64738
            - 64738:64738/udp
            - 6502:6502
        volumes:
            - ./data/:/data
        environment:
            MUMBLE_CONFIG_WELCOMETEXT: <replace this with your welcome text> 
            MUMBLE_CONFIG_PORT: 64738
            MUMBLE_CONFIG_USERS: <replace this with max users for server>
            MUMBLE_CONFIG_ICE: "tcp -h 0.0.0.0 -p 6502"
            MUMBLE_CONFIG_SERVERPASSWORD: <replace this with your server password witch will be also needed in .env file>
            MUMBLE_SUPERUSER_PASSWORD: <replace this with your SuperUser password>
        expose:
            - 6502
        networks:
            - mumble-network

    super-spork-bot:
        build:
            context: ./super-spork/.
            dockerfile: Dockerfile
        container_name: super-spork-bot
        restart: on-failure
        environment:
            - TOKEN=${TOKEN}
            - DISCORD_CHANNEL_ID=${DISCORD_CHANNEL_ID}
            - MUMBLE_ICE_PASSWORD=${MUMBLE_ICE_PASSWORD}
        volumes:
            - ./super-spork:/app
            - ./logs:/app/logs
        depends_on:
            - mumble-server
        networks:
            - mumble-network
networks:
    mumble-network:
        driver: bridge
```
  
  
  4. **configure `.env` file**
  this env file should be in the `super-spork` directory and where `compose.yml` file is and this is how it should look like: (replace descriptions in quotes with actual values)
```env
	  TOKEN="this should be set to your discord bot's token"
	  DISCORD_CHANNEL_ID="id of a channel where messages will be sent bot should be added in that server too"
	  MUMBLE_ICE_PASSWORD="whatever is configured as MUMBLE_CONFIG_SERVERPASSWORD in mumble configuration"
```

5. **Build and run the container**
	go to directory where `compose.yml` file is and run: 
	```bash
	sudo docker compose up --build
	```
	use `-d` for detached mode.
6. **Test**
when any message is sent in the `mumble` text chat it will also be send in the `discord` channel like this :
```markdown
**TG_3W3p** in **Minecraft**: hello world
```

## Contributing

- Add new features by creating cogs in super-spork/cogs/ and updating main.py.
- Report issues or suggest improvements by modifying the code.

## License

This project is licensed under the MIT License. See the LICENSE file for details.