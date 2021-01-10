import discord
import discord.ext.commands
import coc
import commands.utils.emojis as emojis
from commands.utils.helpers import *

class Performance(discord.ext.commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@discord.ext.commands.group(
		description = "Displays member CWL performance stats.",
		brief = "Displays member CWL performance stats."
	)
	async def performance(self, ctx: discord.ext.commands.Context):
		if ctx.invoked_subcommand is None:
			await send_command_list(ctx, self.performance)
			return

	@performance.command(
		name="net",
		description = "Displays CWL performance stats in terms of net benefit (attacks - defenses).",
		brief = "Displays CWL performance stats in terms of net benefit (attacks - defenses).",
		usage = "[#CLANTAG or alias]",
		help = "#8PQGQC8"
	)
	async def performance_net(self, ctx: discord.ext.commands.Context, *args):
		if len(args) < 1 or len(args) > 2:
			await send_command_help(ctx, self.performance_net)
			return

		tag = resolve_clan(args[0], ctx)
		clash = ctx.bot.clash
		
		if tag is None:
			await send_command_help(ctx, self.performance_net)
			return

		async with ctx.channel.typing():
			def sort(m: self.Member):
				return (
					m.star_score,
					m.destruction_score,
					m.num_attacks-m.num_rounds,
					m.town_hall_level
				)
			stats = await self.get_stats(tag, clash)
			members = sorted(stats["members"], key=sort, reverse=True)

			lines = []
			if len(args) == 2 and args[1] == "full":
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
			await send_lines_in_embed(ctx.channel, lines, embed=embed)

	@performance.command(
		name="attacks",
		description = "Displays CWL performance stats in terms of attacks.",
		brief = "Displays CWL performance stats in terms of attacks.",
		usage = "[#CLANTAG or alias]",
		help = "#8PQGQC8"
	)
	async def performance_attacks(self, ctx: discord.ext.commands.Context, *args):
		if len(args) < 1 or len(args) > 2:
			await send_command_help(ctx, self.performance_attacks)
			return

		tag = resolve_clan(args[0], ctx)
		clash = ctx.bot.clash
		
		if tag is None:
			await send_command_help(ctx, self.performance_attacks)
			return

		async with ctx.channel.typing():
			def sort(m: self.Member):
				return (
					m.avg_attack_stars,
					m.avg_attack_destruction,
					m.num_attacks-m.num_rounds,
					m.town_hall_level
				)
			stats = await self.get_stats(tag, clash)
			members = sorted(stats["members"], key=sort, reverse=True)

			lines = []
			if len(args) == 2 and args[1] == "full":
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
			await send_lines_in_embed(ctx.channel, lines, embed=embed)

	@performance.command(
		name="defenses",
		description = "Displays CWL performance stats in terms of defenses.",
		brief = "Displays CWL performance stats in terms of defenses.",
		usage = "[#CLANTAG or alias]",
		help = "#8PQGQC8"
	)
	async def performance_defenses(self, ctx: discord.ext.commands.Context, *args):
		if len(args) < 1 or len(args) > 2:
			await send_command_help(ctx, self.performance_attacks)
			return

		tag = resolve_clan(args[0], ctx)
		clash = ctx.bot.clash
		
		if tag is None:
			await send_command_help(ctx, self.performance_attacks)
			return

		async with ctx.channel.typing():
			def sort(m: self.Member):
				return (
					m.avg_defence_stars*-1,
					m.avg_defence_destruction*-1,
					m.num_attacks-m.num_rounds,
					m.town_hall_level
				)
			stats = await self.get_stats(tag, clash)
			members = sorted(stats["members"], key=sort, reverse=True)

			lines = []
			if len(args) == 2 and args[1] == "full":
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
			await send_lines_in_embed(ctx.channel, lines, embed=embed)

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

	async def get_stats(self, tag: str, clash: coc.Client):
		group = await clash.get_league_group(tag)
		if group is None:
			return None
		
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
						members[member.tag] = self.Member(member)
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

def setup(bot: discord.ext.commands.Bot):
	bot.add_cog(Performance(bot))