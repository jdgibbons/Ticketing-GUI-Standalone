import copy
import re

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info as gi
from ticketing import ticket_io as tio
# from helpers import extract_ticket_types

import random as rn

DEBUG = True

nw_type = ''
insta_type = ''
pick_type = ''
hold_type = ''
suffix = ''


def create_instant_winner_image_tickets(amt_list: list[list[int | bool]],
                                        cd_tier: int, addl_imgs: gi.AddImages, numeros: int,
                                        is_first: bool) -> list[uTick]:
    """
    Create tiered instant winner tickets from a list of
    :param amt_list:
    :param cd_tier:
    :param addl_imgs:
    :param numeros:
    :param is_first:
    :return:
    """
    global suffix
    image_list = ig.create_discrete_tiered_image_sets(amt_list, 'winner', suffix)
    ticks = []
    numeros = [''] * numeros
    for img in image_list:
        cd = img[1]
        img = ig.add_additional_image_slots(addl_imgs, [img[0]])
        tick = uTick('', img, numeros, 1, 1, is_first)
        if cd_tier >= cd:
            tick.reset_cd_type('I')
            tick.reset_cd_tier(cd)
        ticks.append(tick)
        is_first = False
    return ticks


def create_instant_winner_shaded_tickets(shades: list[list[str | int | bool]], first: int, last: int,
                                         spots: int, cd_tier: int, exclusions: str, nw_pool: list[str],
                                         addl_imgs: gi.AddImages, num_slots: int, is_first: bool):
    ticks = []
    exclusions = exclusions.split(',')
    for hold in shades:
        exclusions.append(hold[1])
    if exclusions[0] == '':
        exclusions.pop(0)
    addl_nums = num_slots - spots

    for index, hold in enumerate(shades):
        # possum isn't used here, but it's still returned and must be assigned.
        base, color, full, possum = parse_shaded_list(hold)
        imgs = ig.add_additional_image_slots(addl_imgs, [base])
        for shade in hold[0]:
            nw_pool, tick = create_shaded_ticket(addl_nums, color, exclusions, first, full, imgs, is_first, last,
                                                 nw_pool, shade, spots)
            # If the cd_tier is greater or equal to the tier level, set this ticket's
            # cd_type to (I)nstant and set cd_tier to the current tier level.
            if index + 1 <= cd_tier:
                tick.reset_cd_type('I')
                tick.reset_cd_tier(index + 1)
            is_first = False
            ticks.append(tick)
    return ticks, nw_pool


def create_hold_shaded_tickets(shades: list[list[str | int | bool]], first: int, last: int, spots: int,
                               exclusions: str, addl_holds: list[list[str | int]], addl_imgs: gi.AddImages,
                               num_slots: int, is_first: bool = False):
    global suffix
    ticks = []
    nw_pool = []
    addl_nums = num_slots - spots
    exclusions = exclusions.split(',')
    for hold in shades:
        exclusions.append(hold[1])
    if exclusions[0] == '':
        exclusions.pop(0)
    for hold in shades:
        # Base suffix is added in parse_shaded_list.
        base, color, full, possum = parse_shaded_list(hold)
        imgs = ig.add_additional_image_slots(addl_imgs, [base])
        for shade in hold[0]:
            nw_pool, tick = create_shaded_ticket(addl_nums, color, exclusions, first, full, imgs, is_first, last,
                                                 nw_pool, shade, spots, possum)
            is_first = False
            ticks.append(tick)
    nummies = [''] * (addl_nums + spots)
    for hold in addl_holds:
        base = hold[0]
        if isinstance(hold[1], str):
            amt = int(hold[1])
        else:
            amt = hold[1]
        for i in range(amt):
            imgs = ig.add_additional_image_slots(addl_imgs, [f'{base}{str(i + 1).zfill(2)}{suffix}'])
            tick = uTick('', imgs, nummies, 1, 1, is_first)
            is_first = False
            ticks.append(tick)
    return ticks, nw_pool


