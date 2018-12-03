import json, tempfile
import discord
from redbot.core import commands

class Roledump(commands.Cog):
	@commands.command()
	async def roledump(self, ctx):
		#tfile = tempfile.TemporaryFile(mode='w+')
		roles = []
		role_hierarchy = ctx.message.guild.roles
		role_hierarchy.reverse()
		for role in role_hierarchy:
			roles.append({'name':role.name, 'id':role.id})
		tfile = open('roles_temp.json', 'w')
		tfile.write(json.dumps(roles))
		tfile.close()
		tfile = open('roles_temp.json', 'rb')
		await ctx.send(file=discord.File(tfile, filename="roles.json"), content='Here you go, {} roles exported:'.format(len(roles)))
		tfile.close()
