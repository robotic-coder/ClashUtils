import discord
import discord.ext.commands
import coc
import re
from math import floor
from datetime import datetime
from commands.utils.helpers import *
from commands.utils.help import *
from utils.clash import Clash, War
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

@discord.ext.commands.group(
	name = "war",
	description = "Displays information from a clan's current war.",
	brief = "Displays information a clan's current war."
)
async def war_standard(ctx: discord.ext.commands.Context):
	resp = StandardResponder(ctx)
	if ctx.invoked_subcommand is None:
		return await resp.send(embeds=[get_standard_command_list(war_standard)])

async def get_war(resp: Responder, tag: str, num_attacks: str, cwl_round: int):
	if tag is None:
		await resp.send("Invalid clan tag or alias")
		return None

	if cwl_round is None:
		war = await resp.clash.get_current_war(tag, allow_prep=True)
		if war is None:
			clan = await resp.clash.get_clan(tag)
			await resp.send(clan.name+" ("+tag+") has a private war log.")
			return None
		elif war.state == "notInWar":
			clan = await resp.clash.get_clan(tag)
			await resp.send(clan.name+" ("+tag+") is not in war.")
			return None
		elif war.type != "friendly" and num_attacks is not None:
			clan = await resp.clash.get_clan(tag)
			await resp.send(clan.name+" ("+tag+") is not in a friendly war.")
			return None
	else:
		group = await resp.clash.get_league_group(tag)
		if group is None:
			await resp.send(clan.name+" ("+tag+") is not in CWL.")
			return None
		elif cwl_round > len(group.rounds):
			if cwl_round <= 7:
				await resp.send("I can't see wars that haven't started yet. Select a number between 1 and "+str(len(group.rounds))+".")
				return None
			await resp.send("Select a number between 1 and "+str(len(group.rounds))+".")
			return None
		war = await resp.clash.get_league_wars(group.rounds[cwl_round-1], tag, War)._next()
	return war

async def map(resp: Responder, tag: str, show_names: bool, num_attacks: str, cwl_round: int):
	tag = resp.resolve_clan(tag)
	war = await get_war(resp, tag, num_attacks, cwl_round)
	if war is None: return
	
	bases = []
	for i in range(war.team_size):
		base = {}
		base["clan"] = war.clan.members[i]
		base["enemy"] = war.opponent.members[i]
		bases.append(base)

	embed = discord.Embed(title="War Map")
	embed.set_footer(text=war.clan.tag+" vs "+war.opponent.tag)
	if war.status == "won":
		embed.colour = 65280 #00FF00
	elif war.status == "lost":
		embed.colour = 16711680 #FF0000
	elif war.status == "tie":
		embed.colour = 16711422 #FEFEFE
	
	if war.state == "preparation":
		(content, lines) = await create_map_prep(resp.clash, war, bases, show_names)
	else:
		result = create_map_battle(war, bases, show_names, num_attacks)
		if result is None:
			return await resp.send("This clan's war allows members to make 2 attacks.")
		(content, lines) = result
	embeds = generate_embeds(lines, embed)
	await resp.send(content, embeds)
	

