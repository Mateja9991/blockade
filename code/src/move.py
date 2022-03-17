from functools import partial
from src.constants.move import directions, moves_by_val, moves_by_dir, exc_moves_by_dir, exc_moves_by_val, wall_dir_check
from re import fullmatch, split
from src.constants.pieces import X, O, empty
from copy import deepcopy, copy
from src.board import square
from itertools import chain
from src.view.board import create_board_view, draw_board
import ujson
import time

def play_best_move(board, player, players):
    play_move(board, find_best_move(board, player, players), player)

def find_best_move(board, player, players, homes):
    import time
    before = time.time()
    start_state = {'board': board, 'players': players, 'homes': homes, 'move': '' }
    depth = 6 - ((player['green_walls'] + player['blue_walls']) * 2 + 1)
    if depth < 1:
        depth = 1
    print(f'Depth is {depth}')
    state, eval, move =  minimax(start_state, depth, player, None, (start_state, -100000, None), (start_state,  100000, None))
    print('time is: ', time.time() - before)
    return move

def move_pawn(board, move, player):
    pass
def copy_board_ujson(old_board, current_pos, move, next):
    board = copy(old_board)
    board[current_pos[0]] = copy(board[current_pos[0]])
    board[current_pos[0]][current_pos[1]] =  ujson.loads(ujson.dumps(board[current_pos[0]][current_pos[1]]))
    board[move['pawn_position'][0]] = copy(board[move['pawn_position'][0]])
    board[move['pawn_position'][0]][move['pawn_position'][1]] = \
        ujson.loads(ujson.dumps( board[move['pawn_position'][0]][move['pawn_position'][1]]))
    if 'wall_direction' in move:
        board[move['wall_position'][0]] = copy(board[move['wall_position'][0]])
        board[move['wall_position'][0]][move['wall_position'][1]] = \
            ujson.loads(ujson.dumps((board[move['wall_position'][0]][move['wall_position'][1]])))
        board[move['wall_position'][0] + next[0]] = copy(board[move['wall_position'][0] + next[0]])
        board[move['wall_position'][0] + next[0]][move['wall_position'][1] + next[1]] = \
            ujson.loads(ujson.dumps((board[move['wall_position'][0] + next[0]][move['wall_position'][1] + next[1]])))
        board[move['wall_position'][0] + move['wall_direction'][0]] = copy(board[move['wall_position'][0] + move['wall_direction'][0]])
        board[move['wall_position'][0] + move['wall_direction'][0]][move['wall_position'][1] + move['wall_direction'][1]] = \
            ujson.loads(ujson.dumps((board[move['wall_position'][0] + move['wall_direction'][0]][move['wall_position'][1] + move['wall_direction'][1]])))
        board[move['wall_position'][0] + move['wall_direction'][0] + next[0]] = copy(board[move['wall_position'][0] + move['wall_direction'][0] + next[0]])
        board[move['wall_position'][0] + move['wall_direction'][0] + next[0]][move['wall_position'][1] + move['wall_direction'][1] + next[1]]= \
            ujson.loads(ujson.dumps((board[move['wall_position'][0] + move['wall_direction'][0] + next[0]][move['wall_position'][1] + move['wall_direction'][1] + next[1]])))
    return board

def play_move(old_board, move, player):
#
    current_pos = player[move['pawn_symbol'][1]]
    if 'wall_direction' in move:
        key, opposite, next = ('S', 'N', (1, 0)) if move['wall_direction'][1] == 1 else ('E', 'W', (0, 1))
    else:
        next = None
    board = copy_board_ujson(old_board, current_pos, move, next)
    player = deepcopy(player)
    board[current_pos[0]][current_pos[1]]['piece'] = empty
    board[move['pawn_position'][0]][move['pawn_position'][1]]['piece'] = move['pawn_symbol'][0]
    player[move['pawn_symbol'][1]] = (move['pawn_position'][0], move['pawn_position'][1])
    if 'wall_direction' in move:
        board[move['wall_position'][0]][move['wall_position'][1]][key] = True
        board[move['wall_position'][0] + next[0]][move['wall_position'][1] + next[1]][opposite] = True
        board[move['wall_position'][0] + move['wall_direction'][0]][move['wall_position'][1] + move['wall_direction'][1]][key] = True
        board[move['wall_position'][0] + move['wall_direction'][0] + next[0]][move['wall_position'][1] + move['wall_direction'][1] + next[1]][opposite] = True
        if move['wall_direction'][1] == 1:
            player['green_walls'] -= 1
        else:
            player['blue_walls'] -= 1
    return [ board, player ]

