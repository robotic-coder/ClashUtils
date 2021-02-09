import discord.ext.commands
from commands.utils.helpers import *
from commands.utils.responder import *
from commands.utils.help import *

import commands.cwl.leaderboard as leaderboard
import commands.cwl.performance as performance
import commands.cwl.roster as roster

@discord.ext.commands.group(
	name = "cwl",
	description = "Various commands to view CWL data.",
	brief = "Various commands to view CWL data."
)
async def cwl_standard(ctx: discord.ext.commands.Context):
	resp = StandardResponder(ctx)
	if ctx.invoked_subcommand is None:
		return await resp.send(embeds=[get_standard_command_list(cwl_standard)])

def setup(bot: discord.ext.commands.Bot):
	leaderboard.setup(bot, cwl_standard)
	performance.setup(bot, cwl_standard)
	roster.setup(bot, cwl_standard)

	bot.add_command(cwl_standard)