import discord
import discord.ext.commands
import coc
import commands.utils.helpers as helpers

@discord.ext.commands.command()
async def link(ctx: discord.ext.commands.Context, *args):
	if ctx.author.guild_permissions.manage_guild == False:
		await ctx.channel.send("You need `Manage Server` permissions to add aliases in this server.")

	if len(args) != 2:
		await ctx.channel.send("format: `/link [#CLANTAG] [alias]`")
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

@discord.ext.commands.command()
async def unlink(ctx: discord.ext.commands.Context, *args):
	if ctx.author.guild_permissions.manage_guild == False:
		await ctx.channel.send("You need `Manage Server` permissions to remove aliases in this server.")

	if len(args) != 1:
		await ctx.channel.send("format: `/unlink [alias]`")
		return

	alias = args[0]
	tag = helpers.resolve_clan(alias, ctx)
	snowflake = ctx.guild.id
	
	if tag is None:
		await ctx.channel.send("There is no clan linked to the alias `"+alias+"` in this server.")
		return
		
	ctx.bot.unlink_guild(snowflake, alias)
	ctx.bot.storage.unlink_guild(snowflake, alias)
	await ctx.channel.send("You have removed the alias `"+alias+"` from this server.")

	channels = ctx.bot.storage.fetch_all_aliases()
	print(channels)

def setup(bot: discord.ext.commands.Bot):
	link.help = "Links the given alias to the given clan. When linked, you can run commands in this server with the alias instead of the clan tag."
	link.usage = "[#CLANTAG] [alias]"
	setattr(link, "example", "#8PQGQC8 myclan")
	setattr(link, "required_permissions", ["send_messages"])
	bot.add_command(link)
	unlink.help = "Removes the given alias from this server. You must use a previously-linked alias."
	unlink.usage = "[alias]"
	setattr(unlink, "example", "myclan")
	setattr(unlink, "required_permissions", ["send_messages"])
	bot.add_command(unlink)