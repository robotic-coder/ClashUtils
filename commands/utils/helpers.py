import discord
import discord.ext.commands
import coc
import re

def pad_left(data, desired_length, char=" "):
	data = str(data)
	return repeat(char, desired_length-len(data))+data

def pad_right(data, desired_length, char=" "):
	data = str(data)
	return data+repeat(char, desired_length-len(data))

# to be removed
async def send_lines_in_embed(channel: discord.TextChannel, lines: list, embed=discord.Embed(), first_message_content=""):
	embeds = generate_embeds(lines, embed)
	return await send_embeds_in_multiple_messages(channel, embeds, first_message_content)

def generate_embeds(lines: list, embed=discord.Embed()):
	while len(lines) > 0:
		if (embed.description == discord.Embed.Empty):
			embed.description = lines.pop(0)
		elif len(embed.description+"\n"+lines[0]) <= 2048:
			embed.description += "\n"+lines.pop(0)
		else: break

	if len(lines) > 0:
		next_embed = discord.Embed(colour=embed.colour)
		if embed.footer is not discord.Embed.Empty:
			next_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)
			embed.set_footer()

		output = generate_embeds(lines, next_embed)
		return [embed]+output
	else:
		return [embed]

# to be removed
async def send_embeds_in_multiple_messages(channel, embeds, first_message_content=""):
	if len(embeds) > 0:
		message = await channel.send(first_message_content, embed=embeds.pop(0))
		output = await send_embeds_in_multiple_messages(channel, embeds)
		return [message]+output
	elif len(first_message_content) > 0:
		message = await channel.send(first_message_content)
		return [message]
	else:
		return []

# to be removed
def resolve_clan(tag_or_alias, ctx):
	if tag_or_alias.startswith("#"):
		return tag_or_alias
	elif ctx.guild.id in ctx.bot.aliases and tag_or_alias in ctx.bot.aliases[ctx.guild.id]:
		ctx.bot.storage.update_last_used(ctx.guild.id, tag_or_alias)
		return ctx.bot.aliases[ctx.guild.id][tag_or_alias]
	elif tag_or_alias in ctx.bot.global_aliases:
		return ctx.bot.global_aliases[tag_or_alias]
	else: return None

# to be removed
def resolve_clan_slash(tag_or_alias, ctx):
	if tag_or_alias.startswith("#"):
		return tag_or_alias
	elif ctx.guild.id in ctx._discord.aliases and tag_or_alias in ctx._discord.aliases[ctx.guild.id]:
		ctx._discord.storage.update_last_used(ctx.guild.id, tag_or_alias)
		return ctx._discord.aliases[ctx.guild.id][tag_or_alias]
	elif tag_or_alias in ctx._discord.global_aliases:
		return ctx._discord.global_aliases[tag_or_alias]
	else: return None

async def find_current_war(tag: str, clash: coc.Client):
	war = await clash.get_current_war(tag)
	if war is None or (war is not None and war.is_cwl and war.state == "warEnded"):
		war = await clash.get_current_war(tag, cwl_round=coc.WarRound.current_preparation)
	return war

def stars(num_stars):
	output = ""
	for _i in range(0, num_stars):
		output += "★"
	for _i in range(num_stars, 3):
		output += "☆"
	return output

def round_fixed(input, num_places):
	return ("{:."+str(num_places)+"f}").format(round(input, num_places))

def repeat(char, num_repeats):
	return char*num_repeats

def spaces(num_spaces):
	return repeat(" ", num_spaces)

async def send_usage(command, ctx):
	await ctx.channel.send("Unknown syntax. Usage: `"+ctx.prefix+command.name+" "+command.usage+"`")

def get_command_help(ctx, command):
	if ctx is discord.ext.commands.Context:
		prefix = ctx.prefix
	else:
		prefix = "//"
	embed = discord.Embed(title=command.qualified_name, description=command.brief)
	embed.add_field(name="Usage", value=prefix+command.qualified_name+" "+command.usage, inline=False)
	embed.add_field(name="Example", value=prefix+command.qualified_name+" "+command.help, inline=False)
	return embed

async def send_command_help(ctx, command):
	embed = get_command_help(ctx, command)
	await ctx.send("Please check your command syntax:", embed=embed)

async def send_command_list(ctx, command_holder, using_help_command=False):
	embed = discord.Embed()
	if isinstance(command_holder, discord.ext.commands.Group):
		embed.title = command_holder.name
		embed.description = command_holder.brief
	else:
		embed.title = "ClashUtils Help"
	embed.set_footer(text="Use "+ctx.prefix+"help [command] to view more information about a specific command.")

	for command in sorted([cmd for cmd in command_holder.commands if not cmd.hidden], key=lambda cmd: cmd.name):
		if not command.hidden:
			if isinstance(command, discord.ext.commands.Group):
				subcommands = " *("+", ".join([cmd.name for cmd in sorted(command.commands, key=lambda cmd: cmd.name) if not cmd.hidden])+")*"
			else: subcommands = ""
			embed.add_field(name=command.qualified_name+subcommands, value=command.description, inline=False)
	if using_help_command:
		await ctx.send(embed=embed)
	else:
		await ctx.send("Please check your command syntax:", embed=embed)


