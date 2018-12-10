
import discord
from redbot.core import commands

class TriviaHelper(commands.Cog):
	ADMIN_ROLES = [
		279466664884699136, # Redshirt
		275120133305794561, # Senior Officer
		496516286730469387] # Engie

	TEAMS = [406925463697621004, 406925533973315605, 406925579389108224] # team role IDs, in order
	SPECTATE = 406925622020145154 # role ID for spectator
	ALL_ROLES = TEAMS + [SPECTATE] # handy way to iterate over them all

	THREE_CUTOFF = 9 # 9 or more people cause a third team to exist

	def flatten(self, lst):
		# flattens nested lists
		return [i for sl in lst for i in sl]

	def size(self, lst):
		# gets the total number of items in a nested list
		return sum(len(i) for i in lst)

	def role_check(self, user, role_query):
		# returns True or False if a user has named role
		for role in user.roles:
			if role.id in role_query:
				return True
		return False

	def rolelist_filter(self, roles, id_list):
		# filters the full role hierarchy based on the predefined lists above
		out_roles = []
		for role in roles:
			if int(role.id) in id_list:
				out_roles.append(role)
		return out_roles

	def get_role_by_id(self, roles, roleid):
		roleid = str(roleid)
		for role in roles:
			if role.id == roleid:
				return role
		print('role {} not found'.format(roleid))
		return None

	def get_users_with(self, server, role):
		# finds users with a specific roles
		users = []
		for member in server.members:
			if role in member.roles and not member in users:
				users.append(member)
		return users

	def get_teams(self, server):
		# finds all people who are on a trivia team
		return [self.get_users_with(server, self.get_role_by_id(server.roles, rid)) for rid in self.TEAMS]

	def get_participants(self, server):
		return self.flatten(self.get_teams(server)) # flatten the team lists

	def get_spectators(self, server):
		# finds all people who watching the trivia
		return self.get_users_with(server, self.get_role_by_id(server.roles, self.SPECTATE))

	def is_balanced(self, lens):
		# checks if a list of team sizes is appropriately balanced
		for ia,lista in enumerate(lens):
			for ib,listb in enumerate(lens):
				if ia != ib and abs(lista - listb) > 1:
					return False
		return True

	def get_minmax(self, lens):
		# return the index of the minimum and maximum values of a list
		bestmax = -1000
		bestmin = 1000
		imax = 0
		imin = 0
		for idx,val in enumerate(lens): # enumerate so we have index
			if val < bestmin: # simple best so far algo
				bestmin = val
				imin = idx
			if val > bestmax:
				bestmax = val
				imax = idx
		return (imin, imax)

	async def balance_teams(self, server):
		output = '' # buffer for the actions we perform
		# moves people so that the teams are somewhat even
		teams = self.get_teams(server) # list of lists of team members
		players = set(self.flatten(teams)) # extract the "players", people on any team

		assignments_orig = {} # this relates each user to the team they were assigned
		for teamnum,team in enumerate(teams):
			for user in team:
				assignments_orig[user] = teamnum # indexing the teams by zero for now

		if len(players) >= self.THREE_CUTOFF and len(teams) > 2 and not teams[2]:
			output += 'Added a third team\n'
		elif len(players) < self.THREE_CUTOFF:
			if len(teams) > 2 and teams[2]:
				output += 'Removed the third team\n'
			teams[0] += teams.pop()


		balanced = False
		iters = 0
		while not balanced and iters < 30: # just a failsafe to prevent infinite looping
			lens = [len(i) for i in teams]
			balanced = self.is_balanced(lens) # first check if its balanced
			if balanced:
				break # continue on if so
			imin, imax = self.get_minmax(lens) # we want to move one member from the biggest team to the smallest
			if imin != imax:
				teams[imin].append(teams[imax].pop()) # as easy as that?

		assignments_new = {} # relates the users to their new assignments
		for teamnum,team in enumerate(teams):
			for user in team:
				assignments_new[user] = teamnum

		team_roles = [self.get_role_by_id(server.roles, rid) for rid in self.TEAMS] # get the roles so we can manipulate them

		for player in players:
			orig = assignments_orig.get(player)
			new = assignments_new.get(player)
			if orig != new:
				output += 'Switching {} from {} to {}.\n'.format(player.nick if player.nick else player.name,team_roles[orig].name,team_roles[new].name)
				await player.add_roles(team_roles[orig])
				for idx,role in enumerate(player.roles):
					if role == team_roles[orig]:
						del player.roles[idx] # need this terrible hacky fix or else the role won't actually get removed
						break
				await player.add_roles(team_roles[new])

		if not output:
			output = 'The teams are already balanced.'
		await ctx.send(output)



	@commands.command()
	async def starttrivia(self, ctx, play_emote, spectate_emote):
		"""Begins looking at the latest message in announcements for reactions and assigning people trivia roles."""
		if not self.role_check(ctx.message.author, self.ADMIN_ROLES): # restrict to admins
			await ctx.send("That command is reserved for admins.")
			return

		await ctx.send('NYI')

	@commands.command()
	async def freezetrivia(self, ctx):
		"""Stops letting people join trivia via reactions."""
		if not self.role_check(ctx.message.author, self.ADMIN_ROLES): # restrict to admins
			await ctx.send("That command is reserved for admins.")
			return

		await ctx.send('NYI')

	@commands.command()
	async def balanceteams(self, ctx):
		"""Balances the trivia teams."""
		if not self.role_check(ctx.message.author, self.ADMIN_ROLES): # restrict to admins
			await ctx.send("That command is reserved for admins.")
			return

		await self.balance_teams(ctx.message.guild)

	@commands.command()
	async def hastrivia(self, ctx):
		"""Shows everyone who has trivia roles."""
		trivia_roles = self.rolelist_filter(ctx.message.guild.roles, self.ALL_ROLES)

		roles = {}
		for check_role in trivia_roles:
			roles[check_role] = []

		total_roles = 0
		for member in ctx.message.guild.members:
			for check_role in trivia_roles:
				if check_role in member.roles:
					roles[check_role].append(member)
					total_roles += 1

		teams = self.get_teams(ctx.message.guild) # list of lists of team members
		players = set(self.flatten(teams))
		imbalanced = False
		if len(players) >= self.THREE_CUTOFF and len(teams) > 2 and not teams[2]:
			imbalanced = True
		elif len(players) < self.THREE_CUTOFF:
			if len(teams) > 2 and teams[2]:
				imbalanced = True
			del teams[2]
		if not self.is_balanced([len(i) for i in teams]):
			imbalanced = True

		embed = discord.Embed(title='Trivia roles:')
		embed.set_footer(text='{} total'.format(total_roles))
		for check_role in trivia_roles:
			people = '\n'.join(member.mention for member in sorted(roles[check_role], key=lambda usr: usr.nick.lower() if usr.nick else usr.name.lower()))
			if not people:
				people = '*nobody*'
			embed.add_field(name=check_role.name, value=people)
		if imbalanced:
			embed.add_field(name='‼️ Teams are imbalanced ‼️', value='Use the `!balanceteams` command to balance them.')
		await ctx.send(embed=embed)

	@commands.command()
	async def stoptrivia(self, ctx):
		"""Removes any trivia roles from people that have them."""
		if not self.role_check(ctx.message.author, self.ADMIN_ROLES): # restrict to admins
			await ctx.send("That command is reserved for admins.")
			return
		trivia_roles = self.rolelist_filter(ctx.message.guild.roles, self.ALL_ROLES)

		to_remove = {}
		for check_role in trivia_roles:
			to_remove[check_role] = []

		for member in ctx.message.guild.members:
			for check_role in trivia_roles:
				if check_role in member.roles:
					to_remove[check_role].append(member)

		total_removes = 0
		for check_role in trivia_roles:
			for member in to_remove[check_role]:
				await member.remove_roles(check_role)
				total_removes += 1

		embed = discord.Embed(title='Removed the following trivia roles from:')
		embed.set_footer(text='{} roles removed'.format(total_removes))
		for check_role in trivia_roles:
			people = '\n'.join(member.mention for member in sorted(to_remove[check_role], key=lambda usr: usr.nick.lower() if usr.nick else usr.name.lower()))
			if not people:
				people = '*nobody*'
			embed.add_field(name=check_role.name, value=people)
		await ctx.send(embed=embed)