def create_shaded_ticket(addl_nums, color, exclusions, first, full, imgs, is_first,
                         last, nw_pool, shade, spots, pi: bool = False):
    global suffix
    if len(nw_pool) < spots - 1:
        nw_pool = ng.create_number_pools_from_suffix_list(first, last, exclusions, True)
    numbs = []
    if full:
        numbs.append(f'<@{color}FONT>{shade}')
    else:
        numbs.append(f'{shade[:-2]}<@{color}FONT>{shade[-2:]}')
    for _ in range(spots - 1):
        numbs.append(nw_pool.pop(0))
    for _ in range(rn.randint(5, 11)):
        rn.shuffle(numbs)
    for _ in range(addl_nums):
        numbs.append('')
    match = r'FONT'
    index = 0
    base_images = copy.deepcopy(imgs)
    # If there is a 'plus image', find which spot the shaded number is at and
    # add a hold image for that space. (See 31891, Stars for reference).
    if pi:
        offset = -len(suffix)
        for i in range(len(numbs)):
            if re.search(match, numbs[i]):
                base_images[0] = f'{base_images[0][:offset]}-{str(i + 1).zfill(2)}{base_images[0][offset:]}'
                break
    tick = uTick('', base_images, numbs, 1, 1, is_first)
    return nw_pool, tick


def parse_shaded_list(hold):
    global suffix
    color = hold[2]
    if isinstance(hold[3], str) and hold[3] == 'True':
        full = True
    elif isinstance(hold[3], bool) and hold[3]:
        full = True
    else:
        full = False
    if len(hold[4]) != 0:
        base = f'{hold[4]}{suffix}'
    else:
        base = ''
    if len(hold) != 6:
        return base, color, full, False
    if isinstance(hold[5], str) and hold[5] == 'True':
        possum = True
    elif isinstance(hold[5], bool) and hold[5]:
        possum = True
    else:
        possum = False
    return base, color, full, possum


def create_nonwinner_numbers(amt: int, spots: int, first: int, last: int, exclusions: str, base: str,
                             nw_pool: list[str], addl_imgs: gi.AddImages, num_slots: int, is_first: bool = False):
    global suffix
    if exclusions == '':
        exclusions = ['00']
    else:
        exclusions = exclusions.split(',')
    if base != '':
        base = f'{base}{suffix}'
    addl_nums = num_slots - spots
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
    return ticks


def get_total_number_spots(nws: list, instas: list, pickets: list, holdings: list):
    top_number = 0
    if nw_type == 'N':
        if nws[1] > top_number:
            top_number = nws[1]
        if insta_type == 'S':
            if instas[3] > top_number:
                top_number = instas[3]
        if pick_type == 'S':
            pass
        if hold_type == 'S':
            if holdings[3] > top_number:
                top_number = holdings[3]
        return top_number


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs):
    global nw_type, insta_type, pick_type, hold_type, suffix
    print(game_specs)
    first_time = True
    permutations = []
    if DEBUG:
        for spec in game_specs:
            print(spec)

    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    sheet_specs, nw_specs, insta_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    ups, permies, sheets, capacities, reset, subflats, schisms, suffix = sheet_specs
    suffix = sheet_specs.pop()
    partname = name_specs[0]
    filename = name_specs[1]

    tickets = []
    nons_pool = []
    ceedee_tier = 0

    num_count = get_total_number_spots(nw_specs, insta_specs, pick_specs, hold_specs)

    if hold_type == 'S':
        hold_specs.extend([gi.AddImages.NoneAdded, num_count, first_time])
        tickles, nons_pool = create_hold_shaded_tickets(*hold_specs)
        tickets.extend(tickles)
        first_time = False

    if insta_type == 'S':
        insta_specs.extend([nons_pool, gi.AddImages.NoneAdded, num_count, first_time])
        tickies, nons_pool = create_instant_winner_shaded_tickets(*insta_specs)
        ceedee_tier = insta_specs[4]
        tickets.extend(tickies)
        first_time = False
    elif insta_type == 'I':
        if len(insta_specs[0][0]) > 0:
            insta_specs.extend([gi.AddImages.NoneAdded, num_count, first_time])
            tickets.extend(create_instant_winner_image_tickets(*insta_specs))
            ceedee_tier = insta_specs[1]
            first_time = False

    if nw_type == 'N':
        nw_specs.extend([nons_pool, gi.AddImages.NoneAdded, num_count, first_time])
        tickets.extend(create_nonwinner_numbers(*nw_specs))
        first_time = False

    tio.write_tickets_to_file(filename, tickets)

    game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacities[1], True, 0)

    ceedees, blankets = tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets, capacities[1])

    if len(ceedees) > 0:
        tio.write_cd_positions_to_csv_file(partname, filename, ceedees, ceedee_tier, output_folder)
    print('whatevs.')


