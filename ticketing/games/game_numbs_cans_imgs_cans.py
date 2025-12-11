"""
Game Module: Numbers / Cannons Hybrid Configuration
===================================================

Configuration:
    - Nonwinners: Numbers (Randomized or Sequential from a Pool)
    - Instants:   Cannons (Iterative) OR Images (Tiered)
    - Picks:      Images (Not actively used in this logic but supported in signature)
    - Holds:      Cannons (Iterative)

Description:
    This module handles games where non-winning tickets are populated with numbers
    (often derived from a specific suffix logic), and winning/hold tickets are generated
    either as repeated "Cannons" (iterations of the same image/layout) or standard images.

    It serves as the backend logic for games configured as "NCICA" or similar variants.

Workflow:
    1.  `create_game` is called with a bundle of Data Objects.
    2.  It generates Non-Winner tickets populated with numbers (using `number_generator`).
    3.  It generates Hold tickets using "Cannon" logic (repeating a base image for X iterations).
    4.  It generates Instant tickets using either Cannon logic OR Tiered Image logic.
    5.  It merges these separate lists into unified Permutations.
    6.  It writes the permutations to CSV files and generates the layout stacks.
"""

import copy

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi
from ticketing import ticket_io as tio

# NEW IMPORTS
from ticketing.ticket_models import (
    GameInfo, NamesData,
    NonWinnerNumbersTicket, InstantCannonsTicket, InstantImagesTicket,
    HoldCannonsTicket, PickImagesTicket
)

DEBUG = True
img_suffix = ''


def create_nonwinner_numbers(nw_ticket: NonWinnerNumbersTicket,
                             addl_imgs: gi.AddImages, is_first: bool = False):
    """
    Generates a list of Non-Winner tickets populated with numbers.

    Logic:
        Uses a 'Number Pool' derived from the ticket's configuration (First/Last number, Exclusions).
        It draws 'spots' count of numbers from this pool for each ticket. If the pool is exhausted,
        it regenerates/refills the pool.

    Args:
        nw_ticket (NonWinnerNumbersTicket): Configuration (Quantity, Spots, Range, Exclusions).
        addl_imgs (gi.AddImages): Image padding instruction (usually NoneAdded here).
        is_first (bool): CSV Header flag.

    Returns:
        list[uTick]: List of generated tickets.
    """
    global img_suffix

    # Extract object attributes
    amt = nw_ticket.quantity
    spots = nw_ticket.spots
    first = nw_ticket.first_num
    last = nw_ticket.last_num
    base = nw_ticket.base_image

    # Parse exclusions (suffixes)
    suffixes = nw_ticket.exclusions
    if not suffixes:
        suffixes_list = ['00']
    else:
        suffixes_list = suffixes.split(',')

    imgs = ig.add_additional_image_slots(addl_imgs, [''])

    ticks = []
    nw_pool = []
    # Construct base image name if provided
    basic = '' if not base else f'{base}{img_suffix}'

    # Legacy behavior preservation: Remove first suffix from list?
    if suffixes_list:
        suffixes_list.pop(0)

    while len(ticks) < amt:
        # Refill pool if needed
        if len(nw_pool) < spots:
            nw_pool = ng.create_number_pools_from_suffix_list(
                first, last, suffixes_list, True
            )
        # Draw numbers for this ticket
        numbs = []
        for _ in range(spots):
            # Check pool isn't empty before popping
            if nw_pool:
                numbs.append(nw_pool.pop(0))
            else:
                numbs.append(0)  # Fallback safety

        tick = uTick(basic, imgs, numbs, 1, 1, is_first)
        is_first = False
        ticks.append(tick)

    return ticks


