import disnake
from disnake.ext import commands
import sqlite3
from config import DATABASE, localban_role

class JoinRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT left FROM verified WHERE user_id = ?", (member.id,))
        result = cursor.fetchone()
        
        if result and result[0] >= 5:
            roles_to_remove = [role for role in member.roles if role.id != disnake.Object(id=member.guild.id).id]  # Исключаем роль @everyone
            await member.remove_roles(*roles_to_remove, reason="user left 5 times")
            
            ban_role = disnake.utils.get(member.guild.roles, id=localban_role)
            if ban_role:
                await member.add_roles(ban_role, reason="user left 5 times")

        conn.close()

def setup(bot):
    bot.add_cog(JoinRoles(bot))
    print("joinroles loaded!")
