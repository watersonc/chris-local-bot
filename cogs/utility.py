import disnake
from disnake.ext import commands
from datetime import datetime, timedelta

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_response(self, ctx, message=None, embed=None, ephemeral=True):
        if embed:
            await ctx.response.send_message(embed=embed, ephemeral=ephemeral)
        elif message:
            await ctx.response.send_message(message, ephemeral=ephemeral)

    @commands.slash_command(name="clear", description="Очистить чат")
    async def clear(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.channel.purge(limit=101)  # Удаляем 100 сообщений + команду
        await self.send_response(ctx, "Удалено 100 сообщений.")

    @commands.slash_command(name="temp-role", description="Временная роль")
    async def temp_role(self, ctx: disnake.ApplicationCommandInteraction, action: str, user: disnake.User, role: disnake.Role, duration: str):
        if action not in ["add", "remove"]:
            await self.send_response(ctx, "Неверное действие! Используйте 'add' или 'remove'.")
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
            await self.send_response(ctx, "Неверный формат длительности! Используйте 's', 'm', 'h', или 'd'.")
            return

        delta = timedelta(**{duration_map[unit]: int(value)})
        end_time = datetime.now() + delta

        if action == "add":
            await user.add_roles(role)
            await self.send_response(ctx, f"Роль {role.name} выдана пользователю {user.name} до {end_time}.")
            await disnake.utils.sleep_until(end_time)
            await user.remove_roles(role)
            await ctx.channel.send(f"Роль {role.name} была удалена у пользователя {user.name} после истечения времени.")
        elif action == "remove":
            await user.remove_roles(role)
            await self.send_response(ctx, f"Роль {role.name} удалена у пользователя {user.name}.")

    @commands.slash_command(name="ping", description="Узнать текущую задержку бота")
    async def ping(self, ctx: disnake.ApplicationCommandInteraction):
        latency = round(self.bot.latency * 1000)  # latency in ms
        await self.send_response(ctx, f"Пинг бота: {latency}ms")

    @commands.slash_command(name="userinfo", description="Показать информацию об участнике")
    async def userinfo(self, ctx: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        user = user or ctx.author

        embed = disnake.Embed(title=f"Информация об участнике {user}", color=0x2b2d31)
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Создан", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"))
        embed.add_field(name="Имя", value=user.name)
        embed.add_field(name="Статус", value=str(user.status).capitalize())
        if isinstance(user, disnake.Member):
            embed.add_field(name="Дата вступления", value=user.joined_at.strftime("%d/%m/%Y %H:%M:%S"))
        await self.send_response(ctx, embed=embed)

    @commands.slash_command(name="help", description="Показать список команд")
    async def help(self, ctx: disnake.ApplicationCommandInteraction):
        commands_info = {
            "/clear": "Удаление 100 сообщений из чата.",
            "/ping": "Показать текущую задержку бота.",
            "/temp-role <add/remove> <@user | Id> <@role | Id> <duration>": "Добавление или удаление временной роли у пользователя. Пример: `temp-role add @scarlettv4 @admin 1d`",
            "/userinfo [@user | id]": "Показать информацию о пользователе. Примеры: `userinfo`, `userinfo @scarlettv4`"
        }
        
        embed = disnake.Embed(title="Список команд", color=0x2b2d31)
        for cmd, desc in commands_info.items():
            embed.add_field(name=cmd, value=desc, inline=False)
        
        await self.send_response(ctx, embed=embed)

def setup(bot):
    bot.add_cog(Utility(bot))
    print("utilities loaded!")
