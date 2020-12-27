import discord
import discord.ext.commands
from commands.utils.helpers import *

@discord.ext.commands.command(
	description = "Displays information about commands.",
	brief = "Shows this message, or more information about a specific command.",
	usage = "[command]",
	help = "damage"
)
async def help(ctx: discord.ext.commands.Context, *args):
	await send_help(ctx, ctx.bot, *args)
	

async def send_help(ctx, command_holder, *args):
	if len(args) == 0:
		await send_command_list(ctx, command_holder, True)

	elif args[0] in [cmd.name for cmd in command_holder.commands if not cmd.hidden]:
		command = [cmd for cmd in command_holder.commands if cmd.name == args[0]][0]
		if isinstance(command, discord.ext.commands.Group):
			await send_help(ctx, command, *args[1:])
		else:
			await send_command_help(ctx, command, True)

	else:
		await ctx.send("I can't find that command 🤔")

def setup(bot: discord.ext.commands.Bot):
	bot.help_command = None
	bot.add_command(help)