import discord
from discord.ext import commands
from math import *
import os
import asyncio
from deckviewer import show_deckimg


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

c = comb

@bot.event
async def on_ready():
    print(f'{bot.user} としてログインしました。')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user in message.mentions:
        content = message.content.replace(f'<@{bot.user.id}>', '').strip()
        try:
            result = eval(content.replace("　"," "))
            await message.channel.send(result)
        except Exception as e:
            await message.channel.send(f"計算エラー: {e}")

    # 他のon_messageイベントをオーバーライドしないようにこれを追加
    await bot.process_commands(message)

@bot.command()
async def c(ctx, *, message=None):
    if message is None:
        await ctx.send("計算式を入力してください。")
        return
    try:
        result = eval(message.strip().replace("　"," "))
        await ctx.send(result)
    except Exception as e:
        await ctx.send(f"計算エラー: {e}")


@bot.command()
async def deckimg(ctx, *, message):
    print("deckimg start")
    await show_deckimg(ctx, message)
    print("deckimg done")


async def main():
    await bot.start(os.environ['DISCORD_BOT_TOKEN'])

asyncio.run(main())
