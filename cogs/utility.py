import disnake
from disnake.ext import commands
from disnake import Option
from datetime import datetime, timedelta
from config import DATABASE, localban_role, noverify_role
import sqlite3

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_response(self, ctx, message=None, embed=None, ephemeral=True):
        if embed:
            await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
        elif message:
            await ctx.response.send_message(message, ephemeral=ephemeral)

    @commands.slash_command(name="clear", description="clear chat")
    async def clear(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.channel.purge(limit=101)  # Удаляем 100 сообщений + команду
        await self.send_response(ctx, "Удалено 100 сообщений.")

    @commands.slash_command(name="temp-role", description="temp role")
    async def temp_role(self, ctx: disnake.ApplicationCommandInteraction, action: str, user: disnake.User, role: disnake.Role, duration: str):
        if action not in ["add", "remove"]:
            await self.send_response(ctx, "error: use 'add' or 'remove'.")
            return

        duration_map = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days"
        }

        unit = duration[-1]
        value = duration[:-1]

        if not value.isdigit() or unit not in duration_map:
            await self.send_response(ctx, "error: use 's', 'm', 'h', or 'd'.")
            return

        delta = timedelta(**{duration_map[unit]: int(value)})
        end_time = datetime.now() + delta

        if action == "add":
            await user.add_roles(role)
            await self.send_response(ctx, f"role {role.name} given {user.name} for {end_time}.")
            await disnake.utils.sleep_until(end_time)
            await user.remove_roles(role)
            await ctx.channel.send(f"role {role.name} was deleted from {user.name} after expired time.")
        elif action == "remove":
            await user.remove_roles(role)
            await self.send_response(ctx, f"role {role.name} was deleted from {user.name}.")

    @commands.slash_command(name="ping", description="check current ping")
    async def ping(self, ctx: disnake.ApplicationCommandInteraction):
        latency = round(self.bot.latency * 1000)  # latency in ms
        await self.send_response(ctx, f"ping: {latency}ms")

    @commands.slash_command(name="userinfo", description="show info about user")
    async def userinfo(self, ctx: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        user = user or ctx.author

        embed = disnake.Embed(title=f"info about {user}", color=0x2b2d31)
        embed.add_field(name="id", value=user.id)
        embed.add_field(name="created", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"))
        embed.add_field(name="name", value=user.name)
        embed.add_field(name="status", value=str(user.status).capitalize())
        if isinstance(user, disnake.Member):
            embed.add_field(name="logged", value=user.joined_at.strftime("%d/%m/%Y %H:%M:%S"))
        await self.send_response(ctx, embed=embed)

    @commands.slash_command(name="help", description="show list of commands")
    async def help(self, ctx: disnake.ApplicationCommandInteraction):
        commands_info = {
            "/clear": "delete 100 messages from chat where used.",
            "/ping": "show current ping.",
            "/temp-role [add/remove] [@user | id] [@role | id] [duration]": "add / remove temp role for user.",
            "/userinfo [@user | id]": "show info about user. can be used wo args.",
            "/action [@user | id]": "show user action menu"
        }
        
        embed = disnake.Embed(title="chris' commands list:", color=0x2b2d31)
        for cmd, desc in commands_info.items():
            embed.add_field(name=cmd, value=desc, inline=False)
        
        await self.send_response(ctx, embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
    print("utilities loaded!")
