import Ice
import MumbleServer
import discord
from discord.ext import commands, tasks
import asyncio
import os

class MumbleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.communicator = None
        self.adapter = None
        self.channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))  # Discord channel ID
        self.ice_password = os.getenv('MUMBLE_ICE_PASSWORD', 'password')  # Ice secret
        self.start_ice.start()

    def cog_unload(self):
        self.start_ice.cancel()
        if self.adapter:
            self.adapter.deactivate()
        if self.communicator:
            self.communicator.destroy()

    @tasks.loop(count=1)
    async def start_ice(self):
        try:
            self.communicator = Ice.initialize()
            self.adapter = self.communicator.createObjectAdapterWithEndpoints(
                "CallbackAdapter", "tcp -h 127.0.0.1"
            )
            callback = ServerCallbackI(self.bot, self.channel_id)
            callback_obj = self.adapter.addWithUUID(callback)
            self.adapter.activate()

            base = self.communicator.stringToProxy("Meta:tcp -h mumble-server -p 6502 -t 60000")
            meta = MumbleServer.MetaPrx.checkedCast(base)
            if not meta:
                print("Failed to connect to Mumble Meta")
                return

            context = {"secret": self.ice_password}
            server = meta.getServer(1, context)  # Server ID 1
            if not server:
                print("Failed to get Mumble server")
                return

            server.addCallback(callback_obj, context)
            print("Mumble callback registered successfully")
        except Exception as e:
            print(f"Mumble setup error: {e}")

    @start_ice.before_loop
    async def before_start_ice(self):
        await self.bot.wait_until_ready()

class ServerCallbackI(MumbleServer.ServerCallback):
    def __init__(self, bot, channel_id):
        self.bot = bot
        self.channel_id = channel_id

    async def send_to_discord(self, message, sender_name, channel_name):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            formatted_message = f"**{sender_name}** in **{channel_name}**: {message}"
            await channel.send(formatted_message)
        else:
            print(f"Discord channel {self.channel_id} not found")

    def textMessage(self, message, current=None):
        sender_id = message.actor
        server = current.adapter.getCommunicator().stringToProxy(
            f"Server/1:tcp -h mumble-server -p 6502 -t 60000"
        )
        server = MumbleServer.ServerPrx.checkedCast(server)
        sender = server.getUser(sender_id, current.ctx)
        sender_name = sender.name if sender else "Unknown"

        channel_id = message.channelId[0] if message.channelId else -1
        channel = server.getChannel(channel_id, current.ctx) if channel_id != -1 else None
        channel_name = channel.name if channel else "Unknown"

        asyncio.run_coroutine_threadsafe(
            self.send_to_discord(message.text, sender_name, channel_name),
            self.bot.loop
        )

    # Implement other callback methods to avoid errors
    def userConnected(self, state, current=None): pass
    def userDisconnected(self, state, current=None): pass
    def userStateChanged(self, state, current=None): pass
    def channelCreated(self, state, current=None): pass
    def channelRemoved(self, state, current=None): pass
    def channelStateChanged(self, state, current=None): pass

async def setup(bot):
    await bot.add_cog(MumbleCog(bot))