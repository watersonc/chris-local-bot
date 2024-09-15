import disnake
from disnake.ext import commands
from config import *
from disnake.ui import Button, View
import sqlite3


class GuardAnnounce(disnake.Embed):
    def __init__(self):
        super().__init__(
            title=" ***  йо  ***",
            color=disnake.Color.from_rgb(43, 45, 49),
        )

class SetsAnnounce(disnake.Embed):
    def __init__(self):
        super().__init__(
            description=(
                ''
            ),
            color=disnake.Color.from_rgb(47, 49, 54),
        )
        self.set_image(url=f'{NABOR_ICON}')

class GuardButton(View):
    def __init__(self):
        super().__init__()
    @disnake.ui.button(label="ㅤ",style=disnake.ButtonStyle.gray, custom_id="grd")
    async def yes_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        role = disnake.utils.get(interaction.guild.roles, id=verify_role)
        delrole = disnake.utils.get(interaction.guild.roles, id=noverify_role)
        await interaction.response.send_message("давай, друг, пока. до встречи на той стороне!!", ephemeral=True)
        await interaction.author.add_roles(role)
        await interaction.author.remove_roles(delrole)

class ModalsView(disnake.ui.Modal):
    def __init__(self, one):
        self.one = one
        components = [
            disnake.ui.TextInput(
                label=f"{Q1}", 
                placeholder=f"{O1}", 
                custom_id="nameage", 
                max_length=20,
            ),
            disnake.ui.TextInput(
                label=f"{Q2}", 
                placeholder=F"{O2}", 
                custom_id="sphere", 
                max_length=20,
            ),
            disnake.ui.TextInput(
                label=f"{Q3}", 
                placeholder=F"{O3}", 
                custom_id="gender", 
                style=disnake.TextInputStyle.paragraph,
                max_length=100,
            ),
        ]
        super().__init__(title=f"Заявка на {one}", components=components)

    async def callback(self, interaction) -> None:
        embed = disnake.Embed(description="> красава жди теперь пока я посмотрою заявку", color=0x2f3136)
        if self.one == 'CLAN':
            
            channel_id = CLAN_NABOR
            channel = None
            if channel_id is not None:
                channel = disnake.utils.get(interaction.guild.text_channels, id=channel_id)
            if channel is not None:
                view = buttonscln()
                await channel.send(f'<@{interaction.author.id}>', embed=SetsEmbed(interaction,self.one), view=view)
                await interaction.response.send_message(embed=embed, ephemeral=True)

            else:
                await interaction.response.send_message('Канал не найден.', ephemeral=True)
                
        if self.one == 'FAMILY':
            channel_id = FAMILY_NABOR
            channel = None
            if channel_id is not None:
                channel = disnake.utils.get(interaction.guild.text_channels, id=channel_id)
            if channel is not None:
                view = buttonsfam()
                await channel.send(f'<@{interaction.author.id}>', embed=SetsEmbed(interaction,self.one), view=view)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message('Канал не найден.', ephemeral=True)


class SelectSets(disnake.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
    
    @disnake.ui.select(
        custom_id='set',
        min_values=1,
        max_values=1,
        placeholder='левая или правая палочка твикс',
        options=[
            disnake.SelectOption(
                label='CLAN',
                description='умолять меня пустить тебя в клан',
                emoji=F'{EMO}',
                value='cln'
            ),
            disnake.SelectOption(
                label='FAMILY',
                description='умолять тебя пустить меня в семью',
                emoji=F'{EMO}',
                value='fam'
            ),
        ]
    )
    async def select_callback(self, select: disnake.ui.Select, inter):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        if inter.values[0] == 'cln':
            cursor.execute("INSERT INTO nabor (user_id, number) VALUES (?, ?)", (inter.author.id, 0))
            conn.commit()
            await inter.response.send_modal(modal=ModalsView('CLAN'))
        elif inter.values[0] == 'fam':
            cursor.execute("INSERT INTO nabor (user_id, number) VALUES (?, ?)", (inter.author.id, 0))
            conn.commit()
            await inter.response.send_modal(modal=ModalsView('FAMILY'))
        else:
            pass

class SetsEmbed(disnake.Embed):
    def __init__(self, interaction, two):
        super().__init__(
            title=f"менчик кунчик просится в {two}",
            description=f"ID: **{interaction.author.id}**\nПользователь: **{interaction.author.name}**\n",
            color=disnake.Color.from_rgb(47, 49, 54),
        )
        self.add_field(name=F"{Q1}", value=f"{interaction.text_values['nameage']}")
        self.add_field(name=F"{Q2}", value=f"{interaction.text_values['sphere']}", inline=False)
        self.add_field(name=f"{Q3}", value=f"{interaction.text_values['gender']}", inline=False)



class buttonscln(View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green, custom_id="пр")
    async def yes_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        role = disnake.utils.get(interaction.guild.roles, id=clnid)
        await interaction.response.send_message("хорош, нормального мужика принял", ephemeral=True)
        await interaction.author.add_roles(role)
        embed = disnake.Embed(description="тя приняли в chris/cln ты счастлив да ", color=disnake.Color.from_rgb(47, 49, 54))
        embed.set_thumbnail(url=interaction.author.avatar.url)
        embed.set_author(name="chris waterson:", icon_url=IMAGE)
        await interaction.author.send(embed=embed)
        cursor.execute("DELETE FROM nabor WHERE user_id = ?", (interaction.author.id,))
        cursor.execute("INSERT INTO memberscln (user_id, name) VALUES (?, ?)", (interaction.author.id,interaction.author.name))
        conn.commit()

    @disnake.ui.button(label="Отклонить", style=disnake.ButtonStyle.red, custom_id="от")
    async def no_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nabor WHERE user_id = ?", (interaction.author.id,))
        await interaction.message.delete()
        conn.commit()

class buttonsfam(View):
    def __init__(self):
        super().__init__()

    @disnake.ui.button(label="Принять", style=disnake.ButtonStyle.green, custom_id="пр")
    async def yes_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        role = disnake.utils.get(interaction.guild.roles, id=famid)
        await interaction.response.send_message("зншаю твоих родителей хорошие мужики убил бы тебя вот за эту хуйню", ephemeral=True)
        await interaction.author.add_roles(role)
        embed = disnake.Embed(description="тя приняли в chris/fam зайка красавица", color=disnake.Color.from_rgb(47, 49, 54))
        embed.set_thumbnail(url=interaction.author.avatar.url)
        embed.set_author(name="chris family:", icon_url=IMAGE)
        await interaction.author.send(embed=embed)
        cursor.execute("DELETE FROM nabor WHERE user_id = ?", (interaction.author.id,))
        cursor.execute("INSERT INTO familycln (user_id, name) VALUES (?, ?)", (interaction.author.id,interaction.author.name))
        conn.commit()

    @disnake.ui.button(label="Отклонить", style=disnake.ButtonStyle.red, custom_id="от")
    async def no_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nabor WHERE user_id = ?", (interaction.author.id,))
        await interaction.message.delete()
        conn.commit()