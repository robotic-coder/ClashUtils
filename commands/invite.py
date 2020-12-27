import discord
import discord.ext.commands

@discord.ext.commands.command(
	description = "Sends a link that can be used to add me to a server.",
	brief = "Sends a link that can be used to add me to a server.",
	usage = "",
	help = ""
)
async def invite(ctx: discord.ext.commands.Context, *args):
	embed = discord.Embed(description="Click [here](https://discord.com/api/oauth2/authorize?client_id="+str(ctx.bot.user.id)+"&permissions=314432&scope=bot%20applications.commands) to add ClashUtils to your server.")
	await ctx.channel.send(embed=embed)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(invite)