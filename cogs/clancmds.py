import disnake
from disnake.ext import commands
from disnake.ui import Button, View
import sqlite3
from config import *

class ActionCMD(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.slash_command(name='action', description='control the clan members')
    async def action(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = commands.Param(name="member")):
        # Build embed and view
        embed = disnake.Embed(description="error", color=0x2b2d31)
        if member.id == inter.user.id:
            embed.set_thumbnail(url=Q_IMAGE if member.avatar is None else member.avatar.url)
            embed.set_author(name="not yourself", icon_url=IMAGE)
            await inter.response.send_message(embed=embed)
        else:
            embed = disnake.Embed(description=f"tag - <@{member.id}>\nnickname - {member.name}\nid - {member.id}", color=0x2b2d31)
            embed.set_author(name=f"user profile - {member.id}", icon_url=IMAGE)
            embed.set_thumbnail(url=Q_IMAGE if member.avatar is None else member.avatar.url)

            view = View()
            if clnid in [role.id for role in member.roles]:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{member.id}"))
            else:
                view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{member.id}"))
            if famid in [role.id for role in member.roles]:
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{member.id}"))
            else:
                view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{member.id}"))
            await inter.response.send_message(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        # Extract user_id from custom_id
        custom_id_parts = inter.data.custom_id.split("_")
        if len(custom_id_parts) != 2:
            return
        
        action, user_id_str = custom_id_parts
        try:
            user_id = int(user_id_str)
        except ValueError:
            return
        
        # Find user in the guild
        user = inter.guild.get_member(user_id)
        if not user:
            await inter.followup.send("error: no user in db", ephemeral=True)
            return

        embed = disnake.Embed(description=f"tag - <@{user.id}>\nnickname - {user.name}\nid - {user.id}", color=0x2b2d31)
        embed.set_author(name=f"user profile - {user.id}", icon_url=IMAGE)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        embed.set_thumbnail(url=Q_IMAGE if user.avatar is None else user.avatar.url)

        view = View()
        if action == "cinv":
            role = disnake.utils.get(inter.guild.roles, id=clnid)
            if famid in [role.id for role in user.roles]:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
            else:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{user.id}"))
            
            cursor.execute("SELECT user_id FROM memberscln WHERE user_id = ?", (user.id,))
            if cursor.fetchone() is None:
                await inter.response.edit_message(embed=embed, view=view)
                cursor.execute("INSERT INTO memberscln (user_id, user, added) VALUES (?, ?, ?)", (user.id, user.name, inter.author.id))
                await user.add_roles(role)
                embed = disnake.Embed(description="тебя добавили в chris/cln (discord.gg/pKshKqJT3Y)", color=disnake.Color.from_rgb(47, 49, 54))
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_author(name="chris waterson:", icon_url=IMAGE)
                await user.send(embed=embed)
                conn.commit()
            else:
                if clnid not in [role.id for role in user.roles]:
                    await user.add_roles(role)
                    view = self.update_view_for_invite_or_remove(view, user, action)
                    await inter.response.edit_message(embed=embed, view=view)

        elif action == "finv":
            role = disnake.utils.get(inter.guild.roles, id=famid)
            if clnid in [role.id for role in user.roles]:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
            else:
                view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))

            cursor.execute("SELECT user_id FROM familycln WHERE user_id = ?", (user.id,))
            if cursor.fetchone() is None:
                await inter.response.edit_message(embed=embed, view=view)
                cursor.execute("INSERT INTO familycln (user_id, user, added) VALUES (?, ?, ?)", (user.id, user.name, inter.author.id))
                await user.add_roles(role)
                embed = disnake.Embed(description="тебя добавили в chris/fam (discord.gg/pKshKqJT3Y)", color=disnake.Color.from_rgb(47, 49, 54))
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_author(name="chris waterson:", icon_url=IMAGE)
                await user.send(embed=embed)
                conn.commit()
            else:
                if famid not in [role.id for role in user.roles]:
                    await user.add_roles(role)
                    view = self.update_view_for_invite_or_remove(view, user, action)
                    await inter.response.edit_message(embed=embed, view=view)

        elif action == "crem":
            role = disnake.utils.get(inter.guild.roles, id=clnid)
            if famid in [role.id for role in user.roles]:
                view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
            else:
                view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{user.id}"))
                view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{user.id}"))

            cursor.execute("SELECT user_id FROM memberscln WHERE user_id = ?", (user.id,))
            if cursor.fetchone():
                await inter.response.edit_message(embed=embed, view=view)
                cursor.execute("DELETE FROM memberscln WHERE user_id = ?", (user.id,))
                await user.remove_roles(role)
                embed = disnake.Embed(description="тебя исключили из chris/cln (discord.gg/pKshKqJT3Y)", color=disnake.Color.from_rgb(47, 49, 54))
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_author(name="chris waterson:", icon_url=IMAGE)
                await user.send(embed=embed)
                conn.commit()
            else:
                await inter.followup.send("юзер не найден в бд", ephemeral=True)

        elif action == "frem":
            role = disnake.utils.get(inter.guild.roles, id=famid)
            if clnid in [role.id for role in user.roles]:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{user.id}"))
            else:
                view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{user.id}"))
                view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{user.id}"))

            cursor.execute("SELECT user_id FROM familycln WHERE user_id = ?", (user.id,))
            if cursor.fetchone():
                await inter.response.edit_message(embed=embed, view=view)
                cursor.execute("DELETE FROM familycln WHERE user_id = ?", (user.id,))
                await user.remove_roles(role)
                embed = disnake.Embed(description="тебя исключили из chris/fam (discord.gg/pKshKqJT3Y)", color=disnake.Color.from_rgb(47, 49, 54))
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_author(name="chris waterson:", icon_url=IMAGE)
                await user.send(embed=embed)
                conn.commit()
            else:
                await inter.followup.send("юзер не найден в бд", ephemeral=True)

        conn.close()

    def update_view_for_invite_or_remove(self, view: View, user: disnake.Member, action: str) -> View:
        # Update view based on the action
        if action == "cinv":
            if clnid in [role.id for role in user.roles]:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
            else:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{user.id}"))
        elif action == "finv":
            if clnid in [role.id for role in user.roles]:
                view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
            else:
                view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{user.id}"))
                view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
        return view

def setup(client):
    client.add_cog(ActionCMD(client))
    print("clancmds loaded!")
