import dota2api
from hero_profiles import *
from dota_helper_functions import *
import operator

api = dota2api.Initialise("10EB43DE283098AEBC83B0054CFA2A34")

# class, defines the number of matches won/lost for a hero, with another specific hero in the game
class hero_matchup:

    def __init__(self, id):
        self.hero_id = id
        self.winning_matchup = {}
        self.losing_matchup = {}

    # increments values in the dictionaries, which stores number of matches won/lost
    def add_to_winning(self, hero_id):
        if hero_id == self.hero_id:
            return
        if hero_id in self.winning_matchup:
            self.winning_matchup[hero_id] += 1
        else:
            self.winning_matchup[hero_id] = 1

    def add_to_losing(self, hero_id):
        if hero_id == self.hero_id:
            return
        if hero_id in self.losing_matchup:
            self.losing_matchup[hero_id] += 1
        else:
            self.losing_matchup[hero_id] = 1

    # processes a new entry in the form of a match_synergy_data object
    def add_new_entry(self, data):
        if data.won == True:
            for hero in data.heroes:
                self.add_to_winning(hero)
        else:
            for hero in data.heroes:
                self.add_to_losing(hero)

    # calculates win rate of each hero pair, based on currently stored data
    def calc_win_rate(self):
        win_rates = {}
        for hero, wins in self.winning_matchup.iteritems():
            if hero in self.losing_matchup:
                win_rates[hero] = wins*100/(self.losing_matchup[hero]+wins)
            elif wins > 3: # 100 percent win rate, at least 3 games played of it
                win_rates[hero] = 100
        self.win_rates = sorted(win_rates.items(), key=operator.itemgetter(1), reverse = True)


# class, stores a list of hero ids, and a flag to indicate whether match was won or lost
class match_synergy_data:
    def __init__(self, player_won):
        self.won = player_won
        self.heroes = []

    def add_hero(self, hero_id):
        self.heroes.append(hero_id)


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
        self.fav_hero_image = None
        self.hero_matchup_image = {}
        self.hero_matchup_name = {}

    # processes a match_history object and records favourite hero, along with analysing playstyle
    def process_match_history(self, history):
        for match in history["matches"]:
            for player in match["players"]:
                if "account_id" not in player: # some players do not have account id displayed publically
                    continue
                if player["account_id"] == self.id: # if current player is our own player
                    hero = hero_stats[player["hero_id"]]
                    # increment hero frequency dictionary
                    if player["hero_id"] in self.hero_freq:
                        self.hero_freq[player["hero_id"]] += 1
                    else:
                        self.hero_freq[player["hero_id"]] = 1
                    # adds current hero data as a part of playstyle analysis
                    for (key, value) in hero.iteritems():
                        if key == "id" or key == 'localized_name':
                            continue
                        if key in ["spell_caster", "right_clicker", "support"]:
                            if value:
                                self.profiletype[key] += 1
                        else:
                            self.profile[key] += (value * 100) / float(hero_stat_total[key])

    # overall function to calculate favourite hero, playstyle breakdown, synergy
    def calculate_profile(self):
        match_history = api.get_match_history(account_id=self.id)
        self.num_matches = match_history["num_results"]
        self.process_match_history(match_history)

        while match_history["num_results"] != 0:
            match_history = api.get_match_history(account_id=self.id, start_at_match_id= match_history["matches"][-1]["match_id"]-1)
            self.process_match_history(match_history)
        self.hero_freq = sorted(self.hero_freq.items(), key=operator.itemgetter(1), reverse=True)
        self.fav_hero = self.hero_freq[0][0]
        self.profile = sorted(self.profile.items(), key=operator.itemgetter(1), reverse=True)
        self.fav_hero_matchup = hero_matchup(self.fav_hero)
        self.fav_hero_rate = (self.hero_freq[0][1]/5)
        print self.fav_hero_rate
        #self.calc_hero_synergy()

    # generates text based on player's playstyle analysis
    def generate_statement(self):
        self.calculate_profile()
        self.get_images()

        total = self.profiletype["right_clicker"] + self.profiletype["support"] + self.profiletype["spell_caster"]
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
            # case 2a carry
            if self.profiletype["spell_caster"] >= total/2:
                self.playertype = "Spell Caster/ Carry"
            # case 2b more utility/support
            elif self.profiletype["spell_caster"] + self.profiletype["support"] >= total*2/3:
                self.playertype = "Magical Damage/ Utility"
        # case 3
        else:
            if self.profiletype["support"] >= total/2:
                self.playertype = "Hard Support"
            elif self.profiletype["spell_caster"] + self.profiletype["support"] >= total*2/3:
                self.playertype = "Spell Casting Support"

        # if does not fit previous cases, conclude it to be an all rounded player
        if self.playertype=='':
            self.playertype = "Well Rounded Player"

        self.bg_image = profile_type_bg[self.playertype]
        self.playertype_desc = profile_type_template[self.playertype]
        self.playerdesc = "You favour heroes that can "+profile_desc_template[self.profile[0][0]]+ ", as well as ones" \
                                                    " that can " + profile_desc_template[self.profile[1][0]]
        for i in range(5):
            self.profile_type_stats.append((profile_stats[self.profile[i][0]], int(self.profile[i][1])/10))

    # calculates hero synergies
    def calc_hero_synergy(self):

        match_hist = type('D', (object,), api.get_match_history(account_id=73853498, hero_id = self.fav_hero))()
        for match in match_hist.matches:
            print "getting match detail"
            cur_match = type('D', (object,), api.get_match_details(match["match_id"]))()
            side = player_side(cur_match, self.id)
            if player_won(cur_match, side):
                new_synergy = match_synergy_data(True)
            else:
                new_synergy = match_synergy_data(False)
            for player in cur_match.players:
                    if player_side_basic(player) == side:
                        new_synergy.add_hero(player["hero_id"])
            self.fav_hero_matchup.add_new_entry(new_synergy)
        self.fav_hero_matchup.calc_win_rate()

    # gets the link for image files based on favourite heroes + synergy heroes
    def get_images(self):
        heroes = api.get_heroes()
        for hero in heroes['heroes']:
            if hero['id'] == self.fav_hero:
                self.fav_hero_image = hero['url_full_portrait']
                self.fav_hero_name = hero['localized_name']
                print self.fav_hero_image
                return
