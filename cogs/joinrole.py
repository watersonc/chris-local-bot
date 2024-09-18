import disnake
from disnake.ext import commands
import sqlite3
from config import DATABASE, localban_role, noverify_role  # Добавьте unverify_role в импорт

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
            # Исключаем роль @everyone
            everyone_role = member.guild.id
            roles_to_remove = [role for role in member.roles if role.id != everyone_role]
            await member.remove_roles(*roles_to_remove, reason="user left 5 times")
            
            ban_role = disnake.utils.get(member.guild.roles, id=localban_role)
            if ban_role:
                await member.add_roles(ban_role, reason="user left 5 times")
        else:
            # Добавление роли unverify_role при заходе на сервер
            unverify_role_obj = disnake.utils.get(member.guild.roles, id=noverify_role)
            if unverify_role_obj:
                await member.add_roles(unverify_role_obj, reason="Assigned unverified role on join")
        
        
        conn.close()

def setup(bot):
    bot.add_cog(JoinRoles(bot))
    print("JoinRoles loaded!")
