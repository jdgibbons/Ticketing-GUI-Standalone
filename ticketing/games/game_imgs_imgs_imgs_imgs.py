"""
Game Module: All-Image Configuration
====================================

Configuration:
    - Nonwinners: Images (Single or Multiple per ticket)
    - Instants:   Images (Tiered)
    - Picks:      Images (Tiered)
    - Holds:      Images (Simple Quantities)

Description:
    This module handles the generation of games where every ticket type is represented
    by graphical images (as opposed to generated numbers or bingo grids).

    It serves as the backend logic when the user selects 'Images' for all four
    ticket categories in the GUI.

Workflow:
    1.  `create_game` is called with a bundle of Data Objects.
    2.  It calculates column padding (if non-winners use multiple images).
    3.  It calls specific generator functions for Picks, Instants, Holds, and Non-winners.
    4.  It aggregates all generated `UniversalTicket` objects.
    5.  It writes the raw ticket data to a master CSV/file.
    6.  It calculates "Game Stacks" (layout on physical sheets) and outputs the final production files.
"""

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi  # Note: renamed from game_info_gui if you consolidated
from ticketing import ticket_io as tio

# Import the Ticket Models to ensure type safety and attribute access
from ticketing.ticket_models import (
    GameInfo, NamesData,
    NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldImagesTicket
)

DEBUG = True
suffix = ''


def create_instant_winners(inst_ticket: InstantImagesTicket, tkt: int, addl_imgs: gi.AddImages,
                           nummies: int, is_first=True) -> list[uTick]:
    """
    Generates the list of Instant Winner tickets.

    Logic:
        1. Converts the Ticket Object into a list format expected by the `image_generator`.
        2. Generates image filenames based on tiers (e.g., 'winner01.ai', 'winner02.ai').
        3. Creates `UniversalTicket` objects.
        4. Applies "CD" (Check Digit) codes if the ticket's tier is within the CD-tracking range.

    Args:
        inst_ticket (InstantImagesTicket): The configuration object from the GUI.
        tkt (int): The starting ticket number for this batch.
        addl_imgs (gi.AddImages): Padding instructions for CSV alignment.
        nummies (int): Number of numerical slots (usually 0 for image games).
        is_first (bool): Logic flag to determine if CSV headers should be generated.

    Returns:
        list[uTick]: A list of generated Instant Winner objects.
    """
    global suffix

    # Transformation: Extract [Quantity, IsUnique] pairs from the Data Object
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]

    # Generate the actual list of image filenames based on the tiers
    imgs = ig.create_tiered_image_list_augmented(amt_list, 'winner', suffix)

    nums = [''] * nummies
    ticks = []

    for img in imgs:
        # img structure: [image_name, tier_level]

        # Apply column padding if necessary
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])

        # Create the ticket object
        tick = uTick(tkt, pics, nums, 1, 1, is_first)

        # CD Logic: If this ticket's tier is <= the CD tracking level, mark it.
        # This is used for backend tracking of high-value winners.
        if img[1] <= inst_ticket.cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')

        ticks.append(tick)

        # Only the very first ticket in the entire game needs to generate headers
        is_first = False
        tkt += 1

    return ticks


def create_pick_winners(pick_ticket: PickImagesTicket, tkt: int, addl_imgs: gi.AddImages, nummies: int,
                        first: bool = False, permit: int = 1) -> list[uTick]:
    """
    Generates the list of Pick Winner tickets.

    Similar to Instant Winners, but handled separately as "Picks" often have
    different reporting requirements or different naming conventions ('pick' vs 'winner').

    Args:
        pick_ticket (PickImagesTicket): The configuration object.
        tkt (int): Starting ticket number.
        addl_imgs (gi.AddImages): Padding instructions.
        nummies (int): Number of numerical slots.
        first (bool): CSV header flag.
        permit (int): Permutation number (default 1).

    Returns:
        list[uTick]: List of generated Pick tickets.
    """
    global suffix
    ticks = []
    img_list = []
    nums = [''] * nummies

    # Transformation: Extract [Quantity, IsUnique] pairs
    amt_list = [[tier.quantity, tier.is_unique] for tier in pick_ticket.tiers]

    # Special handling for single-tier vs multi-tier Pick definitions
    if len(amt_list) == 1:
        # Single Tier Logic
        imgs = ig.create_prefixed_images(1, amt_list[0][0], 'pick', 1, suffix)
        for img in imgs:
            img_list.append([img, 1])  # [name, tier=1]
    else:
        # Multi-Tier Logic
        img_list.extend(ig.create_tiered_image_list_augmented(amt_list, 'pick', suffix))

    cull_ticket = first

    for img in img_list:
        pics = ig.add_additional_image_slots(addl_imgs, [img[0]])

        # Create Ticket
        ticket = uTick(tkt, pics, nums, permit, 1, cull_ticket)
        cull_ticket = False
        tkt += 1

        # Picks receive a specific CD Type 'P'
        ticket.reset_cd_type('P')
        ticket.reset_cd_tier(img[1])
        ticks.append(ticket)

    return ticks


