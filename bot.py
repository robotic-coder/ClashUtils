import os

import copy
import coc
import re
import discord
import discord.ext.commands
import commands.utils.emojis as emojis
from commands.easter_eggs import easter_eggs
from utils.clash import Clash
from utils.storage import Storage
from discord_slash import SlashCommand, SlashContext

from dotenv import load_dotenv
load_dotenv()

class ClashUtilsBot(discord.ext.commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix="//",
			activity=discord.Activity(type=discord.ActivityType.watching, name="for /help-cu")
		)

		if os.environ["ENVIRONMENT"] == "live":
			self.command_guild_ids = None
			self.slash_command_prefix = ""
		else:
			self.command_guild_ids = [
				738656460430377013, #main guild
				789297914446348299 #slash-only guild
			]
			self.slash_command_prefix = "dev-"

		self.clash = coc.login(
			os.environ["CLASH_EMAIL"],
			os.environ["CLASH_PASSWORD"],
			key_names=os.environ["CLASH_TOKEN_NAME"],
			key_count=2,
			client=Clash
		)

		self.storage = Storage(os.environ["DATABASE_URL"])

		self.aliases = {}
		self.global_aliases = {}
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

		self.slash_command_options = {}

	async def on_ready(self):
		print("Logged in as "+str(self.user))
		emojis.setup(self)
		self.icons = emojis.Emojis(self)
		
		self.slash = SlashCommand(self)

		extensions = [
			#"commands.about",
			"commands.admin",
			"commands.alias_manager",
			"commands.army_levels",
			"commands.cwl.root",
			"commands.damage_calculation",
			"commands.invite",
			"commands.help",
			"commands.max_war_score",
			"commands.war_status"
		]
		for extension in extensions:
			self.load_extension(extension)

		await self.slash.sync_all_commands(True)
		print("Completed setup")
	
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

	def add_slash_command(self, cmd, name=None, description=None, options=None, connector=None):
		self.slash.add_slash_command(
			cmd = cmd,
			name = self.slash_command_prefix+name,
			description = description,
			guild_ids = self.command_guild_ids,
			options = self.strip_options(options),
			connector = connector,
			has_subcommands = False
		)
		cmd_name = cmd.__name__ if name is None else name
		self.slash_command_options[self.slash_command_prefix+cmd_name] = options

	def add_slash_subcommand(self, cmd, base, subcommand_group=None, name=None, description=None, base_description=None, subcommand_group_description=None, options=None, connector=None):
		self.slash.add_subcommand(
			cmd = cmd,
			base = self.slash_command_prefix+base,
			subcommand_group = subcommand_group,
			name = name,
			description = description,
			base_description = base_description,
			subcommand_group_description = subcommand_group_description,
			guild_ids = self.command_guild_ids,
			options = self.strip_options(options),
			connector = connector
		)
		group = " " if subcommand_group is None else " "+subcommand_group+" "
		cmd_name = cmd.__name__ if name is None else name
		self.slash_command_options[self.slash_command_prefix+base+group+cmd_name] = options

	def strip_options(self, options):
		if options is None:
			return None
		output = copy.deepcopy(options)
		for x in output:
			del x["example"]
		return output

bot = ClashUtilsBot()
bot.run(os.environ["DISCORD_TOKEN"])
