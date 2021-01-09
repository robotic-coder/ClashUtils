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
	description = "Displays a clan's current war status.",
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
		(embeds, content) = await currentwar(tag, None, len(args) == 2 and args[1] == "full", clash)
		await send_embeds_in_multiple_messages(ctx.channel, embeds, content)
		
async def currentwar(tag, cwl_round, show_names, clash):
	if cwl_round is None:
		war = await find_current_war(tag, clash)
		if war is None:
			clan = await clash.get_clan(tag)
			return ([], clan.name+" ("+tag+") has a private war log.")
		elif war.state == "notInWar":
			clan = await clash.get_clan(tag)
			return ([], clan.name+" ("+tag+") is not in war.")
	else:
		group = await clash.get_league_group(tag)
		if group is None:
			return([], clan.name+" ("+tag+") is not in CWL.")
		elif cwl_round > len(group.rounds):
			if cwl_round <= 7:
				return([], "I can't see wars that haven't started yet. Select a number between 1 and "+str(len(group.rounds))+".")
			return([], "Select a number between 1 and "+str(len(group.rounds))+".")
		war = await clash.get_league_wars(group.rounds[cwl_round-1], tag)._next()
	
	bases = []
	for i in range(war.team_size):
		base = {}
		base["clan"] = war.clan.members[i]
		base["enemy"] = war.opponent.members[i]
		bases.append(base)

	embed = discord.Embed(title="War Map")
	if war.state == "preparation":
		return await create_map_prep(clash, war, bases, show_names, embed)
	else:
		return create_map_battle(war, bases, show_names, embed)

async def find_current_war(tag, clash):
	war = await clash.get_current_war(tag)
	if war is None or (war is not None and war.is_cwl and war.state == "warEnded"):
		war = await clash.get_current_war(tag, cwl_round=coc.WarRound.current_preparation)
	return war
	

async def create_map_prep(clash, war, bases_input, show_names, embed):
	content = "\n".join([
		"**"+war.clan.name+"** vs **"+war.opponent.name+"**",
		"Starting in "+get_time_delta(war.start_time.now, war.start_time.time)
	])

	bases = []
	clan = await clash.get_players([base["clan"].tag for base in bases_input]).flatten()
	enemy = await clash.get_players([base["enemy"].tag for base in bases_input]).flatten()
	for i in range(len(bases_input)):
		bases.append({
			"clan": clan[i],
			"enemy": enemy[i]
		})

	lines = []
	for index, base in enumerate(bases):
		clan_heroes_list = {
			"Barbarian King": " ",
			"Archer Queen": "  ",
			"Grand Warden": "  ",
			"Royal Champion": "  "
		}
		for hero in base["clan"].heroes:
			if hero.is_home_base: clan_heroes_list[hero.name] = pad_left(hero.level, 2, "0")

		enemy_heroes_list = {
			"Barbarian King": " ",
			"Archer Queen": "  ",
			"Grand Warden": "  ",
			"Royal Champion": "  "
		}
		for hero in base["enemy"].heroes:
			if hero.is_home_base: enemy_heroes_list[hero.name] = pad_left(hero.level, 2, "0")
		
		clan_heroes = "/".join([level for (index, level) in enumerate(clan_heroes_list.values()) if index*2 <= base["clan"].town_hall-7])
		enemy_heroes = "/".join([level for (index, level) in enumerate(enemy_heroes_list.values()) if index*2 <= base["enemy"].town_hall-7])
		clan_name = ""
		enemy_name = ""
		clan_th = base["clan"].town_hall
		enemy_th = base["enemy"].town_hall

		if show_names:
			clan_name = "\u2066"+pad_left(base["clan"].name, 15)+"  "
			enemy_name = "  "+pad_right(base["enemy"].name, 15)

		clan_line = "`"+clan_name+pad_right(clan_heroes, 11)+"`"+str(emojis.th[clan_th])+"`"
		enemy_line = "`"+str(emojis.th[enemy_th])+"`"+pad_right(enemy_heroes, 11)+enemy_name+"`"
		lines.append(clan_line+" "+pad_left((index+1), 2)+" "+enemy_line)
	embeds = generate_embeds(lines, embed)
	return (embeds, content)

def create_map_battle(war, bases, show_names, embed):
	if war.type == "cwl": max_attacks = 1
	else: max_attacks = 2

	if war.state == "inWar":
		state = get_time_delta(war.end_time.now, war.end_time.time)+" remaining"
	elif war.state == "warEnded":
		state = "Ended "+get_time_delta(war.end_time.time, war.end_time.now)+" ago"

	content = "\n".join([
		"**"+war.clan.name+"** vs **"+war.opponent.name+"**",
		state,
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

	bot.slash.add_slash_command(currentwar_slash,
		name="currentwar",
		description="Displays the war status for the given clan.",
		guild_ids=bot.command_guild_ids,
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"required": True
		},
		{
			"type": 4,
			"name": "cwl-round",
			"description": "A specific CWL round to fetch. The war must be in preparation or a later stage.",
			"required": False
		},
		{
			"type": 3,
			"name": "size",
			"description": "The amount of data to be shown. `full` will probably display incorrectly on a phone.",
			"required": False,
			"choices": [
				{
					"name": "full",
					"value": "full"
				},
				{
					"name": "compact",
					"value": "compact"
				}
			]
		}]
	)

async def currentwar_slash(ctx: SlashContext, clan, cwl_round=None, size="compact"):
	await ctx.send(content="Loading...\nNote: This feature is in beta, and not all `//` commands are supported yet.")

	tag = resolve_clan_slash(clan, ctx)
	clash = ctx._discord.clash
	
	if tag is None:
		#await send_command_help(ctx, currentwar_standard)
		return

	if cwl_round == "full" or cwl_round == "compact":
		size = cwl_round
		cwl_round = None

	(embeds, content) = await currentwar(tag, cwl_round, size == "full", clash)
	await ctx.send(content=content, embeds=embeds)