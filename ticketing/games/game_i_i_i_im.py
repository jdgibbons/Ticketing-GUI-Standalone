"""
Nonwinners: Image
Instants: Image
Picks: Image
Holds: Image

This module is called from the CSV Generator when all tickets are composed of simple images.
Instants, picks, and holds are assumed to be single images, while the nonwinners can be
composed of as many images as desired.

The create_game method is the main entry point for this module, and it is called with a list of game specs. That list
contains other lists detailing the specifications for creating the game. The lists, in order, pertain to sheets,
nonwinners, instants, picks, holds, and part and file name. There the final element is a string containing the
output folder. It will be blank if files are to be placed in the default folder.
"""
from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import image_generator as ig
from ticketing import game_info as gi
from ticketing import ticket_io as tio

DEBUG = True
nw_type, insta_type, pick_type, hold_type = '', '', '', ''
suffix = ''


def create_instant_winners(amt: list[list[int | bool]], cd_tier: int, tkt: int, addl_imgs: gi.AddImages,
                           nummies: int, is_first=True) -> list[uTick]:
    """
    Create a list of instant winner tickets consisting of one image and set the ticket's
    CD value equal to its tier level if the level is equal to or less than the cd_tier.

    :param amt: list containing the number of tickets for each ticket tier
    :type amt: list[int]
    :param cd_tier: tier level at which CDs are required (zero if none)
    :type cd_tier: int
    :param tkt: First ticket number.
    :type tkt: int
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param nummies: Number of number slots needed in the csv output.
    :type nummies: int
    :param is_first: Does the first ticket need to set the csv fields?
    :type is_first: bool
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
    # cull_headers = is_first
    # Cycle through the list of image name/tier level lists and create a ticket for each one.
    for img in imgs:
        # Create a list that contains the image and any additional image slots needed.
        # (This is used to reserve slots for three-image nonwinner tickets, if necessary.)
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])
        # Create a new ticket with ticket number, pics, number slots, perm, up, and whether to create the csv fields.
        tick = uTick(tkt, pics, nums, 1, 1, is_first)
        # Set the ticket's cd tier level if it's less than or equal to the passed cd tier.
        if img[1] <= cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')
        # Add the ticket to the list, set the cull ticket flag to False, and increment the ticket number.
        ticks.append(tick)
        is_first = False
        tkt += 1
    # Return the list of instant winner tickets.
    return ticks


def create_pick_winners(amt_list: list[list[int | bool]], tkt: int, addl_imgs: gi.AddImages, nummies: int,
                        first: bool = False, permit: int = 1) -> list[uTick]:
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
    :param permit: permutation number
    :type permit: int
    :return: A list of pick winner tickets
    :rtype: list[UniversalTicket]
    """
    global suffix
    ticks = []
    img_list = []
    # Create a placeholder for the number slots
    nums = [''] * nummies
    # If there's only one dimension to the list, then create this as if it were a normal hold.
    # Otherwise, create a tiered image list, even though all tickets will receive CDs.
    if len(amt_list) == 1:
        imgs = ig.create_prefixed_images(1, amt_list[0][0], 'pick', amt_list[0][1], suffix)
        for img in imgs:
            img_list.append([img, 1])
    else:
        # for amt in amt_list:
        img_list.extend(ig.create_tiered_image_list_augmented(amt_list, 'pick', suffix))
    cull_ticket = first
    # Cycle through the images list. Use each image name (img[0]) and
    # ticket tier level (img[1]) to create a new ticket.
    for img in img_list:
        # Add additional slots to account for other images in the csv file
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])
        # Create a new ticket with ticket number, image (and empty slots), number placeholder,
        # perm, up,  and whether to create the csv fields.
        ticket = uTick(tkt, pics, nums, permit, 1, cull_ticket)
        cull_ticket = False
        tkt += 1
        ticket.reset_cd_type('P')
        ticket.reset_cd_tier(img[1])
        ticks.append(ticket)
    return ticks


def create_imaged_nonwinner_tickets(amt: int, q_nw_image_pool: int, pics_per_ticket: int,
                                    add_imgs: gi.AddImages, numerals: int = 0, is_first: bool = False) -> list[uTick]:
    """
    Create a list of nonwinner tickets consisting of one or more images.

    :param amt: Number of tickets needed.
    :type amt: int
    :param q_nw_image_pool: Number of images in the nonwinner image pool
    :type q_nw_image_pool: int
    :param pics_per_ticket: Number of images on each nonwinner ticket.
    :type pics_per_ticket: int
    :param add_imgs: Additional image slots required to pad the csv output.
    :type add_imgs: gi.AddImages
    :param numerals: Number of numeral slots needed in the csv output.
    :type numerals: int
    :param is_first: Does the first ticket need to set the csv fields?
    :type is_first: bool
    :return: A list of nonwinner tickets.
    :rtype: list[UniversalTicket]
    """
    global suffix
    numbs = [''] * numerals
    if pics_per_ticket == 1:
        nw_image_lines = ig.create_image_lists_from_pool(1, q_nw_image_pool, 'nonwinner',
                                                         amt, pics_per_ticket, suffix)
    else:
        nw_image_lines = ig.create_image_lists_from_pool_perms(1, q_nw_image_pool, 'nonwinner',
                                                               amt, pics_per_ticket, suffix)
    ticks = []
    cull_headers = is_first
    for nw in nw_image_lines:
        pics = ig.add_additional_image_slots(add_imgs, list(nw))
        ticks.append(uTick('', pics, numbs, 1, 1, cull_headers))
        cull_headers = False
    return ticks


