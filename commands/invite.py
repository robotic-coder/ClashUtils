import discord
import discord.ext.commands
from discord_slash import SlashCommand, SlashContext
from commands.utils.responder import *

async def invite(resp: Responder):
	embed = discord.Embed(description="Click [here](https://discord.com/api/oauth2/authorize?client_id="+str(resp.bot.user.id)+"&permissions=314432&scope=bot%20applications.commands) to add ClashUtils to your server.")
	await resp.send(embeds=[embed])

@discord.ext.commands.command(
	name = "invite",
	description = "Sends a link that can be used to add me to a server.",
	brief = "Sends a link that can be used to add me to a server.",
	usage = "",
	help = ""
)
async def invite_standard(ctx: discord.ext.commands.Context, *args):
	resp = StandardResponder(ctx)
	await invite(resp)

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(invite_standard)
	bot.add_slash_command(invite_slash,
		name="invite",
		description="Sends a link that can be used to add me to a server"
	)

async def invite_slash(ctx: SlashContext):
	resp = SlashResponder(ctx)
	await invite(resp)