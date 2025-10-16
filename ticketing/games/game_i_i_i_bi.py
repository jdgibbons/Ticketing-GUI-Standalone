"""
Nonwinners: images
Instants: images
Picks: images
Holds: verified bingos

This module is called from the CSV Generator when the nonwinners, instants, and picks are composed of simple images,
but the holds are composed of verified bingos.

The create_game method is the main entry point for this module, and it is called with a list of game specs. That list
contains other lists detailing the specifications for creating the game. The lists, in order, pertain to sheets,
nonwinners, instants, picks, holds, and part and file name. There the final element is a string containing the
output folder. It will be blank if files are to be placed in the default folder.
"""
import copy

from ticketing import game_info as gi
from ticketing.bingo_ticket import BingoTicket as bTick
from ticketing import verified_bingo as vb
from ticketing import image_generator as ig
from ticketing import ticket_io as tio

DEBUG = True

nw_type, insta_type, pick_type, hold_type = '', '', '', ''
suffix = ''


def create_hold_tickets(non_twos: list[int], stag_twos: list[int], non_ones: list[int],
                        stag_ones: list[int], one_eeyores: list[list[int]], zeroes: bool,
                        free_type: str, v_size: str, csv_rows: int, addl_imgs: gi.AddImages,
                        permits: int, perm_reset: bool = False) -> list[list[bTick]] | None:
    """
    Create the various either/or bingo tickets required by the game. The lists consist of the number and type
    of bingo faces, and the index of each element reflects the number of free spaces required. The exception is
    'one_eeyores,' which describes the construction and number of single-line, either/or bingo tickets. It is a
    list of three integer lists, comprised of [number of tickets, free spots, either/ors].

    :param addl_imgs:
    :param non_twos: Number of nonstaggered, two-line tickets
    :type non_twos: list[int]
    :param stag_twos: number of staggered, two-line tickets
    :type stag_twos: list[int]
    :param non_ones: number of nonstaggered, one-line tickets
    :type non_ones: list[int]
    :param stag_ones: number of staggered, one-line tickets
    :type stag_ones: list[int]
    :param one_eeyores: number of single-line, either/or spotted tickets
    :type one_eeyores: list[list[int]]
    :param zeroes: Are leading zeroes required?
    :type zeroes: bool
    :param free_type: type of free spots (images, text, both, or neither)
    :type free_type: str
    :param v_size: size of the verified list (standard (9000) or extended (27000))
    :type v_size: str
    :param csv_rows: number of integer rows to be used in the csv file
    :type csv_rows: int
    :param addl_imgs: extra slots to be added to the image list
    :type addl_imgs: game_info.AddImages
    :param permits: number of permutations needed
    :type permits: int
    :param perm_reset: Should the bingo list be reset for each permutation?
    :type perm_reset: bool
    :return: list of bingo tickets with various number combinations
    :rtype: list[list[BingoTicket]]
    """
    needs = [non_twos, stag_twos, non_ones, stag_ones, one_eeyores]
    # If there is only one permutation or the list can be reset for each one, call the creation
    # method with reset (refers to the usable faces list). Otherwise, call the method without reset.
    if perm_reset or permits == 1:
        versions = vb.create_all_bingo_permutations_with_reset(needs, permits, csv_rows, v_size != 'S', True)
        if versions[0] is None:
            return versions
    else:
        versions = vb.create_all_bingo_permutations_without_reset(needs, permits, csv_rows, v_size != 'S', True)
        if versions[0] is None:
            return versions
    # Obviously, this will have to be updated to reflect the various image possibilities.
    base = ['base01.ai']
    # Have the ticket constructor create the csv field names list on the first pass. I may
    # change this to a passed parameter, but holds are always first for now.
    is_first = True
    permies = []
    # Cycle through the faces for each pseudo-bingo type and create tickets from them.
    for index, verse in enumerate(versions):
        tkt = 1
        ticks = []
        # Cycle through each face for this pseudo-bingo type.
        for face in verse:
            # Set the bingo type to nonstaggered and change it if necessary.
            b_type = 'N'
            # Choose the base image and adjust the number of rows as
            # required by the expected row count.
            # If there are 3 rows expected, it's either an either/or scenario,
            # or there is a mixture of single and double row bingos.
            if csv_rows == 3:
                # If there's only one row, this is a single bingo line. Assign the base,
                # then append two rows to account for the rows to be used for double spaces.
                if len(face[1]) == 1:
                    face[1] += [['', '', '', '', ''], ['', '', '', '', '']]
                    base = ['base01.ai']
                # If there are two rows, cycle through the spots to determine which kind.
                # If there are columns with one free and one filled spot, it is a staggered
                # double and the bingo type needs to be set to 'S'. Either way, assign the
                # base, then prepend a singe row to account for the single line bingos spaces.
                elif len(face[1]) == 2:
                    # The column check has been moved to its own method. It will return 'S'
                    # for staggered and 'N' for nonstaggered.
                    b_type = determine_b_type(face)
                    face[1].insert(0, ['', '', '', '', ''])
                    base = ['base02.ai']
                # This is an either/or ticket, since only those types will have all three rows
                # populated. Assign the base, since all three rows are already accounted for.
                elif len(face[1]) == 3:

                    base = ['base03.ai']
                    b_type = 'E'
            # This is a double-line bingo game. Assign the base.
            elif csv_rows == 2:
                base = ['base02.ai']
            # This is a single-line bingo game. Assign the base.
            elif csv_rows == 1:
                base = ['base01.ai']
            # Add the additional image slots needed.
            images = ig.add_additional_image_slots(addl_imgs, base)
            # Create a new ticket, set the free and bingo types, then
            # add it to the tickets list.
            tick = bTick(tkt, face[0], face[1], images, zeroes, index + 1, 1, is_first)
            tick.set_free_type(free_type)
            tick.set_bingo_type(copy.deepcopy(b_type))
            ticks.append(tick)
            # Set the first flag to false, since the csv fields only need to be created once.
            is_first = False
            # Increase the ticket number.
            tkt += 1
        # Add the permutation to the permutation list.
        permies.append(ticks)
    # Return the permutation list.
    return permies


