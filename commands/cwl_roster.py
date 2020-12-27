import discord
import discord.ext.commands
import coc
import commands.utils.helpers as helpers
import commands.utils.emojis as emojis

hero_names = [ "Barbarian King", "Archer Queen", "Grand Warden", "Royal Champion" ]

@discord.ext.commands.command(
	description = "Displays a clan's CWL roster.",
	brief = "Displays the CWL roster for the given clan.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def roster(ctx: discord.ext.commands.Context, *args):
	if len(args) < 1 or len(args) > 2:
		await helpers.send_command_help(ctx, roster)
		return

	tag = helpers.resolve_clan(args[0], ctx)
	clash = ctx.bot.clash
	
	if tag is None:
		await helpers.send_command_help(ctx, roster)
		return

	try:
		async with ctx.channel.typing():
			league_group = await clash.get_league_group(tag)
			size = (await clash.get_league_war(league_group.rounds[0][0])).team_size
			clan = next(x for x in league_group.clans if x.tag == tag)
			player_tags = []
			for player in clan.members:
				player_tags.append(player.tag)
			participants = []
			async for player in clash.get_players(player_tags):
				participants.append(summarise_player(player))
			
			participants = sorted(participants, key=sort_participants, reverse=True)
			if len(args) == 1:	
				lines = create_output(clan, participants, size, False)
			elif len(args) == 2 and args[1] == "links":
				lines = create_output(clan, participants, size, True)
			else:
				await ctx.channel.send("format: `//roster #CLANTAG`")
				return
			embed = discord.Embed(title="CWL Roster for "+clan.name)
			embed.set_footer(text=tag)
			await helpers.send_lines_in_embed(ctx.channel, lines, embed)

	except coc.errors.NotFound:
		clan = await clash.get_clan(tag)
		await ctx.channel.send(clan.name+" ("+tag+") is not currently in a Clan War League")
	

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
			output[hero_name] = ""
	return output

def create_output(clan: coc.Clan, participants: list, size: int, links: bool):
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
		
		line_content = str(emojis.th[player["th"]])+"`"+generate_hero_levels(player)+"  "+helpers.pad_left(player["heroes"], 3)+"/"+helpers.pad_right(player["max_heroes"], 3)+"`"
		if links:
			line_content = "\u2066"+line_content+" ["+player["name"]+"](https://link.clashofclans.com/en?action=OpenPlayerProfile&tag="+player["tag"][1:]+")"
		lines.append(line_content)

		if len(lines) == size+4:
			lines.append("`----- estimated top "+str(size)+" -----`")

	for level, count in th_levels.items():
		lines[0] += str(emojis.th[level])+"`"+str(count)+" `"

	return lines

def generate_hero_levels(player):
	output = ""
	for hero_name in hero_names:
		output += " "+helpers.pad_left(player[hero_name], 3)
	return output
#def check_max_hero_levels(member: coc.Player):
	#if member.town_hall

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(roster)