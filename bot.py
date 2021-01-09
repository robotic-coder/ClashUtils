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
			command_prefix="//",
			activity=discord.Activity(type=discord.ActivityType.watching, name="for //help")
		)
		extensions = [
			#"commands.about",
			"commands.admin",
			"commands.alias_manager",
			"commands.army_levels",
			"commands.cwl_performance",
			"commands.cwl_roster",
			"commands.damage_calculation",
			"commands.invite",
			"commands.help",
			"commands.max_war_score",
			"commands.war_status"
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

		self.aliases = {}
		aliases = self.storage.fetch_all_aliases()
		for i in aliases:
			del i["last_used"]
			self.link_guild(i["snowflake"], i["alias"], i["clan"])

		self.desired_permissions = [
			"send_messages",
			"attach_files",
			"embed_links",
			"use_external_emojis"
		]

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
		return [p for p in self.desired_permissions if getattr(permissions, p) == False]

	def link_guild(self, snowflake, alias, clan):
		if snowflake not in self.aliases:
			self.aliases[snowflake] = {}
		self.aliases[snowflake][alias] = clan

	def unlink_guild(self, snowflake, alias):
		del self.aliases[snowflake][alias]
		if len(self.aliases[snowflake].items()) == 0:
			del self.aliases[snowflake]

bot = ClashUtilsBot()
bot.run(os.environ["DISCORD_TOKEN"])