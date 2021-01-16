import coc

class Member:
	def __init__(self, coc_member: coc.ClanWarMember):
		self.tag = coc_member.tag
		self.name = coc_member.name
		self.town_hall_level = coc_member.town_hall
		self.num_rounds = 0
		self.num_attacks = 0
		self.attack_stars = 0
		self.attack_destruction = 0
		self.num_defenses = 0
		self.defence_stars = 0
		self.defence_destruction = 0

	@property
	def avg_attack_stars(self): return self.attack_stars / self.num_rounds
	@property
	def avg_attack_destruction(self): return self.attack_destruction / self.num_rounds
	@property
	def avg_defence_stars(self): return self.defence_stars / self.num_rounds
	@property
	def avg_defence_destruction(self): return self.defence_destruction / self.num_rounds
	@property
	def star_score(self): return self.attack_stars - self.defence_stars
	@property
	def destruction_score(self): return self.attack_destruction - self.defence_destruction

async def get_stats(tag: str, clash: coc.Client):
	try:
		group = await clash.get_league_group(tag)
		num_rounds = 0
		members = {}
		async for war in group.get_wars_for_clan(tag):
			if war.state == "warEnded":
				num_rounds += 1
				lineup = war.clan.members
				attacks = []
				attacked_bases = {}
				for member in lineup:
					if member.tag not in members:
						members[member.tag] = Member(member)
					members[member.tag].num_rounds += 1
					if len(member.attacks) > 0:
						attacks.append(member.attacks[0])
						attacked_bases[member.attacks[0].defender_tag] = {
							"tag": member.attacks[0].defender_tag,
							"stars": 0
						}
					if member.best_opponent_attack is not None:
						members[member.tag].num_defenses += 1
						members[member.tag].defence_stars += member.best_opponent_attack.stars
						members[member.tag].defence_destruction += member.best_opponent_attack.destruction

				attacks = sorted(attacks, key=lambda x: x.order)

				for attack in attacks:
					target = attacked_bases[attack.defender_tag]
					member = members[attack.attacker_tag]
					if attack.stars > target["stars"]:
						member.attack_stars += attack.stars-target["stars"]
						target["stars"] = attack.stars
					member.attack_destruction += attack.destruction
					member.num_attacks += 1
				
		return {
			"members": members.values(),
			"clan_name": [clan.name for clan in group.clans if clan.tag == tag][0],
			"num_rounds": num_rounds
		}
	except coc.errors.NotFound:
		return None

def get_options():
	return [{
		"type": 3,
		"name": "clan",
		"description": "A clan tag or alias",
		"required": True
	},
	{
		"type": 3,
		"name": "size",
		"description": "The amount of data to be shown. `full` will probably display incorrectly on a phone.",
		"required": False,
		"choices": [
			{
				"name": "full",
				"value": "full"
			},
			{
				"name": "compact",
				"value": "compact"
			}
		]
	}]