import discord
from discord.ext import commands
from random import choice, randint
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/responce.log'),
        logging.StreamHandler()
    ]
)

class ResponceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logging.debug("ResponceCog initialized")

    @commands.command()
    async def hello(self, ctx):
        responses = ['hello', 'hi', 'heyy', 'yooooo', 'whats up']
        await ctx.send(choice(responses))
        logging.info(f"Sent response: {ctx.message.content}")

    @commands.command()
    async def gamble(self, ctx):
        number = randint(1, 6)
        await ctx.send(f"your number is {number}")
        logging.info(f"Gamble result: {number}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        content = message.content.lower()
        if content in ['hello', 'hi', 'hey']:
            responses = ['hello', 'hi', 'heyy', 'yooooo', 'whats up']
            await message.channel.send(choice(responses))
            logging.info(f"Responded to {content} with {responses}")
        elif content == 'gamble':
            number = randint(1, 6)
            await message.channel.send(f"your number is {number}")
            logging.info(f"Gamble result: {number}")

async def setup(bot):
    await bot.add_cog(ResponceCog(bot))
    logging.info("ResponceCog loaded")