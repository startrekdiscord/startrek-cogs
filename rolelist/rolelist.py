
import discord
from discord.ext import commands

# constant for paginating embeds
EMBED_MAX_LEN = 2048
# these are for the font padding function, taken from whatever font discord uses on mac
RELATIVE_WIDTH = {'1':11, '2':20, '3':19, '4':24, '5':20, '6':22, '7':20, '8':22, '9':22, '0':24}
SPACE_WIDTH = 13 #width of space char
PADDING_WIDTH = 10 #width of the padding char
PADDING_CHAR = '-' #char to pad with
PAD_SIZE = 4 #width of pad in spaces

class RoleList:
	"""Lists roles and their member count with different categories."""

	## hardcoded role tables because i can't think of a better way to do it:
	ADMIN_ROLES = ['Redshirt', 'Senior Officer'] # needed to call the more spammy commands
	#these IDs have to be ints
	RANK_ROLES = [  361843066254000130, # captain
					361843316733640706, # first officer
					218764794642169859, # commander
					218742589933879296, # lt commander
					218742756380508160, # liutenant
					247676277295808512, # lt jr grade
					218741903439560705, # ensign
					218981687206346753, # cadet
					218745759489589258] # recruit
	DIVISION_ROLES=[275800501944320012, # engineering
					275808065352105986, # comms
					275801077776121856, # security
					275801685534834688, # ops
					275800450589130754, # navigation
					275800221160701952, # command
					275801172516798478, # medical
					371679277915308035, # intelligence
					275801124202741762] # science
	GAME_ROLES = [  408778921463644171, # gta
					411285388204965899, # hoi4
					381711935428755456, # minecraft
					361650526095409152, # overwatch
					333060985369657345, # pulsar
					436786707417923586, # st bridge crew
					363191063302635522, # stellaris
					409076467197280267, # st online
					333062169434390528, # gmod
					467433462563995658, # warframe
					320501120906690573] # vr
	# species roles are too long of a list to maintain here so we trisect the full role list 
	# based on these roles right before and right after all the species
	SPECIES_BEFORE = 332679652164501507 # the Computer role (transparent one)
	SPECIES_AFTER = 275800501944320012 # the Engineering division role

	MAX_USERS = 30 # max people to list for !whohas

	def __init__(self, bot):
		self.bot = bot

	def role_check(self, user, role_query):
		# returns True or False if a user has named role
		for role in user.roles:
			if role.name in role_query:
				return True
		return False

	def alphanum_filter(self, text):
		# filter for searching a role by name without having to worry about case or punctuation
		return ''.join(i for i in text if i.isalnum()).lower()

	def rolelist_filter(self, roles, id_list):
		# filters the full role hierarchy based on the predefined lists above
		out_roles = []
		for role in roles:
			if int(role.id) in id_list:
				out_roles.append(role)
		return out_roles

	def get_named_role(self, server, rolename):
		# finds a role in a server by name
		check_name = self.alphanum_filter(rolename)
		for role in server.roles:
			if self.alphanum_filter(role.name) == check_name:
				return role
		return None

	def role_accumulate(self, check_roles, members):
		## iterate over the members to accumulate a count of each role
		rolecounts = {}
		for role in check_roles: # populate the accumulator dict
			if not role.is_everyone:
				rolecounts[role] = 0

		for member in members:
			for role in member.roles:
				if role in check_roles and not role.is_everyone: # want to exclude @everyone from this list
					rolecounts[role] += 1

		return rolecounts

	async def rolelist_paginate(self, rlist, title='Role List'):
		# takes a list of roles and counts and sends it out as multiple embed as nessecary
		pages = []
		buildstr = ''
		for role,count in rlist: # this generates and paginates the info
			line = '{} {}\n'.format(count,role.mention)
			if len(buildstr) + len(line) > EMBED_MAX_LEN:
				pages.append(buildstr) # split the page here
				buildstr = line
			else:
				buildstr += line
		if buildstr:
			pages.append(buildstr) #if the string has data not already listed in the pages, add it

		for index,page in enumerate(pages): # enumerate so we can add a page number
			embed = discord.Embed(title='{} page {}/{}'.format(title, index+1, len(pages)), description=page)
			await self.bot.say(embed=embed)

	@commands.command(pass_context=True)
	async def roles(self, ctx, category:str='all', sort_order:str='name'):
		"""Shows roles and their member counts. 
		The category is one of: all, species, rank, divion, game 
		and sortorder is one of: default, name, count.
		The species and all categories are only available to admin users."""

		if not category in ['all', 'species', 'rank', 'divion', 'game'] or not sort_order in ['default', 'name', 'count']: # make sure it has valid args
			await self.bot.say("Invalid arguments. Check the help for this command.")
			return
		if not self.role_check(ctx.message.author, self.ADMIN_ROLES) and category in ['all', 'species']: # restrict the spammy ones to admins
			await self.bot.say("That category is reserved for admins.")
			return

		check_roles = [] # the list of roles to search for
		if category == 'all':
			check_roles = ctx.message.server.role_hierarchy # we use role_hierarchy for these because sometimes we want to see the order
		elif category == 'rank':
			check_roles = self.rolelist_filter(ctx.message.server.role_hierarchy, self.RANK_ROLES) # filter from hardcoded list
		elif category == 'division':
			check_roles = self.rolelist_filter(ctx.message.server.role_hierarchy, self.DIVISION_ROLES)
		elif category == 'game':
			check_roles = self.rolelist_filter(ctx.message.server.role_hierarchy, self.GAME_ROLES)
		elif category == 'species': #this is the tricky one
			start = None
			end = None
			for index,role in enumerate(ctx.message.server.role_hierarchy): # search the index of the start and end of species roles
				rid = int(role.id)
				if rid == self.SPECIES_BEFORE:
					start = index
				if rid == self.SPECIES_AFTER:
					end = index
			if start != None and end != None: # if we found both
				check_roles = ctx.message.server.role_hierarchy[start+1:end] # cut list from searched values

		if not check_roles: # failsafe if its not populated
			return

		## now we iterate over the members to accumulate a count of each role
		rolecounts = self.role_accumulate(check_roles, ctx.message.server.members)

		sorted_list = []
		if sort_order == 'default': # default sort = the server role hierarchy
			for role in check_roles:
				if role in rolecounts:
					sorted_list.append((role, rolecounts.get(role,0)))
		elif sort_order == 'name': # name sort = alphabetical by role name
			sorted_list = sorted(rolecounts.items(), key=lambda tup: tup[0].name.lower())
		elif sort_order == 'count': # count sort = decreasing member count
			sorted_list = sorted(rolecounts.items(), key=lambda tup: tup[1], reverse=True)

		if not sorted_list: # another failsafe
			return

		await self.rolelist_paginate(sorted_list) # send the list to get actually printed to discord

	@commands.command(pass_context=True)
	async def rolecall(self, ctx, *, rolename):
		"""Counts the number of members with a specific role."""
		check_role = self.get_named_role(ctx.message.server, rolename)
		if not check_role:
			await self.bot.say("I can't find that role!")
			return

		count = 0
		online = 0
		for member in ctx.message.server.members:
			if check_role in member.roles:
				count += 1
				if member.status != discord.Status.offline:
					online += 1

		embed = discord.Embed(title=check_role.name, description='{}/{} online'.format(online, count), color=check_role.color)
		embed.set_footer(text='ID: {}'.format(check_role.id))
		await self.bot.say(embed=embed)

	@commands.command(pass_context=True)
	async def whohas(self, ctx, *, rolename):
		"""Lists the people who have the specified role.
		Can take a -nick or -username argument to enhance output."""
		mode = 0 # tells how to display: 0 = just mention, 1 = add nickname, 2 = add username
		if '-nick' in rolename:
			mode = 1
			rolename = rolename.replace('-nick','')
		elif '-username' in rolename:
			mode = 2
			rolename = rolename.replace('-username','')

		check_role = self.get_named_role(ctx.message.server, rolename)
		if not check_role:
			await self.bot.say("I can't find that role!")
			return

		users = []
		for member in ctx.message.server.members:
			if check_role in member.roles:
				users.append(member)

		sorted_list = sorted(users, key=lambda usr: usr.nick.lower() if usr.nick else usr.name.lower())
		truncated = False
		if len(sorted_list) > self.MAX_USERS:
			sorted_list = sorted_list[:self.MAX_USERS] ## truncate to the limit
			truncated = True
		if mode == 2: # add full username
			page = '\n'.join('{} ({}#{})'.format(member.mention, member.name, member.discriminator) for member in sorted_list) # not bothering with multiple pages cause 30 members is way shorter than one embed
		elif mode == 1: # add nickname
			page = '\n'.join('{} ({})'.format(member.mention, member.display_name) for member in sorted_list)
		else:
			page = '\n'.join('{}'.format(member.mention) for member in sorted_list)

		if truncated:
			page += '\n*and {} more...*'.format(len(users) - self.MAX_USERS)

		embed = discord.Embed(title='{} members with {}'.format(len(users), check_role.name), description=page, color=check_role.color)
		embed.set_footer(text='ID: {}'.format(check_role.id))
		await self.bot.say(embed=embed)

	@commands.command(pass_context=True)
	async def rolecount(self, ctx):
		"""Simply counts the number of roles on the server. (excluding @everyone)"""
		await self.bot.say('This server has {} total roles.'.format(len(ctx.message.server.roles) - 1))

	@commands.command(pass_context=True)
	async def emptyroles(self, ctx):
		"""Shows a list of roles that have zero members."""
		if not self.role_check(ctx.message.author, self.ADMIN_ROLES): # restrict to admins
			await self.bot.say("That command is reserved for admins.")
			return

		check_roles = ctx.message.server.role_hierarchy # grab in hierarchy order so they're easier to find in the server settings
		rolecounts = self.role_accumulate(check_roles, ctx.message.server.members) # same accumulate as the `roles` command

		sorted_list = []
		for role in check_roles:
			if role in rolecounts and rolecounts[role] == 0: # only add if count = 0
				sorted_list.append((role, rolecounts.get(role,0)))

		if not sorted_list: # another failsafe
			await self.bot.say('Seems there are no empty roles...')

		await self.rolelist_paginate(sorted_list, title='Empty Roles')


def setup(bot):
	bot.add_cog(RoleList(bot))