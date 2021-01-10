import discord
import discord.ext.commands as commands
import coc
import psycopg2
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
		try:
			ctx.bot.storage.link_guild(snowflake, alias, tag)
			ctx.bot.link_guild(snowflake, alias, tag)
			await ctx.channel.send("You have linked `"+alias+"` to "+clan.name+" in this server.")
		except psycopg2.Error:
			await ctx.channel.send(clan.name+" is already linked to another alias in this server.")
			

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

	@alias.command(
		name="list",
		description = "Displays all clan aliases in this server.",
		brief = "Displays all clan aliases in this server.",
		usage = "",
		help = ""
	)
	async def alias_list(self, ctx: commands.Context, *args):
		if len(args) > 0:
			await send_command_help(ctx, self.alias_list)
			return

		aliases = ctx.bot.storage.fetch_guild_aliases(ctx.guild.id)
		clans = await ctx.bot.clash.get_clans([a["clan"] for a in aliases]).flatten()
		lines = []
		for i in range(len(clans)):
			lines.append("`"+aliases[i]["alias"]+"` - "+clans[i].name+" ("+clans[i].tag+")")

		embed = discord.Embed(title="Clan Tag Aliases")
		embed.set_author(name=ctx.guild.name)
		await send_lines_in_embed(ctx.channel, lines, embed)

def setup(bot: commands.Bot):
	bot.add_cog(Alias(bot))