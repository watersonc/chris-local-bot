import disnake
from disnake.ext import commands
from config import MOD_LOGS

class ModLogs(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(
            title="Message Deleted",
            description=f"Message by {message.author.mention} was deleted.",
            color=disnake.Color.red()
        )
        embed.add_field(name="Content", value=message.content or "No content")
        embed.add_field(name="Channel", value=message.channel.mention)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(
            title="Message Edited",
            description=f"Message by {before.author.mention} was edited.",
            color=disnake.Color.orange()
        )
        embed.add_field(name="Before", value=before.content or "No content")
        embed.add_field(name="After", value=after.content or "No content")
        embed.add_field(name="Channel", value=before.channel.mention)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(
            title="Member Joined",
            description=f"{member.mention} has joined the server.",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(
            title="Member Left",
            description=f"{member.mention} has left the server.",
            color=disnake.Color.red()
        )
        embed.set_thumbnail(url=member.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(
            title="Member Banned",
            description=f"{user.mention} has been banned from the server.",
            color=disnake.Color.red()
        )
        embed.set_thumbnail(url=user.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(
            title="Member Unbanned",
            description=f"{user.mention} has been unbanned from the server.",
            color=disnake.Color.green()
        )
        embed.set_thumbnail(url=user.avatar.url)
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        log_channel = self.client.get_channel(MOD_LOGS)
        embed = disnake.Embed(color=disnake.Color.blue())

        if before.channel is None and after.channel is not None:
            embed.title = "Member Joined Voice Channel"
            embed.description = f"{member.mention} joined the voice channel {after.channel.mention}."
            embed.set_thumbnail(url=member.avatar.url)
        elif before.channel is not None and after.channel is None:
            embed.title = "Member Left Voice Channel"
            embed.description = f"{member.mention} left the voice channel {before.channel.mention}."
            embed.set_thumbnail(url=member.avatar.url)
        elif before.channel != after.channel:
            embed.title = "Member Moved Voice Channel"
            embed.description = f"{member.mention} moved from {before.channel.mention} to {after.channel.mention}."
            embed.set_thumbnail(url=member.avatar.url)
        elif before.mute != after.mute:
            embed.title = "Member Muted/Unmuted"
            action = "muted" if after.mute else "unmuted"
            embed.description = f"{member.mention} was {action} in {after.channel.mention}."
            embed.set_thumbnail(url=member.avatar.url)
        elif before.deaf != after.deaf:
            embed.title = "Member Deafened/Undeafened"
            action = "deafened" if after.deaf else "undeafened"
            embed.description = f"{member.mention} was {action} in {after.channel.mention}."
            embed.set_thumbnail(url=member.avatar.url)

        if embed.title:
            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = self.client.get_channel(MOD_LOGS)
        
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            if added_roles:
                role_names = ", ".join([role.name for role in added_roles])
                embed = disnake.Embed(
                    title="Role Added",
                    description=f"{after.mention} was given the role(s): {role_names}.",
                    color=disnake.Color.green()
                )
                embed.set_thumbnail(url=after.avatar.url)
                await log_channel.send(embed=embed)
            
            if removed_roles:
                role_names = ", ".join([role.name for role in removed_roles])
                embed = disnake.Embed(
                    title="Role Removed",
                    description=f"{after.mention} was removed from the role(s): {role_names}.",
                    color=disnake.Color.red()
                )
                embed.set_thumbnail(url=after.avatar.url)
                await log_channel.send(embed=embed)

def setup(client):
    client.add_cog(ModLogs(client))
    print("modlogs loaded!")
