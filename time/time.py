import discord
from discord.ext import commands
import dateparser
from dateutil.tz import tzlocal


class Timecog:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def time(self, ctx, *, time):
        """This does stuff!"""

        timestamp = dateparser.parse(time)
        if timestamp is None:
            await self.bot.say("Unable to convert to date/time: " + time)
        else:
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=tzlocal())
            title = "\""+time+"\"" + \
                " in your local timezone:"
            em = discord.Embed(
                title=title, timestamp=timestamp)
            await self.bot.send_message(ctx.message.channel, embed=em)


def setup(bot):
    bot.add_cog(Timecog(bot))