def create_hold_image_tickets(amt: list[int], addl_imgs: gi.AddImages, addl_nums: int, is_first: bool = False):
    """
    Create a list of hold tickets with a single image.

    :param amt: List containing the number of hold tickets.
    :type amt: list[int]
    :param addl_imgs: Additional image slots required to pad the csv output.
    :type addl_imgs: gi.AddImages
    :param addl_nums: Number of numeral slots needed in the csv output.
    :type addl_nums: int
    :param is_first: Does the first ticket need to set the csv fields?
    :type is_first: bool
    :return: A list of hold tickets.
    :rtype: list[UniversalTicket]
    """
    global suffix
    ticks = []
    # Create a placeholder for the number slots
    nummies = [''] * addl_nums
    # Cycle through the list of hold ticket tiers and create tickets
    for index, hold in enumerate(amt):
        # Create the requested number of tickets for this tier
        for i in range(hold):
            # If there's only one tier, don't bother with the tier indicator.
            if len(amt) == 1:
                img_name = f'hold{str(i + 1).zfill(2)}{suffix}'
            # Add the tier level if this is a multi-tiered hold set.
            else:
                img_name = f'hold{str(index + 1).zfill(2)}-{str(i + 1).zfill(2)}{suffix}'
            # Add additional image slots to the ticket
            imgs = ig.add_additional_image_slots(addl_imgs, [img_name])
            # Create a new ticket with the generated image and any additional image slots needed, number slots,
            # perm = 1, up = 1, and CSV header flag
            tick = uTick('', imgs, nummies, 1, 1, is_first)
            is_first = False
            ticks.append(tick)
    return ticks


def extract_ticket_types(game_specs):
    """
    Extract the types of tickets from the game specifications.

    :param game_specs: Game specifications containing ticket types.
    :type game_specs: list
    :return: A tuple containing the types of tickets (non-winner, instant, pick, hold).
    :rtype: tuple
    """

    # Pop the types off of the front of the nonwinner, instant, pick, and hold specs, and
    # return them as a list.
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_game(game_specs):
    global nw_type, insta_type, pick_type, hold_type, suffix
    if DEBUG:
        for spec in game_specs:
            print(spec)
    first_time = True
    tickets = []

    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    sheet_specs, nw_specs, insta_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    suffix = sheet_specs.pop()
    ups, permies, sheets, capacities, reset, subflats, schisms = sheet_specs
    partname = name_specs[0]
    filename = name_specs[1]
    cd_level = insta_specs[1]
    tkt_count = 1

    # Set additional image slots
    nw_addl_imgs = gi.AddImages.NoneAdded
    insta_addl_imgs = gi.AddImages.NoneAdded
    pick_addl_imgs = gi.AddImages.NoneAdded
    hold_addl_imgs = gi.AddImages.NoneAdded
    if nw_specs[2] != 1:
        nw_addl_imgs = gi.add_images_lookup(-1)
        insta_addl_imgs = gi.add_images_lookup(nw_specs[2])
        pick_addl_imgs = gi.add_images_lookup(nw_specs[2])
        hold_addl_imgs = gi.add_images_lookup(nw_specs[2])

    if pick_specs[0][0][0] != 0:
        pick_specs.extend([tkt_count, pick_addl_imgs, 0, first_time])
        tickets.extend(create_pick_winners(*pick_specs))
        first_time = False
        tkt_count = len(tickets) + 1

    if insta_specs[0][0][0] != 0:
        insta_specs.extend([tkt_count, insta_addl_imgs, 0, first_time])
        tickets.extend(create_instant_winners(*insta_specs))
        first_time = False
        tkt_count = len(tickets) + 1

    if hold_specs[0][0] != 0:
        hold_specs.extend([hold_addl_imgs, 0, first_time])
        tickets.extend(create_hold_image_tickets(*hold_specs))
        first_time = False

    if nw_specs[0] != 0:
        nw_specs.extend([nw_addl_imgs, 0, first_time])
        nw_ticks = create_imaged_nonwinner_tickets(*nw_specs)
        tickets.extend(nw_ticks)
        first_time = False

    tio.write_tickets_to_file(filename, tickets, output_folder)
    mixer = True
    if sheet_specs[3][1] in [113, 240, 396]:
        mixer = False
    game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacities[1], mixer, subflats)

    cd_positions, cd_sheets = tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets,
                                                            capacities[1], output_folder)
    if len(cd_positions) > 0:
        tio.write_cd_positions_to_csv_file(partname, filename, cd_positions, cd_level, output_folder)

    print(f'Created {len(tickets)} tickets.')


if __name__ == "__main__":
    basket = [
        [8, 1, 61, [80, 80], False, 0, 0],
        ['I', 575, 9, 1],
        ['I', [[20, False]], 0],
        ['I', [[0, False]]],
        ['I', [15]],
        ['000', 'BasketCase-31899'],
        ''
    ]

    create_game(basket)
