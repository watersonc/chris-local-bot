import disnake
from disnake.ext import commands
import sqlite3
from config import DATABASE

class Database(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.create_table()

    def create_table(self):
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            tables = {
                "memberscln": """
                    CREATE TABLE IF NOT EXISTS memberscln (
                        user_id INTEGER PRIMARY KEY,
                        user TEXT,
                        added INTEGER
                    )
                """,
                "familycln": """
                    CREATE TABLE IF NOT EXISTS familycln (
                        user_id INTEGER PRIMARY KEY,
                        user TEXT,
                        added INTEGER
                    )
                """,
                "verified": """
                    CREATE TABLE IF NOT EXISTS verified (
                        user_id INTEGER PRIMARY KEY,
                        left INTEGER
                    )
                """,
                "banned_users": """
                    CREATE TABLE IF NOT EXISTS banned_users (
                        user_id INTEGER PRIMARY KEY,
                        reason TEXT
                    )
                """,
            }
            for table in tables.values():
                cursor.execute(table)
            conn.commit()

def setup(client):
    client.add_cog(Database(client))
    print("databases loaded!")
