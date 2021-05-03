import discord
import discord.ext.commands
import coc
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

hero_names = [ "Barbarian King", "Archer Queen", "Grand Warden", "Royal Champion" ]

async def roster(resp: Responder, tag: str, show_names: bool):
	tag = resp.resolve_clan(tag)
	if tag is None: return await resp.send("Invalid clan tag or alias")

	try:
		league_group = await resp.clash.get_league_group(tag)
	except coc.errors.NotFound:
		clan = await resp.clash.get_clan(tag)
		return await resp.send(clan.name+" ("+tag+") is not currently in a Clan War League")
	
	size = (await resp.clash.get_league_war(league_group.rounds[0][0])).team_size
	clan = next(x for x in league_group.clans if x.tag == tag)
	player_tags = []
	for player in clan.members:
		player_tags.append(player.tag)
	participants = []
	async for player in resp.clash.get_players(player_tags):
		participants.append(summarise_player(player))
	
	participants = sorted(participants, key=sort_participants, reverse=True)
	lines = [
		"",
		"",
		"`TH  BK  AQ  GW  RC   Total  `",
		"`----------------------------`"
	]

	th_levels = {}
	for player in participants:
		if player["th"] in th_levels:
			th_levels[player["th"]] += 1
		else:
			th_levels[player["th"]] = 1
		
		line_content = str(emojis.th[player["th"]])+"`"+generate_hero_levels(player)+"  "+pad_left(player["heroes"], 3)+"/"+pad_right(player["max_heroes"], 3)+"`"
		if show_names:
			line_content = "\u2066"+line_content+" ["+player["name"]+"](https://link.clashofclans.com/en?action=OpenPlayerProfile&tag="+player["tag"][1:]+")"
		lines.append(line_content)

		if len(lines) == size+4:
			lines.append("`----- estimated top "+str(size)+" -----`")

	for level, count in th_levels.items():
		lines[0] += str(emojis.th[level])+"`"+str(count)+" `"
	
	embed = discord.Embed(title="CWL Roster")
	embed.set_author(name=clan.name, url=clan.share_link, icon_url=clan.badge.small)
	embed.set_footer(text=tag)
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)
	

def sort_participants(p):
	return (p["th"], p["heroes"], p["Archer Queen"], p["Royal Champion"], p["Grand Warden"], p["Barbarian King"], p["army"])

def summarise_player(player: coc.Player):
	output = {
		"tag": player.tag,
		"name": player.name,
		"th": player.town_hall,
		"army": 0,
		"heroes": 0,
		"max_heroes": 0
	}
	for troop in player.troops:
		if troop.village == "home": output["army"] += troop.level
	for spell in player.spells:
		if spell.village == "home": output["army"] += spell.level
	for hero_name in hero_names:
		hero_filtered = [hero for hero in player.heroes if hero.name == hero_name]
		if len(hero_filtered) > 0:
			output[hero_name] = hero_filtered[0].level
			output["heroes"] += hero_filtered[0].level
			output["max_heroes"] += hero_filtered[0].max_level
		else:
			output[hero_name] = 0
	return output

def generate_hero_levels(player):
	output = ""
	for hero_name in hero_names:
		if player[hero_name] > 0:
			output += " "+pad_left(player[hero_name], 3)
		else:
			output += "    "
	return output
#def check_max_hero_levels(member: coc.Player):
	#if member.town_hall





@discord.ext.commands.command(
	name = "roster",
	description = "Displays a clan's CWL roster.",
	brief = "Displays the CWL roster for the given clan.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def roster_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) < 1 or len(args) > 2:
		await send_command_help(ctx, roster_standard)
		return

	resp = StandardResponder(ctx)
	async with resp:
		await roster(resp, args[0], len(args)==2)

def setup(bot: discord.ext.commands.Bot, group: discord.ext.commands.Group):
	group.add_command(roster_standard)
	bot.add_slash_subcommand(roster_slash, 
		base="cwl",
		base_description="Various commands to view CWL data",
		name="roster",
		description="Displays the CWL roster for the given clan",
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
			"description": "The amount of data to be shown. full will probably display incorrectly on a phone.",
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
		}]
	)

async def roster_slash(ctx: SlashContext, tag, size="compact"):
	resp = SlashResponder(ctx)
	async with resp:
		await roster(resp, tag, size=="full")