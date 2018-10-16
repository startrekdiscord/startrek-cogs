import json, tempfile
import discord
from discord.ext import commands

class Roledump:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def roledump(self, ctx):
		#tfile = tempfile.TemporaryFile(mode='w+')
		roles = []
		for role in ctx.message.server.role_hierarchy:
			roles.append({'name':role.name, 'id':role.id})
		tfile = open('roles_temp.json', 'w')
		tfile.write(json.dumps(roles))
		tfile.close()
		tfile = open('roles_temp.json', 'rb')
		await self.bot.send_file(ctx.message.channel, tfile, filename='roles.json', content='Here you go, {} roles exported:'.format(len(roles)))
		tfile.close()

def setup(bot):
	bot.add_cog(Roledump(bot))