def create_hold_images(hold_ticket: HoldCannonsTicket, permits: int,
                       addl_imgs: gi.AddImages, nums_count: int, is_first: bool = False):
    """
    Generates Hold tickets using 'Cannon' logic.

    Cannon Logic:
        Creates 'permits' (permutations) distinct batches.
        In each batch, it generates 'quantity' tickets.
        The image names are often prefixed sequentially per batch (e.g., hold01-, hold02-).

    Args:
        hold_ticket (HoldCannonsTicket): Configuration (Quantity).
        permits (int): Number of permutations (iterations) to generate.
        addl_imgs (gi.AddImages): Image padding.
        nums_count (int): Number of empty number slots to reserve.
        is_first (bool): CSV Header flag.

    Returns:
        list[list[uTick]]: A list of lists (one list per permutation).
    """
    global img_suffix

    amt = hold_ticket.quantity

    # Reserve empty number slots
    perms = []
    nums = [''] * nums_count if nums_count != 0 else []

    for i in range(permits):
        ticks = []
        # Create prefixed images (e.g. hold01-, hold02-) for this batch
        imgs = ig.create_prefixed_images(1, amt, f'hold{str(i + 1).zfill(2)}-', True, img_suffix)

        for tick_img in imgs:
            # Wrap image in list for slot padding
            padded_imgs = ig.add_additional_image_slots(addl_imgs, [tick_img])
            ticks.append(uTick('', padded_imgs, nums, i + 1, 1, is_first))

        perms.append(ticks)

    return perms


def create_instant_cannons(inst_ticket: InstantCannonsTicket, permits: int,
                           addl_imgs: gi.AddImages, nums_count: int, is_first: bool = False):
    """
    Generates Instant tickets using 'Cannon' logic.

    Logic:
        Similar to Hold Cannons, but typically repeats the SAME image ('winnerXX')
        multiple times within a batch rather than a sequence of unique images.

    Args:
        inst_ticket (InstantCannonsTicket): Configuration.
        permits (int): Number of permutations.
        ...

    Returns:
        list[list[uTick]]: List of lists of tickets.
    """
    global img_suffix
    perms = []
    nums = [''] * nums_count if nums_count != 0 else []

    amt = inst_ticket.quantity

    for i in range(permits):
        ticks = []
        # Create list of the SAME image repeated 'amt' times for this permutation
        imgs = ig.create_image_list_of_same_image(amt, f'winner{str(i + 1).zfill(2)}', img_suffix)

        for tick_img in imgs:
            padded_imgs = ig.add_additional_image_slots(addl_imgs, [tick_img])
            ticks.append(uTick('', padded_imgs, nums, i + 1, 1, is_first))
            is_first = False

        perms.append(ticks)

    return perms


def create_instant_winners_images(inst_ticket: InstantImagesTicket, permits: int,
                                  addl_imgs: gi.AddImages, nummies: int, first=True) -> list[list[uTick]]:
    """
    Generates Instant tickets using standard 'Tiered Image' logic.

    Logic:
        Used when Instants are defined by specific Tiers (e.g., Tier 1: 5 tickets, Tier 2: 10 tickets)
        rather than simple repetition (Cannons).

        It generates ONE master list of tickets and then duplicates it for every permutation.

    Returns:
        list[list[uTick]]: List of lists (duplicated perms).
    """
    global img_suffix

    # Convert Object Data to list for generator
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]
    cd_tier = inst_ticket.cd_tier

    imgs = ig.create_tiered_image_list_augmented(amt_list, 'winner', img_suffix)
    nums = [''] * nummies
    ticks = []

    cull_ticket = first
    tkt = ''  # Original code had empty string for tkt number in uTick?

    for img in imgs:
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])

        tick = uTick(tkt, pics, nums, 1, 1, cull_ticket)

        if img[1] <= cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')

        ticks.append(tick)
        cull_ticket = False

    # Duplicate this batch for every permutation required
    perms = []
    for i in range(permits):
        perms.append(copy.deepcopy(ticks))

    return perms


