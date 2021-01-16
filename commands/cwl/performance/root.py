import discord
import discord.ext.commands
from commands.utils.helpers import *

import commands.cwl.performance.net as net
import commands.cwl.performance.attacks as attacks
import commands.cwl.performance.defenses as defenses

@discord.ext.commands.group(
	description = "Displays member CWL performance stats.",
	brief = "Displays member CWL performance stats."
)
async def performance(ctx: discord.ext.commands.Context):
	if ctx.invoked_subcommand is None:
		await send_command_list(ctx, performance)
		return

def setup(bot: discord.ext.commands.Bot, group: discord.ext.commands.Group):
	group.add_command(performance)
	net.setup(bot, performance)
	attacks.setup(bot, performance)
	defenses.setup(bot, performance)