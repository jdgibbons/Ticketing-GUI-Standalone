"""
Nonwinners: images
Instants: images
Picks: images
Holds: bingo balls (special case: verification numbers required)

This module is called from the CSV Generator when the nonwinners, instants, and picks are composed of simple images,
but the holds are composed of bingo balls. This script is called when the 'Bingo Balls' checkbox is selected on the
Bingos' Hold tab.

The create_game method is the main entry point for this module, and it is called with a list of game specs. That list
contains other lists detailing the specifications for creating the game. The lists, in order, pertain to sheets,
nonwinners, instants, picks, holds, and part and file name. There the final element is a string containing the
output folder. It will be blank if files are to be placed in the default folder.
"""
import copy

from ticketing import game_info_gui as gi
from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import verified_bingo as vb
from ticketing import image_generator as ig
from ticketing import ticket_io as tio

DEBUG = True

nw_type, insta_type, pick_type, hold_type = '', '', '', ''
suffix = ''


def create_hold_tickets(non_twos: list[int], stag_twos: list[int], non_ones: list[int],
                        stag_ones: list[int], one_eeyores: list[list[int]], zeroes: bool,
                        free_type: str, v_size: str, csv_rows: int, addl_imgs: gi.AddImages,
                        permits: int, perm_reset: bool = False) -> list[list[uTick]] | None:
    """
    Create the various either/or bingo tickets required by the game. The lists consist of the number and type
    of bingo faces, and the index of each element reflects the number of free spaces required. The exception is
    'one_eeyores,' which describes the construction and number of single-line, either/or bingo tickets. It is a
    list of three integer lists: [number of tickets, free spots, either/ors].

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
    :type addl_imgs: game_info_gui.AddImages
    :param permits: number of permutations needed
    :type permits: int
    :param perm_reset: Should the bingo list be reset for each permutation?
    :type perm_reset: bool
    :return: list of bingo tickets with various number combinations
    :rtype: list[list[BingoTicket]]
    """
    global suffix
    needs = [non_twos, stag_twos, non_ones, stag_ones, one_eeyores]
    # Create the bingo path equivalents to the required bingo ball images. If there is only
    # one permutation or the list can be reset for each one, call the creation method with reset
    # (refers to the usable faces list). Otherwise, call the method without a list reset. This
    # is required for ticketing_games that have the possibility of perms being played simultaneously.
    if perm_reset or permits == 1:
        versions = vb.create_all_bingo_permutations_with_reset(needs, permits, csv_rows, v_size != 'S', True)
        if versions[0] is None:
            return versions
    else:
        versions = vb.create_all_bingo_permutations_without_reset(needs, permits, csv_rows, v_size != 'S', True)
        if versions[0] is None:
            return versions
    # This will be the standard base for verified bingo ball tickets.
    base = f'base01{suffix}'
    is_first = True
    # Create a list for the permutations
    permies = []
    # Cycle through the bingo path permutations along with their indices to create
    # a list of lists containing bingo ball tickets.
    for index, verse in enumerate(versions):
        # Create a new ticket list for this permutation and
        # reset the ticket number count to one for each perm.
        ticks = []
        tkt = 1
        # Cycle through bingo face for this perm.
        for face in verse:
            # We're only interested in the first two elements of the list (the verification
            # number and the bingo path). There's a lot of extra information here, since this
            # calls the same creation method used for single, double, and either/or bingos.
            verify = face[0]
            bingo = face[1][0]
            # Create the image list using the base image.
            imgs = [base]
            # Cycle through the elements of this bingo path. Use each
            # to create a hold image, then append it to the image list.
            for bing in bingo:
                if bing == '':
                    imgs.append(bing)
                else:
                    imgs.append(f'hold{str(bing).zfill(2)}{suffix}')
            # Add any extra image slots needed to create a consistent csv
            # list across the different ticket types.
            pics = ig.add_additional_image_slots(addl_imgs, imgs)
            # Create a new ticket and add it to the list.
            tick = uTick(tkt, pics, [verify], index + 1, 1, is_first, 0)
            # Increment the ticket count and set the is_first flag to False.
            tkt += 1
            is_first = False
            ticks.append(tick)
        # Add this list of tickets to the permutation list.
        permies.append(ticks)
    # Return the permutation list.
    return permies


