"""
Game Module: Bingo Configuration
================================

Configuration:
    - Nonwinners: Images (Permutations from a pool)
    - Instants:   Images (Tiered)
    - Picks:      Images (Tiered)
    - Holds:      Verified Bingos (Complex Logic)

Description:
    This module handles games where the "Hold" tickets are generated as valid, verifiable
    Bingo cards (often with staggered/non-staggered patterns, free spots, etc.), while
    the other ticket types (Non-winners, Instants, Picks) are simple images.

    Because Bingo cards are generated in batches (permutations) to ensure randomness and
    coverage, the other ticket types must also be generated in permutations to match the structure.

Workflow:
    1.  Calculates necessary column padding (Image Slots) to align Bingos with Images.
    2.  Generates the core Bingo Permutations (Hold Tickets) using the `verified_bingo` library.
    3.  Generates Instant and Non-Winner tickets as permutations.
    4.  Merges all ticket types into a unified list of Permutations.
    5.  Outputs the permutations to files and calculates the layout stacks.
"""

import copy
import re

from ticketing import game_info_gui as gi
from ticketing.bingo_ticket import BingoTicket as bTick
from ticketing import verified_bingo as vb
from ticketing import image_generator as ig
from ticketing import ticket_io as tio

# NEW IMPORTS for Data Object support
from ticketing.ticket_models import (
    GameInfo, NamesData,
    NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldBingosTicket,
    ImageTier
)

DEBUG = True
suffix = ''


def create_hold_tickets(hold_ticket: HoldBingosTicket,
                        csv_rows: int, addl_imgs: gi.AddImages,
                        permits: int, perm_reset: bool = False) -> list[list[bTick]] | None:
    """
    Generates the core Bingo Cards (Hold Tickets).

    This function interacts with the `verified_bingo` (vb) library to generate valid
    bingo face combinations.

    Args:
        hold_ticket (HoldBingosTicket): Configuration (Counts for DNS, DS, SNS, SS, Either-Ors).
        csv_rows (int): The number of rows required in the CSV output (determined by bingo complexity).
        addl_imgs (gi.AddImages): Padding for image columns.
        permits (int): Number of permutations to generate.
        perm_reset (bool): Whether to reset the bingo face pool between permutations.

    Returns:
        list[list[bTick]]: A list of permutations, where each permutation is a list of BingoTicket objects.
                           Returns None if generation fails.
    """
    # Extract lists from the object for the generator
    needs = [
        hold_ticket.dns_counts,
        hold_ticket.ds_counts,
        hold_ticket.sns_counts,
        hold_ticket.ss_counts,
        hold_ticket.either_ors
    ]

    zeroes = hold_ticket.leading_zeroes
    free_type = hold_ticket.free_type

    # Logic: "Standard" vs "Extended" CSV verification lists (S vs E)
    is_extended = hold_ticket.extended_csv == 'E' or hold_ticket.extended_csv is True

    # Call the Verification Library to get raw face data
    if perm_reset or permits == 1:
        versions = vb.create_all_bingo_permutations_with_reset(
            needs, permits, csv_rows, is_extended, True
        )
    else:
        versions = vb.create_all_bingo_permutations_without_reset(
            needs, permits, csv_rows, is_extended, True
        )

    if versions[0] is None:
        return versions

    # 2. CALCULATE DIMENSIONS
    # A. Bingo Line Length (from raw data)
    first_face_data = versions[0][0]
    first_row_numbers = first_face_data[1][0]
    calculated_line_length = len(first_row_numbers)

    # B. Image Slots (Math Approach)
    # Since the base is always 1 image, we just add the padding count to 1.
    # Note: Ensure addl_imgs values of -100/100 are handled correctly if used.
    total_image_slots = abs(addl_imgs) + 1

    # 3. CONFIGURE HEADERS (ONCE)
    bTick.configure_csv_headers(
        schema_depth=csv_rows,
        line_length=calculated_line_length,
        image_count=total_image_slots,
        lotto_count=0
    )

    base = ['base01.ai']
    permies = []

    # Convert Raw Face Data -> BingoTicket Objects
    for index, verse in enumerate(versions):
        tkt = 1
        ticks = []
        for face in verse:
            b_type = 'N'

            # --- Base Image Logic ---
            # Bingo tickets often require specific background images based on the number of rows used.
            # 1 Row = base01, 2 Rows = base02, 3 Rows = base03 (Either/Or)
            if csv_rows == 3:
                if len(face[1]) == 1:
                    face[1] += [['', '', '', '', ''], ['', '', '', '', '']]
                    base = ['base01.ai']
                elif len(face[1]) == 2:
                    # Determine if Staggered or Non-Staggered
                    b_type = determine_bingo_type(face)
                    face[1].insert(0, ['', '', '', '', ''])
                    base = ['base02.ai']
                elif len(face[1]) == 3:
                    base = ['base03.ai']
                    b_type = 'E'
            elif csv_rows == 2:
                base = ['base02.ai']
            elif csv_rows == 1:
                base = ['base01.ai']

            images = ig.add_additional_image_slots(addl_imgs, base)

            tick = bTick(tkt, face[0], face[1], images, zeroes, index + 1, 1)
            tick.set_free_type(free_type)
            tick.set_bingo_type(copy.deepcopy(b_type))
            ticks.append(tick)

            is_first = False
            tkt += 1

        permies.append(ticks)

    return permies


