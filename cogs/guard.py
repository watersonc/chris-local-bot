import disnake
from disnake.ext import commands
from Utils import GuardAnnounce
from Utils import GuardButton
from config import *


class GuardCommand(commands.Cog):
    def __init__(self, bot):
        super().__init__(timeout=None)
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
            await channel.purge(limit=10)
            await channel.send(embed=announce_embed,view=view)
            await channel.send("тапайте кнопочку, мужики <@&1258754004284870726>")
        else:
            await channel.send(embed=announce_embed,view=view)
            
def setup(bot):
    bot.add_cog(GuardCommand(bot))
    print("guardian activated!")