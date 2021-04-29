import discord
import discord.ext.commands
import coc
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

max_th_level = 14

async def maxscore(resp: Responder, tag: str, reach: str, num_attacks: int):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")

	war = await resp.clash.get_current_war(tag, allow_prep=True)
	if war.state == "notInWar":
		clan = await resp.clash.get_clan(tag)
		await resp.send(clan.name+" ("+tag+") is not in war.")
	if war.type != "friendly" and num_attacks is not None:
		clan = await resp.clash.get_clan(tag)
		return await resp.send(clan.name+" ("+tag+") is not in a friendly war.")

	clan_embed = make_embed(war, "clan", "opponent", reach, num_attacks)
	enemy_embed = make_embed(war, "opponent", "clan", reach, num_attacks)
	if clan_embed is None or enemy_embed is None:
		return await resp.send("This clan's war allows members to make 2 attacks.")
	await resp.send(embeds=[clan_embed, enemy_embed])

def make_embed(war: coc.ClanWar, friendly_name: str, enemy_name: str, reach: str, max_attacks: int):
	
	friendly_side: coc.WarClan = getattr(war, friendly_name)
	enemy_side: coc.WarClan = getattr(war, enemy_name)
	
	embed = discord.Embed()
	embed.set_author(name=friendly_side.name, url=friendly_side.share_link, icon_url=friendly_side.badge.small)
	embed.set_footer(text=friendly_side.tag)

	for (index, base) in enumerate(sorted(enemy_side.members, key=lambda x: x.map_position)):
		# Unsure of why this first sort is needed, but it is necessary for correct output.
		# The enemy side list seems to be scrambled when making the 2nd embed. The friendly side list is not sorted while making the first embed so it is unclear why this happens.
		base.map_position = index+1
	enemy_bases = sorted(enemy_side.members, key=sort_bases)
	if max_attacks is None: max_attacks = 2
	if war.type == "cwl": max_attacks = 1
	
	no_attacks = friendly_side.attacks_used == war.team_size*max_attacks
	perfect_war = friendly_side.stars == war.team_size*3
	if no_attacks or perfect_war:
		embed.description = "Stars: "+str(friendly_side.stars)+"\nDestruction: "+round_fixed(friendly_side.destruction, 2)
		embed.title = "Perfect War!" if perfect_war else "No Attacks Remaining"
		return embed

	attacks_remaining = []
	for i in range(max_th_level+1):
		attacks_remaining.append({
			"viable": reach == "unlimited",
			"original_count": 0,
			"running_count": 0
		})
	for member in friendly_side.members:
		if len(member.attacks) > max_attacks:
			return None
		attacks_remaining[member.town_hall]["original_count"] += max_attacks-len(member.attacks)
		attacks_remaining[member.town_hall]["running_count"] += max_attacks-len(member.attacks)

	extra_stars = 0
	extra_destruction = 0
	viable_bases = ""
	num_viable = 0
	for i in range(min(war.team_size, war.team_size*max_attacks-friendly_side.attacks_used)):
		base = enemy_bases[i]
		if base.best_opponent_attack is not None:
			current_stars = base.best_opponent_attack.stars
			current_destruction = base.best_opponent_attack.destruction
		else:
			current_stars = 0
			current_destruction = 0
		if current_stars == 3: continue
		if can_be_attacked(base, attacks_remaining, reach) == False: continue
		
		extra_stars += 3-current_stars
		extra_destruction += (100-current_destruction)/war.team_size
		if num_viable < 25:
			if friendly_name == "clan":
				viable_bases += "`"+pad_left(base.map_position, 2)+"` "+str(emojis.th[base.town_hall])+" "+stars(current_stars)+" `"+pad_left(current_destruction, 3)+"%`\n"
			else:
				viable_bases += "`"+pad_left(current_destruction, 3)+"%` "+stars(current_stars)+" "+str(emojis.th[base.town_hall])+" `"+pad_left(base.map_position, 2)+"`\n"
		num_viable += 1
	
	remaining_list = ""
	ignored_list = ""
	found_viable = False
	for i in range(2, max_th_level+1):
		if attacks_remaining[i]["original_count"] > 0:
			addition = str(emojis.th[i])+"`"+str(attacks_remaining[i]["original_count"])+" `"
			if attacks_remaining[i]["viable"] or found_viable:
				remaining_list = addition+remaining_list
				found_viable = True
			else:
				ignored_list = addition+ignored_list
	if remaining_list == "": remaining_list = "none"
	if ignored_list == "": ignored_list = "none"

	if extra_stars > 0:
		if reach == "unlimited" or ignored_list == "none":
			embed.add_field(name="Attacks Remaining", value=remaining_list, inline=False)
		else:
			embed.add_field(name="Viable Attacks Remaining", value=remaining_list, inline=False)
			embed.add_field(name="Unviable Attacks Remaining", value=ignored_list, inline=False)
		
		stars_line = "Stars: "+str(friendly_side.stars)+" + "+str(extra_stars)+" = "+str(friendly_side.stars+extra_stars)
		destruction_line = "Destruction: "+round_fixed(friendly_side.destruction, 2)+" + "+round_fixed(extra_destruction, 2)+" = "+round_fixed(friendly_side.destruction+extra_destruction, 2)
		embed.add_field(name="Maximum Possible Score", value=stars_line+"\n"+destruction_line, inline=False)
		embed.add_field(name="To get the maximum score, this clan must 3-star the bases below:", value=viable_bases, inline=False)
	else:
		embed.title = "No Attacks Remaining" if ignored_list == "none" else "No Viable Attacks Remaining"
		embed.description = "Stars: "+str(friendly_side.stars)+"\nDestruction: "+round_fixed(friendly_side.destruction, 2)
		if ignored_list != "none":
			embed.add_field(name="Unviable Attacks Remaining", value=ignored_list, inline=False)

	return embed

