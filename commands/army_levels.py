import discord
import discord.ext.commands
import coc
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext

army_levels = None

@discord.ext.commands.command(
	name = "levels",
	description = "Displays all clan members' levels for a specific army unit.",
	brief = "Displays all members' levels for a specific army unit in the given clan.",
	usage = "[#CLANTAG or alias] [unit name]",
	help = "#8PQGQC8 sneaky goblin"
)

async def levels_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) < 2:
		await send_command_help(ctx, levels_standard)
		return

	tag = resolve_clan(args[0], ctx)
	clash = ctx.bot.clash
	
	if tag is None:
		await send_command_help(ctx, levels_standard)
		return
	
	async with ctx.channel.typing():
		(embeds, content) = await levels(tag, " ".join(args[1:]), clash)
		await send_embeds_in_multiple_messages(ctx.channel, embeds, content)

async def levels(tag, name, clash):
	unit = await get_army_details(clash, name)
	if unit is None:
		return ([], "`"+name+"` isn't a valid army unit!")
	clan = await clash.get_clan(tag)
	if clan is None:
		return([], "The clan `"+tag+"` doesn't exist!")

	if clan.level < 5: level_boost = 0
	elif clan.level < 10: level_boost = 1
	else: level_boost = 2

	members = []
	async for player in clan.get_detailed_members():
		search = [u for u in getattr(player, unit.type) if u.name == unit.name or (unit.base is not None and u.name == unit.base.name and u.level >= unit.min and player.town_hall >= 11)]
		if len(search) > 0:
			members.append({
				"account": player,
				"level": search[0].level
			})
	members = sorted(members, key=lambda x: (x["level"]*-1, x["account"].name.lower()))
	lines = []
	for member in members:
		name = member["account"].name
		if member["level"]+level_boost >= unit.max and (unit.type == "troops" or unit.type == "spells"):
			name = "**"+name+"**"
		lines.append(str(emojis.th[member["account"].town_hall])+"` "+pad_left(member["level"], 2)+" `"+name)

	embed = discord.Embed()
	if unit.base is not None:
		min = "min "+str(unit.min)+", "
		embed.set_footer(text="These members are able to activate the "+unit.name+", but don't necessarily have it active.")
	else: min = ""
	embed.set_author(name=clan.name, url=clan.share_link, icon_url=clan.badge.small)
	embed.title = unit.name+" Levels ("+min+"max "+str(unit.max)+")"

	if len(lines) == 0:
		lines.append("no members have this unit unlocked \:(")
	
	embeds = generate_embeds(lines, embed)
	return (embeds, "")

class ArmyUnit:
	def __init__(self, name: str, max_level: int, min_level: int, unit_type: str):
		self.name = name
		self.max = max_level
		self.min = min_level
		self.type = unit_type
		self.base = None
	def setup_super_troop(self, base):
		self.min = base.max-self.max+1
		self.max = base.max
		self.base = base

async def get_army_details(clash: coc.Client, target_name: str):
	global army_levels
	if army_levels is None:
		await init_army_details(clash)

	if target_name.lower() == "pekka": target_name = "p.e.k.k.a"
	for unit in army_levels.values():
		if target_name.lower().startswith(unit.name.lower()):
			return unit
	return None

async def init_army_details(clash: coc.Client):
	global army_levels
	# Use http to get raw data from the API, because coc.py strips out super troops from Player objects
	player = await clash.http.get_player("#GURQUU2Y")
	army_levels = {}
	for troop in player["troops"]:
		if troop["village"] == "home":
			army_levels[troop["name"].lower()] = ArmyUnit(troop["name"], troop["maxLevel"], 1, "troops")

	for unit in army_levels.values():
		match = re.match("^Super (.*)$", unit.name)
		if match is not None and len([u for u in army_levels.values() if u.name == match.group(1)]) > 0:
			unit.setup_super_troop(army_levels[match[1].lower()])
		elif unit.name == "Sneaky Goblin":
			unit.setup_super_troop(army_levels["goblin"])
		elif unit.name == "Inferno Dragon":
			unit.setup_super_troop(army_levels["baby dragon"])
		elif unit.name == "Ice Hound":
			unit.setup_super_troop(army_levels["lava hound"])

	for hero in player["heroes"]:
		if hero["village"] == "home":
			army_levels[hero["name"].lower()] = ArmyUnit(hero["name"], hero["maxLevel"], 1, "heroes")
	
	for spell in player["spells"]:
		if spell["village"] == "home":
			army_levels[spell["name"].lower()] = ArmyUnit(spell["name"], spell["maxLevel"], 1, "spells")
	#print(army_levels)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(levels_standard)
	bot.slash.add_slash_command(levels_slash,
		name="levels",
		description="Displays all members' levels for a specific army unit in the given clan",
		guild_ids=bot.command_guild_ids,
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"required": True
		},
		{
			"type": 3,
			"name": "unit",
			"description": "The army unit to check",
			"required": True
		}]
	)

async def levels_slash(ctx: SlashContext, clan, troop):
	await ctx.send(content="Loading...\nNote: This feature is in beta, and not all `//` commands are supported yet.")

	tag = resolve_clan_slash(clan, ctx)
	clash = ctx._discord.clash
	
	if tag is None:
		#await send_command_help(ctx, currentwar_standard)
		return

	(embeds, content) = await levels(tag, troop, clash)
	await ctx.send(content=content, embeds=embeds)