def determine_b_type(facial):
    """
    Determines the bingo type based on whether there is a blank and a filled
    spot in the same column.
    :param facial:
    :return:
    """
    # Cycle through the two passed lists and compare their respective
    # values in each spot.
    for a, b in zip(facial[1][0], facial[1][1]):
        # Use the xor operator to determine if there is a column
        # with one blank and one filled spot.
        if bool(a.strip()) ^ bool(b.strip()):
            return 'S'
    # Return 'N' (nonstaggered) if no staggered column was found.
    return 'N'


def create_instant_winners_refined(amt: list[list[int, bool]], cd_level: int, addl_imgs: gi.AddImages,
                                   bingo_rows: int, permits: int) -> list[list[bTick]]:
    """
    Create a list of instant winner tickets consisting of one image. Also, set the
    tickets' cd tier value if it's below the threshold (cd_level). The 'refinement'
    here consists of changing the way the permutations are produced. The first
    permutation is created normally, then a deep copy is made for each of the
    remaining ones.

    :param amt: list of number of images for each tier level
    :type amt: list[int]
    :param cd_level: the lowest level ticket that needs a cd value
    :type cd_level: int
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param bingo_rows: number of bingo rows to be accounted for in the csv output
    :type bingo_rows: int
    :param permits: number of permutations
    :type permits: int
    :return: A list of instant winner tickets
    :rtype: list[bTick]
    """
    # Create a list for the permutations and the required number of bingo rows
    permies = []
    digits = []
    for _ in range(bingo_rows):
        digits.append(['', '', '', '', ''])

    # Create a list of images for each tier
    imgs = ig.create_tiered_image_list_augmented(amt, 'winner')
    ticks = []  # list to hold the tickets
    # Create a ticket for each image. Each element has an image and its relative cd tier
    for img in imgs:
        # Place the image in a list, then add the necessary padding to the list.
        imgs = ig.add_additional_image_slots(addl_imgs, [img[0]])
        # Create a ticket for the image
        tick = bTick('', '', digits, imgs, False, 1, 1, False)
        # If the relative cd tier associated with this image is lower than
        # the cd cutoff, set the ticket's cd tier to the image's tier.
        if img[1] <= cd_level and img[1] != 0:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')
        # Set the bingo type to 'O' (other).
        tick.set_bingo_type('O')
        # Add the ticket to the ticket's list.
        ticks.append(tick)

    # Add the ticket list to the permutation list.
    permies.append(ticks)
    # Create a copy of the first permutation for the remaining ones.
    for j in range(1, permits):
        temp_ticks = copy.deepcopy(ticks)
        # Cycle through each ticket and reset its permutation to the current one.
        for tick in temp_ticks:
            tick.reset_permutation(j + 1)
        # Add the new copy to the permutations list.
        permies.append(temp_ticks)

    # return the permutations
    return permies


