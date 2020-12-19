import discord
import discord.ext.commands

@discord.ext.commands.command()
async def help(ctx: discord.ext.commands.Context, *args):

	commands = sorted([cmd for cmd in ctx.bot.commands if not cmd.hidden], key=lambda cmd: cmd.name)

	if len(args) == 0:
		embed = discord.Embed(title="ClashUtils Help", description="")
		for command in commands:
			if not command.hidden:
				usage = str(command.usage[len(command.name)+1:])
				if len(usage) > 0: usage = "*"+usage+"*"
				embed.description += "**"+ctx.prefix+command.name+"** "+usage+"\n"+str(command.help)+"\n"
		await ctx.send(embed=embed)

	elif args[0] in [cmd.name for cmd in commands]:
		command = [cmd for cmd in commands if cmd.name == args[0]][0]
		embed = discord.Embed(title=command.name, description=command.help)
		embed.add_field(name="Usage", value=ctx.prefix+command.usage, inline=False)
		embed.add_field(name="Example", value=ctx.prefix+command.example, inline=False)
		if command.name == "help":
			await ctx.send("Yo dawg, I heard you liked help commands, so I put a help command in your help command, so you can learn to use the help command while you use the help command.", embed=embed)
		else: await ctx.send(embed=embed)

	else:
		await ctx.send("I can't find that command 🤔")

def setup(bot: discord.ext.commands.Bot):
	bot.help_command = None
	help.help = "Shows this message, or more information about a specific command."
	help.usage = "help [command]"
	setattr(help, "example", "help damage")
	setattr(help, "required_permissions", ["send_messages", "embed_links", "use_external_emojis"])
	bot.add_command(help)