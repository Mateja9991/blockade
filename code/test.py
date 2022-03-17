from copy import deepcopy
from src.move import find_best_move
from utils.wrappers import Dotdict
from src.move import parse_move, is_blocked_by_player, play_move, get_player_states, next_states,\
     is_move_pawn_valid, is_move_wall_valid, find_path, find_path_2, evaluate_state,\
     is_game_over, minimax, get_state, find_best_move
from src.constants.move import moves_by_dir, exc_moves_by_dir, directions
from itertools import chain
from src.board import init_board
from src.constants.config import get_default_config
from src.player import init_players
from src.constants.pieces import X, O
conf = get_default_config()
players, human, computer = init_players(conf)
#computer = {'symbol': 'O', '1': (5, 3), '2': (3, 7), 'green_walls': 7, 'blue_walls': 7} 
#human = {'symbol': 'X', '1': (6, 3), '2': (10, 7), 'green_walls': 7, 'blue_walls': 7}
#players = {  'O': computer, 'X': human, }
#players = players
#human = human
#computer = computer
homes = {
        'fp_home1': conf['player1']['home1'],
        'fp_home2': conf['player1']['home2'],
        'sp_home1': conf['player2']['home1'],
        'sp_home2': conf['player2']['home2'],
    }
import multiprocessing
import time
start_board = init_board(conf)
start_state = {
    'board': start_board,
    'players': players,
    'homes': homes
}
from itertools import repeat
def home_squares_blocked(board, players, homes):
    if  not find_path(board, homes['sp_home1'], players['X'], '1') or \
        not find_path(board, homes['sp_home2'], players['X'], '1') or \
        not find_path(board, homes['sp_home1'], players['X'], '2') or \
        not find_path(board, homes['sp_home2'], players['X'], '2') or \
        not find_path(board, homes['fp_home1'], players['O'], '1') or \
        not find_path(board, homes['fp_home2'], players['O'], '1') or \
        not find_path(board, homes['fp_home1'], players['O'], '2') or \
        not find_path(board, homes['fp_home2'], players['O'], '2'):
        return True
    return False
def home_squares_blocked_2(board, players, homes):
    if  not find_path_2(board, homes['sp_home1'], players['X'], '1') or \
        not find_path_2(board, homes['sp_home2'], players['X'], '1') or \
        not find_path_2(board, homes['sp_home1'], players['X'], '2') or \
        not find_path_2(board, homes['sp_home2'], players['X'], '2') or \
        not find_path_2(board, homes['fp_home1'], players['O'], '1') or \
        not find_path_2(board, homes['fp_home2'], players['O'], '1') or \
        not find_path_2(board, homes['fp_home1'], players['O'], '2') or \
        not find_path_2(board, homes['fp_home2'], players['O'], '2'):
        return True
    return False

if __name__ == '__main__':
    before = time.time()
    home_squares_blocked(start_board, players, homes)
    print('time is:  ', time.time() - before)
    before = time.time()
    home_squares_blocked_2(start_board, players, homes)
    print('time is:  ', time.time() - before)



quit()
