import discord
from discord.ext import commands


class countToModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastNum = 0
        self.lastSender = None
        self.senderCount = 0

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.channels["count-to-100k"].edit(slowmode_delay=1)
        await self.bot.channels["count-to-100k"].set_permissions(
            self.bot.channels["count-to-100k"].guild.default_role, send_messages=False
        )

        def removePredicate(message):
            return not (message.content.split()[0]).isdigit()

        needsRemoving = (
            await self.bot.channels["count-to-100k"]
            .history(limit=150)
            .filter(removePredicate)
            .flatten()
        )
        for elem in needsRemoving:
            await elem.delete()

        def predicate(message):
            return not (message.content.split()[0]).isdigit()

        hist = await self.bot.channels["count-to-100k"].history(limit=100).flatten()

        lastNum = 0
        lastNumMsg = None
        pattern = 1

        for i in hist:
            if pattern == 3:
                break
            elif "\n" in i.content or "```" in i.content or len(i.content) > 40:
                await i.delete()
                hist.remove(i)
                pattern = 1
                lastNumMsg = None
                lastNum = 0
            elif lastNum == int(i.content.split()[0]) + pattern:
                pattern += 1
            else:
                pattern = 1
                lastNumMsg = i
                lastNum = int(i.content.split()[0])
        targetIndex = hist.index(lastNumMsg)
        for i in hist[:targetIndex]:
            await i.delete()
        self.lastNum = lastNum
        await self.bot.channels["count-to-100k"].set_permissions(
            self.bot.channels["count-to-100k"].guild.default_role, send_messages=True
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel == self.bot.channels["count-to-100k"]:
            if self.lastNum == 0:
                return await message.author.send(
                    f"Please wait while the bot initializes {self.bot.channels['count-to-100k'].mention}"
                )
            if not (message.content.split()[0]).isdigit():
                await message.delete()
                await message.author.send("Please enter a valid number!")
                return
            if (
                "\n" in message.content
                or "```" in message.content
                or len(message.content) > 40
            ):
                await message.delete()
                await message.author.send(
                    "Please make sure your message meets these criterias:\n- Does not contain a codeblock.\n- Does not go onto a new line.\n- Is Not greater than 40 characters."
                )
                return
            if not int(message.content.split()[0]) - 1 == self.lastNum:
                await message.delete()
                await message.author.send(
                    f"Please make sure the number you have posted follows the previous number (`{self.lastNum}`) which should be `{self.lastNum + 1}`!"
                )
                return
            limitCheck = (
                await self.bot.channels["count-to-100k"].history(limit=52).flatten()
            )
            if all(message.author == msg.author for msg in limitCheck):
                await message.delete()
                await message.author.send(f"You may not send more than 50 in a row!")
                return
            self.lastNum = int(message.content.split()[0])

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.channel == self.bot.channels["count-to-100k"]:
            if not (after.content.split()[0]).isdigit():
                await after.author.send(
                    f"Please make sure that your edit contains the number {before.content.split()[0]} at the start!"
                )
                return
            if (
                "\n" in after.content
                or "```" in after.content
                or len(after.content) > 40
            ):
                await after.author.send(
                    "Please make sure your message meets these criterias:\n- Does not contain a codeblock.\n- Does not go onto a new line.\n- Is Not greater than 40 characters."
                )
                return
            if not int(after.content.split()[0]) == int(before.content.split()[0]):
                await after.author.send(
                    f"Please make sure when you edit the message the number stays the same (`{before.content.split()[0]}`)!"
                )
                return

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        if payload.channel_id == self.bot.channels["count-to-100k"].id:
            msg = await self.bot.channels["count-to-100k"].fetch_message(
                payload.message_id
            )
            if not (msg.content.split()[0]).isdigit():
                await msg.author.send(
                    f"Please make sure that your edit contains the correct number at the start!"
                )
                await self.bot.channels["logging"].send(
                    f"User: {msg.author.mention} edited their message in {self.bot.channels['count-to-100k'].mention}, and the message does not start with a number: {msg.jump_url}"
                )
                return
            if "\n" in msg.content or "```" in msg.content or len(msg.content) > 40:
                await msg.author.send(
                    f"Please make sure your edit meets these criterias:\n- Does not contain a codeblock.\n- Does not go onto a new line.\n- Is Not greater than 40 characters."
                )
                await self.bot.channels["logging"].send(
                    f"User: {msg.author.mention} edited their message in {self.bot.channels['count-to-100k'].mention}, and the message contains illegal parameters: {msg.jump_url}"
                )
                return
            await self.bot.channels["logging"].send(
                f"User: {msg.author.mention} edited their message in {self.bot.channels['count-to-100k'].mention}, and the message is not in the cache therefore cannot be checked: {msg.jump_url}"
            )

    # Useless right now as it cannot find the message if it's not cached therefore cannot find the author.
    # @commands.Cog.listener()
    # async def on_raw_message_delete(self, payload):
    #     if payload.channel_id == self.bot.channels["count-to-100k"].id:
    #         if payload.message_id != self.bot.channels["count-to-100k"].last_message_id:
    #             return await self.bot.channels["logging"].send(
    #                 f"A user deleted their message in {self.bot.channels['count-to-100k'].mention}."
    #             )
