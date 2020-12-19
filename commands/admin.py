import discord.ext.commands
import os

@discord.ext.commands.command()
async def query(ctx: discord.ext.commands.Context, *args):
	if ctx.message.author.id == 411964699429568513:
		statement = " "
		ctx.bot.storage.execute(statement.join(args))
	
	#channels = ctx.bot.storage.fetch_all_channels()
	#print(channels)

@discord.ext.commands.command()
async def test(ctx: discord.ext.commands.Context, *args):
	#This command is used in the development environment to call other commands.
	ctx.message.content = ctx.prefix+" ".join(args)
	new_ctx = await ctx.bot.get_context(ctx.message, cls=discord.ext.commands.Context)
	if new_ctx.command is None:
		return
	await ctx.bot.invoke(new_ctx)

def setup(bot: discord.ext.commands.Bot):
	if os.environ["ENVIRONMENT"] == "dev":
		test.hidden = True
		setattr(test, "required_permissions", ["send_messages"])
		bot.add_command(test)
	query.hidden = True
	bot.add_command(query)
	setattr(test, "required_permissions", ["send_messages"])