def calculate_image_slots(holders, no_wins, free_image):
    """
    Calculates the prefix and suffix AddImage options based on the given data.

    :param holders: A list of lists representing bingo hold values.
    :param no_wins: A list containing information pertaining to nonwinners.
    :param free_image: are free spaces represented with images?
    :type free_image: bool
    :return: A list containing two AddImages enum members representing required, extra image-slots: [prefix, suffix].
    :rtype: list[AddImages]
    """
    # Initially set the image slot values to zero. Only change them if the
    non_base_image_slots = 0
    prefix_value = 0
    # If free spaces are represented by images, calculate how many extra columns are needed.
    if free_image:
        # Calculate non_base_image_slots, finding the index of the first nonzero value from the end.
        # The highest index indicates how many additional columns will be needed.
        non_base_image_slots = 0
        for sublist in holders[:4]:
            for indie, x in enumerate(reversed(sublist)):
                if x != 0:
                    non_base_image_slots = max(non_base_image_slots, len(sublist) - indie - 1)
                    break
        # If there are either/or tickets, get the maximum number of images needed
        # by adding the number of free and either/or spaces for each iteration and
        # using the highest as the number needed.
        if holders[4][0][0] > 0:
            for hold in holders[4]:
                amt, frees, eithers = hold
                non_base_image_slots = max(non_base_image_slots, frees + eithers)
        # If the number of images on nonwinners is greater than one, there needs to be
        # an additional column added for each of them. Otherwise, the image will go in
        # the same container as the base image, so no additional columns are needed.
        if no_wins[2] > 1:
            # The hold images are placed before the nonwinners, so the prefix needs to reflect that.
            # Add the number of nonwinners to the non-base-image slots.
            prefix_value = -(non_base_image_slots + 1)
            non_base_image_slots += no_wins[2]
    # If the frees are not represented by images, then only the nonwinning images matter.
    # If there is only one image then both values remain zero. Otherwise, the base image
    # must be in the prefix value and the non-base-image value is equal to the number of
    # nonwinning images per ticket.
    elif no_wins[2] > 1:
        prefix_value = -1
        non_base_image_slots = no_wins[2]
    # Get the AddImages value for each value
    prefix = gi.add_images_lookup(prefix_value)
    suffix = gi.add_images_lookup(non_base_image_slots)
    # Return the prefix and suffix
    return [prefix, suffix]


