"""
Nonwinners: numbers
Instants: images
Picks: images
Holds: bingo balls

This module is called from the CSV Generator when instant winners and picks are composed of simple, single images,
the nonwinners are composed of numbers, and the hold tickets contain bingo balls.

The create_game method is the main entry point for this module, and it is called with a list of game specs. That list
contains other lists detailing the specifications for creating the game. The lists, in order, pertain to sheets,
nonwinners, instants, picks, holds, and part and file name. There the final element is a string containing the
output folder. It will be blank if files are to be placed in the default folder.

"""
import copy
import ticketing.game_info as gi
from ticketing.universal_ticket import UniversalTicket as uTick
import ticketing.image_generator as ig
import ticketing.number_generator as ng
import ticketing.ticket_io as tio

import random as rn
import itertools as it

DEBUG = True
nw_type, insta_type, pick_type, hold_type = '', '', '', ''
suffix = ''


def calculate_image_slots(nws, holds):
    """
    Calculate additional image slots needed for each ticket type.

    :param nws: nonwinner game specs
    :type nws: list[any]
    :param holds: hold game specs
    :type holds: list[any]
    :return: pre- and post-image list slots values
    :rtype: list[list[gi.AddImages]]
    """
    # Get the number of images for nonwinners and holds and set all
    # pre- and post-values.
    holds_needed = holds[0][2]
    holds_supplemental = 0
    if holds[1][1] > 0:
        holds_supplemental += 1
    nw_pre = 0
    nw_post = 0
    hold_pre = 0
    hold_post = 0
    inst_pre = 0
    inst_post = 0

    if holds_needed > 1:
        nw_post = holds_needed + holds_supplemental
        inst_post = holds_needed + holds_supplemental

    add_nw = [gi.add_images_lookup(nw_pre), gi.add_images_lookup(nw_post)]
    add_hold = [gi.add_images_lookup(hold_pre), gi.add_images_lookup(hold_post)]
    add_inst = [gi.add_images_lookup(inst_pre), gi.add_images_lookup(inst_post)]
    return [add_nw, add_hold, add_inst]


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_instant_winners(amt: list[list[int | bool]], cd_tier: int, tkt: int | str,
                           addl_imgs: list[gi.AddImages], nummies: int, first=True) -> list[uTick]:
    """
    Create a list of instant winner tickets consisting of one image and set the ticket's
    CD value equal to its tier level if the level is equal to or less than the cd_tier.

    :param amt: list containing the number of tickets for each ticket tier
    :type amt: list[int]
    :param cd_tier: tier level at which CDs are required (zero if none)
    :type cd_tier: int
    :param tkt: First ticket number or blank string.
    :type tkt: int | str
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param nummies: Number of number slots needed in the csv output.
    :type nummies: int
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :return: A list of instant winner tickets
    :rtype: list[UniversalTicket]
    """
    global suffix
    # Get a list of lists containing the image name and tier level for the winning tickets.
    imgs = ig.create_tiered_image_list_augmented(amt, 'winner', suffix)
    # Create a placeholder for the number slots
    nums = [''] * nummies
    ticks = []
    # Set a new variable to control the setting of the csv fields. This seems redundant,
    # but the code wasn't fond of resetting the passed value. So, whatever.
    cull_ticket = first
    # Cycle through the list of image name/tier level lists and create a ticket for each one.
    for img in imgs:
        # Create a list that contains the image and any additional image slots needed.
        # (This is used to reserve slots for three-image nonwinner tickets, if necessary.)
        pics = [img[0]]
        for add in addl_imgs:
            pics = ig.add_additional_image_slots(add, pics)
        # Create a new ticket with ticket number, pics, number slots, perm, up, and whether to create the csv fields.
        tick = uTick(tkt, pics, nums, 1, 1, cull_ticket)
        # Set the ticket's cd tier level if it's less than or equal to the passed cd tier.
        if img[1] <= cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')
        # Add the ticket to the list, set the cull ticket flag to False, and increment the ticket number.
        ticks.append(tick)
        cull_ticket = False
        if tkt != '' and isinstance(tkt, int):
            tkt += 1
    # Return the list of instant winner tickets.
    return ticks


