import discord
import discord.ext.commands
from commands.utils.helpers import *
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

@discord.ext.commands.command(
	name = "help",
	description = "Displays information about commands.",
	brief = "Shows this message, or more information about a specific command.",
	usage = "[command]",
	help = "alias add"
)
async def help_standard(ctx: discord.ext.commands.Context, *args):
	await send_help(ctx, ctx.bot, *args)

async def send_help(ctx, command_holder, *args):
	if len(args) == 0:
		await send_command_list(ctx, command_holder, True)

	elif args[0] in [cmd.name for cmd in command_holder.commands if not cmd.hidden]:
		command = [cmd for cmd in command_holder.commands if cmd.name == args[0]][0]
		if isinstance(command, discord.ext.commands.Group):
			await send_help(ctx, command, *args[1:])
		else:
			embed = get_command_help(ctx, command)
			if command.name == "help":
				await ctx.send("Yo dawg, I heard you liked `"+ctx.prefix+"help`. So I put `help` in `"+ctx.prefix+"help`, so you can learn to use `"+ctx.prefix+"help` while you use `"+ctx.prefix+"help`.", embed=embed)
			else: await ctx.send(embed=embed)

	else:
		await ctx.send("I can't find that command 🤔")

def setup(bot: discord.ext.commands.Bot):
	bot.help_command = None
	bot.add_command(help_standard)

	bot.add_slash_command(help_slash,
		name="cu-help",
		description="Displays details about commands",
		options=[{
			"type": 3,
			"name": "command",
			"description": "A specific command to search for",
			"example": "alias add",
			"required": False
		}]
	)

async def help_slash(ctx: SlashContext, command=None):
	resp = SlashResponder(ctx)

	if command is None:
		return await slash_send_command_list(resp, resp.bot.slash.commands)

	lookup = command_search(resp, command.split(" "))
	if lookup is None:
		return await resp.send("Unknown command")
	else:
		(result, result_type) = lookup

	if result_type == "command":
		await slash_send_command_details(resp, result)
	else:
		await slash_send_command_list(resp, result)

def command_search(resp, query):
	matches = [(key, value) for (key, value) in resp.bot.slash.commands.items() if key==query[0]]
	if len(matches) == 0:
		return None
	(name, cmd) = matches[0]
	if (cmd.has_subcommands):
		return search_subcommands(resp.bot.slash.subcommands, query)
	else:
		return (cmd, "command")

async def slash_send_command_details(resp, command):
	message = ""
	if hasattr(command, "base"):
		if command.subcommand_group is not None:
			title = command.base+" "+command.subcommand_group+" "+command.name
		else:
			title = command.base+" "+command.name
	else:
		title = command.name
		if command.name == "help":
			message = "Yo dawg, I heard you liked `/help`. So I put `help` in `/help`, so you can learn to use `/help` while you use `/help`."
	
	embed = discord.Embed(title=title, description=command.description)

	example = "/"+title
	options = resp.bot.slash_command_options[title]
	if options is not None:
		embed.add_field(name="Options", value="\n".join(["`"+o["name"]+"` ("+("required" if o["required"] else "optional")+"): "+o["description"] for o in options]), inline=False)
		example += "".join([" `"+o["name"]+": "+o["example"]+"`" for o in options])
	embed.add_field(name="Example", value=example, inline=False)
	await resp.send(message, [embed])

async def slash_send_command_list(resp, result):
	first = list(result.values())[0]
	if hasattr(first, "base"):
		if first.subcommand_group is not None:
			title = first.base+" "+first.subcommand_group
			description = first.subcommand_group_description
		else:
			title = first.base
			description = first.base_description
		embed = discord.Embed(title=title, description=description)
		for cmd in sorted(list(result.values()), key=lambda x: x.name):
			embed.add_field(name=title+" "+cmd.name, value=cmd.description, inline=False)
	else:
		embed = discord.Embed(title="ClashUtils Help")
		for cmd in sorted(list(result.values()), key=lambda x: x.name):
			extras = ""
			subs = command_search(resp, [cmd.name])
			if subs is not None and subs[1] == "list":
				extras = " *("+", ".join(sorted(list(subs[0].keys())))+")*"
			embed.add_field(name=cmd.name+extras, value=cmd.description, inline=False)
	embed.set_footer(text="Use /help [command] to view more information about a specific command.")
	await resp.send(embeds=[embed])

"""async def search_base(resp):
	for (name, cmd) in resp.bot.slash.commands.items():
		print(cmd.name)
		print(cmd.description)
		if cmd.has_subcommands:
			for (name2, cmd2) in resp.bot.slash.subcommands[name].items():
				if isinstance(cmd2, dict):
					print("\t"+name2)
					print("\t"+list(resp.bot.slash.subcommands[name][name2].values())[0].subcommand_group_description)
					for (name3, cmd3) in resp.bot.slash.subcommands[name][name2].items():
						print("\t\t"+cmd3.name)
						print("\t\t"+cmd3.description)
				else:
					print("\t"+cmd2.name)
					print("\t"+cmd2.description)"""

def search_subcommands(commands_dict, query):
	matches = [x for x in commands_dict.items() if x[0]==query[0]]
	
	if len(matches) == 0:
		return None

	(name, cmd) = matches[0]
	if len(query) == 1:
		if isinstance(cmd, dict):
			return (cmd, "list")
		else:
			return (cmd, "command")
	elif len(query) > 0 and isinstance(cmd, dict):
		return search_subcommands(commands_dict[name], query[1:])
	else:
		return None
			
