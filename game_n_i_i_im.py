import copy

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info as gi
from ticketing import ticket_io as tio

import random as rn

DEBUG = True


def create_nonwinner_numbered_tickets(amt: int, spots: int, first: int, last: int, suffixes: str, base: str,
                                      nw_pool: list[str], addl_imgs: gi.AddImages, addl_nums: int,
                                      is_first: bool = False):
    if suffixes == '':
        exclusions = ['00']
    else:
        exclusions = suffixes.split(',')
    if base != '':
        base = f'{base}.ai'
    imgs = ig.add_additional_image_slots(addl_imgs, [base])
    ticks = []
    while len(ticks) < amt:
        if len(nw_pool) < spots:
            nw_pool = ng.create_number_pools_from_suffix_list(first, last, exclusions, True)
        numbs = []
        for _ in range(spots):
            numbs.append(nw_pool.pop(0))
        for _ in range(addl_nums):
            numbs.append('')
        tick = uTick('', imgs, numbs, 1, 1, is_first)
        is_first = False
        ticks.append(tick)
    return ticks, nw_pool


def create_hold_image_tickets(amt: list[int], addl_imgs: gi.AddImages, addl_nums: int, is_first: bool = False):
    ticks = []
    nummies = [''] * addl_nums
    for index, hold in enumerate(amt):
        for i in range(hold):
            if len(amt) == 1:
                img_name = f'hold{str(i + 1).zfill(2)}.ai'
            else:
                img_name = f'hold{str(index + 1).zfill(2)}-{str(i + 1).zfill(2)}.ai'
            imgs = ig.add_additional_image_slots(addl_imgs, [img_name])
            tick = uTick('', imgs, nummies, 1, 1, is_first)
            is_first = False
            ticks.append(tick)
    return ticks


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs):
    if DEBUG:
        for spec in game_specs:
            print(spec)
    first_time = True
    tickets = []

    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    sheet_specs, nw_specs, insta_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    ups, permies, sheets, capacities, reset, subflats, schisms = sheet_specs
    partname = name_specs[0]
    filename = name_specs[1]
    nons_pool = []
    nw_addl_imgs = gi.AddImages.NoneAdded
    inst_addl_imgs = gi.AddImages.NoneAdded
    pick_addl_imgs = gi.AddImages.NoneAdded
    if nw_type == 'I':
        if nw_specs[2] != 1:
            nw_addl_imgs = gi.add_images_lookup(-1)
            inst_addl_imgs = gi.add_images_lookup(nw_specs[2])

    if insta_type == 'I':
        pass

    if hold_type == 'I':
        hold_specs.extend([gi.AddImages.NoneAdded, 5, first_time])
        tickets.extend(create_hold_image_tickets(*hold_specs))

    if nw_type == 'N':
        nw_specs.extend([nons_pool, gi.AddImages.NoneAdded, 0, first_time])
        nw_ticks, nons_pool = create_nonwinner_numbered_tickets(*nw_specs)
        tickets.extend(nw_ticks)
        first_time = False

    tio.write_tickets_to_file(filename, tickets)

    game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacities[1], True, 0)

    tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets, capacities[1], output_folder)

    print(f'Created {len(tickets)} tickets.')


if __name__ == "__main__":
    specs = [[40, 1, 140, [80, 80], False, 0, 0],
             ['N', 265, 5, 1001, 9999, '', ''],
             ['I', [[0]], 0],
             ['I', [[0, False]]],
             ['I', [15]],
             ['000', 'BigTopBingo-31894'], '']

    create_game(specs)