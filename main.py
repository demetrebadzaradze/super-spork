import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        await bot.load_extension('cogs.responce')
        await bot.load_extension('cogs.mumble')
        print("Cogs loaded successfully")
    except Exception as e:
        print(f"Error loading cogs: {e}")

bot.run(TOKEN)