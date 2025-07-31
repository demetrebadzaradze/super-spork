import Ice
import MumbleServer
import discord
from discord.ext import commands, tasks
import asyncio
import os
import logging

# Set up logging to both file and stderr
log_dir = '/app/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir, mode=0o777)
file_handler = logging.FileHandler('/app/logs/mumble_bot.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
file_handler.flush = True
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        file_handler,
        logging.StreamHandler()
    ]
)
logging.debug("Testing mumble log file creation")
logging.getLogger().handlers[0].flush()

class MumbleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.communicator = None
        self.adapter = None
        try:
            self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
        except (ValueError, TypeError) as e:
            logging.error(f"Invalid DISCORD_CHANNEL_ID: {os.getenv('DISCORD_CHANNEL_ID')}, error: {e}")
            raise
        self.ice_password = os.getenv('MUMBLE_ICE_PASSWORD', 'password')
        logging.debug("MumbleCog initialized")
        self.start_ice.start()

    def cog_unload(self):
        logging.debug("Unloading MumbleCog")
        self.start_ice.cancel()
        if self.adapter:
            self.adapter.deactivate()
        if self.communicator:
            self.communicator.destroy()

    @tasks.loop(count=1)
    async def start_ice(self):
        try:
            logging.debug("Starting Ice communicator")
            props = Ice.createProperties()
            props.setProperty("Ice.MessageSizeMax", "1024")
            props.setProperty("Ice.Trace.Network", "2")
            props.setProperty("Ice.Trace.Protocol", "1")
            init_data = Ice.InitializationData()
            init_data.properties = props
            self.communicator = Ice.initialize(init_data)
            self.adapter = self.communicator.createObjectAdapterWithEndpoints(
                "CallbackAdapter", "tcp -h 0.0.0.0"
            )
            callback = ServerCallbackI(self.bot, self.channel_id)
            callback_obj = self.adapter.add(callback, self.communicator.stringToIdentity("ServerCallback"))
            callback_proxy = MumbleServer.ServerCallbackPrx.checkedCast(callback_obj)
            if not callback_proxy:
                logging.error("Failed to cast callback_obj to ServerCallbackPrx")
                return
            self.adapter.activate()
            logging.debug(f"Ice adapter activated, callback proxy: {callback_proxy}")
            logging.debug(f"Callback proxy interfaces: {callback_proxy.ice_id()}")

            base = self.communicator.stringToProxy("Meta:tcp -h mumble-server -p 6502 -t 60000")
            meta = MumbleServer.MetaPrx.checkedCast(base)
            if not meta:
                logging.error("Failed to connect to Mumble Meta")
                return

            context = {"secret": self.ice_password}
            server = meta.getServer(1, context)
            if not server:
                logging.error("Failed to get Mumble server")
                return

            logging.debug(f"Registering callback with server: {server}")
            server.addCallback(callback_proxy, context)
            logging.info("Mumble callback registered successfully")
        except Exception as e:
            logging.error(f"Mumble setup error: {e}", exc_info=True)

    @start_ice.before_loop
    async def before_start_ice(self):
        await self.bot.wait_until_ready()
        logging.debug("Waiting for bot to be ready")

class ServerCallbackI(MumbleServer.ServerCallback):
    def __init__(self, bot, channel_id):
        MumbleServer.ServerCallback.__init__(self)
        self.bot = bot
        self.channel_id = channel_id
        logging.debug("ServerCallbackI initialized")

    async def send_to_discord(self, message, sender_name, channel_name):
        try:
            channel = self.bot.get_channel(self.channel_id)
            if channel:
                formatted_message = f"**{sender_name}** in **{channel_name}**: {message}"
                await channel.send(formatted_message)
                logging.info(f"Sent to Discord: {formatted_message}")
                logging.getLogger().handlers[0].flush()
            else:
                logging.error(f"Discord channel {self.channel_id} not found")
        except Exception as e:
            logging.error(f"Error sending to Discord: {e}", exc_info=True)

    def textMessage(self, message, current=None):
        logging.debug(f"Received Mumble textMessage: {message.text}")
        self._handle_message(None, message, current)

    def userTextMessage(self, state, message, current=None):
        logging.debug(f"Received Mumble userTextMessage: {message.text}, from user: {state.name}")
        self._handle_message(state, message, current)

    def _handle_message(self, state, message, current):
        try:
            sender_name = state.name if state else "Unknown"
            channel_id = message.channels[0] if message.channels else -1
            server = current.adapter.getCommunicator().stringToProxy(
                f"s/1:tcp -h mumble-server -p 6502 -t 60000"
            )
            server = MumbleServer.ServerPrx.checkedCast(server)
            if not server:
                logging.error("Failed to get Mumble server proxy")
                return
            channel = server.getChannel(channel_id, current.ctx) if channel_id != -1 else None
            channel_name = channel.name if channel else "Unknown"

            asyncio.run_coroutine_threadsafe(
                self.send_to_discord(message.text, sender_name, channel_name),
                self.bot.loop
            )
        except Exception as e:
            logging.error(f"Error processing message: {e}", exc_info=True)

    def userConnected(self, state, current=None): logging.debug(f"User connected: {state.name}")
    def userDisconnected(self, state, current=None): logging.debug(f"User disconnected: {state.name}")
    def userStateChanged(self, state, current=None): logging.debug(f"User state changed: {state.name}")
    def channelCreated(self, state, current=None): logging.debug(f"Channel created: {state.name}")
    def channelRemoved(self, state, current=None): logging.debug(f"Channel removed: {state.name}")
    def channelStateChanged(self, state, current=None): logging.debug(f"Channel state changed: {state.name}")

async def setup(bot):
    await bot.add_cog(MumbleCog(bot))