def create_pick_winners(amt_list: list[int], tkt: int, addl_imgs: gi.AddImages, bingo_rows: int,
                        permits: int, first: bool = False, uniq: bool = False) -> list[list[bTick]]:
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
    :param bingo_rows: Number of number slots needed in the csv output.
    :type bingo_rows: int
    :param permits: Number of permutations
    :type permits: int
    :param first: Does the first ticket need to set the csv fields?
    :type first: bool
    :param uniq: Does each tier level have unique images?
    :type uniq: bool
    :return: A list of pick winner tickets
    :rtype: list[UniversalTicket]
    """
    # Create a list for the permutations and the required number of bingo rows
    permies = []
    img_list = []
    # Create a placeholder for the number slots
    nums = []
    for _ in range(bingo_rows):
        nums.append(['', '', '', '', ''])
    # If there's only one dimension to the list, then create this as if it were a normal hold.
    # Otherwise, create a tiered image list, even though all tickets will receive CDs.
    if len(amt_list) == 1:
        imgs = ig.create_prefixed_images(1, amt_list[0], 'pick', uniq)
        for img in imgs:
            img_list.append([img, 1])
    else:
        img_list = ig.create_tiered_image_list(amt_list, 'pick', uniq)
    cull_ticket = first
    # Iterate for each permutation
    for x in range(permits):
        # Create a list to contain this permutation's tickets.
        ticks = []
        # Cycle through the images list. Use each image name (img[0]) and
        # ticket tier level (img[1]) to create a new ticket.
        for img in img_list:
            # Add additional slots to account for other images in the csv file
            pics = ig.add_additional_image_slots(addl_imgs, [img[0]])
            # Create a new ticket with ticket number, image (and empty slots), number placeholder,
            # perm, up,  and whether to create the csv fields.
            ticket = bTick(tkt, '', nums, pics, False, 1, 1, cull_ticket)
            cull_ticket = False
            tkt += 1
            # Reset the cd type, cd tier, and bingo type
            ticket.reset_cd_type('P')
            ticket.reset_cd_tier(img[1])
            ticket.set_bingo_type('O')
            # Add the ticket to the ticket list
            ticks.append(ticket)
        # Add the ticket list to the permutations list.
        permies.append(ticks)
    # Return the permutations.
    return permies


def create_nonwinning_ticket(amt: int, pool_size: int, ipt: int, addl_imgs: gi.AddImages,
                             bingo_rows: int, permits: int, firstly: bool = False) -> list[list[bTick]]:
    """
    Create a list of nonwinning tickets from a pool of images.

    :param amt: the number of tickets needed
    :type amt: int
    :param pool_size: the number of images available to use
    :type pool_size: int
    :param ipt: the number of images on each ticket
    :type ipt: int
    :param addl_imgs: the extra slots needed to pad the csv output
    :type addl_imgs: gi.AddImages
    :param bingo_rows: the number of bingo rows needed in the csv output
    :type bingo_rows: int
    :param permits: the number of permutations needed
    :type permits: int
    :param firstly: Is this the first ticket created?
    :type firstly: bool
    :return: list of nonwinning tickets
    :rtype: list[list[bTick]]
    """
    # Create a list for the permutations and the required number of bingo rows
    permies = []
    digits = []
    is_first = firstly
    for _ in range(bingo_rows):
        digits.append(['', '', '', '', ''])
    # Iterate for each permutation
    for j in range(permits):
        # Create a list of nonwinning image lists from the available image pool.
        nws_perms = ig.create_image_lists_from_pool_perms(1, pool_size, 'nonwinner', amt, ipt)
        # Create a list to contain created tickets.
        ticks = []
        # Cycle through the list of image lists
        for nws_perm in nws_perms:
            # adjust the image list to account for images of other ticket types
            imgs = ig.add_additional_image_slots(addl_imgs, nws_perm)
            # Create a ticket with this image list
            tick = bTick('', '', digits, imgs, False, j + 1, 1, is_first)
            # set the bingo type to 'O' (other)
            tick.set_bingo_type('O')
            # Reset the first ticket flag to false, since it only needs to be active for one ticket.
            is_first = False
            # Add the ticket to the ticket list
            ticks.append(tick)
        # Add the ticket list to the permutations list
        permies.append(ticks)
    # Return the permutations.
    return permies


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs: list, bugging: bool = False):
    """
    Initializes and generates a bingo-style work order based on specifications from a gui-based form. This
    function supports different types of tickets including pick and instant winners, non-winners, and a
    variety of bingo tickets. Finally, it writes the generated tickets and game stacks to specified output files.

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
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    suffix = sheet_specs.pop()
    part_name, file_name = name_specs
    ups, perms, sheets, capacities, reset_perms, subflats, schisms = sheet_specs

    nw_addls, hold_addls = calculate_image_slots(hold_specs, nw_specs, hold_specs[6] in ['Images', 'Both'])
    inst_addls, pick_addls = [hold_addls] * 2
    cd_tier = inst_specs[1]
    bingrows = hold_specs[8]
    num_slots = 5 * bingrows

    # Create the hold tickets (there is no quantity check; we wouldn't be
    # here if there were no bingo holds).
    hold_specs.extend([hold_addls, perms, reset_perms])
    permits = create_hold_tickets(*hold_specs)

    # If there are any instant winners needed, append the necessary data to
    # the instant specs list and call the creation method.
    if inst_specs[0][0][0] > 0:
        inst_specs.extend([inst_addls, bingrows, perms])
        i_permits = create_instant_winners_refined(*inst_specs)
        for i in range(len(i_permits)):
            permits[i].extend(i_permits[i])

    # If there are any nonwinners needed, append the necessary data to
    # the nonwinners specs list and call the creation method.
    if nw_specs[0] > 0:
        nw_specs.extend([nw_addls, bingrows, perms])
        n_permits = create_nonwinning_ticket(*nw_specs)
        for i in range(len(n_permits)):
            permits[i].extend(n_permits[i])

    # Write the permutations to csv files.
    tio.write_permutations_to_files(file_name, permits, False, output_folder)

    # Create the needed game stacks from the permutations.
    game_stacks = tio.create_game_stacks_from_permutations(permits, ups, sheets, capacities[0], True)

    # Write the ticketing_games stacks to csv files and receive cd position data for all cd tickets.
    cds, sheeters = tio.write_game_stacks_to_file(file_name, game_stacks, ups, sheets, capacities[0], output_folder)

    # If any cds were returned, write out the position information to a csv file.
    if len(cds) > 0:
        tio.write_cd_positions_to_csv_file(part_name, file_name, cds, cd_tier, output_folder)
        tio.write_cd_positions_to_xml_file(part_name, file_name, cds, cd_tier, ups, output_folder)

    print('whatevs.')


