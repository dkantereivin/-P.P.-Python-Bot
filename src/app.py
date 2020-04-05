from asyncio import Event
import json
import os

# from modules.cogs.database import ConnectionHolder
from sys import exit
from traceback import format_exception, format_exc
import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone
import pymongo
import urllib.parse

# Set path to bot directory
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

with open("data/config.json") as config:
    config = json.load(config)

cogs = ["modules.cogs.fun.__init__", "modules.cogs.utility.__init__"]


class PPBot(commands.Bot):
    """Main bot class!"""

    def __init__(self, command_prefix: str):
        super().__init__(command_prefix=command_prefix)

        self.london = timezone("Europe/London")
        self.startup = self.london.localize(datetime.now())

        self.actions = []
        self.pruning = False
        self.failed_cogs = []
        self.exitcode = 0
        self.db = pymongo.MongoClient(config["connectionURI"]).bot
        self.config = self.db.bot.find_one({})

        self.channels = self.db.channels.find_one({})
        self.roles = self.db.roles.find_one({})

    def load_cogs(self):
        for extension in cogs:
            try:
                self.load_extension(extension)
            except BaseException as e:
                print(e)
                print(f"{extension} failed to load.", extension)
                self.failed_cogs.append([extension, type(e).__name__, e])

    @staticmethod
    def escape_text(text):
        text = str(text)
        return discord.utils.escape_markdown(discord.utils.escape_mentions(text))

    async def on_ready(self):
        if self.config["presenceType"] == "playing":
            activity = discord.Activity(
                name=self.config["presence"], type=discord.ActivityType.playing
            )
        elif self.config["presenceType"] == "watching":
            activity = discord.Activity(
                name=self.config["presence"], type=discord.ActivityType.watching
            )
        elif self.config["presenceType"] == "streaming":
            activity = discord.Activity(
                name=self.config["presence"], type=discord.ActivityType.streaming
            )
        else:
            activity = discord.Activity(
                name=self.config["presence"], type=discord.ActivityType.listening
            )

        # Default status if undefined
        status = discord.Status.online
        status = (
            discord.Status.online
            if self.config["status"].lower() == "online"
            else status
        )
        status = (
            discord.Status.invisible
            if self.config["status"].lower() in ["offline", "invisible"]
            else status
        )
        status = (
            discord.Status.idle
            if self.config["status"].lower() in ["idle", "away"]
            else status
        )
        status = (
            discord.Status.dnd
            if self.config["status"].lower()
            in ["dnd", "do_not_disturb", "do not disturb"]
            else status
        )

        await self.change_presence(activity=activity, status=status)

        self.guild = self.get_guild(int(self.config["guild"]))

        for n in self.channels.keys():
            if (
                n != "_id"
                and isinstance(self.channels[n], int)
                or isinstance(self.channels[n], str)
            ):
                self.channels[n] = self.get_channel(int(self.channels[n]))
                if self.channels[n] is not None:
                    print(f"Found channel: {n}")
                else:
                    print(f"Failed to find channel {n}")

        for n in self.roles.keys():
            if (
                n != "_id"
                and isinstance(self.roles[n], int)
                or isinstance(self.roles[n], str)
            ):
                self.roles[n] = self.guild.get_role(int(self.roles[n]))
                if self.roles[n] is not None:
                    print(f"Found role: {n}")
                else:
                    print(f"Failed to find role: {n}")

        startup_message = f"PP Bot has started! {self.guild.name} has {self.guild.member_count} members"
        if len(self.failed_cogs) != 0:
            startup_message += "\n\nSome addons failed to load:\n"
            for f in self.failed_cogs:
                print(f)
                f[0] = f[0].replace("_", "\_")
                startup_message += "\n{}: ```py\n{}: {}```".format(*f)
        embed = discord.Embed(
            description=startup_message, colour=0x36393F, timestamp=self.startup
        )
        embed.set_author(
            name="Python",
            icon_url="https://www.stickpng.com/assets/images/5848152fcef1014c0b5e4967.png",
        )

        print(startup_message)
        await self.channels["logging"].send(embed=embed)

    async def on_command_error(
        self, ctx: commands.Context, exc: commands.CommandInvokeError
    ):
        author: discord.Member = ctx.author
        command: commands.Command = ctx.command or "<unknown cmd>"
        exc = getattr(exc, "original", exc)

        if isinstance(exc, commands.CommandNotFound):
            return

        elif isinstance(exc, commands.NoPrivateMessage):
            await ctx.send(f"`{command}` cannot be used in direct messages.")

        elif isinstance(exc, commands.MissingPermissions):
            await ctx.send(
                f"{author.mention} You don't have permission to use `{command}`."
            )

        elif isinstance(exc, commands.CheckFailure):
            await ctx.send(f"{author.mention} You cannot use `{command}`.")

        elif isinstance(exc, commands.BadArgument):
            await ctx.send(f"{author.mention} A bad argument was given: `{exc}`\n")
            await ctx.send_help(ctx.command)

        elif isinstance(exc, discord.ext.commands.errors.CommandOnCooldown):
            if str(ctx.author.id) not in self.config["developers"]:
                try:
                    await ctx.message.delete()
                except (discord.errors.NotFound, discord.errors.Forbidden):
                    pass
                await ctx.send(
                    f"{ctx.message.author.mention} This command was used {exc.cooldown.per - exc.retry_after:.2f}s ago and is on cooldown. Try again in {exc.retry_after:.2f}s.",
                    delete_after=10,
                )
            else:
                await ctx.reinvoke()

        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send(
                f"{author.mention} You are missing required argument {exc.param.name}.\n"
            )
            await ctx.send_help(ctx.command)

        elif isinstance(exc, discord.NotFound):
            await ctx.send(f"ID not found.")

        elif isinstance(exc, discord.Forbidden):
            await ctx.send(f"💢 AAAAAA The server isn't letting me in!\n`{exc.text}`.")

        elif isinstance(exc, commands.CommandInvokeError):
            await ctx.send(
                f"{author.mention} `{command}` raised an exception during usage"
            )
            msg = "".join(format_exception(type(exc), exc, exc.__traceback__))
            for chunk in [msg[i : i + 1800] for i in range(0, len(msg), 1800)]:
                await self.channels["logging"].send(f"```\n{chunk}\n```")
        else:
            if not isinstance(command, str):
                command.reset_cooldown(ctx)
            await ctx.send(
                f"{author.mention} Unexpected exception occurred while using the command `{command}`"
            )
            msg = "".join(format_exception(type(exc), exc, exc.__traceback__))
            for chunk in [msg[i : i + 1800] for i in range(0, len(msg), 1800)]:
                await self.channels["logging"].send(f"```\n{chunk}\n```")

    async def on_error(self, event_method, *args, **kwargs):
        await self.channels["logging"].send(f"Error in {event_method}:")
        msg = format_exc()
        for chunk in [msg[i : i + 1800] for i in range(0, len(msg), 1800)]:
            await self.channels["logging"].send(f"```\n{chunk}\n```")

    def add_cog(self, cog):
        super().add_cog(cog)

    async def close(self):
        print("PP Bot is shutting down")
        await super().close()

    async def is_all_ready(self):
        """Checks if the bot is finished setting up."""
        return self._is_all_ready.is_set()

    async def wait_until_all_ready(self):
        """Wait until the bot is finished setting up."""
        await self._is_all_ready.wait()


def main():
    """Main script to run the bot."""

    bot = PPBot((".", "!"))
    bot.help_command = commands.DefaultHelpCommand(dm_help=None)
    print(f"Starting the bot!")
    bot.load_cogs()
    bot.run(bot.config["token"])

    return bot.exitcode


if __name__ == "__main__":
    exit(main())