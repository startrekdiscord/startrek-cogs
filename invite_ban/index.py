import discord
from redbot.core import commands

class InviteBan(commands.Cog):
    def __init__(self):
        self.badlist = ["discord.gg", "twitch.tv", "twitter.com"]

    async def _check_name_for_invite(self, member):
        """
            Looks for discord.gg etc anywhere in a user's name or in their
            server-specific name, and immediately ban them if it does
        """
        if any(n in member.display_name.lower() for n in self.badlist):
            await member.guild.ban(member)

    async def on_member_join(self, member):
        """ check every user when they join """
        await self._check_name_for_invite(member)

    async def on_member_update(self, before, after):
        """ check every user when they change their name """
        await self._check_name_for_invite(after)

    async def on_message(self, message):
        """find welcome messages (or mentions) and delete them too"""
        if message.mentions:
            user = message.mentions[0]
            if any(n in user.display_name.lower() for n in self.badlist):
                await message.delete()