if __name__ == '__main__':
    carnival = [
        [28, 4, 133, [56, 56], False, 0, 0],
        ['I', 0, 9, 1],
        ['I', [[3, False]], 0],
        ['I', [[0, False]]],
        ['B', [179, 70, 14, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [[0]], True, 'Images', 'S', 2],
        ['006-142', 'Carnival-52944'],
        ''
    ]

    specs_output = [
        [28, 4, 133, [56, 56], False, 0, 0],
        ['I', 0, 9, 1],
        ['I', [[3, False]], 0],
        ['I', [[0, False]]],
        ['B', [179, 70, 14, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [[0]], True, 'Images', 'E', 2],
        ['006-142', 'Carnival-52944'],
        'C:/_destination_one'
    ]

    more_stuff = [
        [28, 2, 133, [56, 56], False, 0, 0],
        ['I', 59, 9, 3],
        ['I', [[1, False], [3, False], [8, False], [15, False]], 2],
        ['I', [[0, False]]],
        ['B', [120, 50, 10, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [[0]], False, 'Images', 'S', 2],
        ['000-011', 'ZZtestme-10230'],
        ''
    ]

    sucker = [
        [4, 1, 75, [56, 56], False, 0, 0, '.ai'],
        ['I', 776, 9, 3],
        ['I', [[1, False], [1, False], [2, False], [70, False]], 0],
        ['I', [[0, False]]],
        ['B', [0, 0, 0, 0], [100, 50, 30, 20], [0, 0, 0, 0], [0, 0, 0, 0], [[0, 0, 0]], False, 'Images', 'E', 2],
        ['000', 'testify'],
        ''
    ]

    sucker_plus_eeyores = [
        [4, 1, 75, [56, 56], False, 0, 0, '.ai'],
        ['I', 676, 9, 3],
        ['I', [[1, False], [1, False], [2, False], [70, False]], 0],
        ['I', [[0, False]]],
        ['B',
         [0, 0, 0, 0],
         [100, 50, 30, 20],  # Double-line, staggered bingos
         [0, 0, 0, 0],
         [0, 0, 0, 0],
         [
             [50, 0, 1],  # either/ors, 0 frees, 1 double
             [20, 0, 2],  # either/ors, 0 frees, 2 doubles
             [15, 1, 1],  # either/ors, 1 free,  1 double
             [10, 1, 2],  # either/ors, 1 free,  2 doubles
             [5, 2, 2]],  # either/ors, 2 frees, 2 doubles
         False, 'Images', 'E', 3],
        ['010-220', 'TestBingo-55443'],
        ''
    ]

    create_game(sucker_plus_eeyores)
