
def draw_square(board_view, square, borders_to_draw = ['N', 'W']):
    i = square['row']
    j = square['column']
    mi = (i * 2) + 1
    mj = (j * 2) + 1
    piece = square['piece'] 
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    END = '\033[0m'
    if piece == ' ' and square['home_to']:
        piece = f"{BLUE if square['home_to'] == 'X' else GREEN}·{END}"
        #piece = 'H'
    board_view[mi][mj] = ''.join([' ', piece, ' '])
    board_view[mi - 1][mj] = '═══' if square['N'] else '───' 
    board_view[mi][mj - 1] = 'ǁ' if square['W'] else '|' 
    if 'S' in borders_to_draw:
        board_view[mi + 1][mj] = '═══' if square['S'] else '───' 
    if 'E' in borders_to_draw:
        board_view[mi][mj + 1] = 'ǁ' if square['E'] else '|' 