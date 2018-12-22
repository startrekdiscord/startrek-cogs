import discord
from redbot.core import commands
import re
import urllib

spoilerTagRegex = re.compile(r"\[spoiler ([^\]]+)\]", re.IGNORECASE)
KEY_REACTION_EMOJI = "\U0001F440" # :eyes:

class Spoiler(commands.Cog):

    """Hide spoilers by delivering them via DM"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def on_message(self, message: discord.Message):
        """Hide spoiler text and have it delivered via DM."""
        
        containsSpoiler = spoilerTagRegex.search(message.content) is not None

        if not containsSpoiler:
            return

        try:
            await message.delete()
        except discord.Forbidden:
            await message.channel.send("I require the 'manage messages' permission "
                           "to hide spoilers!")

        name = message.author.nick
        if name is None:
            name = message.author.name
        
        def despoilerify(spoiler):
            spoilerText = spoiler.group(1)
            queryString = urllib.parse.urlencode({'q': spoilerText})
            return "[HOVER TO REVEAL](https://google.com?{} \"{}\")".format(queryString, spoilerText)

        def demarkup(spoiler):
            return spoiler.group(1)

        despoilered = spoilerTagRegex.sub(despoilerify, message.content)
        demarkuped = spoilerTagRegex.sub(demarkup, message.content)

        embed = discord.Embed(description=despoilered, color=0xff0000)
        embed.set_author(name=name, url="https://google.com?q={}".format(message.author.id))
        embed.set_footer(text="↙[click for DM]")

        spoilerMessage = await message.channel.send(embed=embed)


        await spoilerMessage.add_reaction(KEY_REACTION_EMOJI)

        def check(reaction: discord.Reaction, user: discord.Member):
            return not user.bot and reaction.emoji == KEY_REACTION_EMOJI and reaction.message.id == spoilerMessage.id

        async def listenForReaction():
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60 * 60.0, check=check)
            except asyncio.TimeoutError:
                None
            else:
                dmEmbed = discord.Embed(description=demarkuped, color=0xff0000)
                dmEmbed.set_author(name=name, url="https://google.com?q={}".format(message.author.id))
                await user.send(embed=dmEmbed)
                await listenForReaction()
        await listenForReaction()
