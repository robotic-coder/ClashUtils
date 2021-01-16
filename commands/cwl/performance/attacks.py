import discord
import discord.ext.commands
import coc
import commands.utils.emojis as emojis
from commands.utils.helpers import *
from commands.utils.responder import *
from commands.cwl.performance.utils import *

async def attacks(resp: Responder, tag: str, show_details: bool):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")

	def sort(m: Member):
		return (
			m.avg_attack_stars,
			m.avg_attack_destruction,
			m.num_attacks-m.num_rounds,
			m.town_hall_level
		)
	stats = await get_stats(tag, resp.clash)
	if stats is None:
		clan = await resp.clash.get_clan(tag)
		return await resp.send(clan.name+" ("+tag+") is not currently in a Clan War League")
		
	members = sorted(stats["members"], key=sort, reverse=True)

	lines = []
	if show_details:
		lines.append("`   | STARS      | DESTRUCTION |      |                    `")
		lines.append("` # | Tot  Avg   | Tot  Avg    | Atks | Member             `")
		lines.append("`---|------------|-------------|------|--------------------`")
		for (index, member) in enumerate(members):
			rank = pad_left(index+1, 2)
			stars = pad_left(member.attack_stars, 3)
			avg_stars = round_fixed(member.avg_attack_stars, 3)
			destruction = pad_left(member.attack_destruction, 3)
			avg_destruction = pad_left(round_fixed(member.avg_attack_destruction, 3), 7)
			num_attacks = str(member.num_attacks)
			num_rounds = str(member.num_rounds)
			th = str(emojis.th[member.town_hall_level])

			if member.num_attacks < member.num_rounds:
				marker = "*"
			else: marker = " "
			lines.append("\u2066`"+rank+" | "+stars+"  "+avg_stars+" | "+destruction+" "+avg_destruction+" | "+marker+num_attacks+"/"+num_rounds+" | `"+th+" `"+member.name+"`")
	else:
		lines.append("`   Avg    Avg                  `")
		lines.append("` # Stars  Dest  Member         `")
		lines.append("`-------------------------------`")
		for (index, member) in enumerate(members):
			rank = pad_left(index+1, 2)
			avg_stars = pad_left(round_fixed(member.avg_attack_stars, 1), 5)
			avg_destruction = pad_left(round_fixed(member.avg_attack_destruction, 1), 5)

			if member.num_attacks < member.num_rounds:
				marker = "*"
			else: marker = " "
			lines.append("\u2066`"+rank+" "+avg_stars+" "+avg_destruction+" "+marker+member.name+"`")
	
	embed = discord.Embed(title=stats["clan_name"]+": CWL Average Attacks after "+str(stats["num_rounds"])+" rounds")
	embed.set_footer(text=tag)
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)





@discord.ext.commands.command(
	name="attacks",
	description = "Displays CWL performance stats in terms of attacks.",
	brief = "Displays CWL performance stats in terms of attacks.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def attacks_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) < 1 or len(args) > 2:
		await send_command_help(ctx, attacks_standard)
		return
	resp = StandardResponder(ctx)
	async with resp:
		await attacks(resp, args[0], len(args)==2 and args[1]=="full")

def setup(bot: discord.ext.commands.Bot, group: discord.ext.commands.Group):
	group.add_command(attacks_standard)

	bot.slash.add_subcommand(attacks_slash, 
		base=bot.slash_command_prefix+"cwl",
		base_description="Various commands to view CWL data",
		subcommand_group="performance",
		subcommand_group_description="Displays member CWL performance stats",
		name="attacks",
		description="Displays CWL performance stats in terms of attacks",
		guild_ids=bot.command_guild_ids,
		options=get_options()
	)

async def attacks_slash(ctx, clan, size="compact"):
	resp = SlashResponder(ctx)
	async with resp:
		await attacks(resp, clan, size=="full")