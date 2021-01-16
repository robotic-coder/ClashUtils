import discord
import discord.ext.commands
import coc
import commands.utils.emojis as emojis
from commands.utils.helpers import *
from commands.utils.responder import *
from commands.cwl.performance.utils import *

async def net(resp: Responder, tag: str, show_details: bool):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")

	def sort(m: Member):
		return (
			m.star_score,
			m.destruction_score,
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
		lines.append("`   | STARS       | DESTRUCTION    | COUNT        |                    `")
		lines.append("` # | Atk Def A-D | Atk  Def  A-D  | Atk Def Rnds | Member             `")
		lines.append("`---|-------------|----------------|--------------|--------------------`")
		for (index, member) in enumerate(members):
			rank = pad_left(index+1, 2)
			attack_stars = pad_left(member.attack_stars, 3)
			defence_stars = pad_left(member.defence_stars, 3)
			star_score = pad_left(member.star_score, 3)
			attack_destruction = pad_left(member.attack_destruction, 3)
			defence_destruction = pad_left(member.defence_destruction, 3)
			destruction_score = pad_left(member.destruction_score, 4)
			num_attacks = str(member.num_attacks)
			num_defenses = pad_left(member.num_defenses, 3)
			num_rounds = str(member.num_rounds)
			th = str(emojis.th[member.town_hall_level])

			if member.num_attacks < member.num_rounds:
				marker = "*"
			else: marker = " "
			lines.append("\u2066`"+rank+" | "+attack_stars+" "+defence_stars+" "+star_score+" | "+attack_destruction+"  "+defence_destruction+"  "+destruction_score+" |  "+marker+num_attacks+" "+num_defenses+"    "+num_rounds+" | `"+th+" `"+member.name+"`")
	else:
		lines.append("`   Net   Net                  `")
		lines.append("` # Stars Dest  Member         `")
		lines.append("`------------------------------`")
		for (index, member) in enumerate(members):
			rank = pad_left(index+1, 2)
			star_score = pad_left(member.star_score, 4)
			destruction_score = pad_left(member.destruction_score, 4)

			if member.num_attacks < member.num_rounds:
				marker = "*"
			else: marker = " "
			lines.append("\u2066`"+rank+" "+star_score+"  "+destruction_score+" "+marker+member.name+"`")
	
	embed = discord.Embed(title=stats["clan_name"]+": CWL Net Gain after "+str(stats["num_rounds"])+" rounds")
	embed.set_footer(text=tag)
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)






@discord.ext.commands.command(
	name="net",
	description = "Displays CWL performance stats in terms of net benefit (attacks - defenses).",
	brief = "Displays CWL performance stats in terms of net benefit (attacks - defenses).",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def net_standard(ctx: discord.ext.commands.Context, *args):
	if len(args) < 1 or len(args) > 2:
		await send_command_help(ctx, net_standard)
		return
	resp = StandardResponder(ctx)
	async with resp:
		await net(resp, args[0], len(args)==2 and args[1]=="full")

def setup(bot: discord.ext.commands.Bot, group: discord.ext.commands.Group):
	group.add_command(net_standard)

	bot.slash.add_subcommand(net_slash, 
		base=bot.slash_command_prefix+"cwl",
		base_description="Various commands to view CWL data",
		subcommand_group="performance",
		subcommand_group_description="Displays member CWL performance stats",
		name="net",
		description="Displays CWL performance stats in terms of net benefit (attacks - defenses)",
		guild_ids=bot.command_guild_ids,
		options=get_options()
	)

async def net_slash(ctx, clan, size="compact"):
	resp = SlashResponder(ctx)
	async with resp:
		await net(resp, clan, size=="full")