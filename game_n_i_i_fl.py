# Reference Bluecoats Mini Flashboard - 4854
from ticketing.universal_ticket import UniversalTicket as uTick

from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info as gi


nw_type, insta_type, pick_type, hold_type = '', '', '', ''
DEBUG = True


def create_numbered_nonwinner_tickets(amt: int, spots: int, first: int, last: int, prefixes: str,
                                      add_imgs: list[gi.AddImages], is_first: bool = True):
    ticks = []
    nw_pool = []
    imgs = ['']
    pres = prefixes.split(',')
    if pres[0] == '':
        pres = ['00']
    while len(ticks) < amt:
        if len(nw_pool) < spots:
            # Adding 'RED' to provide a DesignMerge tag. It won't be used, but it's needed.
            wins, nw_pool = ng.create_number_pools(first, last, pres, first, last,
                                                   'RED', False)
        nums = []
        for _ in range(spots):
            nums.append(nw_pool.pop(0))
        tick = uTick('', imgs, nums, 1, 1, is_first)
        ticks.append(tick)
        is_first = False
    return ticks


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs):
    global nw_type, insta_type, pick_type, hold_type
    if DEBUG:
        print(game_specs)
    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    if DEBUG:
        print("\n\n")
        print(game_specs)
    first_timer = True
    mix_flat = True
    tickets = []
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    part_name, file_name = name_specs


if __name__ == '__main__':
    specs = [
        [32, 8, 100, [64, 64], False, 0, 0],
        ['N', 185, 5, 1001, 9999, '', ''],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['F', 15, 5, False, True, True, ['white', '', '', '', '']],
        ['000', 'blue-4854'],
        ''
    ]
