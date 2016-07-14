import dota2api
import operator
api = dota2api.Initialise("10EB43DE283098AEBC83B0054CFA2A34")

class all_hero_matchup:
    def __init__(self, id):
        self.player_id = id
        self.hero_matchups = {}

    def update_matchup(self, hero_id, result):
        if hero_id not in self.hero_matchups:
            self.hero_matchups[hero_id] = hero_matchup(hero_id)
            print "adding new hero with id", hero_id
        self.hero_matchups[hero_id].add_new_entry(result)

    def print_all_matchups(self):
        for hero in self.hero_matchups:
            print "for hero id:", self.hero_matchups[hero].hero_id
            #self.hero_matchups[hero].print_result()
            print self.hero_matchups[hero].winning_matchup


class hero_matchup:
    def __init__(self, id):
        self.hero_id = id
        self.winning_matchup = {}
        self.losing_matchup = {}

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

    def add_new_entry(self, data):
        if data.won == True:
            for hero in data.heroes:
                self.add_to_winning(hero)
        else:
            for hero in data.heroes:
                self.add_to_losing(hero)

    def print_result(self):
        sorted_winning = sorted(self.winning_matchup.items(), key=operator.itemgetter(1), reverse=True)
        #sorted_losing = sorted(self.losing_matchup(), key=operator.itemgetter(1), reverse=True)
        if len(sorted_winning)>3:
            for i in range(3):
                print sorted_winning[i]

class match_synergy_data:
    def __init__(self, player_won):
        self.won = player_won
        self.heroes = []

    def add_hero(self, hero_id):
        self.heroes.append(hero_id)

def player_won(match, player_id):
    radiant_won = match.radiant_win
    side = player_side(match, player_id)
    if side=="radiant" and radiant_won or side=="dire" and not radiant_won:
        return True
    return False

def player_side(match, player_id):
    for player in match.players:
        if player["account_id"] == player_id:
#               print player["player_slot"]
            if player["player_slot"] < 128:  # radiant player
                return "radiant"
            else:
                return "dire"

def player_side_basic(player):
    if player["player_slot"] < 128:
        return "radiant"
    return "dire"


def player_hero(match, player_id):
    for player in match.players:
        if player["account_id"] == player_id:
            return player["hero_id"]

args = {"account_id":73853498, "matches_requested":500}
hist = type('D', (object,), api.get_match_history(account_id=73853498))()

print len(hist.matches)
match = type('D', (object,), api.get_match_details(2478972693))()
print player_won(match, 73853498)


#print api.get_match_details(hist["matches"][0]["match_id"])
#print api.get_match_details(hist.matches[0].match_id)

def calc_hero_synergy(match_hist,player_id):
    result = all_hero_matchup(player_id)
    i = 0
    for match in match_hist.matches:
        print ("match count:", i)
        cur_match = type('D', (object,),api.get_match_details(match["match_id"]))()
        side = player_side(cur_match,player_id)
        if player_won(cur_match,player_id):
            new_synergy = match_synergy_data(True)
            for player in cur_match.players:
                if player_side_basic(player) == side:
                    new_synergy.add_hero(player["hero_id"])

        else:
            new_synergy = match_synergy_data(False)
            for player in cur_match.players:
                if not player_side(cur_match, player["account_id"]) == side:
                    new_synergy.add_hero(player["hero_id"])
        print len(new_synergy.heroes)
        result.update_matchup(player_hero(cur_match, player_id), new_synergy)
        i += 1
    return result

synergies = calc_hero_synergy(hist, 73853498)
synergies.print_all_matchups()