def is_move_valid(board, str_move, player, players, homes):
    if not is_move_syntax_valid(str_move):
        return False
    move = parse_move(str_move)
    if is_move_logic_valid(board, move, player, players, homes):
        return True
    return False
def parse_move(str_move):
    move_arr = str_move.replace('[', '').replace(']', '').split(' ')
    move = { 
        'pawn_symbol': ''.join(move_arr[:2]),
        'pawn_position':  (int(move_arr[2], 16), int(move_arr[3], 16))
    }
    if len(move_arr) > 4:
        move['wall_direction'] = (0, 1) if move_arr[4] == 'Z' else (1, 0)
        move['wall_position'] =  (int(move_arr[5], 16), int(move_arr[6], 16))
    return move

def is_move_syntax_valid(str_move):
    if str_move == None:
        return False
    if not fullmatch("\[[XO] [12]] \[[0-9A-F] [0-9A-F]]( \[[ZP] [0-9A-F] [0-9A-F]])?", str_move):
        return False
    return True

def is_move_logic_valid(board, move, player, players, homes):
    if not move['pawn_symbol'][0] == player['symbol']:
        return False
    if 'wall_direction' in move:
        if not is_move_wall_valid(board, move, player):
            return False
    else: 
        if player['blue_walls'] or player['green_walls']:
            return False
    if not is_move_pawn_valid(board, move, player):
        return False
    current_board, current_player = play_move(board, move, player,)
    players = deepcopy(players)
    players[current_player['symbol']] = current_player
    if home_squares_blocked(current_board, players, homes):
        return False
    return True

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

def home_squares_blocked2(board, players, homes):
    return False

def is_move_pawn_valid(board, move, player):
    opponent = X if player['symbol'] == O else O
    if move['pawn_position'][0] >= len(board) or move['pawn_position'][0] < 0 \
    or move['pawn_position'][1] >= len(board[0]) or move['pawn_position'][1] < 0:
        return False
    if not board[move['pawn_position'][0]][move['pawn_position'][1]]['piece'] == ' ' and not\
         board[move['pawn_position'][0]][move['pawn_position'][1]]['home_to'] == opponent:
        return False
    current_position = player[move['pawn_symbol'][1]]
    squares_by_row =move['pawn_position'][0] -  current_position[0]
    row_dir = sign(squares_by_row) 
    squares_by_column = move['pawn_position'][1] - current_position[1]
    column_dir = sign(squares_by_column)
    if abs(squares_by_row) + abs(squares_by_column) > 2:
        return False
    exc = False
    if abs(squares_by_row) + abs(squares_by_column) == 1:
        if not board[move['pawn_position'][0]][move['pawn_position'][1]]['home_to'] == opponent and\
            (move['pawn_position'][0] + row_dir >= len(board) or move['pawn_position'][1] + column_dir >= len(board[0]) or\
            board[move['pawn_position'][0] + row_dir][move['pawn_position'][1] + column_dir]['piece'] == empty):
            return False
        exc = True
    key =str(row_dir) + str(column_dir)
    is_path_found = False
    moves_dict = moves_by_val if not exc else exc_moves_by_val
    for ind, wall_border in enumerate(wall_dir_check[key]):
        mv = moves_dict[key][ind]
        try:
            if not board[current_position[0] + mv[0][0]][current_position[1] +  mv[0][1]][wall_border[0]] \
            and not board[current_position[0] + mv[0][0] +  mv[1][0]][current_position[1] + mv[0][1] + mv[1][1]][wall_border[1]]:
                is_path_found = True
        except IndexError:
            pass
    if not is_path_found:
        return False
    return True


def is_move_wall_valid(board, move, player):
    if move['wall_position'][0] >= len(board) or move['wall_position'][0] < 0 \
    or move['wall_position'][1] >= len(board[0]) or move['wall_position'][1] < 0:
        return False
    if move['wall_position'][0] + move['wall_direction'][0] >= len(board) \
    or move['wall_position'][1] + move['wall_direction'][1] >= len(board[0]):
        return False
    if move['wall_position']:
        if (move['wall_direction'][1] and player['green_walls'] == 0) or \
            (move['wall_direction'][0] and player['blue_walls'] == 0):
            return False

    if move['wall_direction'][0]:
        if board[move['wall_position'][0]][move['wall_position'][1]]['E'] or board[move['wall_position'][0] + move['wall_direction'][0]][move['wall_position'][1]]['E']:
            return False
    else:
        if board[move['wall_position'][0]][move['wall_position'][1]]['S'] or board[move['wall_position'][0]][move['wall_position'][1] + move['wall_direction'][1]]['S']:
            return False
    return True

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0     

