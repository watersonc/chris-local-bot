import disnake
from disnake.ext import commands
from config import *


class JoinRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if role := member.guild.get_role(noverify_role):
            await member.add_roles(role)


def setup(bot):
    bot.add_cog(JoinRoles(bot))
    print("joinroles activated!")