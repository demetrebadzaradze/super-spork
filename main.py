from typing import Final
import asyncio
import os
from dotenv import load_dotenv
from discord import Intents, Message
from discord.ext import commands
import responce  # Assuming this is your custom response module
from flask import Flask
from threading import Thread

# Create a Flask web server
app = Flask(__name__)

# Load environment variables
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_BOT_TOKEN")

# Set up intents
intents: Intents = Intents.default()
intents.message_content = True  # Required to read messages

# Create a bot instance with a command prefix
bot = commands.Bot(command_prefix="/", intents=intents)

async def Send_Message(message: Message, user_message: str) -> None:
    if not user_message:
        print("Message is empty due to invalid setup")
        return

    is_private = user_message.startswith("?")
    if is_private:
        user_message = user_message[1:]  # Remove '?' from message

    try:
        response: str = responce.responde(user_message)  # Get response from custom module
        if response == 'exit':
            return
        if is_private:
            await message.author.send(response)  # Send private message
        else:
            await message.channel.send(response)  # Send public message
    except Exception as e:
        print(e)

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

# Event: Handle messages (Custom message responses)
@bot.event
async def on_message(msg: Message):
    if msg.author == bot.user:
        return  # Ignore bot messages

    username: str = str(msg.author)
    content: str = str(msg.content)
    channel: str = str(msg.channel)

    print(f'[{channel}] {username}: "{content}"')
    await Send_Message(msg, content)

    await bot.process_commands(msg)  # Ensure commands still work

# Example Command: /hello
@bot.command()
async def hello(ctx):
    await ctx.send("Hello! 👋")

@bot.command()
async def spam(ctx, string: str ,x: int):
    if x > 20:
        x = 20
    for _ in range(x):
        await ctx.send(string)
        await asyncio.sleep(1)


def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()
