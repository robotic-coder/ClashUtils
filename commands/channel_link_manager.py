import discord
import discord.ext.commands
import coc
import commands.utils.helpers as helpers

@discord.ext.commands.command()
async def link(ctx: discord.ext.commands.Context, *args):
	#TODO prevent creating more than 1 prefix for 1 clan in a channel
	(tag, params) = helpers.resolve_clan(ctx)
	clash = ctx.bot.clash
	
	if tag is None or len(params) != 1:
		await ctx.channel.send("format: `<@786654276185096203> link [#CLANTAG] [prefix]`")
		return
	
	snowflake = ctx.channel.id
	prefix = params[0]
	if len(prefix) > 5:
		await ctx.channel.send("max prefix length: 5 characters")
		return
		
	clan = await clash.get_clan(tag)
	ctx.bot.link_channel(snowflake, prefix, tag)
	ctx.bot.storage.link_channel(snowflake, prefix, tag)
	await ctx.channel.send("You have linked "+ctx.channel.mention+" (prefix `"+prefix+"`) to "+clan.name)

	channels = ctx.bot.storage.fetch_all_channels()
	print(channels)

@discord.ext.commands.command()
async def unlink(ctx: discord.ext.commands.Context, *args):
	(tag, params) = helpers.resolve_clan(ctx)
	clash = ctx.bot.clash
	
	if str(ctx.bot.user.id) in ctx.prefix:
		await ctx.channel.send("You cannot unlink channels by tagging me! Please use a valid pre")
		return

	if tag is None:
		await ctx.channel.send("There is no clan linked to the prefix `"+ctx.prefix+"` in this channel.")
		return
	
	if len(params) != 0:
		await ctx.channel.send("format: `"+ctx.prefix+"unlink`")
		return

	snowflake = ctx.channel.id
		
	clan = await clash.get_clan(tag)
	ctx.bot.unlink_channel(snowflake, ctx.prefix)
	ctx.bot.storage.unlink_channel(snowflake, ctx.prefix)
	await ctx.channel.send("You have unlinked "+ctx.channel.mention+" (prefix `"+ctx.prefix+"`) from "+clan.name)

	channels = ctx.bot.storage.fetch_all_channels()
	print(channels)

def setup(bot: discord.ext.commands.Bot):
	link.help = "Links this channel and the given prefix to the given clan. When linked, you can call commands with this prefix and leave out clan tags."
	link.usage = "link [#CLANTAG] [prefix]"
	setattr(link, "example", "link #8PQGQC8 /")
	bot.add_command(link)
	unlink.help = "Unlinks this channel/prefix combination from its clan. You must use a previously-linked prefix."
	unlink.usage = "unlink"
	setattr(unlink, "example", "unlink")
	bot.add_command(unlink)