def determine_bingo_type(facial):
    """
    Helper: Determines if a 2-row bingo ticket is Staggered ('S') or Non-Staggered ('N').

    Logic:
        Iterates through the columns. If it finds a column where one row has a value
        and the other row is blank (XOR check), it is Staggered.
    """
    for a, b in zip(facial[1][0], facial[1][1]):
        # Bitwise XOR: True if exactly one operand is True.
        # Checks if (HasValue) XOR (HasValue) is True.
        if bool(a.strip()) ^ bool(b.strip()):
            return 'S'
    return 'N'


def create_instant_winners_refined(inst_ticket: InstantImagesTicket, cd_level: int,
                                   addl_imgs: gi.AddImages, bingo_rows: int,
                                   permits: int) -> list[list[bTick]]:
    """
    Generates Instant Winners as Permutations.

    Because the core of this game is based on Permutations (for Bingo), the
    Instant Winners must also be structured as a list of lists (permutations).

    Strategy:
        1. Generate the base list of winners (Tier 1, Tier 2, etc.).
        2. Assign them to Permutation 1.
        3. Deep Copy that list for every subsequent permutation required.
    """
    global suffix
    permies = []

    # Initialize empty digit rows to match the Bingo CSV structure
    digits = []
    for _ in range(bingo_rows):
        digits.append(['', '', '', '', ''])

    # Convert Ticket Object to Generator List format
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]

    imgs = ig.create_tiered_image_list_augmented(amt_list, 'winner', suffix)
    ticks = []

    for img in imgs:
        img_padded = ig.add_additional_image_slots(addl_imgs, [img[0]])

        # Create as a BingoTicket (bTick) to match the file output format,
        # even though it's just an image.
        tick = bTick('', '', digits, img_padded, False, 1, 1)

        if img[1] <= cd_level and img[1] != 0:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')

        tick.set_bingo_type('O')  # 'O' for Other (Not a Bingo card)
        ticks.append(tick)

    permies.append(ticks)

    # Duplicate for remaining permutations
    for j in range(1, permits):
        temp_ticks = copy.deepcopy(ticks)
        for tick in temp_ticks:
            tick.reset_permutation(j + 1)
        permies.append(temp_ticks)

    return permies


def calculate_image_slots(hold_ticket: HoldBingosTicket, nw_ticket: NonWinnerImagesTicket,
                          free_image: bool):
    """
    Calculates complex image padding requirements.

    Logic:
        Bingo games are tricky because free spots might be images ('Free Space' star),
        or the Non-Winners might use multiple images.

        This function calculates the maximum width required by ANY ticket type
        so that all rows in the CSV line up correctly.
    """
    non_base_image_slots = 0
    prefix_value = 0

    if free_image:
        # If Free Spaces use images, we need to scan the bingo definitions
        # to see how many image slots are consumed by free spaces.
        holders_lists = [
            hold_ticket.dns_counts,
            hold_ticket.ds_counts,
            hold_ticket.sns_counts,
            hold_ticket.ss_counts
        ]

        for sublist in holders_lists:
            for indie, x in enumerate(reversed(sublist)):
                if x != 0:
                    # Calculate depth of free spots needed
                    non_base_image_slots = max(non_base_image_slots, len(sublist) - indie - 1)
                    break

        # Check Either/Ors for max free spots
        if hold_ticket.either_ors and hold_ticket.either_ors[0][0] > 0:
            for hold in hold_ticket.either_ors:
                # hold is [qty, frees, eithers]
                if len(hold) >= 3:
                    frees = hold[1]
                    eithers = hold[2]
                    non_base_image_slots = max(non_base_image_slots, frees + eithers)

        # If Non-Winners also have extra images, we shift the prefix
        if nw_ticket.images_per_ticket > 1:
            prefix_value = -(non_base_image_slots + 1)
            non_base_image_slots += nw_ticket.images_per_ticket

    elif nw_ticket.images_per_ticket > 1:
        prefix_value = -1
        non_base_image_slots = nw_ticket.images_per_ticket

    prefix = gi.add_images_lookup(prefix_value)
    suffix_lookup = gi.add_images_lookup(non_base_image_slots)

    return [prefix, suffix_lookup]


