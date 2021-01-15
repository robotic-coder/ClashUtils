import discord.ext.commands
import commands.cwl.performance as performance
import commands.cwl.roster as roster
from commands.utils.helpers import *

@discord.ext.commands.group(
	description = "Various commands to view CWL data.",
	brief = "Various commands to view CWL data."
)
async def cwl(ctx: discord.ext.commands.Context):
	if ctx.invoked_subcommand is None:
		await send_command_list(ctx, cwl)
		return

def setup(bot: discord.ext.commands.Bot):
	performance.setup(cwl)
	roster.setup(cwl)
	bot.add_command(cwl)