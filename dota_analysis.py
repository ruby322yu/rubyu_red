import dota2api
from hero_profiles import *
import operator

api = dota2api.Initialise("10EB43DE283098AEBC83B0054CFA2A34")

def get_player_name(id):
    player = player_data(api.get_player_summaries(id), id)
    return player.name
# player name and profile picture

class player_data:
    def __init__(self, player_summ,id):
        self.id = id
        if "realname" in player_summ["players"][0]:
            self.name = player_summ["players"][0]["realname"]
        else:
            self.name = player_summ["players"][0]["personaname"]
        self.avatar = player_summ["players"][0]["avatar"]
        self.profile = {
            "initiate": 0.0,
            "big_ult": 0.0,
            "offlane": 0.0,
            "tank": 0.0,
            "heal": 0.0,
            "push": 0.0,
            "gank": 0.0,
            "mobile": 0.0
        }
        self.profiletype = {
            "spell_caster": 0,
            "right_clicker": 0,
            "support": 0,
        }
        self.profile_type_stats = []
        self.hero_freq = {}
        self.playertype = ''
        self.playerdesc = ''
        self.total_matches = 0


    def process_match_history(self, history):
        for match in history["matches"]:
            for player in match["players"]:
                if "account_id" not in player:
                    continue
                if player["account_id"] == self.id:
                   # if not player["hero_id"] in hero_stats: #just in case
                     #   continue
                    hero = hero_stats[player["hero_id"]]
                    if player["hero_id"] in self.hero_freq:
                        self.hero_freq[player["hero_id"]] += 1
                    else:
                        self.hero_freq[player["hero_id"]] = 1
                    for (key, value) in hero.iteritems():
                        if key == "id" or key == 'localized_name':
                            continue
                        if key in ["spell_caster", "right_clicker", "support"]:
                            if value:
                                self.profiletype[key] += 1
                        else:
                            self.profile[key] += (value * 100) / float(hero_stat_total[key])
    def calculate_profile(self):
        self.total_matches = 0
        match_history = api.get_match_history(account_id=self.id)
        self.num_matches = match_history["num_results"]
        self.process_match_history(match_history)

        while match_history["num_results"] != 0:
            self.total_matches += match_history["num_results"]
            match_history = api.get_match_history(account_id=self.id, start_at_match_id= match_history["matches"][-1]["match_id"]-1)
            self.process_match_history(match_history)
        self.hero_freq = sorted(self.hero_freq.items(), key=operator.itemgetter(1), reverse=True)
        self.fav_hero = self.hero_freq[0][0]
        self.profile = sorted(self.profile.items(), key=operator.itemgetter(1), reverse=True)
        print self.profile
        print self.total_matches
        #print self.hero_freq


    def generate_statement(self):
        self.calculate_profile()
        total = self.profiletype["right_clicker"] + self.profiletype["support"] + self.profiletype["spell_caster"]
        playertype = ''
        playerdesc = ''
        #case 1 right clicker highest
        if self.profiletype["right_clicker"] >= self.profiletype["support"] and self.profiletype["right_clicker"] >= self.profiletype["spell_caster"]:
            # case 1a. pure right click
            if self.profiletype["right_clicker"] >= total/2:
                self.playertype = "Right Click Carry"
            # case 1b. right click + magical damage
            elif self.profiletype["right_clicker"] + self.profiletype["spell_caster"] >= total*2/3:
                self.playertype = "General Damage Dealer"
        # case 2
        elif self.profiletype["spell_caster"] >= self.profiletype["support"]:
            # case 2a not very supporty
            if self.profiletype["spell_caster"] >= total/2:
                self.playertype = "Spell Caster/ Carry"
            elif self.profiletype["spell_caster"] + self.profiletype["support"] >= total*2/3:
                self.playertype = "Magical Damage/ Utility"
        # case 3
        else:
            if self.profiletype["support"] >= total/2:
                self.playertype = "Hard Support"
            elif self.profiletype["spell_caster"] + self.profiletype["support"] >= total*2/3:
                self.playertype = "Spell Casting Support"

        if self.playertype=='':
            self.playertype = "Well Rounded Player"

        self.bg_image = profile_type_bg[self.playertype]
        self.playertype_desc = profile_type_template[self.playertype]
        self.playerdesc = "You favour heroes that can "+profile_desc_template[self.profile[0][0]]+ ", as well as ones" \
                                                    " that can " + profile_desc_template[self.profile[1][0]]
        for i in range(5):
            self.profile_type_stats.append((profile_stats[self.profile[i][0]], int(self.profile[i][1])/10))


        print self.profile_type_stats
        print self.playertype
        print self.playerdesc


#print(get_player_name(73853498))

# top 3 favourite heroes + hero synergies (win rate with friendly heroes, lose rate against enemies

# average win rate + kda
#player = player_data(api.get_player_summaries(109760), 9338760)
#player.generate_statement()


