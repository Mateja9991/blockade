
def get_default_config(n=11, m=14, gw=3, bw=3, x1_x = 3, x1_y=3, \
            x2_x=7, x2_y=3, o1_x=3, o1_y=10, o2_x=7, o2_y=10):
    return {
        'n': n,
        'm': m,
        'green_walls': gw,
        'blue_walls': bw,
        'first_player': 'Human',
        'player1': {
            'home1': (x1_x, x1_y),
            'home2': (x2_x, x2_y),
        },
        'player2': {
            'home1': (o1_x, o1_y),
            'home2': (o2_x, o2_y),
        }
    }