def create_hold_tickets(bb_options: list[int], bool_options: list[bool | str],
                        sup_holds: list[int | list[list[str | int]]],
                        tkt: int | str, addl_bb_imgs: list[gi.AddImages], addl_sup_imgs: list[gi.AddImages],
                        permits: int, nummies: int, first: bool) -> list[list[uTick]] | None | str:
    """
    Create bingo ball and supplemental hold tickets.

    :param bb_options: list containing ticket quantities, spots, and number of filler images
    :type bb_options: list[int]
    :param bool_options: list of bools for downlines, nw image use, and keep bingo image (for free spaces)
    :type bool_options: list[bool]
    :param sup_holds: list containing information about supplemental holds
    :type sup_holds: list[int | list[list[str | int]]]
    :param tkt: First ticket number.
    :type tkt: int
    :param addl_bb_imgs: Additional image slots required to pad the csv output for bingo ball holds.
    :type addl_bb_imgs: list[gi.AddImages]
    :param addl_sup_imgs: Additional image slots required to pad the csv output for supplemental holds.
    :type addl_sup_imgs: list[gi.AddImages]
    :param permits: number of perms needed
    :type permits: int
    :param nummies: number of number slots needed in the csv output
    :type nummies: int
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :return: list of hold tickets
    :rtype: list[uTick] | None | str
    """
    # Breakdown some of the passed lists into their component parts.
    bb_amt, bpt, spt, fill_pool, frees = bb_options
    downs, shazams, sortie, base, match_bbs = bool_options
    perms = []
    # If there are needed bingo ball type holds, create them.
    if bb_amt > 0:
        perms = create_bingo_ball_tickets(bb_amt, bpt, spt, downs, permits, first, nummies, fill_pool,
                                          addl_bb_imgs, tkt, shazams, base, sortie)
        first = False
    # If there are supplemental holds needed, create those.
    if sup_holds[0] > 0:
        # Should the additional holds use the same number of images per ticket as the bingo balls,
        # or should they be limited to a single image?
        if match_bbs:
            ticks = create_bb_match_image_holds(sup_holds[1], addl_bb_imgs, fill_pool, spt, base, first)
        else:
            ticks = create_single_image_holds(sup_holds[1], addl_sup_imgs, first)
        first = False
        if len(perms) == 0:
            perms.append([])
        for index, perm in enumerate(perms):
            single_copy = copy.deepcopy(ticks)
            for tick in single_copy:
                tick.reset_permutation(index + 1)
                perm.append(tick)
    return perms


def create_single_image_holds(suppers: list[list[str | int]], addl_imgs: list[gi.AddImages], first: bool):
    """
    Create a list of single-image hold-tickets from a list containing pairs of
    prefix parts and quantities.

    :param suppers: list of lists containing prefix parts and quantities
    :type suppers: list[list[str | int]]
    :param addl_imgs: list of additional image slots required to pad the csv output.
    :type addl_imgs: list[gi.AddImages]
    :param first: does the first ticket need to set the csv fields?
    :type first: bool
    :return: list of hold tickets
    :rtype: list[uTick]
    """
    global suffix
    ticks = []
    numbs = []
    # Cycle through the list of prefixes and quantities and create a list of tickets for each one.
    for sup in suppers:
        # Create the full prefix then create the list of images for this downline.
        prefix = f'{sup[0]}'
        pics = ig.create_prefixed_images(1, sup[1], prefix, True, suffix)
        # Cycle through each image and create a ticket based on it.
        for pic in pics:
            imgs = [pic]
            # Add additional image slots for csv purposes.
            for add in addl_imgs:
                imgs = ig.add_additional_image_slots(add, imgs)
            # Create the ticket and add it to the list.
            ticks.append(uTick('', imgs, numbs, 1, 1, first))
            first = False
    return ticks


