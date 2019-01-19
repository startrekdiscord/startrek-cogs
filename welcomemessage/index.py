import discord
from redbot.core import commands
from redbot.core import Config
from redbot.core import checks

class WelcomeMessage(commands.Cog):
    default_guild_settings = {"message": "Welcome to the Star Trek Discord!", "status": "off"}

    def __init__(self):
        self.config = Config.get_conf(self, identifier=359838393)  # random identifier
        self.config.register_guild(**self.default_guild_settings)

    async def on_member_join(self, member):
        """Send message when user joins"""

        status = await self.config.guild(member.guild).status()
        if status == "on":
            message = await self.config.guild(member.guild).message()
            await member.send(content=message)

    @commands.group()
    @commands.guild_only()
    async def welcomemessage(self, ctx: commands.Context):
        """Manage welcome message."""
        pass

    @checks.is_owner()
    @welcomemessage.command(name="set")
    @commands.guild_only()
    async def _set(self, ctx: commands.Context, *, new_welcome_message: str):
        """Sets welcome message."""

        await self.config.guild(ctx.guild).message.set(new_welcome_message)
        await ctx.send(content="Welcome DM set to: {}".format(new_welcome_message))

    @checks.is_owner()
    @welcomemessage.command(name="view")
    @commands.guild_only()
    async def _view(self, ctx: commands.Context):
        """Outputs welcome message."""

        message = await self.config.guild(ctx.guild).message()
        await ctx.send(content=message)


    @checks.is_owner()
    @welcomemessage.command(name="disable")
    @commands.guild_only()
    async def _disable(self, ctx: commands.Context):
        """Disables welcome message."""

        await self.config.guild(ctx.guild).status.set("off")
        await ctx.send(content="Welcome DMs disabled.")

    @checks.is_owner()
    @welcomemessage.command(name="enable")
    @commands.guild_only()
    async def _enable(self, ctx: commands.Context):
        """Enables welcome message."""

        await self.config.guild(ctx.guild).status.set("on")
        await ctx.send(content="Welcome DMs enabled.")
