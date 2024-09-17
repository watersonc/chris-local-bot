import disnake
from disnake.ext import commands
from disnake.ui import View
import sqlite3
from config import DATABASE, verify_role, noverify_role, GUARD_LOGS, GUARD_CHANNEL

class GuardAnnounce(disnake.Embed):
    def __init__(self):
        super().__init__(
            title=" ***  йо  ***",
            color=disnake.Color.from_rgb(43, 45, 49),
        )

class GuardButton(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @disnake.ui.button(label="ㅤ", style=disnake.ButtonStyle.gray, custom_id="grd")
    async def guardbtn(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        role = disnake.utils.get(interaction.guild.roles, id=verify_role)
        delrole = disnake.utils.get(interaction.guild.roles, id=noverify_role)

        cursor.execute("SELECT left FROM verified WHERE user_id = ?", (interaction.author.id,))
        result = cursor.fetchone()
        
        if result is None:
            cursor.execute("INSERT INTO verified (user_id, left) VALUES (?, ?)", (interaction.author.id, 1))
            await interaction.response.send_message("давай, друг, пока. до встречи на той стороне!!", ephemeral=True)
            await interaction.author.add_roles(role)
            await interaction.author.remove_roles(delrole)
            print(f"{interaction.author.name} верифицировался на сервере первый раз.")
            
            channel = disnake.utils.get(interaction.guild.text_channels, id=GUARD_LOGS)
            if channel:
                await channel.send(f"<@{interaction.author.id}> ({interaction.author.name}) верифицировался на сервере первый раз")
            else:
                await interaction.followup.send('Канал не найден.', ephemeral=True)
        else:
            cursor.execute("UPDATE verified SET left = left + 1 WHERE user_id = ?", (interaction.author.id,))
            await interaction.response.send_message("у тебя есть всего 5 перезаходов на сервер, на шестой даётся локал бан", ephemeral=True)
            print(f"{interaction.author.name} перезашёл на сервер {result[0]} раз.")
            await interaction.author.add_roles(role)
            await interaction.author.remove_roles(delrole)
            channel = disnake.utils.get(interaction.guild.text_channels, id=GUARD_LOGS)
            if channel:
                await channel.send(f"<@{interaction.author.id}> ({interaction.author.name}) перезашёл на сервер {result[0]} раз")
            else:
                await interaction.followup.send('Канал не найден.', ephemeral=True)
                
        conn.commit()
        conn.close()

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
            await channel.purge(limit=10)
        
        await channel.send(embed=announce_embed, view=view)
        await channel.send("тапайте кнопочку, мужики <@&1258754004284870726>")

def setup(bot):
    bot.add_cog(GuardCommand(bot))
    print("guardian loaded!")