def create_bb_match_image_holds(suppers: list[list[int | str]], addl_imgs: list[gi.AddImages], nws: int,
                                spt: int, base: str, first: bool):
    global suffix
    ticks = []
    numbs = []
    nw_pics = []
    if base != '':
        base = f'{base}{suffix}'
    for sup in suppers:
        prefix = f'{sup[0]}'
        pics = ig.create_prefixed_images(1, sup[1], prefix, True, suffix)
        for pic in pics:
            if len(nw_pics) < spt - 1:
                nw_pics = ig.create_image_pool(1, nws, 'nonwinner', True, suffix)
            imgs = [pic]
            while len(imgs) < spt:
                imgs.insert(rn.randint(0, len(imgs)), nw_pics.pop())
            imgs.insert(0, base)
            for add in addl_imgs:
                imgs = ig.add_additional_image_slots(add, imgs)
            ticks.append(uTick('', imgs, numbs, 1, 1, first))
            first = False
    return ticks


def create_bingo_ball_tickets(bb_amt, bpt, spt, downs, permits: int, first, nums, nw_pool,
                              addl_bb_imgs, tkt, shazams: int, basic: str, sortie: bool = True):
    """
    Create a list of bingo-ball-type hold-tickets (either random or downline).

    :param bb_amt: number of hold tickets needed
    :type bb_amt: int
    :param bpt: number of bingo spots per ticket
    :type bpt: int
    :param downs: Are these downline bingos?
    :type downs: bool
    :param permits: number of permutations needed
    :type permits: int
    :param first: does the first ticket need to set the csv fields?
    :type first: bool
    :param nums: number of number spots (zero for now)
    :type nums: int
    :param nw_pool: size of the nonwinner image pool
    :type nw_pool: int
    :param spt: total spots per ticket
    :type spt: int
    :param addl_bb_imgs: list of additional image slots required to pad the csv output.
    :type addl_bb_imgs: list[gi.AddImages]
    :param tkt: First ticket number.
    :type tkt: int | str
    :param shazams: number of tickets containing shazam-style images
    :type shazams: int
    :param basic: string containing the name of the base file
    :type basic: str
    :param sortie: sort bingo balls in ascending order?
    :type sortie: bool
    :return: list of lists of hold tickets
    :rtype: list[list[uTick]]
    """
    global suffix
    perms = []
    numbs = [''] * nums
    # Create a list to represent the position of all the tickets created for a single permutation.
    # This list will be used to randomly select which tickets receive shazam images (if any).
    tick_places = list(range(bb_amt))
    if downs:
        bangles = [create_downline_image_lists(bb_amt, bpt)]
    else:
        # bangles = ig.create_bingo_ball_image_list(bb_amt, bpt, 'hold')
        bangles = ig.create_bingo_ball_image_permutations(bb_amt, bpt, permits, 'hold', sortie, suffix)
    for index, bingos in enumerate(bangles):
        # Shuffle the ticket position list, then take a slice of the list equal to the
        # number of Shazams needed. Sort the list and use it to flag which tickets
        # will receive a shazam image (again, only if there are any).
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(tick_places)
        places = tick_places[0: shazams]
        places.sort(reverse=True)
        # This will keep track of the shazam position list index.
        shizzle = copy.deepcopy(shazams)
        ticks = []
        # If there are other images besides the bingo balls, add them here.
        if bpt != spt:
            # Create the extra images, most likely from a nonwinner pool.
            nw_imgs = ig.create_image_pool(1, nw_pool, 'nonwinner', True, suffix)
            # Shuffle the extra image pool and create a cycle iterator.
            for _ in range(rn.randint(2, 5)):
                rn.shuffle(nw_imgs)
            nw_cycle = it.cycle(nw_imgs)
            # Cycle through the image lists and add the needed images at random
            # spots in the list. Use the next image in the cycle to populate the
            # new list images.
            for bingo in bingos:
                while len(bingo) < spt:
                    bingo.insert(rn.randint(0, len(bingo) + 1), next(nw_cycle))
        # Create a list representing the position of each ticket, shuffle it, then
        # create a cycle iterator to run through the list as needed.
        positions = list(range(1, spt + 1))
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(positions)
        pos_cycle = it.cycle(positions)

        tick_no = tkt
        # Cycle through the image lists and create tickets with them.
        for innie, bingo in enumerate(bingos):
            # Create the pics list using the base image as the first element.
            pics = [''] if basic in ['', 'none', 'blank', '0', '000'] else [f'{basic}{suffix}']
            # If shazams are a part of this game . . .
            if shazams > 0:
                # If there are still shazams left to be added . . .
                if shizzle > 0:
                    # If the list index equals the current shazam position value,
                    # add the next shazam in the cycle to the image list.
                    if innie == places[shizzle - 1]:
                        pics.append(f'shazam{str(next(pos_cycle)).zfill(2)}{suffix}')
                        shizzle -= 1
                    else:
                        pics.append('')
                # Otherwise, add a blank space.
                else:
                    pics.append('')
            # Add the images to the pics list.
            pics.extend(bingo)
            for addl in addl_bb_imgs:
                pics = ig.add_additional_image_slots(addl, pics)
            # Create the ticket and add it to the ticket list.
            ticks.append(uTick(tick_no, pics, numbs, index + 1, 1, first))
            if tick_no != '' and isinstance(tick_no, int):
                tick_no += 1
            first = False
        perms.append(ticks)
    return perms


