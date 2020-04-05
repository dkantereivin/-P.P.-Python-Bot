import discord
from discord.ext import commands

from modules.utility.time import time_since


class User(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(aliases=["user_info", "userdetails", "user_details", "whois"])
    async def user(self, ctx, *, user: discord.Member = None):
        """ Get user information """
        user = user or ctx.author
        premium_status = "Not a nitro booster"
        premium_status = (
            f"This user has been boosting for {time_since(past_datetime = user.premium_since, max_units=3)}."
            if user.premium_since
            else "This user is not boosting the server"
        )
        # if user.premium_since:
        #     premium_status = (
        #         f"server boosing since {utils.default.date(user.premium_since)}."
        #     )
        show_roles = (
            ", ".join(
                [
                    f"<@&{x.id}>"
                    for x in sorted(user.roles, key=lambda x: x.position, reverse=True)
                    if x.id != ctx.guild.default_role.id
                ]
            )
            if len(user.roles) > 1
            else f"None"
        )

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_author(name=f"{user} ({user.id})")

        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Full name", value=user, inline=False)
        embed.add_field(name="Nickname", value=user.nick or "None", inline=False)
        embed.add_field(
            name="Account created",
            value=time_since(past_datetime=user.created_at, max_units=3),
            inline=False,
        )
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(
            name="Join date",
            value=time_since(past_datetime=user.created_at, max_units=3),
            inline=False,
        )
        embed.add_field(
            name="Is a bot", value="Yes" if user.bot else "No", inline=False
        )
        embed.add_field(name="Roles", value=show_roles, inline=False)

        embed.set_footer(icon_url=user.avatar_url, text=premium_status)

        await ctx.send(embed=embed)
