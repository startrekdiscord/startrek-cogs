import discord
from redbot.core import commands
from redbot.core import Config
from redbot.core import checks

class Admin(commands.Cog):
    """Admin commands for Star Trek Discord"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.admin()
    async def purge(self, ctx: commands.Context, limit=0):
        """Remove messages from chat
           
           Usage: /purge [n]
           by default, will remove the purge command and the previous message
        """
        # delete typed message(s) from chat
        if int(limit) > 1000:
            await ctx.send(content="Max 1000!")
        else:
            await ctx.message.channel.purge(limit=int(limit))
