def player_won(match, player_on_rad):
    radiant_won = match.radiant_win
    if (player_on_rad and radiant_won) or (not player_on_rad and not radiant_won):
        return True
    return False


def player_side(match, player_id):
    for player in match.players:
        if player["account_id"] == player_id:
            if player["player_slot"] < 128:  # radiant player
                return True
            else:
                return False


def player_side_basic(player):
    if player["player_slot"] < 128:
        return True
    return False


def player_hero(match, player_id):
    for player in match.players:
        if player["account_id"] == player_id:
            return player["hero_id"]
