import discord
import discord.ext.commands
import coc
from math import floor
from datetime import datetime
from commands.utils.helpers import *
import commands.utils.emojis as emojis


@discord.ext.commands.command()
async def currentwar(ctx: discord.ext.commands.Context, *args):
	(tag, params) = resolve_clan(ctx)
	clash = ctx.bot.clash
	
	if tag is not None:
		async with ctx.channel.typing():
			war = await clash.get_current_war(tag)
			if war.state != "notInWar":
				show_names = len(params) == 1 and params[0] == "full"
				if war.type == "cwl": max_attacks = 1
				else: max_attacks = 2
				embed = discord.Embed(title=war.clan.name+" vs "+war.opponent.name)
				
				bases = []
				for i in range(war.team_size):
					base = {}
					base["clan"] = war.clan.members[i]
					base["enemy"] = war.opponent.members[i]
					bases.append(base)

				if war.state == "preparation":
					status = "starting in "+get_time_delta(end=war.start_time.time)
					print(war.start_time)
				elif war.state == "inWar":
					status = get_time_delta(end=war.end_time.time)+" remaining"
				elif war.state == "warEnded":
					status = "ended "+get_time_delta(start=war.end_time.time)+" ago"
				else:
					status = "unknown status"

				lines = [
					"`Stars             "+pad_left(war.clan.stars, 3)+" - "+pad_right(war.opponent.stars, 3)+spaces(4)+"`",
					"`Destruction   "+pad_left(round_fixed(war.clan.destruction, 2)+"%", 7)+" - "+pad_right(round_fixed(war.opponent.destruction, 2)+"%", 7)+"`",
					"`Attacks Used      "+pad_left(war.clan.attacks_used, 3)+" - "+pad_right(war.opponent.attacks_used, 3)+spaces(4)+"`",
					"`Attacks Remaining "+pad_left(max_attacks*war.team_size-war.clan.attacks_used, 3)+" - "+pad_right(max_attacks*war.team_size-war.opponent.attacks_used, 3)+spaces(4)+"`",
					"",
					"**War Map** - "+status
				]
				for index, base in enumerate(bases):
					clan_name = ""
					clan_stars = 0
					clan_dest = ""
					enemy_name = ""
					enemy_stars = 0
					enemy_dest = ""
					clan_attacks = ""
					enemy_attacks = ""
					clan_th = base["clan"].town_hall
					enemy_th = base["enemy"].town_hall

					if show_names: clan_name = "\u2066"+pad_left(base["clan"].name, 15)+" "
					if base["clan"].best_opponent_attack is not None:
						clan_stars = base["clan"].best_opponent_attack.stars
						clan_dest = str(base["clan"].best_opponent_attack.destruction)+"%"

					for i in range(len(base["clan"].attacks), max_attacks): clan_attacks += "*"
					for i in range(0, len(base["clan"].attacks)): clan_attacks += " "

					if show_names: enemy_name = " "+pad_right(base["enemy"].name, 15)
					if base["enemy"].best_opponent_attack is not None:
						enemy_stars = base["enemy"].best_opponent_attack.stars
						enemy_dest = str(base["enemy"].best_opponent_attack.destruction)+"%"

					for i in range(0, len(base["enemy"].attacks)): enemy_attacks += " "
					for i in range(len(base["enemy"].attacks), max_attacks): enemy_attacks += "*"

					clan_line = "`"+clan_name+pad_left(clan_dest, 4)+"` "+stars(clan_stars)+" "+str(emojis.th[clan_th])+"`"+clan_attacks
					enemy_line = enemy_attacks+"`"+str(emojis.th[enemy_th])+" "+stars(enemy_stars)+" `"+pad_right(enemy_dest, 4)+enemy_name+"`"
					lines.append(clan_line+" "+pad_left((index+1), 2)+" "+enemy_line)
				
				await send_lines_in_embed(ctx.channel, lines, embed)

			else:
				clan = await clash.get_clan(tag)
				await ctx.channel.send(clan.name+" ("+tag+") is not in war.")
	else:
		await ctx.channel.send("format: `<@786654276185096203> roster #CLANTAG`")

#async def getWarSize(clash: Client, channel: TextChannel):

def get_time_delta(start=datetime.utcnow(), end=datetime.utcnow()):
	delta = end-start
	if delta.seconds < 0:
		return "now"
	minutes = floor(delta.seconds/60)
	hours = floor(minutes/60)
	minutes %= 60

	output = str(minutes)+"m"

	if hours > 0: output = str(hours)+"h "+output
	else: return output

	if delta.days > 0: output = str(delta.days)+"d "+output
	return output

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(currentwar)