import discord.ext.commands
from commands.utils.helpers import *

import commands.cwl.leaderboard as leaderboard
import commands.cwl.performance as performance
import commands.cwl.roster as roster

@discord.ext.commands.group(
	name = "cwl",
	description = "Various commands to view CWL data.",
	brief = "Various commands to view CWL data."
)
async def cwl_standard(ctx: discord.ext.commands.Context):
	if ctx.invoked_subcommand is None:
		await send_command_list(ctx, cwl_standard)
		return

def setup(bot: discord.ext.commands.Bot):
	leaderboard.setup(bot, cwl_standard)
	performance.setup(bot, cwl_standard)
	roster.setup(bot, cwl_standard)

	bot.add_command(cwl_standard)