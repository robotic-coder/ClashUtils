import discord
import discord.ext.commands
import commands.utils.help as help
from discord_slash import SlashCommand, SlashContext
	
class Responder():
	def __init__(self, ctx):
		self._ctx = ctx
		self.bot = ctx.bot
		self.clash = ctx.bot.clash

		self.author = ctx.author
		self.author_id: int
		self.channel = ctx.channel
		self.channel_id: int
		self.guild = ctx.guild
		self.guild_id: int

	async def send(self, content="", embeds=[]):
		pass

	async def send_help(self, error=""):
		pass

	def resolve_clan(self, input: str):
		if input.startswith("#"):
			return input.upper()
		elif self.guild_id in self.bot.aliases and input in self.bot.aliases[self.guild_id]:
			self.bot.storage.update_last_used(self.guild_id, input)
			return self.bot.aliases[self.guild_id][input]
		elif input in self.bot.global_aliases:
			return self.bot.global_aliases[input]
		else: return None

class StandardResponder(Responder):
	def __init__(self, ctx: discord.ext.commands.Context):
		super().__init__(ctx)
		self.author_id = ctx.author.id
		self.channel_id = ctx.channel.id
		self.guild_id = ctx.guild.id
		self._loading = self.channel.typing()

	async def send(self, content="", embeds=[]):
		if len(embeds) > 0:
			message = await self.channel.send(content, embed=embeds.pop(0))
			output = await self.send("", embeds)
			return [message]+output
		elif len(content) > 0:
			message = await self.channel.send(content)
			return [message]
		else:
			return []

	async def send_help(self, error=""):
		lookup = self._ctx.command.qualified_name.split(" ")
		return await self.send(content=error, embeds=[help.get_help_standard(self.bot, *lookup)])

	async def __aenter__(self):
		if self._loading is not None:
			try:
				await self._loading.__aenter__()
			except discord.errors.Forbidden:
				self._loading = None
		return self

	async def __aexit__(self, err_type, err_value, traceback):
		if err_value is not None:
			await self.send("An error occurred!\nError details: `"+str(err_value)+"`")
		if self._loading is not None:
			await self._loading.__aexit__(err_type, err_value, traceback)

class SlashResponder(Responder):
	def __init__(self, ctx: SlashContext):
		super().__init__(ctx)
		self.author_id = ctx.author_id
		self.channel_id = ctx.channel_id
		self.guild_id = ctx.guild_id

	async def send(self, content="", embeds=[]):
		return await self.__send(content, embeds)

	async def __send(self, content, embeds):
		size = 0
		i = 0
		while i < len(embeds) and size+len(embeds[i]) <= 6000 and i+1 <= 10:
			size += len(embeds[i])
			i += 1
		message = await self._ctx.send(content=content, embeds=embeds[:i])
		if i < len(embeds):
			output = await self.__send("", embeds[i:])
			return [message]+output
		else: return [message]

	async def send_help(self, error=""):
		return await self.send(content=error, embeds=[help.get_help_slash(self.bot, self.__command)])

	async def send_command(self, params):
		await self._ctx.send(content="Due to a Discord bug you might not be able to fully copy your command on PC. Here it is, in case you want to copy it:", hidden=True)
		await self._ctx.send(content="/"+self.__command+" "+" ".join([key+": "+value for (key, value) in params.items()]), hidden=True)

	async def __aenter__(self):
		await self._ctx.defer()
		return self

	async def __aexit__(self, err_type, err_value, traceback):
		if err_value is not None:
			await self.send("An error occurred!\nError details: `"+str(err_value)+"`")

	@property
	def __command(self):
		output = self._ctx.name
		if self._ctx.subcommand_group is not None:
			output += " "+self._ctx.subcommand_group
		if self._ctx.subcommand_name is not None:
			output += " "+self._ctx.subcommand_name
		return output