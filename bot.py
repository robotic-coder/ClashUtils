import os

import coc
import re
import discord
import discord.ext.commands
import commands.utils.emojis as emojis
from commands.easter_eggs import easter_eggs
from utils.storage import Storage

from dotenv import load_dotenv
load_dotenv()

class ClashUtilsBot(discord.ext.commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix=self.check_prefix,
			activity=discord.Activity(type=discord.ActivityType.watching, name="for @ClashUtils help")
		)
		extensions = [
			"commands.admin",
			#"commands.channel_link_manager",
			"commands.current_war_map",
			"commands.cwl_roster",
			"commands.damage_calculation",
			"commands.invite",
			"commands.help",
			"commands.max_war_score"
		]
		for extension in extensions:
			self.load_extension(extension)

		self.clash = coc.login(
			os.environ["CLASH_EMAIL"],
			os.environ["CLASH_PASSWORD"],
			key_names=os.environ["CLASH_TOKEN_NAME"],
			key_count=2
		)

		self.storage = Storage()

		self.linked_channels = {}
		channels = self.storage.fetch_all_channels()
		for c in channels: 
			del c["last_used"]
			self.link_channel(c["snowflake"], c["prefix"], c["clan"])

	async def on_ready(self):
		print("Logged in as "+str(self.user))
		emojis.setup(self)
	
	async def on_message(self, message):
		if message.author.bot: return	
		if os.environ["ENVIRONMENT"] == "dev" and message.author.id != 411964699429568513: return
		if await easter_eggs(self, message): return
		
		ctx = await self.get_context(message, cls=discord.ext.commands.Context)
		if ctx.command is None:
			return

		missing_permissions = self.find_missing_permissions(ctx)
		if len(missing_permissions) == 0:
			await self.invoke(ctx)
		else:
			await ctx.channel.send("I am missing the following permission(s) in this channel:```\n"+"\n".join(missing_permissions)+"```")
	
	def find_missing_permissions(self, ctx: discord.ext.commands.Context):
		permissions = ctx.channel.permissions_for(ctx.me)
		return [p for p in ctx.command.required_permissions if getattr(permissions, p) == False]

	def link_channel(self, snowflake, prefix, clan):
		if snowflake not in self.linked_channels:
			self.linked_channels[snowflake] = {}
		self.linked_channels[snowflake][prefix] = clan

	def unlink_channel(self, snowflake, prefix):
		del self.linked_channels[snowflake][prefix]
		if len(self.linked_channels[snowflake].items()) == 0:
			del self.linked_channels[snowflake]

	async def check_prefix(self, bot, message):
		ping = ["<@786654276185096203> ", "<@!786654276185096203> "]
		if message.channel.id in self.linked_channels:
			return list(self.linked_channels[message.channel.id].keys()) + ping
		else: return ping

bot = ClashUtilsBot()
bot.run(os.environ["DISCORD_TOKEN"])