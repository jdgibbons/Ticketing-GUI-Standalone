"""
Nonwinners: numbers
Instants: cannons
Picks: Image
Holds: cannons

This module is called from the CSV Generator when the nonwinners, instants, and picks are composed of simple images,
but the holds are composed of five-row bingos. The number of spaces in each row is determined by a user-provided
pattern.

The create_game method is the main entry point for this module, and it is called with a list of game specs. That list
contains other lists detailing the specifications for creating the game. The lists, in order, pertain to sheets,
nonwinners, instants, picks, holds, and part and file name. There the final element is a string containing the
output folder. It will be blank if files are to be placed in the default folder.
"""
import copy

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi
from ticketing import ticket_io as tio

DEBUG = True
nw_type, insta_type, pick_type, hold_type = '', '', '', ''
img_suffix = ''


def create_nonwinner_numbers(amt: int, spots: int, first: int, last: int, suffixes: str, base: str,
                             addl_imgs: gi.AddImages, is_first: bool = False):
    global img_suffix
    if suffixes == '':
        suffixes = ['00']
    else:
        suffixes = suffixes.split(',')
    imgs = ig.add_additional_image_slots(addl_imgs, [''])

    ticks = []
    nw_pool = []
    basic = '' if base == '' else f'{base}{img_suffix}'
    suffixes.pop(0)
    while len(ticks) < amt:
        if len(nw_pool) < spots:
            nw_pool = ng.create_number_pools_from_suffix_list(first, last, suffixes, True)
        numbs = []
        for _ in range(spots):
            numbs.append(nw_pool.pop(0))
        tick = uTick(basic, imgs, numbs, 1, 1, is_first)
        is_first = False
        ticks.append(tick)
    return ticks


def create_hold_images(amt: int, permits: int, addl_imgs: gi.AddImages, nums: int, is_first: bool = False):
    global img_suffix
    perms = []
    if nums != 0:
        nums = [''] * nums
    else:
        nums = []

    for i in range(permits):
        ticks = []
        imgs = ig.create_prefixed_images(1, amt, f'hold{str(i + 1).zfill(2)}-', True, img_suffix)
        # imgs = ig.add_additional_image_slots(addl_imgs, imgs)
        # ticks.append(uTick('', imgs, nums, i + 1, 1, is_first))
        # perms.append(ticks)
        for tick in imgs:
            tick = ig.add_additional_image_slots(addl_imgs, [tick])
            ticks.append(uTick('', tick, nums, i + 1, 1, is_first))
        perms.append(ticks)
    return perms


def create_instant_images(amt: int, permits: int, addl_imgs: gi.AddImages, nums: int, is_first: bool = False):
    """

    :param amt:
    :param permits:
    :param addl_imgs:
    :param nums:
    :param is_first:
    :return:
    """
    global img_suffix
    perms = []
    if nums != 0:
        nums = [''] * nums
    else:
        nums = []

    for i in range(permits):
        ticks = []
        imgs = ig.create_image_list_of_same_image(amt, f'winner{str(i + 1).zfill(2)}', img_suffix)
        for tick in imgs:
            tick = ig.add_additional_image_slots(addl_imgs, [tick])
            ticks.append(uTick('', tick, nums, i + 1, 1, is_first))
            is_first = False
        perms.append(ticks)
    return perms


