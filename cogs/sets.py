import disnake
from disnake.ext import commands
from Utils import SelectSets
from Utils import SetsAnnounce
from config import *

class SetsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        channel = self.bot.get_channel(NABOR_CHANNEL)
        
        if not channel:
            return
        last_message = await channel.history(limit=1).find(lambda m: m.author == self.bot.user)
        select_view = SelectSets()
        announce_embed = SetsAnnounce()
        
        if last_message:
            await last_message.edit(embed=announce_embed, view=select_view)
        else:
            await channel.send(embed=announce_embed, view=select_view)

def setup(bot):
    bot.add_cog(SetsCommand(bot))
    print("СИСТЕМА ГОТОВА НА ВЗЛЁТ ТРЕШ ЖЕСТЬ ОМГ")
