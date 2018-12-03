from .index import Countdown

def setup(bot):
	bot.add_cog(Countdown(bot))