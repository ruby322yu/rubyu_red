from dota_analysis import *

account_id =  44272179
player = player_data(api.get_player_summaries(account_id), account_id)
player.generate_statement()