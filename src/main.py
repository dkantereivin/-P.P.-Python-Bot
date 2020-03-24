import discord
from discord.ext import commands
from cogs.webserver import keep_alive
bot = commands.Bot(command_prefix="p!", description="Python bot for the programmers palace")

# OAUTH with admin privs:
# https://discordapp.com/api/oauth2/authorize?client_id=692056261985828934&permissions=8&scope=bot
inital_extension = [
  'cogs.countToModeration'
]
if __name__ == '__main__':
  for extension in inital_extension:
    bot.load_extension(extension)


TOKEN = "NjkyMDU2MjYxOTg1ODI4OTM0.Xno9pg.xcupmOdI8GJkcWn28nYVRcRL2N4"
keep_alive()
bot.run(TOKEN)