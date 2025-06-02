import copy

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import image_generator as ig
from ticketing import game_info as gi
from ticketing import ticket_io as tio
# from helpers import extract_ticket_types

import random as rn
import itertools as it

DEBUG = True

nw_type, insta_type, pick_type, hold_type = '', '', '', ''


def create_imaged_nonwinner_tickets(amt: int, q_nw_image_pool: int, pics_per_ticket: int,
                                    add_imgs: list[gi.AddImages], first: bool, numerals: int = 0) -> list[uTick]:
    """
    Create a list of nonwinner tickets consisting of one or more images.

    :param amt: Number of tickets needed.
    :type amt: int
    :param q_nw_image_pool: Number of images in the nonwinner image pool
    :type q_nw_image_pool: int
    :param pics_per_ticket: Number of images on each nonwinner ticket.
    :type pics_per_ticket: int
    :param add_imgs: Additional image slots required to pad the csv output.
    :type add_imgs: list[gi.AddImages]
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :param numerals: Number of numeral slots needed in the csv output.
    :type numerals: int
    :return: A list of nonwinner tickets.
    :rtype: list[UniversalTicket]
    """
    numbs = [''] * numerals
    nw_image_lines = ig.create_image_lists_from_pool(1, q_nw_image_pool, 'nonwinner', amt, pics_per_ticket)
    ticks = []
    for nw in nw_image_lines:
        pics = nw
        for add in add_imgs:
            pics = ig.add_additional_image_slots(add, list(pics))
        ticks.append(uTick('', pics, numbs, 1, 1, first))
        first = False
    return ticks