def create_downline_image_lists(amt: int, bpt: int) -> list[list[str]] | None:
    """
    Create bingo downlines comprised of the specified number of spots, shuffle
    them, then cull any excess from the end of the list.

    :param amt: number of downlines needed
    :type amt: int
    :param bpt: number of bingo spots per ticket
    :type bpt: int
    :return: list of bingo image downlines
    :rtype: list[list[str]]
    """
    global suffix
    # Get a list of all downlines containing the desired number of spots.
    bingos = ig.create_bingo_downlines(bpt, 'hold', False, suffix)
    # If there aren't enough downlines, return None.
    if len(bingos) < amt:
        return None
    # Shuffle the list and return the number of downlines needed.
    for _ in range(rn.randint(5, 10)):
        rn.shuffle(bingos)
    return bingos[0: amt]


def create_nonwinner_numbered_tickets(amt: int, spots: int, first: int, last: int, suffixes: str, base: str,
                                      addl_imgs: list[gi.AddImages], addl_nums: int, is_first: bool = False):
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
    global suffix
    # Always add '00' to the exclusion list if it's not already there.
    if suffixes == '':
        exclusions = ['00']
    else:
        exclusions = suffixes.split(',')
        if '00' not in exclusions:
            exclusions.append('00')
    # Add the suffix to the base if a base is present.
    if base != '':
        base = f'{base}{suffix}'
    imgs = [base]
    # Add any additional images slots necessary to properly format the csv.
    for addl_img in addl_imgs:
        imgs = ig.add_additional_image_slots(addl_img, imgs)
    # Create a list for the tickets and loop until there are the required amount.
    ticks = []
    nw_pool = []
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
    return ticks


