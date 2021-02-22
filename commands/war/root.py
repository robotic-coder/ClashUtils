import discord.ext.commands
from commands.utils.helpers import *
from commands.utils.responder import *
from commands.utils.help import *

import commands.war.map as map
#import commands.war.events as events

@discord.ext.commands.group(
	name = "war",
	description = "Displays a clan's current war.",
	brief = "Displays a clan's current war."
)
async def war_standard(ctx: discord.ext.commands.Context):
	resp = StandardResponder(ctx)
	if ctx.invoked_subcommand is None:
		return await resp.send(embeds=[get_standard_command_list(war_standard)])

def setup(bot: discord.ext.commands.Bot):
	map.setup(bot, war_standard)
	#events.setup(bot, war_standard)

	bot.add_command(war_standard)