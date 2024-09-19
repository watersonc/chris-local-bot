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
        # Деферим взаимодействие, чтобы предотвратить тайм-аут
        await inter.response.defer(ephemeral=True)

        embed = disnake.Embed(description="error", color=0x2b2d31)
        if member.id == inter.user.id:
            embed.set_thumbnail(url=Q_IMAGE if member.avatar is None else member.avatar.url)
            embed.set_author(name="not yourself", icon_url=IMAGE)
            await inter.edit_original_message(embed=embed)
            return

        embed = disnake.Embed(description=f"tag - <@{member.id}>\nnickname - {member.name}\nid - {member.id}", color=0x2b2d31)
        embed.set_author(name=f"user profile - {member.id}", icon_url=IMAGE)
        embed.set_thumbnail(url=Q_IMAGE if member.avatar is None else member.avatar.url)

        view = View()

        # Проверка на наличие user_id в banned_users
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (member.id,))
            if cursor.fetchone():
                view.add_item(Button(label="Unban User", style=disnake.ButtonStyle.success, custom_id=f"unban_{member.id}"))
            else:
                view.add_item(Button(label="Ban User", style=disnake.ButtonStyle.danger, custom_id=f"ban_{member.id}"))

        # Кнопки для управления кланом и семьей
        if clnid in [role.id for role in member.roles]:
            view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{member.id}"))
        else:
            view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{member.id}"))

        if famid in [role.id for role in member.roles]:
            view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{member.id}"))
        else:
            view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{member.id}"))

        await inter.edit_original_message(embed=embed, view=view)

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
        embed.set_thumbnail(url=Q_IMAGE if user.avatar is None else user.avatar.url)

        view = View()
        view = self.update_view_for_invite_or_remove(view, user, action)
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        if action == "ban":
            cursor.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user.id,))
            if cursor.fetchone():
                await inter.followup.send("User is already banned.", ephemeral=True)
                return
            
            reason = f"banned by {inter.author.id}"
            cursor.execute("INSERT INTO banned_users (user_id, reason, by) VALUES (?, ?, ?)", (user.id, reason, inter.author.id))
            role = disnake.utils.get(inter.guild.roles, id=localban_role)
            await user.add_roles(role)
            
            everyone_role_id = inter.guild.id
            roles_to_remove = [role for role in user.roles if role.id != everyone_role_id]
            if roles_to_remove:
                await user.remove_roles(*roles_to_remove, reason="delete all roles before give local ban")
            
            embed.description = f"User <@{user.id}> has been banned."
            await inter.response.edit_message(embed=embed)

        elif action == "unban":
            cursor.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user.id,))
            if not cursor.fetchone():
                await inter.followup.send("User is not banned.", ephemeral=True)
                return
            
            cursor.execute("DELETE FROM banned_users WHERE user_id = ?", (user.id,))
            cursor.execute("DELETE FROM verified WHERE user_id = ?", (user_id,))
            role = disnake.utils.get(inter.guild.roles, id=localban_role)
            rolenew = disnake.utils.get(inter.guild.roles, id= noverify_role)
            await user.remove_roles(role)
            await user.add_roles(rolenew)
            embed.description = f"User <@{user.id}> has been unbanned."
            await inter.response.edit_message(embed=embed)

        # Обработка других действий (cinv, finv, crem, frem)
        elif action == "cinv":
            role = disnake.utils.get(inter.guild.roles, id=clnid)
            cursor.execute("SELECT user_id FROM memberscln WHERE user_id = ?", (user.id,))
            if cursor.fetchone() is None:
                await user.add_roles(role)
                cursor.execute("INSERT INTO memberscln (user_id, user, added) VALUES (?, ?, ?)", (user.id, user.name, inter.author.id))
                embed.description += f"\nUser <@{user.id}> has been invited to the clan."
            else:
                await inter.followup.send("User is already in the clan.", ephemeral=True)

            await inter.response.edit_message(embed=embed)

        elif action == "finv":
            role = disnake.utils.get(inter.guild.roles, id=famid)
            cursor.execute("SELECT user_id FROM familycln WHERE user_id = ?", (user.id,))
            if cursor.fetchone() is None:
                await user.add_roles(role)
                cursor.execute("INSERT INTO familycln (user_id, user, added) VALUES (?, ?, ?)", (user.id, user.name, inter.author.id))
                embed.description += f"\nUser <@{user.id}> has been invited to the family."
            else:
                await inter.followup.send("User is already in the family.", ephemeral=True)

            await inter.response.edit_message(embed=embed)

        elif action == "crem":
            role = disnake.utils.get(inter.guild.roles, id=clnid)
            cursor.execute("SELECT user_id FROM memberscln WHERE user_id = ?", (user.id,))
            if cursor.fetchone():
                await user.remove_roles(role)
                cursor.execute("DELETE FROM memberscln WHERE user_id = ?", (user.id,))
                embed.description += f"\nUser <@{user.id}> has been removed from the clan."
            else:
                await inter.followup.send("User is not in the clan.", ephemeral=True)

            await inter.response.edit_message(embed=embed)

        elif action == "frem":
            role = disnake.utils.get(inter.guild.roles, id=famid)
            cursor.execute("SELECT user_id FROM familycln WHERE user_id = ?", (user.id,))
            if cursor.fetchone():
                await user.remove_roles(role)
                cursor.execute("DELETE FROM familycln WHERE user_id = ?", (user.id,))
                embed.description += f"\nUser <@{user.id}> has been removed from the family."
            else:
                await inter.followup.send("User is not in the family.", ephemeral=True)

            await inter.response.edit_message(embed=embed)

        conn.commit()

    def update_view_for_invite_or_remove(self, view: View, user: disnake.Member, action: str) -> View:
        view = View()

        # Проверка на наличие user_id в banned_users
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM banned_users WHERE user_id = ?", (user.id,))
            if cursor.fetchone():
                view.add_item(Button(label="Unban User", style=disnake.ButtonStyle.success, custom_id=f"unban_{user.id}"))
            else:
                view.add_item(Button(label="Ban User", style=disnake.ButtonStyle.danger, custom_id=f"ban_{user.id}"))

        # Кнопки для управления кланом и семьей
        if clnid in [role.id for role in user.roles]:
            view.add_item(Button(label="remove from clan", style=disnake.ButtonStyle.gray, custom_id=f"crem_{user.id}"))
        else:
            view.add_item(Button(label="invite in clan", style=disnake.ButtonStyle.gray, custom_id=f"cinv_{user.id}"))

        if famid in [role.id for role in user.roles]:
            view.add_item(Button(label="remove from family", style=disnake.ButtonStyle.gray, custom_id=f"frem_{user.id}"))
        else:
            view.add_item(Button(label="invite in family", style=disnake.ButtonStyle.gray, custom_id=f"finv_{user.id}"))
        return view

def setup(client):
    client.add_cog(ActionCMD(client))
    print("actioncmd loaded!")
