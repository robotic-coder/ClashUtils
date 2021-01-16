import discord
import discord.ext.commands
import coc
import psycopg2
from commands.utils.helpers import *
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

@discord.ext.commands.group(
	description = "Manages aliases that can be used in place of clan tags.",
	brief = "Manages aliases that can be used in place of clan tags."
)
async def alias(ctx: discord.ext.commands.Context):
	if ctx.invoked_subcommand is None:
		await send_command_list(ctx, alias)
		return

async def add(resp: Responder, alias_name: str, tag: str):
	if resp.author is None:
		return await resp.send("I can't see your server permissions. Please add me to the server.")
	if resp.author.guild_permissions.manage_guild == False:
		return await resp.send("You need `Manage Server` permissions to add aliases in this server.")
	if alias_name.startswith("#"):
		return await resp.send("Alias cannot begin with a #")
	if len(alias_name) > 15:
		return await resp.send("Max alias length: 15 characters")

	duplicate = resp.resolve_clan(alias_name)
	if duplicate is not None:
		clan = await resp.clash.get_clan(duplicate)
		return await resp.send("`"+alias_name+"` is already linked to "+clan.name+" ("+clan.tag+") in this server.")
	
	snowflake = resp.guild_id
	clan = await resp.clash.get_clan(tag)
	try:
		resp.bot.storage.link_guild(snowflake, alias_name, tag)
		resp.bot.link_guild(snowflake, alias_name, tag)
		await resp.send("You have linked `"+alias_name+"` to "+clan.name+" in this server.")
	except psycopg2.Error:
		await resp.send(clan.name+" is already linked to another alias in this server.")

async def remove(resp: Responder, alias_name: str):
	if resp.author is None:
		return await resp.send("I can't see your server permissions. Please add me to the server.")
	if resp.author.guild_permissions.manage_guild == False:
		return await resp.send("You need `Manage Server` permissions to remove aliases in this server.")

	tag = resp.resolve_clan(alias_name)
	snowflake = resp.guild_id
	
	if tag is None:
		return await resp.send("There is no clan linked to the alias `"+alias_name+"` in this server.")
		
	resp.bot.unlink_guild(snowflake, alias_name)
	resp.bot.storage.unlink_guild(snowflake, alias_name)
	await resp.send("You have removed the alias `"+alias_name+"` from this server.")

async def _list(resp: Responder):
	aliases = resp.bot.storage.fetch_guild_aliases(resp.guild_id)
	clans = await resp.clash.get_clans([a["clan"] for a in aliases]).flatten()
	lines = []
	for i in range(len(clans)):
		lines.append("`"+aliases[i]["alias"]+"` - "+clans[i].name+" ("+clans[i].tag+")")

	embed = discord.Embed(title="Clan Tag Aliases")
	embed.set_author(name=resp.guild.name)
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)

@alias.command(
	name="add",
	description = "Adds a clan alias to this server.",
	brief = "Links the given alias to the given clan. When linked, you can run commands in this server with the alias instead of the clan tag.",
	usage = "[alias] [#CLANTAG]",
	help = "myclan #8PQGQC8"
)
async def add_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) != 2:
		await send_command_help(ctx, add_standard)
		return
	resp = StandardResponder(ctx)
	async with resp:
		await add(resp, args[0], args[1])

@alias.command(
	name="remove",
	description = "Removes an alias from this server.",
	brief = "Removes the given alias from this server. You must use a previously-linked alias.",
	usage = "[alias]",
	help = "myclan"
)
async def remove_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) != 1:
		await send_command_help(ctx, remove_standard)
		return
	resp = StandardResponder(ctx)
	await remove(resp, args[0])

@alias.command(
	name="list",
	description = "Displays all clan aliases in this server.",
	brief = "Displays all clan aliases in this server.",
	usage = "",
	help = ""
)
async def list_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) > 0:
		await send_command_help(ctx, list_standard)
		return
	resp = StandardResponder(ctx)
	async with resp:
		await _list(resp)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(alias)
	
	bot.slash.add_subcommand(add_slash, 
		base=bot.slash_command_prefix+"alias",
		base_description="Manages aliases that can be used in place of clan tags",
		name="add",
		description="Adds a clan alias to this server",
		guild_ids=bot.command_guild_ids,
		options=[{
			"type": 3,
			"name": "alias",
			"description": "A clan alias. May not begin with a #.",
			"required": True
		},
		{
			"type": 3,
			"name": "clan-tag",
			"description": "The tag of the clan to link.",
			"required": True
		}]
	)

	bot.slash.add_subcommand(remove_slash, 
		base=bot.slash_command_prefix+"alias",
		base_description="Manages aliases that can be used in place of clan tags",
		name="remove",
		description="Removes a clan alias from this server",
		guild_ids=bot.command_guild_ids,
		options=[{
			"type": 3,
			"name": "alias",
			"description": "A clan alias on this server",
			"required": True
		}]
	)

	bot.slash.add_subcommand(list_slash, 
		base=bot.slash_command_prefix+"alias",
		base_description="Manages aliases that can be used in place of clan tags",
		name="list",
		description="Displays all clan aliases in this server",
		guild_ids=bot.command_guild_ids,
		options=[]
	)

async def add_slash(ctx: SlashContext, alias, tag):
	resp = SlashResponder(ctx)
	async with resp:
		await add(resp, alias, tag)

async def remove_slash(ctx: SlashContext, alias):
	resp = SlashResponder(ctx)
	async with resp:
		await remove(resp, alias)

async def list_slash(ctx: SlashContext):
	resp = SlashResponder(ctx)
	async with resp:
		await _list(resp)