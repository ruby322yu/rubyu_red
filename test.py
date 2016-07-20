from dota_analysis import *

player = player_data(api.get_player_summaries(73853498), 73853498)
player.generate_statement()