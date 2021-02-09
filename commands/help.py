import discord
import discord.ext.commands
from commands.utils.helpers import *
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *
from commands.utils.help import *

@discord.ext.commands.command(
	name = "help",
	description = "Displays information about commands.",
	brief = "Shows this message, or more information about a specific command.",
	usage = "[command]",
	help = "alias add"
)
async def help_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	embed = get_help_standard(resp.bot, *args)
	if embed is not None:
		await resp.send(embeds=[embed])
	else:
		await resp.send("I can't find that command 🤔")

def setup(bot: discord.ext.commands.Bot):
	bot.help_command = None
	bot.add_command(help_standard)

	bot.add_slash_command(help_slash,
		name="help-cu",
		description="Displays details about commands",
		options=[{
			"type": 3,
			"name": "command",
			"description": "A specific command to search for",
			"example": "alias add",
			"required": False
		}]
	)

async def help_slash(ctx: SlashContext, command=None):
	resp = SlashResponder(ctx)

	if command is None:
		embed = get_slash_command_list(resp.bot, resp.bot.slash.commands)
	else:
		embed = get_help_slash(resp.bot, command)

	if embed is not None:
		await resp.send(embeds=[embed])
	else:
		await resp.send("I can't find that command 🤔")
			
