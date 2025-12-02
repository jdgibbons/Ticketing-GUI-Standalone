"""
Nonwinners: Image
Instants: Image
Picks: Image
Holds: Image

Refactored to use Ticket Models.
"""
from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi  # Note: renamed from game_info_gui if you consolidated
from ticketing import ticket_io as tio

# Import the models so we can type hint and access fields
from ticketing.ticket_models import (
    GameInfo, NamesData,
    NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldImagesTicket
)

DEBUG = True
suffix = ''


def create_instant_winners(inst_ticket: InstantImagesTicket, tkt: int, addl_imgs: gi.AddImages,
                           nummies: int, is_first=True) -> list[uTick]:
    """
    Create a list of instant winner tickets consisting of one image.
    """
    global suffix

    # Convert Object Data to the list format expected by image_generator
    # ig.create_tiered_image_list_augmented expects [[qty, unique], ...]
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]

    imgs = ig.create_tiered_image_list_augmented(amt_list, 'winner', suffix)

    nums = [''] * nummies
    ticks = []

    for img in imgs:
        # img structure from generator: [image_name, tier_level]
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])

        tick = uTick(tkt, pics, nums, 1, 1, is_first)

        # Check CD Tier logic
        if img[1] <= inst_ticket.cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')

        ticks.append(tick)
        is_first = False
        tkt += 1

    return ticks


def create_pick_winners(pick_ticket: PickImagesTicket, tkt: int, addl_imgs: gi.AddImages, nummies: int,
                        first: bool = False, permit: int = 1) -> list[uTick]:
    """
    Create a list of pick winner tickets.
    """
    global suffix
    ticks = []
    img_list = []
    nums = [''] * nummies

    # Convert Object Data to format for image generator
    # We need [[qty, unique], ...]
    amt_list = [[tier.quantity, tier.is_unique] for tier in pick_ticket.tiers]

    # If there's only one dimension/tier
    if len(amt_list) == 1:
        # amt_list[0][0] is qty, amt_list[0][1] is unique bool
        imgs = ig.create_prefixed_images(1, amt_list[0][0], 'pick', 1, suffix)
        for img in imgs:
            img_list.append([img, 1])  # [name, tier=1]
    else:
        img_list.extend(ig.create_tiered_image_list_augmented(amt_list, 'pick', suffix))

    cull_ticket = first

    for img in img_list:
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])

        ticket = uTick(tkt, pics, nums, permit, 1, cull_ticket)
        cull_ticket = False
        tkt += 1

        ticket.reset_cd_type('P')
        ticket.reset_cd_tier(img[1])
        ticks.append(ticket)

    return ticks


def create_imaged_nonwinner_tickets(nw_ticket: NonWinnerImagesTicket, add_imgs: gi.AddImages,
                                    numerals: int = 0, is_first: bool = False) -> list[uTick]:
    """
    Create a list of nonwinner tickets.
    """
    global suffix
    numbs = [''] * numerals

    if nw_ticket.images_per_ticket == 1:
        nw_image_lines = ig.create_image_lists_from_pool(
            1, nw_ticket.pool_size, 'nonwinner',
            nw_ticket.quantity, nw_ticket.images_per_ticket, suffix
        )
    else:
        nw_image_lines = ig.create_image_lists_from_pool_perms(
            1, nw_ticket.pool_size, 'nonwinner',
            nw_ticket.quantity, nw_ticket.images_per_ticket, suffix
        )

    ticks = []
    cull_headers = is_first
    for nw in nw_image_lines:
        pics = ig.add_additional_image_slots(add_imgs, list(nw))
        ticks.append(uTick('', pics, numbs, 1, 1, cull_headers))
        cull_headers = False

    return ticks


def create_hold_image_tickets(hold_ticket: HoldImagesTicket, addl_imgs: gi.AddImages,
                              addl_nums: int, is_first: bool = False):
    """
    Create a list of hold tickets.
    """
    global suffix
    ticks = []
    nummies = [''] * addl_nums

    # We clean the list to remove trailing zeros, matching previous logic
    # Or simply iterate over non-zero quantities
    valid_holds = [q for q in hold_ticket.quantities if q > 0]

    for index, hold_qty in enumerate(valid_holds):
        for i in range(hold_qty):
            if len(valid_holds) == 1:
                img_name = f'hold{str(i + 1).zfill(2)}{suffix}'
            else:
                img_name = f'hold{str(index + 1).zfill(2)}-{str(i + 1).zfill(2)}{suffix}'

            imgs = ig.add_additional_image_slots(addl_imgs, [img_name])

            tick = uTick('', imgs, nummies, 1, 1, is_first)
            is_first = False
            ticks.append(tick)

    return ticks


