import discord
from discord.ext import commands
import dateparser
from dateutil.tz import tzlocal
import sqlite3
import requests
import time

GOOGLE_MAPS_API_KEY = 'AIzaSyDnuQ_OgMeVMIZdUT252SAvjgC__Hsv-N8'


class Timecog:
    """Cog for handling time communication"""

    def __init__(self, bot):
        self.bot = bot
        self.db_connection = sqlite3.connect('user_timezones.db')
        self.db = self.db_connection.cursor()
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS user_timezones (user_id text, location text, latitude float, longitude float)''')
        self.db_connection.commit()

    def __del__(self):
        self.db_connection.close()

    @commands.command(pass_context=True)
    async def ilivein(self, ctx, *, location):
        """Tells the system where you live so it can know what your clock reads"""

        userId = ctx.message.author.id
        api_url = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + \
            location+'&key='+GOOGLE_MAPS_API_KEY
        response = requests.get(api_url).json()

        if response['status'] != "OK":
            await self.bot.say("Unable to parse location: " + location+". Either this isn't a location or we've run out of quota with Google's API")
        else:
            latlng = response['results'][0]['geometry']['location']
            latitude = latlng['lat']
            longitude = latlng['lng']
            self.db.execute(
                '''DELETE FROM user_timezones WHERE user_id=?''', [userId])
            self.db.execute(
                '''INSERT INTO user_timezones VALUES(?, ?, ?, ?)''', [userId, location, latitude, longitude])
            self.db_connection.commit()
            await self.bot.say("Location for " +
                               ctx.message.author.display_name+" set to: "+location)

    @commands.command(pass_context=True)
    async def timefor(self, ctx, *, atless_mention):
        """Outputs what a given user's clock reads"""

        targetUser = None
        for member in ctx.message.server.members:
            if atless_mention == member.name + '#' + member.discriminator:
                targetUser = member
        if targetUser is None:
            await self.bot.say("Unable to locate the specified user: " + atless_mention)
            return
        targetUserId = targetUser.id
        self.db.execute(
            '''SELECT * FROM user_timezones WHERE user_id=?''', [targetUserId])
        result = self.db.fetchone()
        if result is None:
            await self.bot.say("I do not have timezone information for that user. If this user exists, they should use the ilivein command to set their location.")
        else:
            latitude = result[2]
            longitude = result[3]
            currentEpochTimestamp = int(time.time())
            api_url = 'https://maps.googleapis.com/maps/api/timezone/json?location=' + str(latitude) + \
                ',' + str(longitude) + '&timestamp=' + \
                str(currentEpochTimestamp) + '&key=' + GOOGLE_MAPS_API_KEY
            response = requests.get(api_url).json()
            dstOffset = response['dstOffset']
            rawOffset = response['rawOffset']
            totalOffset = dstOffset + rawOffset
            if totalOffset < 0:
                theirTime = dateparser.parse(str(abs(totalOffset))+' seconds ago UTC')
            else:
                theirTime = dateparser.parse('in '+str(totalOffset)+' seconds UTC')
            theirTime = theirTime.replace(tzinfo=tzlocal())
            await self.bot.say("The current time for "+targetUser.display_name+" is "+theirTime.strftime("%A @ %I:%M%p (%H:%M)"))

    @commands.command(pass_context=True)
    async def time(self, ctx, *, time):
        """Display time in reader's timezone"""

        timestamp = dateparser.parse(time)
        if timestamp is None:
            await self.bot.say("Unable to convert to date/time: " + time)
        else:
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=tzlocal())
            title = "\""+time+"\" in your local timezone:"
            em = discord.Embed(
                title=title, timestamp=timestamp)
            await self.bot.send_message(ctx.message.channel, embed=em)


def setup(bot):
    bot.add_cog(Timecog(bot))
