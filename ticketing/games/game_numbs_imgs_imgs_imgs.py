import copy

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi
from ticketing import ticket_io as tio

import random as rn

DEBUG = True
nw_type, insta_type, pick_type, hold_type = '', '', '', ''
img_suffix = ''


def create_nonwinner_numbered_tickets(amt: int, spots: int, first: int, last: int, suffixes: str, base: str,
                                      nw_pool: list[str], addl_imgs: gi.AddImages, addl_nums: int,
                                      is_first: bool = False):
    """
    Create a list of nonwinner tickets, each comprised of a specified number of numbered integers. Add
    a base image to the tickets if a name is provided.
    :param amt: The number of tickets to create.
    :type amt: int
    :param spots: The number of integers per ticket.
    :type spots: int
    :param first: The smallest number in the range of possible integers.
    :type first: int
    :param last: The highest number in the range of possible integers.
    :type last: int
    :param suffixes: The list of suffixes to exclude from the pool of possible integers.
    :type suffixes: str
    :param base: The base image name.
    :type base: str
    :param nw_pool:
    :param addl_imgs:
    :param addl_nums:
    :param is_first:
    :return:
    """
    global img_suffix
    # Always add '00' to the exclusion list if it's not already there.
    if suffixes == '':
        exclusions = ['00']
    else:
        exclusions = suffixes.split(',')
        if '00' not in exclusions:
            exclusions.append('00')
    # Add the suffix to the base if a base is present.
    if base != '':
        base = f'{base}{img_suffix}'
    # Add any additional images slots necessary to properly format the csv.
    imgs = ig.add_additional_image_slots(addl_imgs, [base])
    # Create a list for the tickets and loop until there are the required amount.
    ticks = []
    while len(ticks) < amt:
        # If there aren't enough available integers to create a new ticket, replenish
        # the supply of integers.
        if len(nw_pool) < spots:
            nw_pool = ng.create_number_pools_from_suffix_list(first, last, exclusions, True)
        # Create a list to hold the integers, then pop off the next one until
        # there are enough to satisfy the requirements.
        numbs = []
        for _ in range(spots):
            numbs.append(nw_pool.pop(0))
        # Add any additional number slots necessary to properly format the csv.
        for _ in range(addl_nums):
            numbs.append('')
        # Create a new ticket, reset the first flag, and add the ticket to the list.
        tick = uTick('', imgs, numbs, 1, 1, is_first)
        is_first = False
        ticks.append(tick)
    return ticks, nw_pool


def create_instant_winners(amt: list[list[int | bool]], cd_tier: int, addl_imgs: gi.AddImages,
                           add_nums: int, tkt: int | str = '', is_first=True) -> list[uTick]:
    """
    Create a list of instant winner tickets consisting of one image and set the ticket's
    CD value equal to its tier level if the level is equal to or less than the cd_tier.

    :param amt: list containing the number of tickets for each ticket tier
    :type amt: list[int]
    :param cd_tier: tier level at which CDs are required (zero if none)
    :type cd_tier: int
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param add_nums: Number of number slots needed in the csv output.
    :type add_nums: int
    :param tkt: First ticket number.
    :type tkt: int | str
    :param is_first: Does the first ticket need to set the csv fields?
    :type is_first: bool
    :return: A list of instant winner tickets
    :rtype: list[UniversalTicket]
    """
    global img_suffix
    # Get a list of lists containing the image name and tier level for the winning tickets.
    imgs = ig.create_tiered_image_list_augmented(amt, 'winner', img_suffix)
    # Create a placeholder for the number slots
    nummies = [''] * add_nums
    ticks = []

    # Set a new variable to control the setting of the csv fields. This seems redundant,
    # but the code wasn't fond of resetting the passed value. So, whatever.
    # cull_headers = is_first
    # Cycle through the list of image name/tier level lists and create a ticket for each one.
    for img in imgs:
        # Create a list that contains the image and any additional image slots needed.
        # (This is used to reserve slots for three-image nonwinner tickets, if necessary.)
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])
        # Create a new ticket with ticket number, pics, number slots, perm, up, and whether to create the csv fields.
        tick = uTick(tkt, pics, nummies, 1, 1, is_first)
        # Set the ticket's cd tier level if it's less than or equal to the passed cd tier.
        if img[1] <= cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')
        # Add the ticket to the list, set the cull ticket flag to False, and increment the ticket number.
        ticks.append(tick)
        is_first = False
        if isinstance(tkt, int):
            tkt += 1
    # Return the list of instant winner tickets.
    return ticks


