import os
import disnake
from disnake.ext import commands
from config import TOKEN, GUILD_ID

bot = commands.Bot(command_prefix="ch!", intents=disnake.Intents.all(), test_guilds=[GUILD_ID])

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(TOKEN)