def create_game(game_specs: list):
    """
    Initializes and generates a bingo-ball style work order based on specifications from a gui-based form. This
    function supports different types of tickets including pick and instant winners, shaded or imaged holds, and
    imaged or shaded non-winners. Finally, it writes the generated tickets and game stacks to specified output files.

    :param game_specs: A tuple containing specifications for creating the game. The tuple typically consists of:
                       - sheets_specs: Specifications related to sheet configurations.
                       - nowin_specs: Specifications for non-winner tickets.
                       - instant_specs: Specifications for instant win tickets.
                       - picks_specs: Specifications for pick winner tickets.
                       - holds_specs: Specifications for hold tickets.
                       - names_specs: Contains party and file name information.
                       - output_folder: The folder where output files are stored.
    :type game_specs: tuple
    :return: A status message indicating that all items have been successfully written to the files.
    :rtype: str
    """
    global nw_type, insta_type, pick_type, hold_type, suffix
    if DEBUG:
        print(game_specs)
    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    if DEBUG:
        print("\n\n")
        print(game_specs)
    first_timer = True
    mix_flat = True
    tickets = []
    # Extract the separate spec types and place them in their own variables.
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    suffix = sheet_specs.pop()
    numbies = nw_specs[1]
    # Extract the high-level game information from the sheet_specs
    ups, perms, sheets, capacities, reset_perms, subflats, schisms = sheet_specs
    # Get file and part names from name_specs
    part_name, file_name = name_specs
    # Get additional image slots needed for the various ticket types to maintain
    # a consistent csv.
    addl_nw, addl_hold, addl_inst = calculate_image_slots(nw_specs, hold_specs)
    # Do these ticket types need to contain a ticket number field. This may eventually be
    # set with passed parameters.
    inst_tkt_int = False
    pick_tkt_int = False
    hold_tkt_int = True
    tkt_no = 'unassigned'

    instants = []
    if inst_specs[0][0][0] > 0:
        if inst_tkt_int:
            tkt_no = len(tickets) + 1
        else:
            tkt_no = ''
        inst_specs.extend([tkt_no, addl_inst, numbies, first_timer])
        instants.extend(create_instant_winners(*inst_specs))
        first_timer = False
    picks = []
    # if pick_specs[0][0][0] > 0:
    #     if pick_tkt_int:
    #         if inst_tkt_int:
    #             tkt_no = len(tickets) + 1
    #         else:
    #             tkt_no = 1
    #     else:
    #         tkt_no = ''
    #     picks.extend(create_pick_winners(pick_specs[0], tkt_no, addl_inst,
    #                                      0, first_timer, pick_specs[1]))
    #     first_timer = False
    holds = []
    if hold_specs[0][0] > 0 or hold_specs[2][0] > 0:
        if hold_tkt_int:
            if inst_tkt_int and pick_tkt_int:
                tkt_no = len(instants) + len(picks) + 1
            elif pick_tkt_int:
                tkt_no = pick_specs[0][0][0] + 1
            elif inst_tkt_int:
                tkt_no = len(instants) + 1
            else:
                tkt_no = 1
        hold_specs.extend([tkt_no, addl_hold, addl_inst, perms, numbies, first_timer])
        holds = create_hold_tickets(*hold_specs)
        if isinstance(holds, str) or holds is None:
            return holds
        first_timer = False
    nonwinners = []
    if nw_specs[0] > 0:
        nw_specs.extend([addl_nw, first_timer])
        nonwinners = create_nonwinner_numbered_tickets(*nw_specs)
        first_timer = False
    #
    for index, hold in enumerate(holds):
        if len(instants) > 0:
            for snap in instants:
                snap.reset_permutation(index + 1)
            hold.extend(copy.deepcopy(instants))
        if len(picks) > 0:
            for snap in picks:
                snap.reset_permutation(index + 1)
            hold.extend(copy.deepcopy(picks))
        if len(nonwinners) > 0:
            for snap in nonwinners:
                snap.reset_permutation(index + 1)
            hold.extend(copy.deepcopy(nonwinners))

    if len(holds) == 1:
        tio.write_tickets_to_file(file_name, holds[0], output_folder)
        game_stacks = tio.create_game_stacks(holds[0], ups, sheets, capacities[0], True, subflats)
    else:
        tio.write_permutations_to_files(file_name, holds, output_folder)
        game_stacks = tio.create_game_stacks_from_permutations(holds, ups, sheets, capacities[0],
                                                               True, subflats)

    cds, sheeters = tio.write_game_stacks_to_file(file_name, game_stacks, ups, sheets, capacities[0], output_folder)

    if len(cds) > 0:
        tio.write_cd_positions_to_csv_file(part_name, file_name, cds, inst_specs[1])
        tio.write_cd_positions_to_xml_file(part_name, file_name, cds, inst_specs[1], ups, output_folder)
    return "CSVs created without incident! Let's shout both 'Whoo!' and 'Hoo!'"


if __name__ == '__main__':
    ssbb = [
        [16, 1, 64, [80, 80], False, 0, 0, '.ai'],
        ['N', 170, 4, 101, 9999, '00', ''],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['B', [150, 3, 3, 0, [0, 0, 0]], [True, 0, True, 'base', False], [0, [['', 0]]]],
        ['992-060', 'SuperSmokeBreakBingo-31965'],
        ''
    ]

    print(create_game(ssbb))
