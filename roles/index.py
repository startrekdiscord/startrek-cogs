import discord
from redbot.core import commands
from redbot.core import Config
from redbot.core import checks

class Roles(commands.Cog):

    default_guild_settings = {"departments": []}

    def __init__(self):
        self.config = Config.get_conf(self, identifier=829937541)  # random identifier

        self.config.register_guild(**self.default_guild_settings)

    @commands.group()
    @commands.guild_only()
    async def department(self, ctx: commands.Context):
        """Manage departments."""
        pass

    @department.command(name="list")
    @commands.guild_only()
    async def _list_departments(self, ctx: commands.Context):
        """List departments."""

        departmentIds = await self.config.guild(ctx.guild).departments()

        output = 'Departments:\n'

        if len(departmentIds) == 0:
            output = output + '\t(none)\n'

        for role in ctx.guild.roles:
            if role.id in departmentIds:
                output = output + '\t- ' + role.name + '\n'

        await ctx.send(content=output)

    @checks.mod_or_permissions(manage_guild=True)
    @department.command(name="add")
    @commands.guild_only()
    async def _add_department(self, ctx: commands.Context, *, role_name: str):
        """Add department."""

        departmentIds = await self.config.guild(ctx.guild).departments()

        targetRole = None
        for role in ctx.guild.roles:
            if role.name == role_name:
                targetRole = role

        if targetRole is None:
            await ctx.send(content="Role not found: {}".format(role_name))
            return

        if targetRole.id in departmentIds:
            await ctx.send(content="'{}' already a department.".format(targetRole))
            return

        departmentIds.append(targetRole.id)
        await self.config.guild(ctx.guild).departments.set(departmentIds)
        await ctx.send(content="Department added: {}".format(targetRole))

    @checks.mod_or_permissions(manage_guild=True)
    @department.command(name="remove")
    @commands.guild_only()
    async def _remove_department(self, ctx: commands.Context, *, role_name: str):
        """Remove department."""

        departmentIds = await self.config.guild(ctx.guild).departments()

        targetRole = None
        for role in ctx.guild.roles:
            if role.name == role_name:
                targetRole = role

        if targetRole is None:
            await ctx.send(content="Role not found: {}".format(role_name))
            return

        if targetRole.id not in departmentIds:
            await ctx.send(content="'{}' is not a department.".format(targetRole))
            return

        departmentIds.remove(targetRole.id)
        await self.config.guild(ctx.guild).departments.set(departmentIds)
        await ctx.send(content="Department removed: {}".format(targetRole))

    @department.command(name="select")
    @commands.guild_only()
    async def _select_department(self, ctx: commands.Context, *, role_name: str):
        """Select department."""

        departmentIds = await self.config.guild(ctx.guild).departments()

        departmentsToBeRemoved = []
        targetRole = None
        for role in ctx.guild.roles:
            if role.id in departmentIds and role in ctx.message.author.roles:
                departmentsToBeRemoved.append(role)
            if role.name == role_name:
                targetRole = role

        if targetRole is None:
            await ctx.send(content="Role not found: {}".format(role_name))
            return

        if targetRole.id not in departmentIds:
            await ctx.send(content="{} not a department".format(targetRole))
            return

        await ctx.message.author.remove_roles(*departmentsToBeRemoved)
        await ctx.message.author.add_roles(targetRole)
        await ctx.send(content="{}'s department is now {}".format(ctx.message.author.name, targetRole))
        

