import discord

class IconList:
	def __init__(self, bot):

		self.heroes = {
			"king": bot.get_emoji(744711959580115075),
			"queen": bot.get_emoji(744712003897262132),
			"warden": bot.get_emoji(744712034209497108),
			"champion": bot.get_emoji(744712056623595712),
		}

		self.th = {
			2: bot.get_emoji(744711577000738869),
			3: bot.get_emoji(744711605022883890),
			4: bot.get_emoji(744711633900929135),
			5: bot.get_emoji(744711657724575787),
			6: bot.get_emoji(744711687332036648),
			7: bot.get_emoji(744711725244219413),
			8: bot.get_emoji(744711759377727568),
			9: bot.get_emoji(744711793829740665),
			10: bot.get_emoji(744711824355753995),
			11: bot.get_emoji(744711852738740294),
			12: bot.get_emoji(765501467477540894),
			13: bot.get_emoji(765501454852161556),
			14: bot.get_emoji(828970456233148476)
		}

		self.spells = {
			"lightning": bot.get_emoji(776194523150811156),
			"earthquake": bot.get_emoji(776194265712820225)
		}

	def th_str(self, level: int):
		if level in self.th:
			return str(self.th[level])
		else:
			return f"({str(level)})"

#Legacy emojis

heroes = {}
th = {}
spells = {}

def setup(bot: discord.Client):
	server = [guild for guild in bot.guilds if guild.id == 738656460430377013][0]

	for emoji in server.emojis:
		if emoji.id == 744711959580115075: heroes["king"] = emoji
		elif emoji.id == 744712003897262132: heroes["queen"] = emoji
		elif emoji.id == 744712034209497108: heroes["warden"] = emoji
		elif emoji.id == 744712056623595712: heroes["champion"] = emoji

		elif emoji.id == 744711577000738869: th[2] = emoji
		elif emoji.id == 744711605022883890: th[3] = emoji
		elif emoji.id == 744711633900929135: th[4] = emoji
		elif emoji.id == 744711657724575787: th[5] = emoji
		elif emoji.id == 744711687332036648: th[6] = emoji
		elif emoji.id == 744711725244219413: th[7] = emoji
		elif emoji.id == 744711759377727568: th[8] = emoji
		elif emoji.id == 744711793829740665: th[9] = emoji
		elif emoji.id == 744711824355753995: th[10] = emoji
		elif emoji.id == 744711852738740294: th[11] = emoji
		elif emoji.id == 765501467477540894: th[12] = emoji
		elif emoji.id == 765501454852161556: th[13] = emoji
		elif emoji.id == 828970456233148476: th[14] = emoji
		
		elif emoji.id == 776194523150811156: spells["lightning"] = emoji
		elif emoji.id == 776194265712820225: spells["earthquake"] = emoji