def create_imaged_nonwinner_tickets(nw_ticket: NonWinnerImagesTicket, add_imgs: gi.AddImages,
                                    numerals: int = 0, is_first: bool = False) -> list[uTick]:
    """
    Generates the bulk Non-Winner tickets.

    Logic:
        Non-winners often pull images from a "Pool" (e.g., a pool of 9 images).
        This function handles distributing that pool across the requested quantity
        of tickets, ensuring variety.

    Args:
        nw_ticket (NonWinnerImagesTicket): Config object (Quantity, Pool Size, Images/Ticket).
        add_imgs (gi.AddImages): Padding instructions.
        numerals (int): Number slots (usually 0).
        is_first (bool): CSV header flag.

    Returns:
        list[uTick]: List of non-winner tickets.
    """
    global suffix
    numbs = [''] * numerals

    # Determine generation strategy based on images per ticket
    if nw_ticket.images_per_ticket == 1:
        # Simple 1-image generation
        nw_image_lines = ig.create_image_lists_from_pool(
            1, nw_ticket.pool_size, 'nonwinner',
            nw_ticket.quantity, nw_ticket.images_per_ticket, suffix
        )
    else:
        # Complex multi-image generation (Permutations from pool)
        nw_image_lines = ig.create_image_lists_from_pool_perms(
            1, nw_ticket.pool_size, 'nonwinner',
            nw_ticket.quantity, nw_ticket.images_per_ticket, suffix
        )

    ticks = []
    cull_headers = is_first

    # Convert generated image lines into Ticket Objects
    for nw in nw_image_lines:
        pics = ig.add_additional_image_slots(add_imgs, list(nw))
        ticks.append(uTick('', pics, numbs, 1, 1, cull_headers))
        cull_headers = False

    return ticks


