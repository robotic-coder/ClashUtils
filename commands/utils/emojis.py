import discord

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
		
		elif emoji.id == 776194523150811156: spells["lightning"] = emoji
		elif emoji.id == 776194265712820225: spells["earthquake"] = emoji

