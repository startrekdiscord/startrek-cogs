import discord
import sqlite3
from discord.ext import commands
import requests

class TV:
    """Cog for interacting with the episodes database"""

    def __init__(self, bot):
        self.bot = bot
        
    #tuple indexes    
    #series == 0
    #season == 1
    #episode  == 2
    #series name == 3
    #episode title == 4
    #episode description == 5
    #episode wiki link == 6
    
    def get_titlecard(self, episode):
        # gets the titlecard image from the api
        image_url_base = "http://memory-alpha.wikia.com/wiki/Special:FilePath/"
        # the query + grab the episode title as wikia shows it
        api_url = (
            "http://memory-alpha.wikia.com/api.php?action=query&prop=images&format=json&titles="
            + episode[6].split("/")[-1]
        )
        # get it
        result = requests.get(api_url).json()
        # un-nest the json. the list... part is to get the api's internal page number
        # sorry this is confusing to read, but it works (somehow) and gives the image filename
        filename = result["query"]["pages"][list(result["query"]["pages"].keys())[0]][
            "images"
        ][0]["title"][5:]
        # gives back the actual expanded version of the url
        return requests.get(image_url_base + filename).url

    def embed_episode(self, episode):
        # put a given episode in an embedded discord format
        episode_name = episode[4]
        episode_url = episode[6]
        embedTitle = (
            episode[0]
            + " S"
            + str(episode[1])
            + "E"
            + str(episode[2])
            + ": "
            + episode_name
        )
        embed = discord.Embed(title=embedTitle, url=episode_url, description=episode[5])
        # get our image and embed it (can be embed.set_thumbnail but its way too small to see)
        embed.set_image(url=self.get_titlecard(episode))
        return embed
    
    @commands.command()
    async def trekommend(self, *arg):
        """Recommends a random episode of Star Trek! Include "TOS" or "DS9" for a recommendation from a specific series"""
        try:
            conn = sqlite3.connect('episodes.db')
            if(len(arg) == 0): 
                #Get a random episode
                c = conn.cursor()
                c.execute('SELECT * FROM episodes ORDER BY RANDOM() LIMIT 1')
                episode = c.fetchone()
            
                if(episode):
                    #Output
                    await self.bot.say("I recommend:")
                    await self.bot.say(embed=self.embed_episode(episode))  
    
            else:
                #Get a random episode from a given series
                c = conn.cursor()
                c.execute('SELECT * FROM episodes WHERE series=? ORDER BY RANDOM() LIMIT 1', (arg[0].upper(),))
                rows = c.fetchall()

                if(len(rows) != 0):                
                    episode = rows[0]
                    #Output
                    await self.bot.say("I recommend:")
                    await self.bot.say(embed=self.embed_episode(episode))  

                
        except Exception as inst:
            print("Exception occured:")
            print(inst)     # the exception instance
            print(inst.args)     # arguments stored in .args
            await self.bot.say("Whoops, an error occured!")
                
                
    @commands.command()
    async def episode(self, *arg):
        """Provide details about a given episode"""
        try:
            conn = sqlite3.connect('episodes.db')
            if(len(arg) > 0):
                #Try to get Episode details by title
                i = 1
                episode_title = arg[0]
                while i < len(arg):
                    episode_title = episode_title + " " + arg[i]
                    i += 1                
                c = conn.cursor()
                c.execute('SELECT * FROM episodes WHERE UPPER(name) LIKE UPPER(?) LIMIT 1', (episode_title,))
                episode = c.fetchone()     
                if(episode):
                    await self.bot.say(embed=self.embed_episode(episode))  
                    return
                
            if(len(arg) == 2):
                #Try to get Episode details by series/season#/episode#
                series = arg[0]
                season = arg[1][1]
                episode = arg[1].split("e")[1]
                c = conn.cursor()
                c.execute('SELECT * FROM episodes WHERE series=? AND season=? AND episode=? ORDER BY name LIMIT 1', (series.upper(),season,episode))
                episode = c.fetchone()

                if(episode):
                    await self.bot.say(embed=self.embed_episode(episode))  
                    return
                        
            #episode not found in DB 
            await self.bot.say("Please restate request. Accepted requests are in the following format:\n`In the pale moonlight` \n`DS9 s6e19`")
                
        except Exception as inst:
            print("Exception occured:")
            print(inst)     # the exception instance
            print(inst.args)     # arguments stored in .args
            await self.bot.say("Please restate request. Accepted requests are in the following format:\n`In the pale moonlight` \n`DS9 s6e19`")
            
def setup(bot):
    bot.add_cog(TV(bot))


