import discord
import discord.ext.commands
import coc
from commands.utils.helpers import *
import commands.utils.emojis as emojis
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

async def maxscore(resp: Responder, tag: str):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")

	war = await find_current_war(tag, resp.clash)
	if war.state == "notInWar":
		clan = await resp.clash.get_clan(tag)
		await resp.send(clan.name+" ("+tag+") is not in war.")

	await resp.send(embeds=[make_embed(war, "clan", "opponent"), make_embed(war, "opponent", "clan")])

def make_embed(war, friendly_name, enemy_name):
	friendly_side: coc.WarClan = getattr(war, friendly_name)
	enemy_side: coc.WarClan = getattr(war, enemy_name)
	
	making_embed_for_home_clan = friendly_name == "clan"

	embed = discord.Embed()
	embed.set_author(name=friendly_side.name, url=friendly_side.share_link, icon_url=friendly_side.badge.small)
	embed.set_footer(text=friendly_side.tag)
	enemy_bases = sorted(enemy_side.members, key=sort_bases)
	if war.type == "cwl": max_attacks = 1
	else: max_attacks = 2

	attacks_remaining = []
	for i in range(13+1):
		attacks_remaining.append(0)
	for member in friendly_side.members:
		attacks_remaining[member.town_hall] += max_attacks-len(member.attacks)

	remaining_list = ""
	for i in reversed(range(2, 13+1)):
		if attacks_remaining[i] > 0:
			remaining_list += str(emojis.th[i])+"`"+str(attacks_remaining[i])+" `"
	if remaining_list == "": remaining_list = "none"

	extra_stars = 0
	extra_destruction = 0
	viable_bases = ""
	for i in range(min(25, war.team_size, war.team_size*max_attacks-friendly_side.attacks_used)):
		base = enemy_bases[i]
		if base.best_opponent_attack is not None:
			current_stars = base.best_opponent_attack.stars
			current_destruction = base.best_opponent_attack.destruction
		else:
			current_stars = 0
			current_destruction = 0
		if current_stars == 3: continue
		extra_stars += 3-current_stars
		extra_destruction += (100-current_destruction)/war.team_size
		if making_embed_for_home_clan:
			viable_bases += "`"+pad_left(base.map_position, 2)+"` "+str(emojis.th[base.town_hall])+" "+stars(current_stars)+" `"+pad_left(current_destruction, 3)+"%`\n"
		else:
			viable_bases += "`"+pad_left(current_destruction, 3)+"%` "+stars(current_stars)+" "+str(emojis.th[base.town_hall])+" `"+pad_left(base.map_position, 2)+"`\n"
	
	if extra_stars > 0:
		stars_line = "Stars: "+str(friendly_side.stars)+" + "+str(extra_stars)+" = "+str(friendly_side.stars+extra_stars)
		destruction_line = "Destruction: "+round_fixed(friendly_side.destruction, 2)+" + "+round_fixed(extra_destruction, 2)+" = "+round_fixed(friendly_side.destruction+extra_destruction, 2)
		embed.add_field(name="Attacks Remaining", value=remaining_list, inline=False)
		embed.add_field(name="Maximum Possible Score", value=stars_line+"\n"+destruction_line, inline=False)
		embed.add_field(name="To get the maximum score, this clan must 3-star the bases below:", value=viable_bases, inline=False)
	else:
		embed.description = "Stars: "+str(friendly_side.stars)+"\nDestruction: "+round_fixed(friendly_side.destruction, 2)
		if friendly_side.stars == war.team_size*3:
			embed.title = "Perfect War!"
		else:
			embed.title = "No Attacks Remaining"

	return embed

def sort_bases(base):
	if base.best_opponent_attack is not None:
		stars = base.best_opponent_attack.stars
		destruction = base.best_opponent_attack.destruction
	else:
		stars = 0
		destruction = 0
	return (stars, destruction, base.map_position*-1)








@discord.ext.commands.command(
	name = "maxscore",
	description = "Calculates the maximum possible scores in a clan's current war.",
	brief = "Calculates the maximum possible scores in a clan's current war.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def maxscore_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) != 1:
		await send_command_help(ctx, maxscore)
		return
	resp = StandardResponder(ctx)
	async with resp:
		await maxscore(resp, args[0])

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
		}]
	)

async def maxscore_slash(ctx: SlashContext, tag):
	resp = SlashResponder(ctx)
	async with resp:
		await maxscore(resp, tag)