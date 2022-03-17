# borders = ['S', 'N', 'W', 'E']
from src.constants.pieces import X, O, empty
from copy import deepcopy
def square(piece, row, column, borders={}):
    return {
        'piece': piece,
        'row': row,
        'column': column,
        'S': borders.get('S', False),
        'N': borders.get('N', False),
        'W': borders.get('W', False),
        'E': borders.get('E', False),
        'home_to': piece if piece in (X, O) else None
    }

def init_board(config):
    rows = config['n']
    columns = config['m']
    board = [[ 0 for i in range(columns) ] for j in range(rows)]
    for i in range(rows):
        for j in range(columns):
            board[i][j] = square(empty, i, j)
    board[config['player1']['home1'][0]][config['player1']['home1'][1]] = \
        square(X, config['player1']['home1'][0], config['player1']['home1'][1])
    board[config['player1']['home2'][0]][config['player1']['home2'][1]] = \
        square(X, config['player1']['home2'][0], config['player1']['home2'][1])
    board[config['player2']['home1'][0]][config['player2']['home1'][1]] = \
        square(O, config['player2']['home1'][0], config['player2']['home1'][1])
    board[config['player2']['home2'][0]][config['player2']['home2'][1]] = \
        square(O, config['player2']['home2'][0], config['player2']['home2'][1])
    for i in [0, rows - 1]:    
        for j in range(columns):
            board[i][j]['S'] = (i == (rows - 1))
            board[i][j]['N'] = i == 0
    for j in [0, columns - 1]:    
        for i in range(rows):
            board[i][j]['W'] = j == 0
            board[i][j]['E'] = (j == (columns - 1))
    return board
