import discord
import discord.ext.commands
from discord_slash import SlashCommand, SlashContext
	
class Responder():
	def __init__(self, ctx, bot):
		self._ctx = ctx
		self.bot = bot
		self.clash = bot.clash

		(self.author, self.author_id) = self.__get_details(ctx.author)
		(self.channel, self.channel_id) = self.__get_details(ctx.channel)
		(self.guild, self.guild_id) = self.__get_details(ctx.guild)

		if self.channel is not None:
			self._loading = ctx.channel.typing()
		else: self._loading = None

	def __get_details(self, element):
		if element is None or isinstance(element, int):
			return (None, element)
		else:
			return (element, element.id)

	async def send(self, content="", embeds=[]):
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
		
	async def __aenter__(self):
		if self._loading is not None:
			await self._loading.__aenter__()

	async def __aexit__(self, err_type, err_value, traceback):
		if self._loading is not None:
			await self._loading.__aexit__(err_type, err_value, traceback)

class StandardResponder(Responder):
	def __init__(self, ctx: discord.ext.commands.Context):
		super().__init__(ctx, ctx.bot)
		self._loading = ctx.channel.typing()

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

class SlashResponder(Responder):
	def __init__(self, ctx: SlashContext):
		super().__init__(ctx, ctx._discord)
		self.__loading_message_sent = False

	async def send(self, content="", embeds=[]):
		await self.__send(content, embeds)
		if self.__loading_message_sent:
			await self._ctx.delete()
			self.__loading_message_sent = False

	async def __send(self, content, embeds):
		if len(embeds) > 10:
			await self._ctx.send(content=content, embeds=embeds[:10])
			await self.__send("", embeds[10:])
		elif len(embeds) > 0 or len(content) > 0:
			await self._ctx.send(content=content, embeds=embeds)
		return []

	async def __aenter__(self):
		if self.author is None and self.author_id is not None and self.guild is not None:
			self.author = await self.guild.fetch_member(self.author_id)
		
		if not self.__loading_message_sent:
			await self.send(content="Loading...")
			self.__loading_message_sent = True
		
		try:
			await super().__aenter__()
		except discord.errors.Forbidden:
			self._loading = None