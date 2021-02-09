import discord
import discord.ext.commands
from commands.utils.helpers import *
from discord_slash import SlashCommand, SlashContext

def get_help_standard(command_holder, *args):
	if len(args) == 0:
		return get_standard_command_list(command_holder)

	elif args[0] in [cmd.name for cmd in command_holder.commands if not cmd.hidden]:
		command = [cmd for cmd in command_holder.commands if cmd.name == args[0]][0]
		if isinstance(command, discord.ext.commands.Group):
			return get_help_standard(command, *args[1:])
		else:
			return get_standard_command_details(command)
	else:
		return None

def get_standard_command_details(command):
	embed = discord.Embed(title=command.qualified_name, description=command.brief)
	embed.add_field(name="Usage", value="//"+command.qualified_name+" "+command.usage, inline=False)
	embed.add_field(name="Example", value="//"+command.qualified_name+" "+command.help, inline=False)
	return embed

def get_standard_command_list(command_holder):
	embed = discord.Embed()
	if isinstance(command_holder, discord.ext.commands.Group):
		embed.title = command_holder.name
		embed.description = command_holder.brief
	else:
		embed.title = "ClashUtils Help"
	embed.set_footer(text="Use //help [command] to view more information about a specific command.")

	for command in sorted([cmd for cmd in command_holder.commands if not cmd.hidden], key=lambda cmd: cmd.name):
		if not command.hidden:
			if isinstance(command, discord.ext.commands.Group):
				subcommands = " *("+", ".join([cmd.name for cmd in sorted(command.commands, key=lambda cmd: cmd.name) if not cmd.hidden])+")*"
			else: subcommands = ""
			embed.add_field(name=command.qualified_name+subcommands, value=command.description, inline=False)
	return embed









def get_help_slash(bot: discord.ext.commands.Bot, command: str):
	lookup = slash_command_search(bot, command.split(" "))
	if lookup is None:
		return None
	else:
		(result, result_type) = lookup

	if result_type == "command":
		return get_slash_command_details(bot, result)
	else:
		return get_slash_command_list(bot, result)

def slash_command_search(bot: discord.ext.commands.Bot, query: str):
	matches = [(key, value) for (key, value) in bot.slash.commands.items() if key==query[0]]
	if len(matches) == 0:
		return None
	(name, cmd) = matches[0]
	if (cmd.has_subcommands):
		return slash_subcommand_search(bot.slash.subcommands, query)
	else:
		return (cmd, "command")

def get_slash_command_details(bot: discord.ext.commands.Bot, command):
	#message = ""
	if hasattr(command, "base"):
		if command.subcommand_group is not None:
			title = command.base+" "+command.subcommand_group+" "+command.name
		else:
			title = command.base+" "+command.name
	else:
		title = command.name
		#if command.name == "help":
			#message = "Yo dawg, I heard you liked `/help`. So I put `help` in `/help`, so you can learn to use `/help` while you use `/help`."
	
	embed = discord.Embed(title=title, description=command.description)

	example = "/"+title
	options = bot.slash_command_options[title]
	if options is not None:
		embed.add_field(name="Options", value="\n".join(["`"+o["name"]+"` ("+("required" if o["required"] else "optional")+"): "+o["description"] for o in options]), inline=False)
		example += "".join([" `"+o["name"]+": "+o["example"]+"`" for o in options])
	embed.add_field(name="Example", value=example, inline=False)
	return embed

def get_slash_command_list(bot: discord.ext.commands.Bot, result):
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
			subs = slash_command_search(bot, [cmd.name])
			if subs is not None and subs[1] == "list":
				extras = " *("+", ".join(sorted(list(subs[0].keys())))+")*"
			embed.add_field(name=cmd.name+extras, value=cmd.description, inline=False)
	embed.set_footer(text="Use /help-cu [command] to view more information about a specific command.")
	return embed

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

def slash_subcommand_search(commands_dict, query):
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
		return slash_subcommand_search(commands_dict[name], query[1:])
	else:
		return None
			
