from .candy import Candy
from .countToModeration import countToModeration
from .emotes import Emote


def setup(bot):
    """Initialises fun cogs"""
    bot.add_cog(Candy(bot))
    bot.add_cog(countToModeration(bot))
    bot.add_cog(Emote(bot))