def create_nonwinning_ticket(nw_ticket: NonWinnerImagesTicket, addl_imgs: gi.AddImages,
                             bingo_rows: int, permits: int, firstly: bool = False) -> list[list[bTick]]:
    """
    Generates Non-Winning tickets as Permutations.

    Logic:
        Unlike Instants (which are identical across perms), Non-Winners usually draw
        from a large pool of images. We generate unique sets for each permutation
        to maximize variety.
    """
    global suffix
    permies = []
    digits = []
    is_first = firstly
    for _ in range(bingo_rows):
        digits.append(['', '', '', '', ''])

    for j in range(permits):
        # Generate unique image lists for this specific permutation 'j'
        if nw_ticket.images_per_ticket == 1:
            # Generate unique image lists for this specific permutation 'j'
            nws_perms = ig.create_image_lists_from_pool_perms(
                1, nw_ticket.pool_size, 'nonwinner', nw_ticket.quantity,
                nw_ticket.images_per_ticket, suffix
            )
        else:
            nws_perms = ig.create_image_lists_from_pool_perms(
                1, nw_ticket.pool_size, 'nonwinner', nw_ticket.quantity,
                nw_ticket.images_per_ticket, suffix
            )

        ticks = []
        for nws_perm in nws_perms:
            imgs = ig.add_additional_image_slots(addl_imgs, nws_perm)

            # Create as BingoTicket with empty digits
            tick = bTick('', '', digits, imgs, False, j + 1, 1)
            tick.set_bingo_type('O')
            is_first = False
            ticks.append(tick)

        permies.append(ticks)

    return permies


def create_game(data_bundle):
    """
    Main Entry Point (Controller).

    Orchestrates the generation of a Bingo-based game.

    Key Responsibilities:
    1.  Calculates complex image padding (slots) based on whether Free Spaces are images.
    2.  Generates the Hold Tickets (The Bingo Cards) first.
    3.  Generates Instants and NonWinners and appends them to the permutation lists.
        (This ensures every permutation has a mix of Holds, Instants, and NWs).
    4.  Outputs the Permutation files and Stack layouts.
    """
    global suffix

    # 1. Unpack Objects
    game_info = data_bundle[0]  # type: GameInfo
    nw_specs = data_bundle[1]  # type: NonWinnerImagesTicket
    inst_specs = data_bundle[2]  # type: InstantImagesTicket
    pick_specs = data_bundle[3]  # type: PickImagesTicket
    hold_specs = data_bundle[4]  # type: HoldBingosTicket
    name_specs = data_bundle[5]  # type: NamesData
    output_folder = data_bundle[6]

    if DEBUG:
        print(f"Game: {name_specs.file_name}")
        print(f"Perms: {game_info.permutations}")

    suffix = game_info.image_suffix
    part_name = name_specs.base_part
    file_name = name_specs.file_name

    ups = game_info.ups
    perms = game_info.permutations
    sheets = game_info.sheets
    # capacity is tuple (bottom_in, bottom_out)
    capacity = game_info.capacity[0]
    reset_perms = game_info.reset_pool
    subflats = game_info.subflats

    # 2. Calculate Image Slots (Padding)
    # Check if 'Images' or 'Both' is selected for free spots
    use_free_images = hold_specs.free_type in ['Images', 'Both']

    nw_addls, hold_addls = calculate_image_slots(hold_specs, nw_specs, use_free_images)

    # Instants and Picks match Holds padding here
    inst_addls, pick_addls = [hold_addls] * 2

    cd_tier = inst_specs.cd_tier
    bingrows = hold_specs.columns_needed

    # 3. Create Hold Tickets (Bingos)
    # This initializes the 'permits' list of lists.
    permits = create_hold_tickets(
        hold_specs, bingrows, hold_addls, perms, perm_reset=reset_perms
    )

    if permits is None:
        return "Error creating Bingo Permutations (Check VerifiedBingo logic)."

    # 4. Create Instant Winners (Append to Permutations)
    # We generate the Instants, then loop through the permutations and extend them.
    if inst_specs.total_quantity > 0:
        i_permits = create_instant_winners_refined(
            inst_specs, cd_tier, inst_addls, bingrows, perms
        )
        # Merge into main permits list
        for i in range(len(i_permits)):
            permits[i].extend(i_permits[i])

    # 5. Create NonWinners (Append to Permutations)
    if nw_specs.quantity > 0:
        n_permits = create_nonwinning_ticket(
            nw_specs, nw_addls, bingrows, perms
        )
        for i in range(len(n_permits)):
            permits[i].extend(n_permits[i])

    # 6. Output Files
    tio.write_permutations_to_files(file_name, permits, False, output_folder)

    # 7. Create Game Stacks
    game_stacks = tio.create_game_stacks_from_permutations(
        permits, ups, sheets, capacity, True
    )

    cds, sheeters = tio.write_game_stacks_to_file(
        file_name, game_stacks, ups, sheets, capacity, output_folder
    )

    if len(cds) > 0:
        tio.write_cd_positions_to_csv_file(
            part_name, file_name, cds, cd_tier, output_folder
        )

    return "Successfully created Bingo game files."
