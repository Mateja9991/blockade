from src.view.square import draw_square

def create_board_view(board):
    board_view = [[' ' for x in range(len(board[0]) * 2 + 1)] for y in range(len(board) * 2 + 1)] 
    for row in board:
        for square in row:
            borders = ['N', 'W']
            if row == board[-1]:
                borders += ['S']
            if square == row[-1]:
                borders += ['E']
            draw_square(board_view, square, borders)
    return board_view
        
def board_to_string(board):
    result = ''
    for i, row in enumerate(create_board_view(board)):
        row_hex = ''
        if i % 2 == 1:
            row_hex = format(i // 2, 'x')
        result += row_hex.ljust(2, ' ')
        result += ''.join( row ) + '\n'
    return result

def print_num_row(columns):
    print(end='   ')
    for i in range(columns):
        hex_view = format(i, 'x').center(4, ' ')
        print(hex_view, end='')
    print()

def draw_board(board):
    print_num_row(len(board[0]))

    print(    board_to_string(board), end=''    )

    print_num_row(len(board[0]))