def create_instant_winners(amt: list[list[int, bool]], cd_tier: int, tkt: int | str,
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
    # Get a list of lists containing the image name and tier level for the winning tickets.
    imgs = ig.create_tiered_image_list_augmented(amt, 'winner')
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


def create_pick_winners(amt_list: list[int], tkt: int, addl_imgs: list[gi.AddImages], nummies: int,
                        first: bool = False, uniq: bool = False) -> list[uTick]:
    """
    Create a list of pick winner tickets consisting of one image and set the ticket's cd
    tier value to its accompanying tier level if the level. Pick's always have CDs (at
    least I think they do).

    :param amt_list: list containing the number of tickets for each ticket tier (usually one)
    :type amt_list: list[int]
    :param tkt: First ticket number.
    :type tkt: int
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param nummies: Number of number slots needed in the csv output.
    :type nummies: int
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :param uniq: Does each tier level have unique images?
    :type uniq: bool
    :return: A list of pick winner tickets
    :rtype: list[UniversalTicket]
    """
    ticks = []
    img_list = []
    # Create a placeholder for the number slots
    nums = [''] * nummies
    # If there's only one dimension to the list, then create this as if it were a normal hold.
    # Otherwise, create a tiered image list, even though all tickets will receive CDs.
    if len(amt_list) == 1:
        imgs = ig.create_prefixed_images(1, amt_list[0], 'pick', uniq)
        for img in imgs:
            img_list.append([img, 1])
    else:
        img_list = ig.create_tiered_image_list(amt_list, 'pick', False)
    cull_ticket = first
    # Cycle through the images list. Use each image name (img[0]) and
    # ticket tier level (img[1]) to create a new ticket.
    for img in img_list:
        # Add additional slots to account for other images in the csv file
        pics = [img[0]]
        for add in addl_imgs:
            pics = ig.add_additional_image_slots(add, pics)
        # Create a new ticket with ticket number, image (and empty slots), number placeholder,
        # perm, up,  and whether to create the csv fields.
        ticket = uTick(tkt, pics, nums, 1, 1, cull_ticket)
        cull_ticket = False
        if tkt != '' and isinstance(tkt, int):
            tkt += 1
        ticket.reset_cd_type('P')
        ticket.reset_cd_tier(img[1])
        ticks.append(ticket)
    return ticks


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
    # Get a list of all downlines of the desired number of spots
    bingos = ig.create_bingo_downlines(bpt)
    # If there aren't enough downlines, return None.
    if len(bingos) < amt:
        return None
    # Shuffle the list and return the number of downlines needed.
    for _ in range(rn.randint(5, 10)):
        rn.shuffle(bingos)
    return bingos[0: amt]


def create_hold_tickets(bb_options: list[int], bool_options: list[bool | str],
                        sup_holds: list[int | list[list[str | int]]],
                        tkt: int | str, addl_bb_imgs: list[gi.AddImages], addl_sup_imgs: list[gi.AddImages],
                        permits: int, first: bool) -> list[list[uTick]] | None | str:
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
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :return: list of hold tickets
    :rtype: list[uTick] | None | str
    """
    # Breakdown some of the passed lists into their component parts.
    bb_amt, bpt, spt, fill_pool, frees = bb_options
    downs, shazams, sortie, base = bool_options
    perms = []
    # If there are needed bingo ball type holds, create them.
    if bb_amt > 0:
        perms = create_bingo_ball_tickets(bb_amt, bpt, spt, downs, permits, first, 0, fill_pool,
                                          addl_bb_imgs, tkt, shazams, base, sortie)
        first = False
    # If there are supplemental holds needed, create those.
    if sup_holds[0] > 0:
        ticks = create_single_image_holds(sup_holds[1], addl_sup_imgs, first)
        first = False
        for index, perm in perms:
            for tick in ticks:
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
    ticks = []
    numbs = []
    # Cycle through the list of prefixes and quantities and create a list of tickets for each one.
    for sup in suppers:
        # Create the full prefix then create the list of images for this downline.
        prefix = f'{sup[0]}'
        pics = ig.create_prefixed_images(1, sup[1], prefix, True)
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
    :return: list of hold tickets
    :rtype: list[uTick]
    """
    perms = []
    numbs = [''] * nums
    # Create a list to represent the position of all the tickets created for a single permutation.
    # This list will be used to randomly select which tickets receive shazam images (if any).
    tick_places = list(range(bb_amt))
    if downs:
        bangles = [create_downline_image_lists(bb_amt, bpt)]
    else:
        # bangles = ig.create_bingo_ball_image_list(bb_amt, bpt, 'hold')
        bangles = ig.create_bingo_ball_image_permutations(bb_amt, bpt, permits, 'hold', sortie)
    for index, bingos in enumerate(bangles):
        # Shuffle the ticket position list, then take a slice of the list equal to the
        # number of Shazams needed. Sort the list and use it to flag which tickets
        # will receive a shazam image (again, only if there are any).
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(tick_places)
        places = tick_places[0: shazams]
        places.sort(reverse=True)
        # This will keep track of the index of the shazam position list.
        shizzle = copy.deepcopy(shazams)
        ticks = []
        # If there are other images besides the bingo balls, add them here.
        if bpt != spt:
            # Create the extra images, most likely from a nonwinner pool.
            nw_imgs = ig.create_image_pool(1, nw_pool, 'nonwinner')
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
            pics = [''] if basic in ['none.ai', 'blank.ai', '0.ai', '000.ai'] else [basic]
            # If shazams are a part of this game . . .
            if shazams > 0:
                # If there are still shazams left to be added . . .
                if shizzle > 0:
                    # If the list index equals the current shazam position value,
                    # add the next shazam in the cycle to the image list.
                    if innie == places[shizzle - 1]:
                        pics.append(f'shazam{str(next(pos_cycle)).zfill(2)}.ai')
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
    nws_needed = nws[2]
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
    # if the nonwinners contain more than one image
    if nws_needed != 1:
        # If holds and nonwinners fill the same spaces, set the pre-nonwinners and
        # pre-holds to -1, and set the post instants to the number of hold spaces.
        if holds_needed == nws_needed:
            nw_pre = -1
            inst_post = holds_needed
            if holds_supplemental > 0:
                nw_pre -= 1
                inst_post += 1
        # If the number of holds equals one, then set post-instants and post-holds
        # the number of nonwinners, and set pre-nonwinners to -1.
        elif holds_needed == 1:
            inst_post = nws_needed
            hold_post = nws_needed
            nw_pre = -1
        # The holds and nonwinners are different, so they'll each need their own slots.
        # Set the pre-nonwinners to the number of holds plus one (for instant/base), and
        # the post-holds to the number of nonwinners.
        else:
            nw_pre = -(holds_needed + 1)
            hold_post = nws_needed
            inst_post = holds_needed + nws_needed
            if holds_supplemental > 0:
                nw_pre -= 1
                inst_post += 1
    # if nonwinners are 1 image and the holds contain more than 1
    elif holds_needed != 1:
        nw_post = holds_needed
        inst_post = holds_needed
        if holds_supplemental > 0:
            nw_post -= 1
            inst_post += 1
    add_nw = [gi.add_images_lookup(nw_pre), gi.add_images_lookup(nw_post)]
    add_hold = [gi.add_images_lookup(hold_pre), gi.add_images_lookup(hold_post)]
    add_inst = [gi.add_images_lookup(inst_pre), gi.add_images_lookup(inst_post)]
    return [add_nw, add_hold, add_inst]


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


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
    # Extract the separate spec types and place them in their own variables.
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    # Extract the high-level game information from the sheet_specs
    ups, perms, sheets, capacities, reset_perms, subflats, schisms = sheet_specs
    # Get file and part names from name_specs
    part_name, file_name = name_specs
    # Get additional image slots needed for the various ticket types to maintain
    # a consistent csv.
    addl_nw, addl_hold, addl_inst = calculate_image_slots(nw_specs, hold_specs)
    # Do these ticket types need to contain a number field. This may eventually be
    # set by passed parameters.
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
        inst_specs.extend([tkt_no, addl_inst, 0, first_timer])
        instants.extend(create_instant_winners(*inst_specs))
        first_timer = False
    picks = []
    if pick_specs[0][0][0] > 0:
        if pick_tkt_int:
            if inst_tkt_int:
                tkt_no = len(tickets) + 1
            else:
                tkt_no = 1
        else:
            tkt_no = ''
        picks.extend(create_pick_winners(pick_specs[0], tkt_no, addl_inst,
                                         0, first_timer, pick_specs[1]))
        first_timer = False
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
        hold_specs.extend([tkt_no, addl_hold, addl_inst, perms, first_timer])
        holds = create_hold_tickets(*hold_specs)
        if isinstance(holds, str) or holds is None:
            return holds
        first_timer = False
    nonwinners = []
    if nw_specs[0] > 0:
        nw_specs.extend([addl_nw, first_timer])
        nonwinners = create_imaged_nonwinner_tickets(*nw_specs)
        first_timer = False

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
    holy_k_fun = [
        [40, 4, 83, [80, 80], False, 0, 0],
        ['I', 0, 9, 1],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['B', [121, 3, 3, 75, ['0', '0', '0', '0', '0']], [False, False],
         [45, [['red', 15], ['white', 15], ['blue', 15]]]],
        ['000', 'test-10122'],
        ''
    ]

    holy_k = [
        [40, 4, 83, [80, 80], False, 0, 0],
        ['I', 0, 9, 1],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['B', [166, 3, 3, 75, ['0', '0', '0', '0', '0']], [False, False], [0, [['', 0]]]],
        ['000-135', 'HolyKielbasa-31681'],
        ''
    ]

    holy_k_new = [
        [40, 4, 83, [80, 80], False, 0, 0],
        ['I', 0, 9, 1],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['B', [166, 3, 3, 9, ['0', '0', '0']], [False, False], [0, [['', 0]]]],
        ['000', 'test-000'],
        ''
    ]

    shaz = [
        [8, 8, 100, [56, 56], False, 0, 0],
        ['I', 622, 10, 3],
        ['I', [[1, False], [4, False], [48, False]], 0],
        ['I', [[0, False]]],
        ['B', [25, 3, 3, 10, [0, 0, 0]], [False, 3, False, 'base01.ai'], [0, [['', 0]]]],
        ['006-171', 'ShazamBalls-52655'],
        ''
    ]

    mbga = [
        [32, 4, 80, [64, 64], False, 0, 0],
        ['I', 130, 9, 3],
        ['I', [[5, False]], 0],
        ['I', [[0, False]]],
        ['B', [25, 3, 3, 0, [0, 0, 0]], [True, 0, False, 'base.ai'], [0, [['', 0]]]],
        ['000', 'MakeBingoGreatAgain-4858'],
        ''
    ]

    chick = [
        [8, 1, 43, [56, 56], False, 0, 0],
        ['I', 151, 9, 3],
        ['I', [[0, False]], 0],
        ['I', [[0, False]]],
        ['B', [150, 3, 3, 0, [0, 0, 0]], [True, 0, True, 'none.ai'], [0, [['', 0]]]],
        ['000', 'ChickinPickin-53706'],
        ''
    ]

    create_game(chick)
