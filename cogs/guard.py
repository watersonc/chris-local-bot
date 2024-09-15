import disnake
from disnake.ext import commands
from Utils import GuardAnnounce
from Utils import GuardButton
from config import *


class GuardCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        channel = self.bot.get_channel(GUARD_CHANNEL)
        
        if not channel:
            return
        last_message = await channel.history(limit=1).find(lambda m: m.author == self.bot.user)
        view = GuardButton()
        announce_embed = GuardAnnounce()
        
        if last_message:
            await last_message.edit(embed=announce_embed, view=view)
        else:
            await channel.send(embed=announce_embed, view=view)

def setup(bot):
    bot.add_cog(GuardCommand(bot))
    print("Верификация включена.")