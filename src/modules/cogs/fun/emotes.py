from discord.ext import commands


class Emote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emotes = self.bot.db.emotes.find_one({})

    @commands.command(aliases=["emotes", "emoticon"])
    async def emote(self, ctx, name):
        await ctx.message.delete()
        if name.lower() in self.emotes and name != "_id":
            await ctx.send(self.emotes[name])
        else:
            await ctx.author.send(f"We could not find the emote: {name}!")
