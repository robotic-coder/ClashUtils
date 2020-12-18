import discord

def pad_left(data, desired_length):
	data = str(data)
	return spaces(desired_length-len(data))+data

def pad_right(data, desired_length):
	data = str(data)
	return data+spaces(desired_length-len(data))

async def send_lines_in_embed(channel: discord.TextChannel, lines: list, embed=discord.Embed(), first_message_content=""):
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

		message = await channel.send(first_message_content, embed=embed)
		output = await send_lines_in_embed(channel, lines, next_embed)
		output.append(message)
		return output
	else:
		message = await channel.send(first_message_content, embed=embed)
		return [message]

def resolve_clan(ctx):
	clan = None
	params = ctx.args[1:]

	if len(params) > 0 and params[0].startswith("#"):
		clan = params.pop(0)
	elif ctx.channel.id in ctx.bot.linked_channels and ctx.prefix in ctx.bot.linked_channels[ctx.channel.id]:
		clan = ctx.bot.linked_channels[ctx.channel.id][ctx.prefix]
		ctx.bot.storage.update_last_used(ctx.channel.id, ctx.prefix)

	return (clan, params)

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