def create_instant_winners_refined(amt: list[list[int | bool]], cd_level: int, addl_imgs: gi.AddImages,
                                   permits: int) -> list[list[uTick]]:
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
    :param permits: number of permutations
    :type permits: int
    :return: A list of instant winner tickets
    :rtype: list[bTick]
    """
    global suffix
    # Create a list for the permutations and the required number of bingo rows
    permies = []
    digits = ['']

    # Create a list of images for each tier
    imgs = ig.create_tiered_image_list_augmented(amt, 'winner', suffix)
    ticks = []  # list to hold the tickets
    # Create a ticket for each image. Each element has an image and its relative cd tier
    for img in imgs:
        # Place the image in a list, then add the necessary padding to the list.
        imgs = ig.add_additional_image_slots(addl_imgs, [img[0]])
        # Create a ticket for the image
        tick = uTick('', imgs, digits, 1, 1, False)
        # If the relative cd tier associated with this image is lower than
        # the cd cutoff, set the ticket's cd tier to the image's tier.
        if img[1] <= cd_level and img[1] != 0:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')
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


def create_nonwinning_ticket(amt: int, pool_size: int, ipt: int, addl_imgs: list[gi.AddImages],
                             permits: int, firstly: bool = False) -> list[list[uTick]]:
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
    :param permits: the number of permutations needed
    :type permits: int
    :param firstly: Is this the first ticket created?
    :type firstly: bool
    :return: list of nonwinning tickets
    :rtype: list[list[bTick]]
    """
    # Create a list for the permutations and the required number of bingo rows
    permies = []
    digits = ['']
    is_first = firstly
    # Iterate for each permutation
    for j in range(permits):
        # Create a list of nonwinning image lists from the available image pool.
        nws_perms = ig.create_image_lists_from_pool_perms(1, pool_size, 'nonwinner', amt, ipt, suffix)
        # Create a list to contain created tickets.
        ticks = []
        # Cycle through the list of image lists
        for nws_perm in nws_perms:
            imgs = nws_perm
            # adjust the image list to account for images of other ticket types
            for addl in addl_imgs:
                imgs = ig.add_additional_image_slots(addl, imgs)
            # Create a ticket with this image list
            tick = uTick('', imgs, digits, j + 1, 1, is_first)
            # set the bingo type to 'O' (other)
            # Reset the first ticket flag to false, since it only needs to be active for one ticket.
            is_first = False
            # Add the ticket to the ticket list
            ticks.append(tick)
        # Add the ticket list to the permutations list
        permies.append(ticks)
    # Return the permutations.
    return permies


