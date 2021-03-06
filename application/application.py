import asyncio
import discord

from typing import Any
from discord.utils import get
from datetime import datetime, timedelta

from redbot.core import Config, checks, commands
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.antispam import AntiSpam

from redbot.core.bot import Red

Cog: Any = getattr(commands, "Cog", object)


class Application(Cog):
    """
    Simple application cog, basically.
    **Use `[p]applysetup` first.**
    """

    __author__ = "saurichable"
    __version__ = "1.0.0"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, 5641654654621651651, force_registration=True
        )
        self.antispam = {}

    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def apply(self, ctx: commands.Context):
        """Apply to be a staff member."""
        author = ctx.author
        guild = ctx.guild
        bot = self.bot
        role_add = get(guild.roles, name="Staff Applicant")
        channel = get(guild.text_channels, name="applications")
        if ctx.guild not in self.antispam:
            self.antispam[ctx.guild] = {}
        if ctx.author not in self.antispam[ctx.guild]:
            self.antispam[ctx.guild][ctx.author] = AntiSpam([(timedelta(days=2), 1)])
        if self.antispam[ctx.guild][ctx.author].spammy:
            return await ctx.send("Uh oh, you're doing this way too frequently.")

        if role_add is None:
            return await ctx.send(
                "Uh oh. Looks like your Admins haven't added the required role."
            )

        if channel is None:
            return await ctx.send(
                "Uh oh. Looks like your Admins haven't added the required channel."
            )

        try:
            await author.send(
                "Let's start right away! You have maximum of 2 minutes for each question.\nWhat position are you applying for?"
            )
        except discord.Forbidden:
            return await ctx.send(
                "I don't seem to be able to DM you. Do you have closed DMs?"
            )

        await ctx.send("Okay, {0}, I've sent you a DM.".format(author.mention))

        def check(m):
            return m.author == author and m.channel == author.dm_channel

        try:
            position = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send("What is your name?")
        try:
            name = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send("How old are you?")
        try:
            age = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send("What timezone are you in? (Google is your friend.)")
        try:
            timezone = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send("How many days per week can you be active?")
        try:
            days = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send("How many hours per day can you be active?")
        try:
            hours = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send(
            "Do you have any previous experience? If so, please describe."
        )
        try:
            experience = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        await author.send("Why do you want to be a member of our staff?")
        try:
            reason = await bot.wait_for("message", timeout=120, check=check)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")

        embed = discord.Embed(color=await ctx.embed_colour(), timestamp=datetime.now())
        embed.set_author(name="New application!", icon_url=author.avatar_url)
        embed.set_footer(
            text="{0}#{1} ({2})".format(author.name, author.discriminator, author.id)
        )
        embed.title = "User: {0}#{1} ({2})".format(
            author.name, author.discriminator, author.id
        )
        embed.add_field(name="Name:", value=name.content, inline=True)
        embed.add_field(name="Age:", value=age.content, inline=True)
        embed.add_field(name="Timezone:", value=timezone.content, inline=True)
        embed.add_field(name="Desired position:", value=position.content, inline=True)
        embed.add_field(name="Active days/week:", value=days.content, inline=True)
        embed.add_field(name="Active hours/day:", value=hours.content, inline=True)
        embed.add_field(
            name="Previous experience:", value=experience.content, inline=False
        )
        embed.add_field(name="Reason:", value=reason.content, inline=False)

        await channel.send(embed=embed)

        await author.add_roles(role_add)

        await author.send("Your application has been sent to the Admins, thank you!")
        self.antispam[ctx.guild][ctx.author].stamp()

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def applysetup(self, ctx: commands.Context):
        """Go through the initial setup process."""
        bot = self.bot
        guild = ctx.guild
        pred = MessagePredicate.yes_or_no(ctx)
        applicant = get(guild.roles, name="Staff Applicant")
        channel = get(guild.text_channels, name="applications")

        await ctx.send(
            "This will create required channel and role. Do you wish to continue? (yes/no)"
        )
        try:
            await bot.wait_for("message", timeout=30, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long. Try again, please.")
        if pred.result is False:
            return await ctx.send("Setup cancelled.")

        if applicant is None:
            try:
                await guild.create_role(
                    name="Staff Applicant", reason="Application cog setup"
                )
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh. Looks like I don't have permissions to manage roles."
                )

        if channel is None:
            await ctx.send(
                "Do you want everyone to see the applications channel? (yes/no)"
            )
            try:
                await bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            if pred.result is True:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        send_messages=False
                    ),
                    guild.me: discord.PermissionOverwrite(send_messages=True),
                }
            else:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        read_messages=False
                    ),
                    guild.me: discord.PermissionOverwrite(read_messages=True),
                }
            try:
                await guild.create_text_channel(
                    "applications",
                    overwrites=overwrites,
                    reason="Application cog setup",
                )
            except discord.Forbidden:
                return await ctx.send(
                    "Uh oh. Looks like I don't have permissions to manage channels."
                )

        await ctx.send(
            "You have finished the setup! Please, move your new channel to the category you want it in."
        )

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def accept(self, ctx: commands.Context, target: discord.Member):
        """Accept a staff applicant.

        <target> can be a mention or an ID."""
        bot = self.bot
        guild = ctx.guild
        applicant = get(guild.roles, name="Staff Applicant")
        role = MessagePredicate.valid_role(ctx)
        if applicant in target.roles:
            await ctx.send(
                "What role do you want to accept {0} as?".format(target.name)
            )
            try:
                await bot.wait_for("message", timeout=30, check=role)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            role_add = role.result
            await target.add_roles(role_add)
            await target.remove_roles(applicant)
            await ctx.send("Accepted {0} as {1}.".format(target.mention, role_add))
            await target.send(
                "You have been accepted as {0} in {1}.".format(role_add, guild.name)
            )
        else:
            await ctx.send(
                "Uh oh. Looks like {0} hasn't applied for anything.".format(
                    target.mention
                )
            )

    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_roles=True)
    async def deny(self, ctx: commands.Context, target: discord.Member):
        """Deny a staff applicant.

        <target> can be a mention or an ID"""
        bot = self.bot
        guild = ctx.guild
        author = ctx.author
        applicant = get(guild.roles, name="Staff Applicant")
        if applicant in target.roles:
            await ctx.send("Would you like to specify a reason? (yes/no)")
            pred = MessagePredicate.yes_or_no(ctx)
            try:
                await bot.wait_for("message", timeout=30, check=pred)
            except asyncio.TimeoutError:
                return await ctx.send("You took too long. Try again, please.")
            if pred.result is True:
                await ctx.send("Please, specify your reason now.")

                def check(m):
                    return m.author == author

                try:
                    reason = await bot.wait_for("message", timeout=120, check=check)
                except asyncio.TimeoutError:
                    return await ctx.send("You took too long. Try again, please.")
                await target.send(
                    "Your application in {0} has been denied.\n*Reason:* {1}".format(
                        guild.name, reason.content
                    )
                )
            else:
                await target.send(
                    "Your application in {0} has been denied.".format(guild.name)
                )
            await target.remove_roles(applicant)
            await ctx.send("Denied {0}'s application.".format(target.mention))
        else:
            await ctx.send(
                "Uh oh. Looks like {0} hasn't applied for anything.".format(
                    target.mention
                )
            )
