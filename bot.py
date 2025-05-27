import discord
from discord.ext import commands
from math import *
import os
import asyncio
from deckviewer import show_deckimg


intents = discord.Intents.all()
intents.messages = True

DATABASE_URL = os.environ['DATABASE_URL']

bot = commands.Bot(command_prefix='!', intents=intents)

c = comb

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました。')

@bot.event
async def on_message(ctx, *, message=None):
    if message.author == bot.user:
        return
    if bot.user in message.mentions:
        message = eval(message.strip().replace("　"," "))
        await ctx.send(message)

    # 他のon_messageイベントをオーバーライドしないようにこれを追加
    await bot.process_commands(message)

@bot.command()
async def c(ctx, *, message=None):
    message = eval(message.strip().replace("　"," "))
    await ctx.send(message)


@bot.command()
async def deckimg(ctx, *, message):
    print("deckimg start")
    await show_deckimg(ctx, message)
    print("deckimg done")


async def main():
    await bot.start(os.environ['DISCORD_BOT_TOKEN'])

asyncio.run(main())