# def create_hold_image_tickets(amt: list[int], addl_imgs: gi.AddImages, addl_nums: int, is_first: bool = False):
#     global img_suffix
#     ticks = []
#     nummies = [''] * addl_nums
#     for index, hold in enumerate(amt):
#         for i in range(hold):
#             if len(amt) == 1:
#                 img_name = f'hold{str(i + 1).zfill(2)}{img_suffix}'
#             else:
#                 img_name = f'hold{str(index + 1).zfill(2)}-{str(i + 1).zfill(2)}{img_suffix}'
#             imgs = ig.add_additional_image_slots(addl_imgs, [img_name])
#             tick = uTick('', imgs, nummies, 1, 1, is_first)
#             is_first = False
#             ticks.append(tick)
#     return ticks


def create_hold_image_tickets(amt: list[int], addl_imgs: gi.AddImages,
                              addl_nums: int, is_first: bool = False):
    global img_suffix
    ticks = []
    nummies = [''] * addl_nums
    imgs = ig.create_tiered_image_list(amt, 'hold', True, img_suffix)
    for img in imgs:
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])
        tick = uTick('', pics, nummies, 1, 1, is_first)
        is_first = False
        ticks.append(tick)
    return ticks


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs):
    global nw_type, insta_type, pick_type, hold_type, img_suffix
    if DEBUG:
        print('\nGame Specs:\n')
        print(game_specs)
        print('\nBy element: ')
        for spec in game_specs:
            print(spec)
    first_time = True
    tickets = []

    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    sheet_specs, nw_specs, insta_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    img_suffix = sheet_specs.pop()
    ups, permies, sheets, capacities, reset, subflats, schisms = sheet_specs
    partname = name_specs[0]
    filename = name_specs[1]
    nons_pool = []
    nw_addl_imgs = gi.AddImages.NoneAdded
    inst_addl_imgs = gi.AddImages.NoneAdded
    pick_addl_imgs = gi.AddImages.NoneAdded
    hold_addl_imgs = gi.AddImages.NoneAdded
    tkt_no = ''

    nw_number_slots = nw_specs[1]
    # if nw_type == 'I':
    #     if nw_specs[2] != 1:
    #         nw_addl_imgs = gi.add_images_lookup(-1)
    #         inst_addl_imgs = gi.add_images_lookup(nw_specs[2])

    if insta_type == 'I' and insta_specs[0][0] != 0:
        insta_specs.extend([inst_addl_imgs, nw_number_slots, tkt_no, first_time])
        tickets.extend(create_instant_winners(*insta_specs))

    if hold_type == 'I':
        hold_specs.extend([hold_addl_imgs, nw_number_slots, first_time])
        tickets.extend(create_hold_image_tickets(*hold_specs))

    if nw_type == 'N':
        nw_specs.extend([nons_pool, nw_addl_imgs, 0, first_time])
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

    finish_line = [
        [80, 1, 100, [80, 80], False, 0, 0, '.ai'],
        ['N', 85, 3, 101, 9999, '00', ''],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['I', [15]],
        ['992-052', 'FinishLineII-31951'],
        ''
    ]
    # Finish Line with instants added.
    fake_the_line = [
        [80, 1, 136, [80, 80], False, 0, 0, '.pdf'],
        ['N', 85, 3, 101, 9999, '00', 'bassie01'],
        ['I', [[1, False], [5, False], [10, False], [20, False]], 0],
        ['I', [[0, False]]],
        ['I', [15]],
        ['992-052', 'FakeLineII-31951'],
        ''
    ]

    create_game(finish_line)
