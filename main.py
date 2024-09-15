import os
import ssl
import json
import time
from config import *
import sqlite3

from multiprocessing import Process, freeze_support

import disnake
from disnake.ext import commands


bot = commands.Bot(command_prefix="ch!", intents=disnake.Intents.all(), test_guilds=[1258009098125971601])

if __name__ == "__main__":
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(TOKEN)