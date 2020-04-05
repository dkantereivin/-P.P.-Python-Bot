import discord
import asyncio
from discord.ext import commands
from random import randint


class PrivateRooms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timers = {}
        self.idToUser = {}
        self.userToId = {}
        self.userHasRoom = {}
        self.listOfRooms = [0]

    @commands.command(aliases=["privateroom"])
    async def createroom(self, ctx, *, numOfPeople: str = "10"):
        if ctx.author not in self.userHasRoom:
            self.userHasRoom[ctx.author] = False

        tempid = 0
        while tempid in self.listOfRooms:
            tempid = randint(100, 999)

        guild = ctx.guild

        if (not numOfPeople.isdigit()) or (1 > int(numOfPeople) > 10):
            numOfPeople = 10
        else:
            numOfPeople = int(numOfPeople)

        if self.userHasRoom[ctx.author]:
            return

        self.idToUser[tempid] = ctx.author
        self.userToId[ctx.author] = tempid
        self.userHasRoom[ctx.author] = True
        self.listOfRooms.append(tempid)

        category = discord.utils.get(guild.categories, name="Private Rooms")

        vc = await guild.create_voice_channel(
            name=f"private room #{tempid}",
            overwrites=None,
            category=category,
            user_limit=numOfPeople,
        )

        self.timers[tempid] = True
        await self.startCountdown(tempid, vc)

    @commands.command()
    async def removeroom(self, ctx):
        guild = ctx.guild

        if ctx.author not in self.userHasRoom:
            return

        if self.userHasRoom[ctx.author]:
            tempid = self.userToId[ctx.author]
            vc = discord.utils.get(guild.voice_channels, name=f"private room #{tempid}")
            await self.stopCountdown(tempid)
            await vc.delete()
            self.userHasRoom[ctx.author] = False
            self.listOfRooms.remove(tempid)

        else:
            return

    async def startCountdown(self, tempid, vc):
        self.timers[tempid] = True
        x = 30
        while self.timers[tempid]:
            await asyncio.sleep(1)
            x = x - 1
            if x == 0:
                await self.stopCountdown(tempid)
                await vc.delete()
                self.userHasRoom[self.idToUser[tempid]] = False
                self.listOfRooms.remove(tempid)

    async def stopCountdown(self, tempid):
        self.timers[tempid] = False
        return

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None:
            tempid = int(after.channel.name.strip("private room #"))

            if len(after.channel.members) != 0:
                await self.stopCountdown(tempid)

        else:
            tempid = int(before.channel.name.strip("private room #"))
            await self.startCountdown(tempid, before.channel)
