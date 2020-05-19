import discord

from discord.ext.commands.cooldowns import BucketType
from discord.ext import commands
import asyncio


class Candy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1, 5, BucketType.user)
    async def candy(self, ctx):
        """Get the candy before anyone else!"""

        embed = discord.Embed(
            description="🍬 | First one to take the candy gets the candy!",
            colour=0x36393F,
        )
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🍬")

        def check(reaction, user):
            return (
                user != self.bot.user
                and str(reaction.emoji) == "🍬"
                and reaction.message.id == msg.id
            )

        try:
            msg0 = await self.bot.wait_for("reaction_add", check=check, timeout=5.0)
        except asyncio.TimeoutError:
            embed.description = "You didnt eat the candy in time!"
        else:
            embed.description = f"🍬 | {msg0[1].mention} won and ate the candy!"
            res = await self.bot.db.candy.find_one({"userid": str(ctx.author.id)})
            if res is not None:
                await self.bot.db.candy.find_one_and_update(
                    {"userid": str(ctx.author.id)},
                    {"$set": {"count": str(int(res["count"]) + 1)}},
                )
            else:
                await self.bot.db.candy.insert_one(
                    {"userid": str(ctx.author.id), "count": "1"}
                )
        await msg.edit(embed=embed)

    @candy.command(aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        """The leaderboard of the best candy players!"""
        tmp = await self.bot.db.candy.find({})
        lb = {}
        for i in tmp:
            lb[i["userid"]] = i["count"]
        lbSorted = sorted(lb, key=lambda x: lb[x], reverse=True)
        print(lbSorted)
        res = ""
        counter = 0
        for a in lbSorted:
            counter += 1
            if counter > 10:
                break
            u = self.bot.get_user(int(a))
            res += f"\n**{counter}.** {u.mention} - **{lb[str(a)]} 🍬**"
        embed = discord.Embed(description=res, colour=0x36393F)
        await ctx.send(embed=embed)
