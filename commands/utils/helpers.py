import discord
import discord.ext.commands
import coc
import re

def pad_left(data, desired_length):
	data = str(data)
	return spaces(desired_length-len(data))+data

def pad_right(data, desired_length):
	data = str(data)
	return data+spaces(desired_length-len(data))

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
		next_embed = discord.Embed()
		if embed.footer is not discord.Embed.Empty:
			next_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)
			embed.set_footer()

		output = generate_embeds(lines, next_embed)
		return [embed]+output
	else:
		return [embed]

async def send_embeds_in_multiple_messages(channel, embeds, first_message_content=""):
	message = await channel.send(first_message_content, embed=embeds.pop(0))
	if len(embeds) > 0:
		output = await send_embeds_in_multiple_messages(channel, embeds)
		output.append(message)
		return output
	else:
		return [message]

def resolve_clan(tag_or_alias, ctx):
	if tag_or_alias.startswith("#"):
		return tag_or_alias
	elif ctx.guild.id in ctx.bot.aliases and tag_or_alias in ctx.bot.aliases[ctx.guild.id]:
		ctx.bot.storage.update_last_used(ctx.guild.id, tag_or_alias)
		return ctx.bot.aliases[ctx.guild.id][tag_or_alias]
	else: return None

def stars(num_stars):
	output = ""
	for _i in range(0, num_stars):
		output += "★"
	for _i in range(num_stars, 3):
		output += "☆"
	return output

def round_fixed(input, num_places):
	return ("{:."+str(num_places)+"f}").format(round(input, num_places))

def spaces(num_spaces):
	return " "*num_spaces

async def send_usage(command, ctx):
	await ctx.channel.send("Unknown syntax. Usage: `"+ctx.prefix+command.name+" "+command.usage+"`")


async def send_command_help(ctx, command, using_help_command=False):
	embed = discord.Embed(title=command.qualified_name, description=command.brief)
	embed.add_field(name="Usage", value=ctx.prefix+command.qualified_name+" "+command.usage, inline=False)
	embed.add_field(name="Example", value=ctx.prefix+command.qualified_name+" "+command.help, inline=False)
	if using_help_command:
		if command.name == "help":
			await ctx.send("Yo dawg, I heard you liked `"+ctx.prefix+"help`. So I put `help` in `"+ctx.prefix+"help`, so you can learn to use `"+ctx.prefix+"help` while you use `"+ctx.prefix+"help`.", embed=embed)
		else: await ctx.send(embed=embed)
	else: await ctx.send("Please check your command syntax:", embed=embed)


async def send_command_list(ctx, command_holder, using_help_command=False):
	if isinstance(command_holder, discord.ext.commands.Group):
		title = command_holder.name
	else:
		title = "ClashUtils Help"

	embed = discord.Embed(title=title, description="")
	for command in sorted([cmd for cmd in command_holder.commands if not cmd.hidden], key=lambda cmd: cmd.name):
		if not command.hidden:
			if isinstance(command, discord.ext.commands.Group):
				subcommands = ", ".join([cmd.name for cmd in command.commands if not cmd.hidden])
				embed.description += "**"+ctx.prefix+command.qualified_name+"** *"+subcommands+" ...*\n"+command.brief+"\n"
			else:
				usage = command.usage
				if usage != "": usage = "*"+usage+"*"
				embed.description += "**"+ctx.prefix+command.qualified_name+"** "+usage+"\n"+command.brief+"\n"
	if using_help_command:
		await ctx.send(embed=embed)
	else:
		await ctx.send("Please check your command syntax:", embed=embed)