def calculate_image_slots(nwspec: list):
    """
    Calculates the number of additional image slots needed for different ticket types
    (non-winning, instant winner, and hold) based on the non-winning ticket specification.
    The number of hold images will always be 5. The number of instant winners will be 1.

    This function determines pre- and post-image slot adjustments based on the number
    of images per ticket (nws) in the non-winning specification. It then uses a lookup
    table (gi.add_images_lookup) to convert these adjustments into concrete slot numbers.

    :param nwspec: A list containing specifications for non-winning tickets. The relevant
                   element is nwspec[2], which specifies the number of images per ticket.
    :type nwspec: list
    :return: A list of lists, where each inner list contains pre- and post-image slot
             adjustments for non-winning, instant winner, and hold tickets, respectively.
             Format: [[nw_pre, nw_post], [insta_pre, insta_post], [hold_pre, hold_post]]
    :rtype: list[list[int]]
    """

    # Get the number of nonwinning images needed.
    nws = nwspec[2]
    # Set all image adjustments to 0.
    nw_pre = 0
    nw_post = 0
    hold_pre = 0
    hold_post = 0
    insta_pre = 0
    insta_post = 0
    # If the number of nonwinners is one, the image will reside in the same column
    # as the base image. The five bingo ball images must be accounted for. The
    # instants have the same issue.
    if nws == 1:
        nw_post = 5
        insta_post = 5
    # If there are 5 nonwinners, then they will reside in the same spaces as the
    # bingo balls, so there needs to be a column inserted before those spaces to
    # account for the base image in the first column. Instants will still have
    # five trailing image slots needed.
    elif nws == 5:
        nw_pre = -1
        insta_post = 5
    # If there are different nonwinner and hold image counts, then the holds need
    # to account for the extra nonwinner columns; the nonwinners need to account for
    # the five hold images plus the base; and the instants need to account for the
    # extra nonwinner and hold columns.
    else:
        hold_post = nws
        nw_pre = -6
        insta_post = nws + 5
    # Create GameInfo.AddImage values from the number of columns needed.
    nw_pre = gi.add_images_lookup(nw_pre)
    nw_post = gi.add_images_lookup(nw_post)
    hold_pre = gi.add_images_lookup(hold_pre)
    hold_post = gi.add_images_lookup(hold_post)
    insta_pre = gi.add_images_lookup(insta_pre)
    insta_post = gi.add_images_lookup(insta_post)
    # Return the pre- and post-column value pairs.
    return [[nw_pre, nw_post], [insta_pre, insta_post], [hold_pre, hold_post]]


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs: list):
    """
    Initializes and generates a bingo-ball style work order based on specifications from a gui-based form. This
    function supports different types of tickets, including pick and instant winners; shaded or imaged holds; and
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
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    suffix = sheet_specs.pop()
    part_name, file_name = name_specs
    ups, perms, sheets, capacities, reset_perms, subflats, schisms = sheet_specs

    nw_addls, inst_addls, hold_addls = calculate_image_slots(nw_specs)
    cd_tier = inst_specs[1]

    # Append the hold specs with pertinent info (additional image slots, perms, and
    # whether the bingo list can be reset) and then create the hold tickets. No need
    # to check quantities--we wouldn't be here if we weren't using this hold type.
    hold_specs.extend([hold_addls[1], perms, reset_perms])
    permits = create_hold_tickets(*hold_specs)

    # If there are any instant winners needed, append the necessary data to
    # the instant specs list and call the creation method.
    if inst_specs[0][0][0] > 0:
        inst_specs.extend([inst_addls[1], perms])
        i_permits = create_instant_winners_refined(*inst_specs)
        for i in range(len(i_permits)):
            permits[i].extend(i_permits[i])

    # If there are any nonwinners needed, append the necessary data to
    # the nonwinners specs list and call the creation method.
    if nw_specs[0] > 0:
        nw_specs.extend([nw_addls, perms])
        n_permits = create_nonwinning_ticket(*nw_specs)
        for i in range(len(n_permits)):
            permits[i].extend(n_permits[i])

    # Write permutations to csv files.
    tio.write_permutations_to_files(file_name, permits, False, output_folder)

    # Create game stacks from permutations.
    game_stacks = tio.create_game_stacks_from_permutations(permits, ups, sheets, capacities[0], True)

    # Write game stacks to csv files and receive cd position information for cd tickets.
    cds, sheeters = tio.write_game_stacks_to_file(file_name, game_stacks, ups, sheets, capacities[0], output_folder)

    # If any cds were returned, write out the position information to a csv file.
    if len(cds) > 0:
        tio.write_cd_positions_to_csv_file(part_name, file_name, cds, cd_tier, output_folder)
        tio.write_cd_positions_to_xml_file(part_name, file_name, cds, cd_tier, ups, output_folder)

    print('whatevs')


if __name__ == '__main__':
    specs = [
        [4, 1, 76, [56, 56], False, 0, 0, '.pdf'],
        ['I', 905, 9, 3],
        ['I', [[5, False]], 0],
        ['I', [[0, False]]],
        ['B', [0, 0, 0, 0], [0, 0, 0, 0], [154, 0, 0, 0], [0, 0, 0, 0], [[0]], True, 'Images', 'S', 1],
        ['993-007', 'MegaBalls-53704'],
        ''
    ]

    modified_megaballs = [
        [4, 1, 76, [56, 56], False, 0, 0, '.pdf'],
        ['I', 905, 9, 3],
        ['I', [[5, False]], 0],
        ['I', [[0, False]]],
        ['B', [0, 0, 0, 0], [0, 0, 0, 0], [100, 50, 4, 0], [0, 0, 0, 0], [[0]], True, 'Images', 'S', 1],
        ['993-007', 'MegaBalls-53704'],
        ''
    ]

    create_game(modified_megaballs)
