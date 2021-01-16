import discord
import discord.ext.commands
import coc
import commands.utils.emojis as emojis
from commands.utils.helpers import *
from commands.utils.responder import *

@discord.ext.commands.group(
	name = "performance",
	description = "Displays member CWL performance stats.",
	brief = "Displays member CWL performance stats."
)
async def performance_standard(ctx: discord.ext.commands.Context):
	if ctx.invoked_subcommand is None:
		await send_command_list(ctx, performance_standard)
		return

async def performance(resp: Responder, tag: str, metric: str, show_details: bool):
	if metric == "net":
		await net(resp, tag, show_details)
	elif metric == "attacks":
		await attacks(resp, tag, show_details)
	elif metric == "defenses":
		await defenses(resp, tag, show_details)

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







class Member:
	def __init__(self, coc_member: coc.ClanWarMember):
		self.tag = coc_member.tag
		self.name = coc_member.name
		self.town_hall_level = coc_member.town_hall
		self.num_rounds = 0
		self.num_attacks = 0
		self.attack_stars = 0
		self.attack_destruction = 0
		self.num_defenses = 0
		self.defence_stars = 0
		self.defence_destruction = 0

	@property
	def avg_attack_stars(self): return self.attack_stars / self.num_rounds
	@property
	def avg_attack_destruction(self): return self.attack_destruction / self.num_rounds
	@property
	def avg_defence_stars(self): return self.defence_stars / self.num_rounds
	@property
	def avg_defence_destruction(self): return self.defence_destruction / self.num_rounds
	@property
	def star_score(self): return self.attack_stars - self.defence_stars
	@property
	def destruction_score(self): return self.attack_destruction - self.defence_destruction

async def get_stats(tag: str, clash: coc.Client):
	try:
		group = await clash.get_league_group(tag)
		num_rounds = 0
		members = {}
		async for war in group.get_wars_for_clan(tag):
			if war.state == "warEnded":
				num_rounds += 1
				lineup = war.clan.members
				attacks = []
				attacked_bases = {}
				for member in lineup:
					if member.tag not in members:
						members[member.tag] = Member(member)
					members[member.tag].num_rounds += 1
					if len(member.attacks) > 0:
						attacks.append(member.attacks[0])
						attacked_bases[member.attacks[0].defender_tag] = {
							"tag": member.attacks[0].defender_tag,
							"stars": 0
						}
					if member.best_opponent_attack is not None:
						members[member.tag].num_defenses += 1
						members[member.tag].defence_stars += member.best_opponent_attack.stars
						members[member.tag].defence_destruction += member.best_opponent_attack.destruction

				attacks = sorted(attacks, key=lambda x: x.order)

				for attack in attacks:
					target = attacked_bases[attack.defender_tag]
					member = members[attack.attacker_tag]
					if attack.stars > target["stars"]:
						member.attack_stars += attack.stars-target["stars"]
						target["stars"] = attack.stars
					member.attack_destruction += attack.destruction
					member.num_attacks += 1
				
		return {
			"members": members.values(),
			"clan_name": [clan.name for clan in group.clans if clan.tag == tag][0],
			"num_rounds": num_rounds
		}
	except coc.errors.NotFound:
		return None
	





@performance_standard.command(
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

@performance_standard.command(
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

@performance_standard.command(
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
	group.add_command(performance_standard)
	bot.slash.add_subcommand(performance_slash, 
		base=bot.slash_command_prefix+"cwl",
		base_description="Various commands to view CWL data",
		name="performance",
		description="Displays member CWL performance stats",
		guild_ids=bot.command_guild_ids,
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"required": True
		},
		{
			"type": 3,
			"name": "metric",
			"description": "The data used to determine CWL performance: net (attacks-defenses), avg attacks or avg defenses",
			"required": True,
			"choices": [
				{
					"name": "net",
					"value": "net"
				},
				{
					"name": "attacks",
					"value": "attacks"
				},
				{
					"name": "defenses",
					"value": "defenses"
				}
			]
		},
		{
			"type": 3,
			"name": "size",
			"description": "The amount of data to be shown. `full` will probably display incorrectly on a phone.",
			"required": False,
			"choices": [
				{
					"name": "full",
					"value": "full"
				},
				{
					"name": "compact",
					"value": "compact"
				}
			]
		}]
	)

async def performance_slash(ctx, metric, clan, size="compact"):
	resp = SlashResponder(ctx)
	async with resp:
		await performance(resp, clan, metric, size=="full")