async def create_map_prep(clash, war, bases_input, show_names):
	content = "\n".join([
		"**"+war.clan.name+"** vs **"+war.opponent.name+"**"+("\nCWL round "+str(war.cwl_round) if war.cwl_round is not None else ""),
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
	return (content, lines)

def create_map_battle(war, bases, show_names, max_attacks):
	if max_attacks is not None:
		max_attacks = int(max_attacks)
	elif war.type == "cwl":
		max_attacks = 1
	else:
		max_attacks = 2

	if war.state == "inWar":
		state = get_time_delta(war.end_time.now, war.end_time.time)+" remaining"
	elif war.state == "warEnded":
		state = "Ended "+get_time_delta(war.end_time.time, war.end_time.now)+" ago"

	duration_tiebreaker = war.clan.stars == war.team_size*3 and war.opponent.stars == war.team_size*3
	
	content = "\n".join([
		"**"+war.clan.name+"** vs **"+war.opponent.name+"**"+("\nCWL round "+str(war.cwl_round) if war.cwl_round is not None else ""),
		state,
		"`Stars             "+pad_left(war.clan.stars, 3)+" - "+pad_right(war.opponent.stars, 3)+spaces(4)+"`",
		"`Destruction   "+pad_left(round_fixed(war.clan.destruction, 2)+"%", 7)+" - "+pad_right(round_fixed(war.opponent.destruction, 2)+"%", 7)+"`",
		"`Attacks Used      "+pad_left(war.clan.attacks_used, 3)+" - "+pad_right(war.opponent.attacks_used, 3)+spaces(4)+"`",
		"`Attacks Remaining "+pad_left(max_attacks*war.team_size-war.clan.attacks_used, 3)+" - "+pad_right(max_attacks*war.team_size-war.opponent.attacks_used, 3)+spaces(4)+"`"
	])

	lines = []
	if duration_tiebreaker:
		score_padding = 6
	else: score_padding = 4
	for index, base in enumerate(bases):
		if len(base["clan"].attacks) > max_attacks or len(base["enemy"].attacks) > max_attacks:
			return None

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
			if duration_tiebreaker:
				clan_dest = convert_duration(base["clan"].best_opponent_attack.duration)
			else:
				clan_dest = str(base["clan"].best_opponent_attack.destruction)+"%"

		for i in range(len(base["clan"].attacks), max_attacks): clan_attacks += "*"
		for i in range(0, len(base["clan"].attacks)): clan_attacks += " "

		if show_names: enemy_name = " "+pad_right(base["enemy"].name, 15)
		if base["enemy"].best_opponent_attack is not None:
			enemy_stars = base["enemy"].best_opponent_attack.stars
			if duration_tiebreaker:
				enemy_dest = convert_duration(base["enemy"].best_opponent_attack.duration)
			else:
				enemy_dest = str(base["enemy"].best_opponent_attack.destruction)+"%"

		for i in range(0, len(base["enemy"].attacks)): enemy_attacks += " "
		for i in range(len(base["enemy"].attacks), max_attacks): enemy_attacks += "*"

		clan_line = "`"+clan_name+pad_left(clan_dest, score_padding)+"` "+stars(clan_stars)+" "+str(emojis.th[clan_th])+"`"+clan_attacks
		enemy_line = enemy_attacks+"`"+str(emojis.th[enemy_th])+" "+stars(enemy_stars)+" `"+pad_right(enemy_dest, score_padding)+enemy_name+"`"
		lines.append(clan_line+" "+pad_left((index+1), 2)+" "+enemy_line)

	return (content, lines)

def convert_duration(duration: int):
	seconds = duration % 60
	minutes = int((duration-seconds)/60)
	return str(minutes)+"m "+pad_left(seconds, 2, "0")+"s"

def get_time_delta(start, end):
	delta = end-start
	seconds = delta.total_seconds()
	if seconds < 0:
		return "0s"
	minutes = floor(seconds/60)
	hours = floor(minutes/60)
	minutes %= 60

	output = str(minutes)+"m"

	if hours > 0:
		if delta.days > 0: hours %= 24
		output = str(hours)+"h "+output
	else:
		return output

	if delta.days > 0: output = str(delta.days)+"d "+output
	return output

async def attacks(resp: Responder, tag: str, show_names: bool, max_attacks: str, cwl_round: int):
	tag = resp.resolve_clan(tag)
	war = await get_war(resp, tag, max_attacks, cwl_round)
	if war is None: return

	if war.state == "preparation":
		clan = await resp.clash.get_clan(tag)
		await resp.send(clan.name+" ("+tag+") is not in battle.")
		return None

	if max_attacks is not None:
		max_attacks = int(max_attacks)
	elif war.type == "cwl":
		max_attacks = 1
	else:
		max_attacks = 2

	for base in war.members:
		if len(base.attacks) > max_attacks:
			return await resp.send("This clan's war allows members to make 2 attacks.")

	embed = discord.Embed(title="Attacks")
	embed.set_footer(text=war.clan.tag+" vs "+war.opponent.tag)
	if war.status == "won":
		embed.colour = 65280 #00FF00
	elif war.status == "lost":
		embed.colour = 16711680 #FF0000
	elif war.status == "tie":
		embed.colour = 16711422 #FEFEFE

	if war.state == "inWar":
		state = get_time_delta(war.end_time.now, war.end_time.time)+" remaining"
	elif war.state == "warEnded":
		state = "Ended "+get_time_delta(war.end_time.time, war.end_time.now)+" ago"
	content = "\n".join([
		"**"+war.clan.name+"** vs **"+war.opponent.name+"**"+("\nCWL round "+str(war.cwl_round) if war.cwl_round is not None else ""),
		state,
		"`Stars             "+pad_left(war.clan.stars, 3)+" - "+pad_right(war.opponent.stars, 3)+spaces(4)+"`",
		"`Destruction   "+pad_left(round_fixed(war.clan.destruction, 2)+"%", 7)+" - "+pad_right(round_fixed(war.opponent.destruction, 2)+"%", 7)+"`",
		"`Attacks Used      "+pad_left(war.clan.attacks_used, 3)+" - "+pad_right(war.opponent.attacks_used, 3)+spaces(4)+"`",
		"`Attacks Remaining "+pad_left(max_attacks*war.team_size-war.clan.attacks_used, 3)+" - "+pad_right(max_attacks*war.team_size-war.opponent.attacks_used, 3)+spaces(4)+"`"
	])

	lines = []
	for attack in war.attacks:
		if attack.attacker.clan == war.clan: (clan_member, enemy_member) = (attack.attacker, attack.defender)
		else: (clan_member, enemy_member) = (attack.defender, attack.attacker)
		
		clan_name = "`"+pad_left(clan_member.name, 15)+"` " if show_names else ""
		clan = str(emojis.th[clan_member.town_hall])+" ` "+pad_left(clan_member.map_position, 2)+" `"
		if attack.attacker == clan_member:
			score = " ➡ "+stars(attack.stars)+" `"+pad_left(str(attack.destruction)+"%", 4)+"` "
		else:
			score = " `"+pad_left(str(attack.destruction)+"%", 4)+"` "+stars(attack.stars)+" ⬅ "
		enemy = "` "+pad_left(enemy_member.map_position, 2)+" ` "+str(emojis.th[enemy_member.town_hall])
		enemy_name = " `"+pad_right(enemy_member.name, 15)+"`" if show_names else ""
		lines.append(clan_name+clan+score+enemy+enemy_name)

	embeds = generate_embeds(lines, embed)
	await resp.send(content, embeds)



@war_standard.command(
	name = "map",
	description = "Displays a clan's current war status.",
	brief = "Displays the current war for the given clan.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def map_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	if len(args) != 1:
		return await resp.send_help()
	async with resp:
		await map(resp, args[0], False, None, None)

@war_standard.command(
	name = "attacks",
	description = "Displays a clan's current war attacks.",
	brief = "Displays the attacks in the given clan's current war.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def attacks_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	if len(args) != 1:
		return await resp.send_help()
	async with resp:
		await attacks(resp, args[0], False, None, None)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(war_standard)
	bot.add_slash_subcommand(map_slash,
		base="war",
		base_description="Various commands to view clan war information.",
		name="map",
		description="Displays the current war map for the given clan.",
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"example": "#8PQGQC8",
			"required": True
		},
		{
			"type": 3,
			"name": "size",
			"description": "The amount of data to be shown. `full` will probably display incorrectly on a phone.",
			"example": "full",
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
		},
		{
			"type": 3,
			"name": "num-attacks",
			"description": "[Friendly Wars Only] The number of attacks players are able to make.",
			"example": "1",
			"required": False,
			"choices": [
				{
					"name": "1",
					"value": "1"
				},
				{
					"name": "2",
					"value": "2"
				}
			]
		},
		{
			"type": 4,
			"name": "cwl-round",
			"description": "[CWL Only] A specific CWL round (must have already started prep). Fetches current day if omitted.",
			"example": "6",
			"required": False
		}]
	)

	bot.add_slash_subcommand(attacks_slash,
		base="war",
		base_description="Various commands to view clan war information.",
		name="attacks",
		description="Displays the attacks in the given clan's current war.",
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"example": "#8PQGQC8",
			"required": True
		},
		{
			"type": 3,
			"name": "size",
			"description": "The amount of data to be shown. `full` will probably display incorrectly on a phone.",
			"example": "full",
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
		},
		{
			"type": 3,
			"name": "num-attacks",
			"description": "[Friendly Wars Only] The number of attacks players are able to make.",
			"example": "1",
			"required": False,
			"choices": [
				{
					"name": "1",
					"value": "1"
				},
				{
					"name": "2",
					"value": "2"
				}
			]
		},
		{
			"type": 4,
			"name": "cwl-round",
			"description": "[CWL Only] A specific CWL round (must have already started prep). Fetches current day if omitted.",
			"example": "6",
			"required": False
		}]
	)

