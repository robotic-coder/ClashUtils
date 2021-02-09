import discord
import discord.ext.commands
import coc
import commands.utils.emojis as emojis
from commands.utils.helpers import *
from commands.utils.responder import *

async def leaderboard(resp: Responder, tag: str, after_round: int):
	tag = resp.resolve_clan(tag)
	if tag is None:
		return await resp.send("Invalid clan tag or alias")

	try:
		group = await resp.clash.get_league_group(tag)
	except coc.errors.NotFound:
		clan = await resp.clash.get_clan(tag)
		return await resp.send(clan.name+" ("+tag+") is not currently in a Clan War League")
	
	if after_round is not None and after_round > len(group.rounds):
		return await resp.send("Invalid CWL round number")

	clans = {}
	for clan in group.clans:
		clans[clan.tag] = {
			"tag": clan.tag,
			"name": clan.name,
			"badge": clan.badge.small,
			"link": clan.share_link,
			"stars": 0,
			"destruction": 0
		}

	if after_round is None:
		embed = discord.Embed(title="Current CWL Leaderboard")
		num_rounds = len(group.rounds)
	else:
		embed = discord.Embed(title="CWL Leaderboard after "+str(after_round)+" round(s)")
		num_rounds = after_round
	embed.set_author(name=clans[tag]["name"], url=clans[tag]["link"], icon_url=clans[tag]["badge"])
	embed.set_footer(text=tag)
	
	for i in reversed(range(num_rounds)):
		round_tags = group.rounds[i]
		async for war in resp.clash.get_league_wars(round_tags):
			if war.state != "warEnded" and after_round is not None:
				return await resp.send("Select a CWL round that has ended")
			if war.state == "preparation": break

			clans[war.clan.tag]["stars"] += war.clan.stars + (10 if war.status == "won" else 0)
			clans[war.clan.tag]["destruction"] += round(war.clan.destruction*war.team_size)
			clans[war.opponent.tag]["stars"] += war.opponent.stars + (10 if war.status == "lost" else 0) #home clan lost, opponent wins
			clans[war.opponent.tag]["destruction"] += round(war.opponent.destruction*war.team_size)

	clans = sorted(clans.values(), key=lambda c: (c["stars"]*-1, c["destruction"]*-1, c["name"].lower()))

	lines = []
	lines.append("`# Stars  Dest   Clan           `")
	lines.append("`-------------------------------`")
	for (index, clan) in enumerate(clans):
		rank = str(index+1)
		stars = pad_left(clan["stars"], 5)
		destruction = pad_left(clan["destruction"], 5)
		lines.append("\u2066`"+rank+" "+stars+"  "+destruction+"  "+clan["name"]+"`")
	
	embeds = generate_embeds(lines, embed)
	await resp.send(embeds=embeds)






@discord.ext.commands.command(
	name="leaderboard",
	description = "Displays a clan's CWL leaderboard.",
	brief = "Displays a clan's CWL leaderboard.",
	usage = "[#CLANTAG or alias]",
	help = "#8PQGQC8"
)
async def leaderboard_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	if len(args) != 1:
		return await resp.send_help()
	async with resp:
		await leaderboard(resp, args[0], None)

def setup(bot: discord.ext.commands.Bot, group: discord.ext.commands.Group):
	group.add_command(leaderboard_standard)
	bot.add_slash_subcommand(leaderboard_slash, 
		base="cwl",
		base_description="Various commands to view CWL data",
		name="leaderboard",
		description="Displays a clan's CWL leaderboard",
		options=[{
			"type": 3,
			"name": "clan",
			"description": "A clan tag or alias",
			"example": "#8PQGQC8",
			"required": True
		},
		{
			"type": 4,
			"name": "after-round",
			"description": "Shows the leaderboard after this round ended. Leave out to show the current leaderboard.",
			"example": "2",
			"required": False
		}]
	)

async def leaderboard_slash(ctx, clan, after_round=None):
	resp = SlashResponder(ctx)
	async with resp:
		await leaderboard(resp, clan, after_round)