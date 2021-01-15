import discord
import discord.ext.commands
from discord_slash import SlashCommand, SlashContext
	
class Responder():
	def __init__(self, ctx):
		self.ctx = ctx
		self.bot = None
		self.clash = None
		self.loading = None

	async def send(self, content="", embeds=[]):
		pass

	def resolve_clan(self, input: str):
		if input.startswith("#"):
			return input
		elif self.ctx.guild.id in self.bot.aliases and input in self.bot.aliases[self.ctx.guild.id]:
			self.bot.storage.update_last_used(self.ctx.guild.id, input)
			return self.bot.aliases[self.ctx.guild.id][input]
		elif input in self.bot.global_aliases:
			return self.bot.global_aliases[input]
		else: return None
		
	async def __aenter__(self):
		if self.loading is not None:
			await self.loading.__aenter__()

	async def __aexit__(self, err_type, err_value, traceback):
		if self.loading is not None:
			await self.loading.__aexit__(err_type, err_value, traceback)

class StandardResponder(Responder):
	def __init__(self, ctx: discord.ext.commands.Context):
		self.ctx = ctx
		self.bot = ctx.bot
		self.clash = ctx.bot.clash
		self.loading = ctx.channel.typing()

	async def send(self, content="", embeds=[]):
		if len(embeds) > 0:
			message = await self.ctx.channel.send(content, embed=embeds.pop(0))
			output = await self.send("", embeds)
			return [message]+output
		elif len(content) > 0:
			message = await self.ctx.channel.send(content)
			return [message]
		else:
			return []

class SlashResponder(Responder):
	def __init__(self, ctx: SlashContext):
		self.ctx = ctx
		self.bot = ctx._discord
		self.clash = ctx._discord.clash
		if ctx.channel is not None:
			self.loading = ctx.channel.typing()
		self.loading_message_sent = False

	async def send(self, content="", embeds=[]):
		await self.__send(content, embeds)
		if self.loading_message_sent:
			await self.ctx.delete()
			self.loading_message_sent = False

	async def __send(self, content, embeds):
		if len(embeds) > 10:
			await self.ctx.send(content=content, embeds=embeds[:10])
			await self.__send("", embeds[10:])
		elif len(embeds) > 0 or len(content) > 0:
			await self.ctx.send(content=content, embeds=embeds)
		return []

	async def __aenter__(self):
		if not self.loading_message_sent:
			await self.send(content="Loading...")
			self.loading_message_sent = True
		if self.loading is not None:
			try:
				await self.loading.__aenter__()
			except discord.errors.Forbidden:
				self.loading = None