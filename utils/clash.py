import coc

class War(coc.ClanWar):
	@property
	def cwl_round(self):
		if self.league_group is None: return None
		for (index, war_round) in enumerate(self.league_group.rounds):
			if self.war_tag in war_round:
				return index+1


class Clash(coc.Client):
	async def get_current_war(self, clan_tag: str, cwl_round=coc.WarRound.current_war, cls=War, allow_prep: bool = False, **kwargs):
		if cwl_round == coc.WarRound.current_war:
			war = await super().get_current_war(clan_tag, cwl_round=coc.WarRound.current_war, cls=cls, **kwargs)
			group = war.league_group if war is not None and war.is_cwl else None
			if war is None and allow_prep:
				# if no in-battle war is found but prep is allowed, look for a war in prep day
				war = await super().get_current_war(clan_tag, cwl_round=coc.WarRound.current_preparation, cls=cls, **kwargs)
			elif group is not None and war.state == "warEnded" and not (len(group.rounds) == group.number_of_rounds and war.war_tag in group.rounds[-1]):
				# if in cwl, the war has ended, and war is not the last round of the week: check the latest round to see if it is out of prep (in battle or ended)
				next_war = (await self.get_league_wars(war.league_group.rounds[-1], clan_tag=clan_tag, cls=cls).flatten())[0]
				if next_war.state != "preparation":
					next_war.league_group = war.league_group # wars from get_league_wars() do not have a cwl group, so attach the previously-fetched group
					war = next_war
			return war
		else:
			return await super().get_current_war(clan_tag, cwl_round=cwl_round, cls=cls, **kwargs)