if __name__ == "__main__":
    twice_fifty = [[20, 1, 100, [80, 80], False, 0, 0, '.pdf'],
                   ['N', 346, 8, 101, 999, '00,50,33,22,11', 'base'],
                   ['S', [[['033', '133', '233', '333', '433', '533', '633', '733', '833', '933', '1033'],
                           '33', 'RED', False, 'winner01'],
                          [['022', '122', '222', '322', '422', '522', '622', '722', '822', '922', '1022'],
                           '22', 'RED', False, 'winner02'],
                          [['011', '111', '211', '311', '411', '511', '611', '711', '811', '911', '1011'], '11',
                           'RED', False, 'winner03']], 101, 999, 6, 0, '50,00'],
                   ['I', [[0, False]]],
                   ['S', [[['050', '150', '250', '350', '450', '550', '650', '750', '850', '950', '1050'],
                           '50', 'RED', True, 'hold01'],
                          [['100', '200', '300', '400', '500', '600', '700', '800', '900', '1000'],
                           '00', 'RED', True, 'hold01']], 101, 999, 6, '33,22,11', []],
                   ['992-016', 'TwiceFifty-31885'],
                   '']

    triple_diamonds = [[2, 1, 142, [56, 56], False, 0, 0, '.ai'],
                       ['N', 3781, 5, 101, 9999, '00,55', 'base'],
                       ['I', [[120, False]], 0],
                       ['I', [[0, False]]],
                       ['S', [
                           [['155', '255', '355', '455', '555', '655', '755', '855', '955', '1055', '1155', '1255',
                             '1355', '1455', '1555', '1655', '1755', '1855', '1955', '2055', '2155', '2255', '2355',
                             '2455', '2555'], '55', 'RED', True, 'base01'],
                           [['100', '200', '300', '400', '500', '600', '700', '800', '900', '1000', '1100', '1200',
                             '1300', '1400', '1500', '1600', '1700', '1800', '1900', '2000', '2100', '2200', '2300',
                             '2400', '2500', '2600', '2700', '2800', '2900', '3000', '3100', '3200', '3300', '3400',
                             '3500', '3600', '3700', '3800', '3900', '4000'], '00', 'GREEN', True, 'base01']],
                        101, 9999, 5, '', [['hold', '10']]],
                       ['993-002', 'TripleDiamondSlots-53691'], '']

    stars = [[40, 1, 70, [80, 80], False, 0, 0, '.pdf'],
             ['N', 113, 4, 101, 9999, '13,55', ''],
             ['S', [[['155', '255'], '55', 'BLUE', False, 'winner01']], 101, 9999, 4, 0, '13'],
             ['I', [[0, False]]],
             ['S', [[['013', '513', '1013', '1513', '2013'], '13', 'RED', False, 'hold01', True],
                    [['113', '213', '313', '413', '613', '713', '813', '913', '1113', '1213', '1313', '1413', '1613',
                      '1713', '1813', '1913', '2113', '2213', '2313', '2413'], '13', 'RED', False, 'hold02', True]],
              101, 9999, 4, '55', []],
             ['000', 'Stars-31891'], '']

    create_game(stars)
