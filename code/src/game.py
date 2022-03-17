from src.board import init_board
from src.view.board import draw_board
from src.move import find_best_move, is_move_valid, is_move_logic_valid, parse_move, play_move, play_best_move, next_states, is_game_over
from src.player import get_player, init_players
from src.constants.pieces import X, O
from src.constants.config import get_default_config

def init_game(config_obj):
    board = init_board(config_obj)
    play_blockade(board, config_obj)

def is_confirmed(answer):
    return answer.strip().lower() in ('da', 'yes', 'y')

def config():
    if not is_confirmed(input('Da li zelite da koristite default konfiguraciju?  ')):
        n = int(input("Unesite broj vrsta.  "))
        m = int(input("Unesite broj kolona.  "))
        gw = int(input("Unesite broj zelenih zidova.  "))
        bw = int(input("Unesite broj plavih zidova.  "))
        x1_x = int(input("Unesite poziciju x za x1.  "))
        x1_y = int(input("Unesite poziciju y za x1.  "))
        x2_x = int(input("Unesite poziciju x za x2.  "))
        x2_y = int(input("Unesite poziciju y za x2.  "))
        o1_x = int(input("Unesite poziciju x za o1.  "))
        o1_y = int(input("Unesite poziciju y za o1.  "))
        o2_x = int(input("Unesite poziciju x za o2.  "))
        o2_y = int(input("Unesite poziciju y za o2.  "))
        config_obj = get_default_config(n, m, gw, bw, x1_x, x1_y, \
            x2_x, x2_y, o1_x, o1_y, o2_x, o2_y)
    else:
        config_obj = get_default_config()
    config_obj['first_player'] = 'Human' if is_confirmed(input("Da li zelite da igrate prvi?  ")) else 'Computer' 
    init_game(config_obj)

def play_blockade(board, config_obj):
    homes = {
        'fp_home1': config_obj['player1']['home1'],
        'fp_home2': config_obj['player1']['home2'],
        'sp_home1': config_obj['player2']['home1'],
        'sp_home2': config_obj['player2']['home2'],
    }
    players, human_player, computer = init_players(config_obj)
    def human_move(board, players, homes, human_player):
        move = input("Play Move: ").upper()
        while not is_move_valid(board, move, human_player, players, homes):
            move = input("Replay Move: ").upper()
        board, human_player = play_move(board, parse_move(move), human_player)
        players[human_player['symbol']] = human_player
        return board, players, human_player
    def computer_move(board, players, homes, computer):
        print('Computer thinking...')
        move = find_best_move(board, computer, players, homes)
        board, computer = play_move(board, move, computer)
        players[computer['symbol']] = computer
        return board, players, computer
    fp = human_player if human_player['symbol'] == X else computer
    sp = human_player if human_player['symbol'] == O else computer
    fp_play = human_move if human_player['symbol'] == X else computer_move
    sp_play = human_move if human_player['symbol'] == O else computer_move
    draw_board(board)
    game_over, winner = is_game_over(players, homes)
    while not game_over:
        board, players, fp = fp_play(board, players, homes, fp)
        draw_board(board)
        game_over, winner = is_game_over(players, homes)
        if game_over:
            break
        board, players, sp = sp_play(board, players, homes, sp)
        draw_board(board)
        game_over, winner = is_game_over(players, homes)
    print(f'{winner} is the winner!!!')

if __name__ == '__main__':
    config()
    