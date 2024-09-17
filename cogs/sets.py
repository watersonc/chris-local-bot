import disnake
from disnake.ext import commands
from disnake.ui import View, Modal, TextInput
import sqlite3
from config import *

class ModalsView(Modal):
    def __init__(self, one):
        self.one = one
        components = [
            TextInput(label=Questions["Q1"], placeholder=Questions["O1"], custom_id="nameage", max_length=20),
            TextInput(label=Questions["Q2"], placeholder=Questions["O2"], custom_id="sphere", max_length=20),
            TextInput(label=Questions["Q3"], placeholder=Questions["O3"], custom_id="gender", style=disnake.TextInputStyle.paragraph, max_length=100)
        ]
        super().__init__(title=f"Заявка на {one}", components=components)

    async def callback(self, interaction):
        embed = disnake.Embed(description="> красава жди теперь пока я посмотрою заявку", color=0x2f3136)
        channel_id = CLAN_NABOR if self.one == 'CLAN' else FAMILY_NABOR
        channel = disnake.utils.get(interaction.guild.text_channels, id=channel_id)
        
        if channel:
            await channel.send(f'<@{interaction.author.id}>', embed=SetsEmbed(interaction, self.one))
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message('Канал не найден.', ephemeral=True)

class SelectSets(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @disnake.ui.select(
        custom_id='set',
        min_values=1,
        max_values=1,
        placeholder='левая или правая палочка твикс',
        options=[
            disnake.SelectOption(label='CLAN', description='умолять меня пустить тебя в клан', emoji=EMO, value='cln'),
            disnake.SelectOption(label='FAMILY', description='умолять тебя пустить меня в семью', emoji=EMO, value='fam')
        ]
    )
    async def select_callback(self, select: disnake.ui.Select, inter: disnake.MessageInteraction):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        table = "memberscln" if inter.values[0] == 'cln' else "familycln"
        role_id = clnid if inter.values[0] == 'cln' else famid
        
        cursor.execute(f"SELECT user_id FROM {table} WHERE user_id = ?", (inter.author.id,))
        result = cursor.fetchone()
        
        if result:
            await inter.response.send_message("ты уже в клане" if inter.values[0] == 'cln' else "ты уже в семье", ephemeral=True)
        else:
            await inter.response.send_modal(ModalsView('CLAN' if inter.values[0] == 'cln' else 'FAMILY'))
        
        conn.close()

class SetsEmbed(disnake.Embed):
    def __init__(self, interaction, two):
        super().__init__(
            title=f"менчик кунчик просится в {two}",
            description=f"ID: **{interaction.author.id}**\nПользователь: **{interaction.author.name}**\n",
            color=0x2b2d31,
        )
        self.add_field(name=Questions["Q1"], value=interaction.text_values['nameage'])
        self.add_field(name=Questions["Q2"], value=interaction.text_values['sphere'], inline=False)
        self.add_field(name=Questions["Q3"], value=interaction.text_values['gender'], inline=False)
        self.add_field(name="ㅤ", value=f"чтобы принять заявку - **/action {interaction.author.id}**", inline=False)

class SetsAnnounce(disnake.Embed):
    def __init__(self):
        super().__init__(
            description='',
            color=disnake.Color.from_rgb(47, 49, 54),
        )
        self.set_image(url=NABOR_ICON)

class SetsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(NABOR_CHANNEL)
        if not channel:
            return
        
        last_message = await channel.history(limit=1).find(lambda m: m.author == self.bot.user)
        view = SelectSets()
        announce_embed = SetsAnnounce()
        
        if last_message:
            await last_message.edit(embed=announce_embed, view=view)
        else:
            await channel.send(embed=announce_embed, view=view)

def setup(bot):
    bot.add_cog(SetsCommand(bot))
    print("setter loaded!")