def create_game(data_bundle):
    """
    Main Entry Point (Controller).

    Orchestrates the generation for 'Numbers/Cannons' hybrid games.

    Key Responsibilities:
    1.  Determines which logic to use for Instants (Cannons vs Images) based on the input object type.
    2.  Generates the distinct components (NW, Holds, Instants).
    3.  Merges them into Permutation batches.
        - Holds and Instants are already generated as lists-of-lists (by permutation).
        - NonWinners are generated once and then Deep Copied into every permutation.
    4.  Outputs the permutations to files.
    """
    global img_suffix

    # 1. Unpack Objects
    game_info = data_bundle[0]  # type: GameInfo
    nw_specs = data_bundle[1]  # type: NonWinnerNumbersTicket
    inst_specs = data_bundle[2]  # type: InstantCannonsTicket | InstantImagesTicket
    pick_specs = data_bundle[3]  # type: PickImagesTicket
    hold_specs = data_bundle[4]  # type: HoldCannonsTicket
    name_specs = data_bundle[5]  # type: NamesData
    output_folder = data_bundle[6]

    if DEBUG:
        print(f"Game: {name_specs.file_name}")

    # 2. Extract Basic Info
    img_suffix = game_info.image_suffix
    filename = name_specs.file_name

    ups = game_info.ups
    perms = game_info.permutations
    sheets = game_info.sheets
    capacity = game_info.capacity[1]  # Bottom Out

    first_time = True
    permutations = []
    tickets = []

    # 3. Create NonWinners (Numbers)
    # Generated as a single flat list initially
    if isinstance(nw_specs, NonWinnerNumbersTicket):
        tickets = create_nonwinner_numbers(
            nw_specs, gi.AddImages.NoneAdded, is_first=first_time
        )
        first_time = False

    # 4. Create Holds (Cannons)
    # Generated as list of lists (per permutation)
    holders = []
    if hold_specs.quantity > 0:
        # We pass nw_specs.spots (int) to reserve number slots on the hold tickets
        holders = create_hold_images(
            hold_specs, perms, gi.AddImages.NoneAdded, nw_specs.spots, is_first=first_time
        )

    # 5. Create Instants (Cannons OR Images)
    instants = []

    # Case: Cannons (Iterative)
    if isinstance(inst_specs, InstantCannonsTicket):
        if inst_specs.quantity > 0:
            instants = create_instant_cannons(
                inst_specs, perms, gi.AddImages.NoneAdded, nw_specs.spots, is_first=first_time
            )
            first_time = False

    # Case: Images (Tiered)
    elif isinstance(inst_specs, InstantImagesTicket):
        if inst_specs.total_quantity > 0:
            instants = create_instant_winners_images(
                inst_specs, perms, gi.AddImages.NoneAdded, nw_specs.spots, first=first_time
            )

    # 6. Merge Lists into Permutations structure
    # We iterate through 'perms' indices and build the final list for that permutation.
    loop_range = len(holders) if holders else len(instants)
    if not loop_range and perms > 0:
        loop_range = perms  # Fallback if only NW?

    for i in range(loop_range):
        current_perm = []

        # Add Holds for this perm
        if i < len(holders):
            current_perm.extend(holders[i])

        # Add Instants for this perm
        if i < len(instants):
            current_perm.extend(instants[i])

        # Add NonWinners (Copy base list and reset perm number)
        if tickets:
            nws = copy.deepcopy(tickets)
            for tick in nws:
                # Reset uTick permutation
                tick.reset_permutation(i + 1)
            current_perm.extend(nws)

        permutations.append(current_perm)

    # 7. Output
    # Write the permutation files (e.g. filename-01.csv, filename-02.csv)
    tio.write_permutations_to_files(filename, permutations, False, output_folder)

    # Calculate stacking layout
    game_stacks = tio.create_game_stacks_from_permutations(
        permutations, ups, sheets, capacity
    )

    # Write stacks to files
    tio.write_game_stacks_to_file(
        filename, game_stacks, ups, sheets, capacity, output_folder
    )

    return f"Created {len(permutations)} permutations."
