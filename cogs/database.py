import disnake
from disnake.ext import commands, tasks
import sqlite3
import time
from config import *

class Database(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nabor (
                user_id INTEGER,
                number INTEGER
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memberscln (
                user_id INTEGER,
                name TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS familycln (
                user_id INTEGER,
                name TEXT
            )
            """
        )
        conn.commit()

def setup(client):
    client.add_cog(Database(client))
    print("БД работает.")