def is_game_over(players, homes):
    if (players['X']['1'][0] == homes['sp_home1'][0] and  players['X']['1'][1] == homes['sp_home1'][1]) or\
        (players['X']['1'][0] == homes['sp_home2'][0] and  players['X']['1'][1] == homes['sp_home2'][1]) or\
        (players['X']['2'][0] == homes['sp_home1'][0] and  players['X']['2'][1] == homes['sp_home1'][1]) or\
        (players['X']['2'][0] == homes['sp_home2'][0] and  players['X']['2'][1] == homes['sp_home2'][1]):
        # print('X IS THE WINNER')
        return (True, X)
    elif (players['O']['1'][0] == homes['fp_home1'][0] and  players['O']['1'][1] == homes['fp_home1'][1]) or\
        (players['O']['1'][0] == homes['fp_home2'][0] and  players['O']['1'][1] == homes['fp_home2'][1]) or\
        (players['O']['2'][0] == homes['fp_home1'][0] and  players['O']['2'][1] == homes['fp_home1'][1]) or\
        (players['O']['2'][0] == homes['fp_home2'][0] and  players['O']['2'][1] == homes['fp_home2'][1]):
        # print('O IS THE WINNER')
        return (True, O)
    return (False, None)

def is_blocked_by_player(board, pawn, comb):
    row_offset = comb[0][0] + comb[1][0] if len(comb) > 1 else 0
    col_offset = comb[0][1] + comb[1][1] if len(comb) > 1 else 0
    if (pawn[0] + row_offset >= len(board) or pawn[1] + col_offset >= len(board[0])):
        return False
    if board[pawn[0] + row_offset][pawn[1] + col_offset]['piece'] != empty:
        return True
    return False
    
def get_state(board, move, players, player, homes):
    new_board, new_player = play_move(board, move, player)
    new_players = deepcopy(players)
    new_players[new_player['symbol']] = new_player
    return {
        'board': new_board,
        'players': new_players,
        'homes': homes
    }
# [x 1] [8 3] [z 5 5]
def next_states(current_state, player):
    board = current_state['board']
    players = current_state['players']
    homes = current_state['homes']

    return chain(get_player_states(board, player, '1', players, homes),\
                 get_player_states(board, player, '2', players, homes))

def chain2(gen1, gen2):
    yield from gen1
    yield from gen2

def is_home_square(board, pawn, direction, symbol):
    dir_comb = {
        'N': (-1, 0),
        'S': (1, 0),
        'W': (0, -1),
        'E': (0, 1),
    }
    comb =  dir_comb[direction]
    row_offset = comb[0]
    col_offset = comb[1]
    if (pawn[0] + row_offset >= len(board) or pawn[1] + col_offset >= len(board[0])):
        return False
    if board[pawn[0] + row_offset][pawn[1] + col_offset]['home_to'] == (X if symbol == O else O):
        return True
    return False

def get_pawn_moves(board, player, pawn):
    exc_dir = {}
    dir = {}
    for direction in directions:         #list -> list -> tuple
        combinations = deepcopy(moves_by_dir[direction])
        for pawn_combination in combinations:
            if direction in dir:
                continue
            if direction in ['S', 'N', 'W', 'E'] and not direction in exc_dir and\
                (is_blocked_by_player(board, player[pawn], pawn_combination) or \
                 is_home_square(board, player[pawn], direction,player['symbol'])):
                exc_dir[direction] = True
                combinations.append(exc_moves_by_dir[direction])
            pawn_move_str = f"[{player['symbol']} {pawn}] [{hex(player[pawn][0] + pawn_combination[0][0] + pawn_combination[1][0])} {hex(player[pawn][1] + pawn_combination[0][1] + pawn_combination[1][1])}]"
            p_pawn_move  = parse_move(pawn_move_str)
            if is_move_pawn_valid(board, p_pawn_move, player):
                if direction in ['SW','NW','SE','NE']:
                    dir[direction] = True
                yield (p_pawn_move, pawn_move_str)

