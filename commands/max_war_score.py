import discord
import discord.ext.commands
import coc
from commands.utils.helpers import *
import commands.utils.emojis as emojis

@discord.ext.commands.command()
async def maxscore(ctx: discord.ext.commands.Context, *args):
	if len(args) != 1:
		return

	tag = resolve_clan(args[0], ctx)
	clash = ctx.bot.clash
	
	if tag is not None:
		async with ctx.channel.typing():
			war = await clash.get_current_war(tag)
			if war.state != "notInWar":
				await ctx.channel.send(embed=make_embed(war, "clan", "opponent"))
				await ctx.channel.send(embed=make_embed(war, "opponent", "clan"))

			else:
				clan = await clash.get_clan(tag)
				await ctx.channel.send(clan.name+" ("+tag+") is not in war.")
	else:
		await ctx.channel.send("format: `<@786654276185096203> roster #CLANTAG`")

def make_embed(war, friendly_name, enemy_name):
	friendly_side: coc.WarClan = getattr(war, friendly_name)
	enemy_side: coc.WarClan = getattr(war, enemy_name)

	embed = discord.Embed(title=friendly_side.name)
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
	embed.add_field(name="Attacks Remaining", value=remaining_list, inline=False)

	extra_stars = 0
	extra_destruction = 0
	viable_bases = ""
	for i in range(min(25, war.team_size, war.team_size*max_attacks-friendly_side.attacks_used)):
		if enemy_bases[i].best_opponent_attack is not None:
			current_stars = enemy_bases[i].best_opponent_attack.stars
			current_destruction = enemy_bases[i].best_opponent_attack.destruction
		else:
			current_stars = 0
			current_destruction = 0
		if current_stars == 3: continue
		extra_stars += 3-current_stars
		extra_destruction += (100-current_destruction)/war.team_size
		viable_bases += "`"+pad_left(enemy_bases[i].map_position, 2)+"` "+str(emojis.th[enemy_bases[i].town_hall])+" "+stars(current_stars)+" `"+pad_left(current_destruction, 3)+"%`\n"
	embed.add_field(name="Best Bases To Hit", value=viable_bases, inline=False)

	stars_line = "Stars: "+str(friendly_side.stars)+" + "+str(extra_stars)+" = "+str(friendly_side.stars+extra_stars)
	destruction_line = "Destruction: "+round_fixed(friendly_side.destruction, 2)+" + "+round_fixed(extra_destruction, 2)+" = "+round_fixed(friendly_side.destruction+extra_destruction, 2)
	embed.add_field(name="Maximum Possible Score", value=stars_line+"\n"+destruction_line, inline=False)

	return embed

def sort_bases(base):
	if base.best_opponent_attack is not None:
		stars = base.best_opponent_attack.stars
		destruction = base.best_opponent_attack.destruction
	else:
		stars = 0
		destruction = 0
	return (stars, destruction, base.map_position*-1)

def setup(bot: discord.ext.commands.Bot):
	maxscore.help = "Calculates the maximum possible scores in a clan war."
	maxscore.usage = "[#CLANTAG or alias]"
	setattr(maxscore, "example", "#8PQGQC8")
	setattr(maxscore, "required_permissions", ["send_messages", "embed_links", "use_external_emojis"])
	bot.add_command(maxscore)