def calculate_image_padding(images_per_ticket: int):
    """
    Determines the padding (AddImages enum) required for all ticket types based on
    the number of images on the NonWinner ticket.

    If NW tickets have >1 image, other single-image tickets (Instants, Picks, Holds)
    need padding to align columns in the CSV.

    Returns:
        tuple: (nw_addl, insta_addl, pick_addl, hold_addl)
    """
    # Default to NoneAdded
    nw_addl = gi.AddImages.NoneAdded
    insta_addl = gi.AddImages.NoneAdded
    pick_addl = gi.AddImages.NoneAdded
    hold_addl = gi.AddImages.NoneAdded

    if images_per_ticket != 1:
        # If NW has multiple images, it usually gets a 'PreOne' (-1) adjustment
        nw_addl = gi.add_images_lookup(-1)

        # The others get padded by the count of NW images
        padding_val = images_per_ticket
        insta_addl = gi.add_images_lookup(padding_val)
        pick_addl = gi.add_images_lookup(padding_val)
        hold_addl = gi.add_images_lookup(padding_val)

    return nw_addl, insta_addl, pick_addl, hold_addl


def create_game(data_bundle):
    """
    Main Entry Point.
    Refactored to accept a list of Data Objects.
    data_bundle = [GameInfo, NW, Inst, Pick, Hold, Names, output_folder]
    """
    global suffix

    # 1. Unpack Objects
    game_info = data_bundle[0]  # type: GameInfo
    nw_specs = data_bundle[1]  # type: NonWinnerImagesTicket
    inst_specs = data_bundle[2]  # type: InstantImagesTicket
    pick_specs = data_bundle[3]  # type: PickImagesTicket
    hold_specs = data_bundle[4]  # type: HoldImagesTicket
    name_specs = data_bundle[5]  # type: NamesData
    output_folder = data_bundle[6]

    # 2. Extract Basic Info
    suffix = game_info.image_suffix
    partname = name_specs.base_part
    filename = name_specs.file_name

    tkt_count = 1
    first_time = True
    tickets = []

    if DEBUG:
        print(f"Creating Game: {filename}")
        print(f"Suffix: {suffix}")

    # 3. Determine Additional Image Slots
    # Refactored call:
    nw_addl_imgs, insta_addl_imgs, pick_addl_imgs, hold_addl_imgs = calculate_image_padding(
        nw_specs.images_per_ticket
    )

    # 4. Generate Tickets

    # --- PICKS ---
    # Check if there are any pick tickets (quantity > 0)
    if pick_specs.total_quantity > 0:
        new_ticks = create_pick_winners(
            pick_specs, tkt_count, pick_addl_imgs, 0, first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False
        tkt_count += len(new_ticks)

    # --- INSTANTS ---
    if inst_specs.total_quantity > 0:
        new_ticks = create_instant_winners(
            inst_specs, tkt_count, insta_addl_imgs, 0, is_first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False
        tkt_count += len(new_ticks)

    # --- HOLDS ---
    if hold_specs.total_quantity > 0:
        new_ticks = create_hold_image_tickets(
            hold_specs, hold_addl_imgs, 0, is_first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False

    # --- NONWINNERS ---
    if nw_specs.quantity > 0:
        new_ticks = create_imaged_nonwinner_tickets(
            nw_specs, nw_addl_imgs, 0, is_first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False

    # 5. Write to File
    print(f'Created {len(tickets)} tickets.')

    tio.write_tickets_to_file(filename, tickets, output_folder)

    # 6. Generate Stacks
    ups = game_info.ups
    sheets = game_info.sheets
    capacity = game_info.capacity[1]  # Bottom-Out Capacity
    subflats = game_info.subflats

    mixer = True
    # Logic from original: disable mixer for specific capacities
    if game_info.window_structure in ['C', 'NC', 'S', 'NS']:
        mixer = False

    game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacity, mixer, subflats)

    cd_positions, cd_sheets = tio.write_game_stacks_to_file(
        filename, game_stacks, ups, sheets, capacity, output_folder
    )

    if len(cd_positions) > 0:
        tio.write_cd_positions_to_csv_file(
            partname, filename, cd_positions, inst_specs.cd_tier, output_folder
        )

    return f"Successfully created {len(tickets) * ups} tickets."
