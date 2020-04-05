import discord
from discord.ext import commands
import asyncio

from modules.utility.time import time_since
from modules.utility.grabColour import grab_colour


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(aliases=["server_info", "guild", "guild_info"])
    async def server(self, ctx):
        created = time_since(ctx.guild.created_at, precision="days")
        features = ", ".join(ctx.guild.features)
        if features == "":
            features = "NONE"
        region = ctx.guild.region

        roles = len(ctx.guild.roles)
        channels = ctx.guild.channels
        text_channels = 0
        category_channels = 0
        voice_channels = 0
        for channel in channels:
            if isinstance(channel, discord.TextChannel):
                text_channels += 1
            if isinstance(channel, discord.CategoryChannel):
                category_channels += 1
            elif isinstance(channel, discord.VoiceChannel):
                voice_channels += 1

        member_count = ctx.guild.member_count
        members = ctx.guild.members
        online = 0
        dnd = 0
        idle = 0
        offline = 0
        for member in members:
            if str(member.status) == "online":
                online += 1
            elif str(member.status) == "offline":
                offline += 1
            elif str(member.status) == "idle":
                idle += 1
            elif str(member.status) == "dnd":
                dnd += 1

        embed = discord.Embed(colour=grab_colour(ctx.guild.icon_url))

        embed.add_field(
            name="Server Information",
            inline=False,
            value="Name: **{}**\nID: **{}**\nCreated: **{}**\nVoice region: **{}**\nSpecial features: **{}**".format(
                ctx.guild.name, ctx.guild.id, created, region, features
            ),
        )

        embed.add_field(
            name="Counts",
            inline=False,
            value="Members: **{}**\nRoles: **{}**\nText channels: **{}**\n Voice channels: **{}**\nChannel categories: **{}**".format(
                member_count, roles, text_channels, voice_channels, category_channels
            ),
        )

        embed.add_field(
            name="Members",
            inline=False,
            value=f"<:online:695811388488024064> {online}\n<:away:695811388379234316> {idle}\n<:dnd:695811388744007700> {dnd}\n<:offline:695811388320514139> {offline}",
        )

        embed.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=embed)
