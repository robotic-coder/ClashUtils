import discord.ext.commands
import commands.cwl.performance as performance
import commands.cwl.roster as roster
from commands.utils.helpers import *

class CWL(discord.ext.commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@discord.ext.commands.group(
		description = "Various commands to view CWL data.",
		brief = "Various commands to view CWL data."
	)
	async def cwl(self, ctx: discord.ext.commands.Context):
		if ctx.invoked_subcommand is None:
			await send_command_list(ctx, self.cwl)
			return
	performance.setup(cwl)
	roster.setup(cwl)

def setup(bot: discord.ext.commands.Bot):
	bot.add_cog(CWL(bot))