def create_hold_image_tickets(hold_ticket: HoldImagesTicket, addl_imgs: gi.AddImages,
                              addl_nums: int, is_first: bool = False):
    """
    Generates Hold Tickets.

    Logic:
        Iterates through the 16 available "Hold Tiers" defined in the GUI.
        Creates specific quantities of named files (e.g., 'hold01.ai', 'hold02.ai').

    Args:
        hold_ticket (HoldImagesTicket): Config object containing the list of 16 quantities.
        addl_imgs (gi.AddImages): Padding instructions.
        addl_nums (int): Number slots.
        is_first (bool): CSV header flag.

    Returns:
        list[uTick]: List of Hold tickets.
    """
    global suffix
    ticks = []
    nummies = [''] * addl_nums

    # We clean the list to remove trailing zeros, matching previous logic
    # Or simply iterate over non-zero quantities
    valid_holds = [q for q in hold_ticket.quantities if q > 0]

    # Filter out tiers with 0 quantity to avoid processing empty requests
    for index, hold_qty in enumerate(valid_holds):
        # Create 'hold_qty' number of tickets for this specific hold type
        for i in range(hold_qty):
            # Naming convention:
            # If only 1 type of hold exists: 'hold01', 'hold02' (sequential)
            # If multiple types exist: 'hold01-01', 'hold01-02' (Type-Sequence)
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
    Calculates the necessary padding (empty image slots) for the CSV output.

    Why this exists:
        If Non-Winner tickets are configured to have multiple images (e.g., 3 images per ticket),
        but Instants/Holds only have 1 image per ticket, the resulting CSV would have uneven columns.

        This function determines how many "blank" image slots need to be added to the single-image
        tickets to align them with the multi-image tickets in the final output file.

    Args:
        images_per_ticket (int): The number of images on a Non-Winner ticket.

    Returns:
        tuple: A tuple of `AddImages` Enums (NW, Instant, Pick, Hold) instructing the
               generator on how to pad each type.
    """
    # Default: No padding needed (assuming 1 image per ticket everywhere)
    nw_addl = gi.AddImages.NoneAdded
    insta_addl = gi.AddImages.NoneAdded
    pick_addl = gi.AddImages.NoneAdded
    hold_addl = gi.AddImages.NoneAdded

    # Logic: If NW has > 1 image, everything else needs padding to match.
    if images_per_ticket != 1:
        # Non-winners usually get a specific 'PreOne' (-1) adjustment logic in the generator
        nw_addl = gi.add_images_lookup(-1)

        # Instants, Picks, and Holds get padded by the NW count to ensure
        # they occupy the same number of columns in the layout.
        padding_val = images_per_ticket
        insta_addl = gi.add_images_lookup(padding_val)
        pick_addl = gi.add_images_lookup(padding_val)
        hold_addl = gi.add_images_lookup(padding_val)

    return nw_addl, insta_addl, pick_addl, hold_addl


def create_game(data_bundle):
    """
    Main Entry Point (Controller).

    This function orchestrates the entire creation process for an "All Images" game.
    It unpacks the data objects, determines formatting requirements, calls the
    generators, and writes the results to disk.

    Args:
        data_bundle (list): A list containing [GameInfo, NW, Inst, Pick, Hold, Names, output_folder].
                            These are typed objects from `ticket_models.py`.

    Returns:
        str: A success message summarizing the number of tickets created.
    """
    global suffix

    # 1. Unpack Objects from the bundle
    #    (These are passed from ticketing_gui.submit_data)
    game_info = data_bundle[0]  # type: GameInfo
    nw_specs = data_bundle[1]  # type: NonWinnerImagesTicket
    inst_specs = data_bundle[2]  # type: InstantImagesTicket
    pick_specs = data_bundle[3]  # type: PickImagesTicket
    hold_specs = data_bundle[4]  # type: HoldImagesTicket
    name_specs = data_bundle[5]  # type: NamesData
    output_folder = data_bundle[6]

    # 2. Extract Basic Configuration info
    suffix = game_info.image_suffix
    partname = name_specs.base_part
    filename = name_specs.file_name

    tkt_count = 1
    first_time = True
    tickets = []

    if DEBUG:
        print(f"Creating Game: {filename}")
        print(f"Suffix: {suffix}")

    # 3. Determine Additional Image Slots (Padding)
    #    This ensures column alignment if NonWinners use multiple images per ticket.
    nw_addl_imgs, insta_addl_imgs, pick_addl_imgs, hold_addl_imgs = calculate_image_padding(
        nw_specs.images_per_ticket
    )

    # 4. Generate Tickets Sequence
    #    Order: Picks -> Instants -> Holds -> NonWinners

    # --- A. PICKS ---
    if pick_specs.total_quantity > 0:
        new_ticks = create_pick_winners(
            pick_specs, tkt_count, pick_addl_imgs, 0, first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False
        tkt_count += len(new_ticks)

    # --- B. INSTANTS ---
    if inst_specs.total_quantity > 0:
        new_ticks = create_instant_winners(
            inst_specs, tkt_count, insta_addl_imgs, 0, is_first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False
        tkt_count += len(new_ticks)

    # --- C. HOLDS ---
    if hold_specs.total_quantity > 0:
        new_ticks = create_hold_image_tickets(
            hold_specs, hold_addl_imgs, 0, is_first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False

    # --- D. NONWINNERS ---
    if nw_specs.quantity > 0:
        new_ticks = create_imaged_nonwinner_tickets(
            nw_specs, nw_addl_imgs, 0, is_first=first_time
        )
        tickets.extend(new_ticks)
        first_time = False

    # 5. Output: Write Raw Tickets to CSV
    print(f'Created {len(tickets)} tickets.')
    tio.write_tickets_to_file(filename, tickets, output_folder)

    # 6. Post-Processing: Create Game Stacks
    #    This calculates how the tickets map to physical sheets based on the 'Ups' and 'Capacity'.
    ups = game_info.ups
    sheets = game_info.sheets
    capacity = game_info.capacity[1]  # Bottom-Out Capacity
    subflats = game_info.subflats

    # Logic: Disable mixer for specific complex window structures (C, NC, S, NS).
    # These structures have specific layout rules that mixing would break.
    mixer = True
    if game_info.window_structure in ['C', 'NC', 'S', 'NS']:
        mixer = False

    game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacity, mixer, subflats)

    # Write the Stacking data to file
    cd_positions, cd_sheets = tio.write_game_stacks_to_file(
        filename, game_stacks, ups, sheets, capacity, output_folder
    )

    # 7. Output: Write CD (Check Digit) Reports if necessary
    if len(cd_positions) > 0:
        tio.write_cd_positions_to_csv_file(
            partname, filename, cd_positions, inst_specs.cd_tier, output_folder
        )

    # Return success message to the GUI
    return f"Successfully created {len(tickets) * ups} tickets."