def create_instant_winners(amt: list[list[int | bool]], cd_tier: int, permits: int,
                           addl_imgs: gi.AddImages, nummies: int, first=True) -> list[uTick]:
    """
    Create a list of instant winner tickets consisting of one image and set the ticket's
    CD value equal to its tier level if the level is equal to or less than the cd_tier.

    :param amt: list containing the number of tickets for each ticket tier
    :type amt: list[int]
    :param cd_tier: tier level at which CDs are required (zero if none)
    :type cd_tier: int
    :param permits: number of permutations
    :type permits: int
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param nummies: Number of number slots needed in the csv output.
    :type nummies: int
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :return: A list of instant winner tickets
    :rtype: list[UniversalTicket]
    """
    # Get a list of lists containing the image name and tier level for the winning tickets.
    global img_suffix
    imgs = ig.create_tiered_image_list_augmented(amt, 'winner', img_suffix)
    # Create a placeholder for the number slots
    nums = [''] * nummies
    ticks = []
    # Set a new variable to control the setting of the csv fields. This seems redundant,
    # but the code wasn't fond of resetting the passed value. So, whatever.
    cull_ticket = first
    tkt = ''
    # Cycle through the list of image name/tier level lists and create a ticket for each one.
    for img in imgs:
        # Create a list that contains the image and any additional image slots needed.
        # (This is used to reserve slots for three-image nonwinner tickets, if necessary.)
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])
        # Create a new ticket with ticket number, pics, number slots, perm, up, and whether to create the csv fields.
        tick = uTick(tkt, pics, nums, 1, 1, cull_ticket)
        # Set the ticket's cd tier level if it's less than or equal to the passed cd tier.
        if img[1] <= cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')
        # Add the ticket to the list and set the cull ticket flag to False.
        ticks.append(tick)
        cull_ticket = False
    perms = []
    for i in range(permits):
        perms.append(copy.deepcopy(ticks))
    # Return the list of instant winner tickets.
    return perms


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs):
    global nw_type, insta_type, pick_type, hold_type, img_suffix
    first_time = True
    permutations = []
    if DEBUG:
        print(game_specs)
        for spec in game_specs:
            print(spec)

    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    sheet_specs, nw_specs, insta_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    img_suffix = sheet_specs.pop()
    ups, permies, sheets, capacities, reset, subflats, schisms = sheet_specs
    partname = name_specs[0]
    filename = name_specs[1]

    tickets = []
    if nw_type == 'N':
        nw_specs.extend([gi.AddImages.NoneAdded, first_time])
        tickets = create_nonwinner_numbers(*nw_specs)
        first_time = False

    holders = []
    if hold_specs[0] > 0:
        hold_specs.extend([gi.AddImages.NoneAdded, nw_specs[1], first_time])
        holders = create_hold_images(*hold_specs)

    instants = []
    if insta_type == 'C':
        if insta_specs[0] > 0:
            insta_specs.extend([gi.AddImages.NoneAdded, nw_specs[1], first_time])
            instants = create_instant_images(*insta_specs)
            first_time = False
    elif insta_type == 'I':
        if insta_specs[0][0][0] > 0:
            insta_specs.extend([hold_specs[1], gi.AddImages.NoneAdded, nw_specs[1], first_time])
            instants = create_instant_winners(*insta_specs)

    for i in range(len(holders)):
        permutations.append(holders[i])
        permutations[i].extend(instants[i])
        nws = copy.deepcopy(tickets)
        for tick in nws:
            tick.reset_permutation(i + 1)
        permutations[i].extend(nws)

    tio.write_permutations_to_files(filename, permutations)
    game_stacks = tio.create_game_stacks_from_permutations(permutations, ups, sheets, capacities[1])
    ceedees, teepees = tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets, capacities[1])

    print('whatevs')


if __name__ == "__main__":
    smackcams = [
        [40, 1, 150, [80, 80], False, 0, 0, '.pdf'],
        ['N', 274, 4, 1001, 9999, '00', ''],
        ['C', 6, 10],
        ['I', [[0, False]]],
        ['C', 20, 10],
        ['000', 'smackcans-10101'],
        ''
    ]

    smackimgs = [
        [40, 1, 150, [80, 80], False, 0, 0, '.pdf'],
        ['N', 274, 4, 1001, 9999, '00', ''],
        ['I', [[6, False]], 0],
        ['I', [[0, False]]],
        ['C', 20, 10], ['000', 'smackims-20202'],
        ''
    ]

    create_game(smackimgs)