def is_wall_connected(board, move,player):
    directions = { 'S', 'N', 'W', 'E' }
    dirs = ['W', 'E', 'E'] if move['wall_direction'][1] else ['N', 'S', 'S'] 
    dirs += dirs
    dirs += [ 'S' ] * 2 if move['wall_direction'][1] else [ 'E' ] * 2
    i= move['wall_position'][0]
    i_incr = int(not move['wall_direction'][0])
    j_incr = int(not move['wall_direction'][1])
    j = move['wall_position'][1]
    i2 = move['wall_position'][0] + move['wall_direction'][0]
    j2 = move['wall_position'][1] + move['wall_direction'][1]
    indexes = [
        (i,j,0), (i,j,1), (i2, j2,2), 
        (i + i_incr, j + j_incr,0), (i + i_incr, j + j_incr,1), (i2 + i_incr, j2 + j_incr,2),
        (i - move['wall_direction'][0], j -move['wall_direction'][1],0),
        (i2 + move['wall_direction'][0], j2 + move['wall_direction'][1],2)
    ]
    count = 0
    found = {}
    for num, (i, j, point) in enumerate(indexes):
        try:
            if not point in found and board[i][j][dirs[num]]:
                count += 1
                if count == 2:
                    return True
                else:
                    found[point] = True
        except IndexError:
            pass
    return False

def get_player_states(board, player, pawn, players, homes):
    # pre_move_eval = evaluate_state(players, homes, board)
    for pawn_move, pawn_move_str in get_pawn_moves(board, player, pawn):
        if (player['green_walls'] > 0 or player['blue_walls'] > 0):
            start_i, end_i = (homes['fp_home1'][0], homes['fp_home2'][0]) 
            if start_i > 2:
                start_i -= 1
            if end_i < len(board) - 2:
                end_i += 1
            start_j, end_j  = (homes['fp_home1'][1], homes['sp_home1'][1])
            if start_j > 2:
                start_j -= 1
            if end_j < len(board[0]) - 2:
                end_j += 1
            for i in range(start_i, end_i):
                for j in range(start_j, end_j):
            # for i in range(len(board) - 1):
            #     for j in range(len(board[0]) - 1):
                    if player['blue_walls'] > 0:
                        p_pawn_move  = parse_move(pawn_move_str + f" [P {hex(i)} {hex(j)}]")
                        if is_move_wall_valid(board, p_pawn_move, player):                
                            curr_state = get_state(board, p_pawn_move, players, player, homes) 
                            # current_eval = evaluate_state(curr_state['players'], curr_state['homes'], curr_state['board'])
                            # if player['symbol'] == 'X' and (pre_move_eval <= current_eval) \
                            #     or pre_move_eval >= current_eval:
                            if not is_wall_connected(board, p_pawn_move, player) or \
                            not home_squares_blocked(curr_state['board'], curr_state['players'], curr_state['homes']):
                                yield (curr_state, p_pawn_move)
                    if player['green_walls'] > 0:
                        z_pawn_move  = parse_move(pawn_move_str + f" [Z {hex(i)} {hex(j)}]")
                        if is_move_wall_valid(board, z_pawn_move, player):                
                            curr_state = get_state(board, z_pawn_move, players, player, homes) 
                            # current_eval = evaluate_state(curr_state['players'], curr_state['homes'], curr_state['board'])
                            # if player['symbol'] == 'X' and (pre_move_eval <= current_eval) \
                            #     or pre_move_eval >= current_eval:
                            if not is_wall_connected(board, z_pawn_move, player) or \
                            not home_squares_blocked(curr_state['board'], curr_state['players'], curr_state['homes']):
                                yield (curr_state, z_pawn_move)
        else:
            curr_state = get_state(board, pawn_move, players, player, homes) 
            yield (curr_state, pawn_move)
              
def minimax(current_state, depth, player, start_move = None, alpha=(0,-1000, None), beta=(0,1000, None)):
    board = current_state['board']
    players = current_state['players']
    next_player = players[X if player['symbol'] == O else O]
    homes = current_state['homes']
    game_over, winner = is_game_over(players, homes)
    if depth == 0 or game_over:
        return (current_state, \
                evaluate_state(players, homes, board, game_over, winner), \
                start_move)
    if player['symbol'] == X:
        maxEval = (0,-100000,0)
        for next_state, move in next_states(current_state, player):
            ret_state, current_eval, sm = minimax(next_state, depth - 1, next_player,  \
                move if start_move == None else start_move, alpha, beta)
            maxEval = maxEval if maxEval[1] > current_eval else (ret_state, current_eval, sm)
            alpha = alpha if alpha[1] > current_eval else (ret_state, current_eval, sm)
            if beta[1] <= alpha[1]:
                break
        return maxEval
    else:
        minEval = (0,100000,0)
        for next_state, move in next_states(current_state, player):
            ret_state, current_eval, sm = minimax(next_state, depth - 1, next_player, \
                move if start_move == None else start_move, alpha, beta)
            minEval = minEval if minEval[1] <= current_eval else (ret_state, current_eval, sm)
            beta = beta if beta[1] < current_eval else (ret_state, current_eval, sm)
            if beta[1] <= alpha[1]:
                break
        return minEval

