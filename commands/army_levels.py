import discord
import discord.ext.commands
import coc
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

army_levels = None

async def levels(resp, tag, name):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")
	
	unit = await get_army_details(resp.clash, name)
	if unit is None:
		return await resp.send("`"+name+"` isn't a valid army unit!")
	clan = await resp.clash.get_clan(tag)
	if clan is None:
		return await resp.send("The clan `"+tag+"` doesn't exist!")

	if clan.level < 5: level_boost = 0
	elif clan.level < 10: level_boost = 1
	else: level_boost = 2

	members = []
	async for player in clan.get_detailed_members():
		if unit.base is not None:
			# super troop
			base = [u for u in getattr(player, unit.type) if u.name == unit.base.name]
			if len(base) > 0:
				search = [u for u in getattr(player, unit.type) if u.name == unit.name and base[0].level >= unit.min and player.town_hall >= 11]
				if len(search) > 0:
					members.append({
						"account": player,
						"level": base[0].level,
						"enabled": 1 if search[0].is_active else 0
					})
		else:
			# other
			search = [u for u in getattr(player, unit.type) if u.name == unit.name]
			if len(search) > 0:
				members.append({
					"account": player,
					"level": search[0].level,
					"enabled": 1
				})
	members = sorted(members, key=lambda x: (x["enabled"]*-1, x["level"]*-1, x["account"].name.lower()))
	lines = []
	#pretend that super troop labels were already sent if unit is not a super troop
	sent_active_label = unit.base is None
	sent_inactive_label = unit.base is None
	for member in members:
		if not sent_active_label and member["enabled"] == 1:
			lines.append("**Active**")
			sent_active_label = True
		elif not sent_inactive_label and member["enabled"] == 0:
			lines.append("**Inactive**")
			sent_inactive_label = True
			
		name = member["account"].name
		if member["level"]+level_boost >= unit.max and unit.donatable:
			name = "**"+name+"**"
		lines.append(str(emojis.th[member["account"].town_hall])+"` "+pad_left(member["level"], 2)+" `"+name)

	embed = discord.Embed()
	if unit.base is not None:
		min = "min "+str(unit.min)+", "
	else: min = ""
	embed.set_author(name=clan.name, url=clan.share_link, icon_url=clan.badge.small)
	embed.set_footer(text=tag)
	embed.title = unit.name+" Levels ("+min+"max "+str(unit.max)+")"

	if len(lines) == 0:
		lines.append("no members have this unit unlocked \:(")
	
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)

class ArmyUnit:
	def __init__(self, name: str, max_level: int, min_level: int, unit_type: str, donatable: bool):
		self.name = name
		self.max = max_level
		self.min = min_level
		self.type = unit_type
		self.donatable = donatable
		self.base = None
	def setup_super_troop(self, base):
		self.min = base.max-self.max+1
		self.max = base.max
		self.base = base

async def get_army_details(clash: coc.Client, target_name: str):
	target_name = target_name.lower()
	global army_levels
	if army_levels is None:
		await init_army_details(clash)

	translations = {
		"pekka": "p.e.k.k.a",
		"lassi": "l.a.s.s.i",
	}

	if target_name in translations.keys(): target_name = translations[target_name]
	for unit in army_levels.values():
		if target_name.lower() == unit.name.lower():
			return unit
	return None

async def init_army_details(clash: coc.Client):
	global army_levels
	player = await clash.get_player("#28QQU9CU")
	army_levels = {}
	for troop in player.troops:
		if troop.is_home_base:
			army_levels[troop.name.lower()] = ArmyUnit(troop.name, troop.max_level, 1, "troops", True)
	
	for unit in army_levels.values():
		match = re.match("^Super (.*)$", unit.name)
		if match is not None:
			unit.setup_super_troop(army_levels[match.group(1).lower()])
		elif unit.name == "Sneaky Goblin":
			unit.setup_super_troop(army_levels["goblin"])
		elif unit.name == "Inferno Dragon":
			unit.setup_super_troop(army_levels["baby dragon"])
		elif unit.name == "Ice Hound":
			unit.setup_super_troop(army_levels["lava hound"])
	
	for spell in player.spells:
		if spell.is_home_base:
			army_levels[spell.name.lower()] = ArmyUnit(spell.name, spell.max_level, 1, "spells", True)

	for hero in player.heroes:
		if hero.is_home_base:
			army_levels[hero.name.lower()] = ArmyUnit(hero.name, hero.max_level, 1, "heroes", False)

	#already included in troops
	#for siege in player.siege_machines:
	#	if siege.is_home_base:
	#		army_levels[siege.name.lower()] = ArmyUnit(siege.name, siege.max_level, 1, "siege_machines", True)

	#already included in troops
	#for pet in player.hero_pets:
	#	if pet.is_home_base:
	#		army_levels[pet.name.lower()] = ArmyUnit(pet.name, pet.max_level, 1, "hero_pets", False)






@discord.ext.commands.command(
	name = "levels",
	description = "Displays all clan members' levels for a specific army unit.",
	brief = "Displays all members' levels for a specific army unit in the given clan.",
	usage = "[#CLANTAG or alias] [unit name]",
	help = "#8PQGQC8 sneaky goblin"
)
async def levels_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	if len(args) < 2:
		return await resp.send_help()
	async with resp:
		await levels(resp, args[0], " ".join(args[1:]))

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(levels_standard)
	bot.add_slash_command(levels_slash,
		name="levels",
		description="Displays all members' levels for a specific army unit in the given clan",
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"example": "#8PQGQC8",
			"required": True
		},
		{
			"type": 3,
			"name": "unit",
			"description": "The army unit to check",
			"example": "sneaky goblin",
			"required": True
		}]
	)

async def levels_slash(ctx: SlashContext, clan, troop):
	resp = SlashResponder(ctx)
	async with resp:
		await levels(resp, clan, troop)