import discord
import discord.ext.commands
import commands.utils.helpers as helpers
import commands.utils.emojis as emojis

earthquake_damage = [ 0.145, 0.17, 0.21, 0.25, 0.29 ]
lightning_damage = [ 150, 180, 210, 240, 270, 320, 400, 480, 560 ]
shield_damage = [ 1260, 1460, 1660, 1860, 1960 ]

@discord.ext.commands.command()
async def damagetest(ctx: discord.ext.commands.Context, *args):
	print("todo")

def setup(bot: discord.ext.commands.Bot):
	bot.add_command(damagetest)