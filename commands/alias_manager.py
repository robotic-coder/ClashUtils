import discord
import discord.ext.commands as commands
import coc
from commands.utils.helpers import *

class Alias(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(
		description = "Manages aliases that can be used in place of clan tags.",
		brief = "Manages aliases that can be used in place of clan tags."
	)
	async def alias(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await send_command_list(ctx, self.alias)
			return

	@alias.command(
		name="add",
		description = "Adds a clan alias to this server.",
		brief = "Links the given alias to the given clan. When linked, you can run commands in this server with the alias instead of the clan tag.",
		usage = "[#CLANTAG] [alias]",
		help = "#8PQGQC8 myclan"
	)
	async def alias_add(self, ctx: commands.Context, *args):
		if ctx.author.guild_permissions.manage_guild == False:
			await ctx.channel.send("You need `Manage Server` permissions to add aliases in this server.")

		if len(args) != 2:
			await send_command_help(ctx, self.alias_add)
			return
		
		tag = args[0]
		alias = args[1]
		clash = ctx.bot.clash
		snowflake = ctx.guild.id

		if alias.startswith("#"):
			await ctx.channel.send("Alias cannot begin with a #")
			return

		if len(alias) > 15:
			await ctx.channel.send("max alias length: 15 characters")
			return
			
		clan = await clash.get_clan(tag)
		ctx.bot.link_guild(snowflake, alias, tag)
		ctx.bot.storage.link_guild(snowflake, alias, tag)
		await ctx.channel.send("You have linked `"+alias+"` to "+clan.name+" in this server.")

		channels = ctx.bot.storage.fetch_all_aliases()
		print(channels)

	@alias.command(
		name="remove",
		description = "Removes an alias from this server.",
		brief = "Removes the given alias from this server. You must use a previously-linked alias.",
		usage = "[alias]",
		help = "myclan"
	)
	async def alias_remove(self, ctx: commands.Context, *args):
		if ctx.author.guild_permissions.manage_guild == False:
			await ctx.channel.send("You need `Manage Server` permissions to remove aliases in this server.")

		if len(args) != 1:
			await send_command_help(ctx, self.alias_remove)
			return

		alias = args[0]
		tag = resolve_clan(alias, ctx)
		snowflake = ctx.guild.id
		
		if tag is None:
			await ctx.channel.send("There is no clan linked to the alias `"+alias+"` in this server.")
			return
			
		ctx.bot.unlink_guild(snowflake, alias)
		ctx.bot.storage.unlink_guild(snowflake, alias)
		await ctx.channel.send("You have removed the alias `"+alias+"` from this server.")

		channels = ctx.bot.storage.fetch_all_aliases()
		print(channels)

def setup(bot: commands.Bot):
	bot.add_cog(Alias(bot))