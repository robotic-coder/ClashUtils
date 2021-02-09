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

def generate_embeds(lines: list, embed=discord.Embed()):
	while len(lines) > 0:
		if (embed.description == discord.Embed.Empty):
			embed.description = lines.pop(0)
		elif len(embed) <= 6000 and len(embed.description+"\n"+lines[0]) <= 2048:
			embed.description += "\n"+lines.pop(0)
		else: break

	if len(lines) > 0:
		next_embed = discord.Embed(colour=embed.colour)
		if embed.footer is not discord.Embed.Empty:
			next_embed.set_footer(text=embed.footer.text, icon_url=embed.footer.icon_url)
			delattr(embed, "_footer")
			# This may break at any time, there is no official way to remove a footer.
			# set_footer() does not properly remove it and causes errors with len(embed).

		output = generate_embeds(lines, next_embed)
		return [embed]+output
	else:
		return [embed]

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