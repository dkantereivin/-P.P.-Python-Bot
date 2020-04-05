from .server import Server
from .user import User
from .privateRooms import PrivateRooms


def setup(bot):
    bot.add_cog(Server(bot))
    bot.add_cog(User(bot))
    bot.add_cog(PrivateRooms(bot))
