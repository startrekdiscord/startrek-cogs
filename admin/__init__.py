from .index import Admin

def setup(bot):
	bot.add_cog(Admin(bot))