from src.constants.pieces import X, O

def get_player(symbol, pawn_1_pos, pawn_2_pos, green_walls, blue_walls):
    return {
        'symbol': symbol,
        '1': pawn_1_pos,
        '2': pawn_2_pos,
        'green_walls': green_walls,
        'blue_walls': blue_walls
    }


def init_players(config_obj):
    players = {}
    if config_obj['first_player'] == 'Computer':
        human_player = get_player(O, config_obj['player2']['home1'], config_obj['player2']['home2'], config_obj['green_walls'], config_obj['blue_walls'])
        computer = get_player(X, config_obj['player1']['home1'], config_obj['player1']['home2'], config_obj['green_walls'], config_obj['blue_walls'])
        players[X] = computer
        players[O] = human_player
    else:
        human_player = get_player(X, config_obj['player1']['home1'], config_obj['player1']['home2'], config_obj['green_walls'], config_obj['blue_walls'])
        computer = get_player(O, config_obj['player2']['home1'], config_obj['player2']['home2'], config_obj['green_walls'], config_obj['blue_walls'])
        players[O] = computer
        players[X] = human_player
    return [ players, human_player, computer]