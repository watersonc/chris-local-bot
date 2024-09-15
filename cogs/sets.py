import disnake
from disnake.ext import commands
from Utils import SelectSets
from Utils import SetsAnnounce
from Utils import SetsAnnounce1
from config import *

class SetsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):

        channel = self.bot.get_channel(NABOR_CHANNEL)
        
        if not channel:
            return
        main_embed = SetsAnnounce1()
        select_view = SelectSets()

        announce_embed = SetsAnnounce()
        await channel.send(embed=announce_embed, view=select_view)
        await channel.send(embed=main_embed, view=select_view)

def setup(bot):
    bot.add_cog(SetsCommand(bot))
    print("СИСТЕМА ГОТОВА НА ВЗЛЁТ ТРЕШ ЖЕСТЬ ОМГ")