def find_path(board, end_pos, player, pawn):
    prev = {}
    g = {}
    f = {}
    boards = {}
    moves = {}
    players = {}
    def save_move(move_str, last_move, new_board, new_player, new_move, new_g):
        g[move_str] = new_g
        f[move_str] = new_g + (get_manhattan_distance(move_str['pawn_position'], end_pos) if new_g != 0 else 0)
        prev[move_str] = last_move
        boards[move_str] = new_board
        moves[move_str] = new_move
        players[move_str] = new_player
    # board = deepcopy(board)
    
    open_set = set()
    closed_set = set()
    start_move_str = f"[{player['symbol']} {pawn}] [{hex(player[pawn][0])} {hex(player[pawn][1])}]"
    start_move = parse_move(start_move_str)
    if start_move['pawn_position'] == end_pos:
        return True
    open_set.add(start_move_str)
    g[start_move_str] = 0
    f[start_move_str] = 0
    prev[start_move_str] = None
    boards[start_move_str] = board
    players[start_move_str] = player
    moves[start_move_str] = start_move 
    found_end = False   
    while len(open_set) and not found_end:
        move_str = ''
        for next_move_str in open_set:
            current_h = get_manhattan_distance(moves[next_move_str]['pawn_position'], end_pos)
            if move_str != '':
                move_h = get_manhattan_distance(moves[move_str]['pawn_position'], end_pos)
            else:
                move_h = 0
            if move_str == '' or g[next_move_str] +  current_h < g[move_str] + move_h:
                move_str = next_move_str
                if moves[move_str]['pawn_position'] == end_pos:
                    return True
        curr_move = moves[move_str]
        curr_board = boards[move_str]
        curr_player = players[move_str]
        new_board, new_player = play_move(curr_board, curr_move, curr_player)
        move_list = list(get_pawn_moves(new_board, new_player, pawn))
        for next_move, next_move_str in move_list:
            if next_move_str not in open_set and next_move_str not in closed_set:
                # if not is_move_pawn_valid(new_board, next_move, new_player):
                #     continue
                boards[next_move_str] = new_board
                players[next_move_str] = new_player
                moves[next_move_str] = next_move
                open_set.add(next_move_str)
                prev[next_move_str] = move_str
                g[next_move_str] = g[move_str] + 1
            else:
                if g[next_move_str] > g[move_str] + 1:
                    g[next_move_str] = g[move_str] + 1
                    prev[next_move_str] = move_str
                    if next_move_str in closed_set:
                        closed_set.remove(next_move_str)
                        open_set.add(next_move_str)
        open_set.remove(move_str)
        closed_set.add(move_str)
    #last_move = f"[{player['symbol']} {pawn}] [{hex(end_pos[0])} {hex(end_pos[1])}]"
    return False

def get_manhattan_distance(first_pos, second_pos):
    return abs(first_pos[0] - second_pos[0]) + abs(first_pos[1] - second_pos[1])

