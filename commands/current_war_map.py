import discord
import discord.ext.commands
import coc
from math import floor
from datetime import datetime
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext

@discord.ext.commands.command(
	name = "currentwar",
	description = "Displays a clan's current war.",
	brief = "Displays the current war for the given clan.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def currentwar_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) < 1 or len(args) > 2:
		await send_command_help(ctx, currentwar_standard)
		return

	tag = resolve_clan(args[0], ctx)
	clash = ctx.bot.clash
	
	if tag is None:
		await send_command_help(ctx, currentwar_standard)
		return

	async with ctx.channel.typing():
		(embeds, content) = await currentwar(tag, len(args) == 2 and args[1] == "full", clash)
		await send_embeds_in_multiple_messages(ctx.channel, embeds, content)
		
async def currentwar(tag, show_names, clash):
	war = await clash.get_current_war(tag)
	if war is None: war = await clash.get_current_war(tag, cwl_round=coc.WarRound.current_preparation)
	if war is None: war = await clash.get_current_war(tag, cwl_round=coc.WarRound.previous_war)
	if war is None:
		clan = await clash.get_clan(tag)
		return ([], clan.name+" ("+tag+") has a private war log.")
	
	if war.state == "notInWar":
		clan = await clash.get_clan(tag)
		return ([], clan.name+" ("+tag+") is not in war.")

	if war.type == "cwl": max_attacks = 1
	else: max_attacks = 2
	
	bases = []
	for i in range(war.team_size):
		base = {}
		base["clan"] = war.clan.members[i]
		base["enemy"] = war.opponent.members[i]
		bases.append(base)

	if war.state == "preparation":
		status = "Starting in "+get_time_delta(war.start_time.now, war.start_time.time)
		print(war.start_time)
	elif war.state == "inWar":
		status = get_time_delta(war.end_time.now, war.end_time.time)+" remaining"
	elif war.state == "warEnded":
		status = "Ended "+get_time_delta(war.end_time.time, war.end_time.now)+" ago"
	else:
		status = "Unknown status"

	embed = discord.Embed(title="War Map")
	embed.set_footer(text=status)

	content = "\n".join([
		"**"+war.clan.name+"** vs **"+war.opponent.name+"**",
		"`Stars             "+pad_left(war.clan.stars, 3)+" - "+pad_right(war.opponent.stars, 3)+spaces(4)+"`",
		"`Destruction   "+pad_left(round_fixed(war.clan.destruction, 2)+"%", 7)+" - "+pad_right(round_fixed(war.opponent.destruction, 2)+"%", 7)+"`",
		"`Attacks Used      "+pad_left(war.clan.attacks_used, 3)+" - "+pad_right(war.opponent.attacks_used, 3)+spaces(4)+"`",
		"`Attacks Remaining "+pad_left(max_attacks*war.team_size-war.clan.attacks_used, 3)+" - "+pad_right(max_attacks*war.team_size-war.opponent.attacks_used, 3)+spaces(4)+"`"
	])

	lines = []
	for index, base in enumerate(bases):
		clan_name = ""
		clan_stars = 0
		clan_dest = ""
		enemy_name = ""
		enemy_stars = 0
		enemy_dest = ""
		clan_attacks = ""
		enemy_attacks = ""
		clan_th = base["clan"].town_hall
		enemy_th = base["enemy"].town_hall

		if show_names: clan_name = "\u2066"+pad_left(base["clan"].name, 15)+" "
		if base["clan"].best_opponent_attack is not None:
			clan_stars = base["clan"].best_opponent_attack.stars
			clan_dest = str(base["clan"].best_opponent_attack.destruction)+"%"

		for i in range(len(base["clan"].attacks), max_attacks): clan_attacks += "*"
		for i in range(0, len(base["clan"].attacks)): clan_attacks += " "

		if show_names: enemy_name = " "+pad_right(base["enemy"].name, 15)
		if base["enemy"].best_opponent_attack is not None:
			enemy_stars = base["enemy"].best_opponent_attack.stars
			enemy_dest = str(base["enemy"].best_opponent_attack.destruction)+"%"

		for i in range(0, len(base["enemy"].attacks)): enemy_attacks += " "
		for i in range(len(base["enemy"].attacks), max_attacks): enemy_attacks += "*"

		clan_line = "`"+clan_name+pad_left(clan_dest, 4)+"` "+stars(clan_stars)+" "+str(emojis.th[clan_th])+"`"+clan_attacks
		enemy_line = enemy_attacks+"`"+str(emojis.th[enemy_th])+" "+stars(enemy_stars)+" `"+pad_right(enemy_dest, 4)+enemy_name+"`"
		lines.append(clan_line+" "+pad_left((index+1), 2)+" "+enemy_line)
	embeds = generate_embeds(lines, embed)
	return (embeds, content)

def get_time_delta(start, end):
	delta = end-start
	if delta.seconds < 0:
		return "now"
	minutes = floor(delta.seconds/60)
	hours = floor(minutes/60)
	minutes %= 60

	output = str(minutes)+"m"

	if hours > 0: output = str(hours)+"h "+output
	else: return output

	if delta.days > 0: output = str(delta.days)+"d "+output
	return output

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(currentwar_standard)

	slash = SlashCommand(bot, auto_register=True)
	slash.add_slash_command(currentwar_slash,
		name="currentwar",
		#guild_ids=[738656460430377013],
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"required": True
		},
		{
			"type": 3,
			"name": "size",
			"description": "The amount of data to be shown. `full` will probably display incorrectly on a phone.",
			"required": False,
			"choices": [
				{
					"name": "full",
					"value": "fl"
				},
				{
					"name": "compact",
					"value": "cmp"
				}
			]
		}]
	)

async def currentwar_slash(ctx: SlashContext, clan, size="compact"):
	await ctx.send(content="This feature is in beta, and not all commands are supported yet.")

	tag = resolve_clan_slash(clan, ctx)
	clash = ctx._discord.clash
	
	if tag is None:
		#await send_command_help(ctx, currentwar_standard)
		return

	(embeds, content) = await currentwar(tag, size == "full", clash)
	await ctx.send(content=content, embeds=embeds)