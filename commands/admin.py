import discord.ext.commands

@discord.ext.commands.command()
async def query(ctx: discord.ext.commands.Context, *args):
	if ctx.message.author.id == 411964699429568513:
		statement = " "
		ctx.bot.storage.execute(statement.join(args))
	
	channels = ctx.bot.storage.fetch_all_channels()
	print(channels)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(query)