def evaluate_state(players, homes, board, game_over=False, winner=None):
    if game_over:
        return 10000 if winner == X else -10000
    point = 1
    eval_value = 0
    sp_home_1 = homes['sp_home1']
    sp_home_2 = homes['sp_home2']
    fp_home_1 = homes['fp_home1']
    fp_home_2 = homes['fp_home2']
    x1_pos = players['X']['1']
    x2_pos = players['X']['2']
    o1_pos = players['O']['1']
    o2_pos = players['O']['2']
    distfp11 = get_manhattan_distance(x1_pos, sp_home_1)
    distfp12 = get_manhattan_distance(x1_pos, sp_home_2)
    distfp21 = get_manhattan_distance(x2_pos, sp_home_1)
    distfp22 = get_manhattan_distance(x2_pos, sp_home_2)
    distsp11 = get_manhattan_distance(o1_pos, fp_home_1)
    distsp12 = get_manhattan_distance(o1_pos, fp_home_2)
    distsp21 = get_manhattan_distance(o2_pos, fp_home_1)
    distsp22 = get_manhattan_distance(o2_pos, fp_home_2)
    eval= distsp11 + distsp12 + distsp21 + distsp22 - distfp11 - distfp12 - distfp21 - distfp22
    eval -= distfp11 if distfp11 < distfp12 else distfp12
    eval -= distfp21 if distfp21 < distfp22 else distfp22
    eval += distsp11 if distsp11 < distsp12 else distsp12
    eval += distsp21 if distsp21 < distsp22 else distsp22
    def create_box(pawn_pos, home_pos, incr):
        home_pos_i, home_pos_j = home_pos
        pawn_pos_i, pawn_pos_j = pawn_pos
        start_i, end_i = (home_pos_i, pawn_pos_i) \
                                    if home_pos_i < pawn_pos_i else \
                                        (pawn_pos_i, home_pos_i)
        start_j, end_j = (home_pos_j, pawn_pos_j) \
                                    if home_pos_j < pawn_pos_j else \
                                        (pawn_pos_j, home_pos_j)
        return (start_i, end_i, start_j, end_j, incr)
    x1_sp1_box = create_box(x1_pos, sp_home_1, -1)
    x1_sp2_box = create_box(x1_pos, sp_home_2, -1)
    x2_sp1_box = create_box(x2_pos, sp_home_1, -1)
    x2_sp2_box = create_box(x2_pos, sp_home_2, -1)
    o1_fp1_box = create_box(o1_pos, fp_home_1, 1)
    o1_fp2_box = create_box(o1_pos, fp_home_2, 1)
    o2_fp1_box = create_box(o2_pos, fp_home_1, 1)
    o2_fp2_box = create_box(o2_pos, fp_home_2, 1)
    boxes = [x1_sp1_box, x1_sp2_box, x2_sp1_box, x2_sp2_box,
                o1_fp1_box, o1_fp2_box, o2_fp1_box, o2_fp2_box]
    checked_dict = {}
    def floodfill(board, i, j, checked, direction, current_len, box_check):
        if f'{i}:{j}:{direction}' in checked:
            return (current_len, checked)
        if not board[i][j][direction]:
            return (current_len, checked)
        if not box_check(i, j):
            return (current_len, checked)
        next_hop = {
            'N': [ (i, j - 1, 'N'), (i, j + 1, 'N'), 
                    (i - 1, j - 1, 'W'), (i - 1, j + 1, 'E'),
                     ],
            'S':[ (i, j - 1, 'S'), (i, j + 1, 'S'),
                    (i + 1, j - 1, 'W'), (i + 1, j + 1, 'E'), ],
            'W':[ (i - 1, j, 'W'), (i + 1, j, 'W'), 
                    (i - 1, j + 1, 'S'), (i + 1, j + 1, 'N') ],
            'E': [ (i - 1, j, 'E'), (i + 1, j, 'E'),
                    (i - 1, j - 1, 'S'), (i + 1, j - 1, 'N') ]
        }
        checked[f'{i}:{j}:{direction}'] = True
        best = (current_len, checked)
        for new_i, new_j, dir_to_check in next_hop[direction]:
            if new_i > 0 and new_j > 0 and new_i < len(board) and new_j < len(board[0]):
                result = floodfill(board, new_i, new_j, checked, dir_to_check, current_len + 1, box_check)
                if current_len == 1:
                    best = (best[0] + result[0], result[1])
                else:
                    best = best if best[0] > result[0] else result
        return best
    def box_check(box_pos, i, j):
        start_i, end_i, start_j, end_j = box_pos
        if i < start_i or i > end_i or j < start_j or j > end_j:
            return False
        return True
    for start_i, end_i, start_j, end_j, incr in boxes:
        checked_dict = {}
        # current_box_check = partial(box_check, (start_i, end_i, start_j, end_j))
        for i in range(start_i, end_i + 1):
            for j in range(start_j, end_j + 1):
                directions = []
                if i != start_i and i != end_i:
                    directions += [ 'S', 'N' ] 
                if j != start_j and j != end_j:
                    directions += [ 'W', 'E' ]

                for  direction in directions:
                    #if f'{i}:{j}:{direction}' and \
                    if board[i][j][direction]:
                        #  and f'{i}:{j}:{direction}' not in checked_dict:
                        # length, new_checked = floodfill(board, i, j, {}, direction, 1, current_box_check)
                        # for key in new_checked:
                        #     checked_dict[key] = True
                        # eval += incr * (length ** 2)
                        eval += incr
    return eval
def max(state):
    pass

def min(state):
    pass

# def home_squares_blocked(board, homes, players):
#     pass