async def map_slash(ctx: SlashContext, tag, size="compact", num_attacks=None, cwl_round=None):
	(size, num_attacks, cwl_round) = fix_params(size, num_attacks, cwl_round)
	resp = SlashResponder(ctx)
	if num_attacks is not None and cwl_round is not None:
		await resp.send("You cannot use `num-attacks` and `cwl-round` together.")
		return
	async with resp:
		await map(resp, tag, size == "full", num_attacks, cwl_round)

async def attacks_slash(ctx: SlashContext, tag, size="compact", num_attacks=None, cwl_round=None):
	(size, num_attacks, cwl_round) = fix_params(size, num_attacks, cwl_round)
	resp = SlashResponder(ctx)
	if num_attacks is not None and cwl_round is not None:
		await resp.send("You cannot use `num-attacks` and `cwl-round` together.")
		return
	async with resp:
		await attacks(resp, tag, size == "full", num_attacks, cwl_round)

def fix_params(size, num_attacks, cwl_round):
	if isinstance(num_attacks, int):
		#tag, size, cwl_round
		cwl_round = num_attacks
		num_attacks = None
	if size != "compact" and size != "full":
		if isinstance(size, str):
			#tag, num_attacks
			num_attacks = size
			size = "compact"
		elif isinstance(size, int):
			#tag, cwl_round
			cwl_round = size
			size = "compact"
	return (size, num_attacks, cwl_round)