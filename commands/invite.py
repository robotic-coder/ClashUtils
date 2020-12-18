import discord
import discord.ext.commands

@discord.ext.commands.command()
async def invite(ctx: discord.ext.commands.Context, *args):
	embed = discord.Embed(title="Add ClashUtils to your server", description="https://discord.com/api/oauth2/authorize?client_id="+str(ctx.bot.user.id)+"&permissions=347200&scope=bot%20applications.commands")
	await ctx.channel.send(embed=embed)

def setup(bot: discord.ext.commands.Bot):
	invite.help = "Sends a link that can be used to add me to a server."
	invite.usage = "invite"
	invite.hidden = True
	setattr(invite, "example", "invite")
	bot.add_command(invite)