def sort_bases(base):
	if base.best_opponent_attack is not None:
		stars = base.best_opponent_attack.stars
		destruction = base.best_opponent_attack.destruction
	else:
		stars = 0
		destruction = 0
	return (stars, destruction, base.map_position*-1)

def can_be_attacked(base: coc.ClanWarMember, attacks_remaining: dict, reach: str):
	if reach == "unlimited": return True
	min_attacker_th = base.town_hall if reach == "none" else base.town_hall-1
	for i in range(min_attacker_th, max_th_level+1):
		if attacks_remaining[i]["running_count"] > 0:
			attacks_remaining[i]["running_count"] -= 1
			attacks_remaining[i]["viable"] = True
			return True
	return False






@discord.ext.commands.command(
	name = "maxscore",
	description = "Calculates the maximum possible scores in a clan's current war.",
	brief = "Calculates the maximum possible scores in a clan's current war.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def maxscore_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	if len(args) != 1:
		return await resp.send_help()
	async with resp:
		await maxscore(resp, args[0], "1 level", None)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(maxscore_standard)
	bot.add_slash_command(maxscore_slash, 
		name="maxscore",
		description="Calculates the maximum possible scores in a clan's current war",
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"example": "#8PQGQC8",
			"required": True
		},
		{
			"type": 3,
			"name": "reach",
			"description": "How many TH levels higher you expect members to be able to 3 star. Defaults to 1 level if omitted.",
			"example": "none",
			"required": False,
			"choices": [
				{
					"name": "none",
					"value": "none"
				},
				{
					"name": "1 level",
					"value": "1 level"
				},
				{
					"name": "unlimited",
					"value": "unlimited"
				}
			]
		},
		{
			"type": 4,
			"name": "num-attacks",
			"description": "[Friendly Wars Only] The number of attacks players are able to make.",
			"example": "1",
			"required": False,
			"choices": [
				{
					"name": 1,
					"value": 1
				},
				{
					"name": 2,
					"value": 2
				}
			]
		}]
	)

async def maxscore_slash(ctx: SlashContext, tag, reach="1 level", num_attacks=None):
	if isinstance(reach, int):
		num_attacks=reach
		reach="1 level"

	resp = SlashResponder(ctx)
	async with resp:
		await maxscore(resp, tag, reach, num_attacks)