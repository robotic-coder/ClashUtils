import discord
import discord.ext.commands
import coc
import commands.utils.emojis as emojis
from commands.utils.helpers import *
from commands.utils.responder import *
from commands.cwl.performance.utils import *

async def defenses(resp: Responder, tag: str, show_details: bool):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")

	def sort(m: Member):
		return (
			m.avg_defence_stars*-1,
			m.avg_defence_destruction*-1,
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
		lines.append("` # | Tot  Avg   | Tot  Avg    | Defs | Member             `")
		lines.append("`---|------------|-------------|------|--------------------`")
		for (index, member) in enumerate(members):
			rank = pad_left(index+1, 2)
			stars = pad_left(member.defence_stars, 3)
			avg_stars = round_fixed(member.avg_defence_stars, 3)
			destruction = pad_left(member.defence_destruction, 3)
			avg_destruction = pad_left(round_fixed(member.avg_defence_destruction, 3), 7)
			num_defenses = str(member.num_defenses)
			num_rounds = str(member.num_rounds)
			th = str(emojis.th[member.town_hall_level])
			lines.append("\u2066`"+rank+" | "+stars+"  "+avg_stars+" | "+destruction+" "+avg_destruction+" |  "+num_defenses+"/"+num_rounds+" | `"+th+" `"+member.name+"`")
	else:
		lines.append("`   Avg    Avg                  `")
		lines.append("` # Stars  Dest  Member         `")
		lines.append("`-------------------------------`")
		for (index, member) in enumerate(members):
			rank = pad_left(index+1, 2)
			avg_stars = pad_left(round_fixed(member.avg_defence_stars, 1), 5)
			avg_destruction = pad_left(round_fixed(member.avg_defence_destruction, 1), 5)
			lines.append("\u2066`"+rank+" "+avg_stars+" "+avg_destruction+"  "+member.name+"`")
	
	embed = discord.Embed(title=stats["clan_name"]+": CWL Average Defenses after "+str(stats["num_rounds"])+" rounds")
	embed.set_footer(text=tag)
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)

@discord.ext.commands.command(
	name="defenses",
	description = "Displays CWL performance stats in terms of defenses.",
	brief = "Displays CWL performance stats in terms of defenses.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def defenses_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) < 1 or len(args) > 2:
		await send_command_help(ctx, defenses_standard)
		return
	resp = StandardResponder(ctx)
	async with resp:
		await defenses(resp, args[0], len(args)==2 and args[1]=="full")

def setup(bot: discord.ext.commands.Bot, group: discord.ext.commands.Group):
	group.add_command(defenses_standard)

	bot.slash.add_subcommand(defenses_slash, 
		base=bot.slash_command_prefix+"cwl",
		base_description="Various commands to view CWL data",
		subcommand_group="performance",
		subcommand_group_description="Displays member CWL performance stats",
		name="defenses",
		description="Displays CWL performance stats in terms of defenses",
		guild_ids=bot.command_guild_ids,
		options=get_options()
	)

async def defenses_slash(ctx, clan, size="compact"):
	resp = SlashResponder(ctx)
	async with resp:
		await defenses(resp, clan, size=="full")