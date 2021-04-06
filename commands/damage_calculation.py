import discord
import discord.ext.commands
import re
from math import floor, ceil
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

earthquake_damage = ( 0.145, 0.17, 0.21, 0.25, 0.29 )
lightning_damage = ( 150, 180, 210, 240, 270, 320, 400, 480, 560 )
shield_damage = ( 1260, 1460, 1660, 1860, 1960, 2060 )

async def damage(resp: Responder, building_hp: str, spell_list: str):
	spell_checker = re.match("^(((\d+)x ((earthquake([1-5]))|(lightning([1-9]))|(shield([1-6])))((, )|$))+)", spell_list)
	if spell_checker is None:
		return await resp.send_help("Invalid syntax.")
	
	spells = spell_list.split(", ")
	if len(spells) >= 14:
		return await resp.send("You can't use more than 14 spells!")
	
	result = calculate(building_hp, spells, calc_rounding_function=floor)
	if result is None:
		await resp.send("You can't use Seeking Shield more than once!")
	(damage_floor, embed_floor) = result
	(damage_float, embed_float) = calculate(building_hp, spells, display_rounding_function=round_two_places)
	(damage_ceil, embed_ceil) = calculate(building_hp, spells, calc_rounding_function=ceil)
	
	if float(damage_floor) >= float(building_hp):
		await resp.send("Total: "+str(damage_floor)+" points ✅", [embed_floor])
	elif float(damage_ceil) >= float(building_hp):
		notice = "I don't know exactly how Clash applies rounding when calculating building damage. You'll need to test this one for yourself."
		embed_ceil.title = "Best Case Scenario (Rounding Up): "+str(damage_ceil)+" points ✅"
		embed_float.title = "No Rounding: "+round_two_places(damage_float)+" points "+("✅" if float(damage_float) >= float(building_hp) else "❌")
		embed_floor.title = "Worst Case Scenario (Rounding Down): "+str(damage_floor)+" points ❌"
		await resp.send(notice, [embed_ceil, embed_float, embed_floor])
	else:
		await resp.send("Total: "+str(damage_floor)+" points ❌", [embed_floor])

def calculate(building_hp, spell_list, calc_rounding_function=lambda x: x, display_rounding_function=str):
	total_damage = 0
	total_damage = 0
	earthquake_count = 0
	shield_count = 0
	last_earthquake_level = None

	embed = discord.Embed(title="Damage Breakdown")
	embed.set_footer(text="Target building HP: "+str(building_hp)+" points")

	for spell in spell_list:
		spell_params = re.match("^(\d+)x ([A-Za-z]*)(\d+)$", spell)
		quantity = int(spell_params.group(1))
		name = spell_params.group(2)
		level = int(spell_params.group(3))

		for _i in range(quantity):
			if name == "lightning":
				total_damage += lightning_damage[level-1]
				damage = str(lightning_damage[level-1])+" points"
				embed.add_field(name=str(emojis.spells["lightning"])+" Lightning Spell level "+str(level), value=damage, inline=False)

			elif name == "earthquake":
				percent = earthquake_damage[level-1]
				divisor = (2*earthquake_count)+1
				effect = calc_rounding_function(float(building_hp) * (percent / float(divisor)))
				total_damage += effect
				earthquake_count += 1

				damage = str(building_hp)+" x "+round_fixed(percent*100, 1)+"% ÷ "+str(divisor)+" = "+display_rounding_function(effect)+" points"
				embed.add_field(name=str(emojis.spells["earthquake"])+" Earthquake Spell level "+str(level), value=damage, inline=False)

				if earthquake_count == 1:
					last_earthquake_level = level
				elif last_earthquake_level != level:
					embed.description = "To maximise damage when using different levels of Earthquake Spells, use them in order of highest to lowest level."
			
			elif name == "shield":
				total_damage += shield_damage[level-1]
				shield_count += 1

				if shield_count == 1:
					damage = str(shield_damage[level-1])+" points"
					embed.add_field(name=str(emojis.heroes["champion"])+" Seeking Shield level "+str(level), value=damage, inline=False)
				else:
					return None

	return (total_damage, embed)

def round_two_places(x: float):
	return round_fixed(x, 2)

@discord.ext.commands.command(
	name = "damage",
	description = "Calculates damage from Lightning/Earthquake spells and the Royal Champion's Seeking Shield ability.",
	brief = "Calculates damage from Lightning/Earthquake spells and the Royal Champion's Seeking Shield ability.",
	usage = "[building hp] [qty]x [item][level], [qty]x [item][level]...",
	help = "4800 6x lightning8, 1x earthquake5, 1x shield5, 1x lightning9"
)
async def damage_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	if len(args) < 3:
		return await resp.send_help()
	await damage(resp, args[0], " ".join(args[1:]))

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(damage_standard)
	bot.add_slash_command(damage_slash,
		name="damage",
		description="Calculates damage from Lightning/Earthquake Spells and the Royal Champion's Seeking Shield",
		options=[{
			"type": 4,
			"name": "building-hp",
			"description": "The hitpoints of the target building",
			"example": "4800",
			"required": True
		},
		{
			"type": 3,
			"name": "items",
			"description": "Each item must be in the format [qty]x [item][level] and separated by a comma and space.",
			"example": "6x lightning8, 1x earthquake5, 1x shield5, 1x lightning9",
			"required": True
		}]
	)

async def damage_slash(ctx: SlashContext, building_hp, spells):
	resp = SlashResponder(ctx)
	await damage(resp, building_hp, spells)
	await resp.send_command({
		"building-hp": str(building_hp),
		"items": spells
	})
