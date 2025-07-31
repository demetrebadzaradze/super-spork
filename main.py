import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

# Set up logging to both file and stderr
log_dir = '/app/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/bot.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()
TOKEN = os.getenv('TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
MUMBLE_ICE_PASSWORD = os.getenv('MUMBLE_ICE_PASSWORD')

logging.debug(f"TOKEN: {'set' if TOKEN else 'not set'}")
logging.debug(f"DISCORD_CHANNEL_ID: {DISCORD_CHANNEL_ID}")
logging.debug(f"MUMBLE_ICE_PASSWORD: {MUMBLE_ICE_PASSWORD}")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'{bot.user} has connected to Discord!')
    try:
        logging.debug("Loading cogs...")
        await bot.load_extension('cogs.responce')
        await bot.load_extension('cogs.mumble')
        logging.info("Cogs loaded successfully")
    except Exception as e:
        logging.error(f"Error loading cogs: {e}", exc_info=True)

try:
    bot.run(TOKEN)
except Exception as e:
    logging.error(f"Error running bot: {e}", exc_info=True)