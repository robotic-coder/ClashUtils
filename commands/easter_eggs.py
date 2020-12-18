import discord
import re

recorded_end_of_battle_day = "Recorded end of battle day. It is now safe to start the next war."

async def easter_eggs(bot, message):
	if message.content == recorded_end_of_battle_day:
		await message.channel.send(recorded_end_of_battle_day)

	elif message.content in recorded_end_of_battle_day and re.match("^Recorded end", message.content):
		reply = recorded_end_of_battle_day[len(message.content):]
		if reply[0] != ".":
			await message.channel.send(reply)
		elif len(reply[1:]) > 0:
			await message.channel.send(reply[1:])

	else: return False

	return True