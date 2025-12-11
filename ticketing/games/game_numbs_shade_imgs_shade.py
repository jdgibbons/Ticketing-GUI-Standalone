"""
Game Module: Numbers / Shaded Configuration
===========================================

Configuration:
    - Nonwinners: Numbers (Randomized or Sequential from a Pool)
    - Instants:   Shaded (Tiered numbers) OR Images
    - Picks:      Images (Not actively used in this logic but supported)
    - Holds:      Shaded (Tiered numbers)

Description:
    This module handles "Shaded" games where specific numbers (usually based on a suffix)
    are highlighted/shaded on the ticket to indicate a win or a hold.

    It uses a shared "Number Pool" to ensure that numbers used for winning tickets
    are removed from the pool available for non-winning tickets.

    It also implements a "Balanced Position" algorithm to ensure that when specific numbers
    are shaded, they appear in different physical spots on the ticket evenly.
"""

import copy
import re
import random as rn

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import number_generator as ng
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi
from ticketing import ticket_io as tio

# NEW IMPORTS
from ticketing.ticket_models import (
    GameInfo, NamesData,
    NonWinnerNumbersTicket, InstantImagesTicket, InstantShadedTicket,
    HoldShadedTicket, PickImagesTicket, ShadedTier
)

DEBUG = True
suffix = ''


def generate_balanced_positions(total_tickets: int, spots: int) -> list[int]:
    """
    Generates a list of positions ensuring even distribution with minimal clumping.

    Logic:
        Instead of shuffling the whole list at once (which allows [0, 0, 1...]),
        we create sets of [0..spots-1], shuffle each set individually, and concatenate them.

    Example (spots=3):
        Chunk 1: [2, 0, 1]
        Chunk 2: [1, 2, 0]
        Result:  [2, 0, 1, 1, 2, 0]

    This guarantees a maximum distance between identical positions.
    """
    base_positions = list(range(spots))
    final_list = []

    # 1. Calculate Full Sets needed
    full_sets = total_tickets // spots

    for _ in range(full_sets):
        chunk = base_positions[:] # Copy
        rn.shuffle(chunk)

        # Anti-Clumping Check:
        # If the start of this new chunk matches the end of the previous list,
        # swap the first element of the new chunk to the back.
        if final_list and final_list[-1] == chunk[0] and len(chunk) > 1:
            chunk[0], chunk[-1] = chunk[-1], chunk[0]

        final_list.extend(chunk)

    # 2. Handle Remainder
    remainder = total_tickets % spots
    if remainder > 0:
        # Take a random sample of 'remainder' unique items to keep it balanced
        chunk = rn.sample(base_positions, remainder)

        # Anti-Clumping Check for the remainder
        if final_list and final_list[-1] == chunk[0] and len(chunk) > 1:
            chunk[0], chunk[-1] = chunk[-1], chunk[0]

        final_list.extend(chunk)

    return final_list


def create_instant_winner_image_tickets(inst_ticket: InstantImagesTicket,
                                        addl_imgs: gi.AddImages, numeros: int,
                                        is_first: bool) -> list[uTick]:
    """
    Create tiered instant winner tickets (Images).
    """
    global suffix

    # Convert Object Data to list for generator
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]
    cd_tier = inst_ticket.cd_tier

    image_list = ig.create_discrete_tiered_image_sets(amt_list, 'winner', suffix)

    ticks = []
    numeros = [''] * numeros

    for img in image_list:
        # img structure: [name, tier_level]
        cd = img[1]
        img_padded = ig.add_additional_image_slots(addl_imgs, [img[0]])

        tick = uTick('', img_padded, numeros, 1, 1, is_first)

        if cd_tier >= cd:
            tick.reset_cd_type('I')
            tick.reset_cd_tier(cd)

        ticks.append(tick)
        is_first = False

    return ticks


def create_instant_winner_shaded_tickets(inst_ticket: InstantShadedTicket,
                                         nw_pool: list[str],
                                         addl_imgs: gi.AddImages, num_slots: int, is_first: bool):
    """
    Create Instant Winners using Shaded Numbers logic.
    """
    ticks = []

    # Parse exclusions from string
    exclusions = inst_ticket.exclusions.split(',') if inst_ticket.exclusions else []

    # Add suffixes from all tiers to exclusions list
    for tier in inst_ticket.tiers:
        if tier.suffix:
            exclusions.append(tier.suffix)

    # Clean empty strings
    exclusions = [x for x in exclusions if x]

    addl_nums = num_slots - inst_ticket.spots

    for index, tier in enumerate(inst_ticket.tiers):
        # Extract Tier Data
        base = f"{tier.base_image}{suffix}" if tier.base_image else ""
        color = tier.color
        full = tier.is_full

        imgs = ig.add_additional_image_slots(addl_imgs, [base])

        # Generate Balanced Positions for this tier
        total_tickets_in_tier = len(tier.numbers)
        position_list = generate_balanced_positions(total_tickets_in_tier, inst_ticket.spots)

        for i, shade in enumerate(tier.numbers):
            pos = position_list[i]

            nw_pool, tick = create_shaded_ticket(
                addl_nums, color, exclusions, inst_ticket.first_num, full, imgs, is_first,
                inst_ticket.last_num, nw_pool, shade, inst_ticket.spots,
                forced_position=pos,
                pi=False  # Instants usually don't use Plus Image
            )

            # Check CD Tier logic (index + 1 is the tier number)
            if index + 1 <= inst_ticket.cd_tier:
                tick.reset_cd_type('I')
                tick.reset_cd_tier(index + 1)

            is_first = False
            ticks.append(tick)

    return ticks, nw_pool


def create_hold_shaded_tickets(hold_ticket: HoldShadedTicket,
                               addl_imgs: gi.AddImages,
                               num_slots: int, is_first: bool = False):
    """
    Create Hold Tickets using Shaded Numbers logic.
    """
    global suffix
    ticks = []
    nw_pool = []

    addl_nums = num_slots - hold_ticket.spots

    # Parse exclusions
    exclusions = hold_ticket.exclusions.split(',') if hold_ticket.exclusions else []

    for tier in hold_ticket.tiers:
        if tier.suffix:
            exclusions.append(tier.suffix)
    exclusions = [x for x in exclusions if x]

    # 1. Process Shaded Numbers
    for tier in hold_ticket.tiers:
        base = f"{tier.base_image}{suffix}" if tier.base_image else ""
        color = tier.color
        full = tier.is_full
        is_pi_enabled = tier.pi_enabled  # Clear variable name

        imgs = ig.add_additional_image_slots(addl_imgs, [base])

        # Generate Balanced Positions
        total_tickets_in_tier = len(tier.numbers)
        position_list = generate_balanced_positions(total_tickets_in_tier, hold_ticket.spots)

        for i, shade in enumerate(tier.numbers):
            pos = position_list[i]

            nw_pool, tick = create_shaded_ticket(
                addl_nums, color, exclusions, hold_ticket.first_num, full, imgs, is_first,
                hold_ticket.last_num, nw_pool, shade, hold_ticket.spots,
                forced_position=pos,
                pi=is_pi_enabled
            )
            is_first = False
            ticks.append(tick)

    # 2. Process Additional Image Holds (if any)
    # image_holds structure: List of [base_name, amount] strings
    nummies = [''] * (addl_nums + hold_ticket.spots)

    for hold in hold_ticket.image_holds:
        if len(hold) >= 2:
            base_name = hold[0]
            amt = int(hold[1])

            for i in range(amt):
                img_name = f'{base_name}{str(i + 1).zfill(2)}{suffix}'
                imgs = ig.add_additional_image_slots(addl_imgs, [img_name])

                tick = uTick('', imgs, nummies, 1, 1, is_first)
                is_first = False
                ticks.append(tick)

    return ticks, nw_pool


def create_shaded_ticket(addl_nums, color, exclusions, first, full, imgs, is_first,
                         last, nw_pool, shade, spots, forced_position, pi: bool = False):
    """
    Helper to generate a single shaded ticket.
    Places the shaded number at 'forced_position' to ensure even distribution.
    """
    global suffix

    # 1. Refill Pool if needed
    if len(nw_pool) < spots - 1:
        nw_pool = ng.create_number_pools_from_suffix_list(first, last, exclusions, True)

    # 2. Format the Shaded Value
    shade_str = str(shade)
    if full:
        shaded_val = f'<@{color}FONT>{shade_str}'
    else:
        # Suffix Only
        if len(shade_str) >= 2:
            shaded_val = f'{shade_str[:-2]}<@{color}FONT>{shade_str[-2:]}'
        else:
            # Fallback for single digit
            shaded_val = f'<@{color}FONT>{shade_str}'

    # 3. Construct the Number List (Deterministic Positioning)
    # Create a list of placeholders
    numbs = [None] * spots

    # Place the shaded value at the specific forced position
    # (Safety check to ensure index is valid)
    idx = forced_position if forced_position < spots else 0
    numbs[idx] = shaded_val

    # Fill the remaining None spots with Non-Winners
    for i in range(spots):
        if numbs[i] is None:
            numbs[i] = nw_pool.pop(0)

    # 4. Add Padding (Additional Nums)
    for _ in range(addl_nums):
        numbs.append('')

    # 5. Handle PI (Plus Image) Logic
    base_images = copy.deepcopy(imgs)
    if pi:
        # We use the known index 'idx' to calculate the filename
        offset = -len(suffix) if suffix else None
        current_base = base_images[0]

        # positions are 0-indexed in code, but 1-based in filenames (01, 02...)
        pos_str = str(idx + 1).zfill(2)

        if offset:
            new_base = f'{current_base[:offset]}-{pos_str}{current_base[offset:]}'
        else:
            new_base = f'{current_base}-{pos_str}'

        base_images[0] = new_base

    tick = uTick('', base_images, numbs, 1, 1, is_first)
    return nw_pool, tick


def create_nonwinner_numbers(nw_ticket: NonWinnerNumbersTicket,
                             nw_pool: list[str], addl_imgs: gi.AddImages,
                             num_slots: int, is_first: bool = False):
    """
    Create Non-Winner tickets using the remaining pool.
    """
    global suffix

    amt = nw_ticket.quantity
    spots = nw_ticket.spots
    first = nw_ticket.first_num
    last = nw_ticket.last_num
    base = nw_ticket.base_image

    exclusions = nw_ticket.exclusions.split(',') if nw_ticket.exclusions else ['00']
    exclusions = [x for x in exclusions if x]

    if base:
        base = f'{base}{suffix}'

    addl_nums = num_slots - spots
    imgs = ig.add_additional_image_slots(addl_imgs, [base])

    ticks = []
    while len(ticks) < amt:
        if len(nw_pool) < spots:
            nw_pool = ng.create_number_pools_from_suffix_list(first, last, exclusions, True)

        numbs = []
        for _ in range(spots):
            if nw_pool:
                numbs.append(nw_pool.pop(0))
            else:
                numbs.append(0)

        for _ in range(addl_nums):
            numbs.append('')

        tick = uTick('', imgs, numbs, 1, 1, is_first)
        is_first = False
        ticks.append(tick)

    return ticks


def get_total_number_spots(nw_obj, inst_obj, pick_obj, hold_obj):
    """
    Determines the maximum number of 'spots' (numbers) required on any ticket
    to align the columns in the CSV.
    """
    top_number = 0

    if isinstance(nw_obj, NonWinnerNumbersTicket):
        if nw_obj.spots > top_number:
            top_number = nw_obj.spots

    if isinstance(inst_obj, InstantShadedTicket):
        if inst_obj.spots > top_number:
            top_number = inst_obj.spots

    if isinstance(hold_obj, HoldShadedTicket):
        if hold_obj.spots > top_number:
            top_number = hold_obj.spots

    return top_number


def create_game(data_bundle):
    """
    Main Entry Point.
    Refactored to use Data Objects.
    """
    global suffix

    # 1. Unpack Objects
    game_info = data_bundle[0]  # type: GameInfo
    nw_specs = data_bundle[1]  # type: NonWinnerNumbersTicket
    inst_specs = data_bundle[2]  # type: InstantImagesTicket | InstantShadedTicket
    pick_specs = data_bundle[3]  # type: PickImagesTicket
    hold_specs = data_bundle[4]  # type: HoldShadedTicket
    name_specs = data_bundle[5]  # type: NamesData
    output_folder = data_bundle[6]

    if DEBUG:
        print(f"Game: {name_specs.file_name}")

    suffix = game_info.image_suffix
    partname = name_specs.base_part
    filename = name_specs.file_name

    ups = game_info.ups
    perms = game_info.permutations
    sheets = game_info.sheets
    capacity = game_info.capacity[1]  # Bottom Out
    subflats = game_info.subflats

    tickets = []
    nons_pool = []
    ceedee_tier = 0
    first_time = True

    # 2. Calculate Max Number Spots
    num_count = get_total_number_spots(nw_specs, inst_specs, pick_specs, hold_specs)

    # 3. Create Holds (Shaded)
    if isinstance(hold_specs, HoldShadedTicket):
        # Note: nons_pool is initialized here by the holds
        tickles, nons_pool = create_hold_shaded_tickets(
            hold_specs, gi.AddImages.NoneAdded, num_count, is_first=first_time
        )
        tickets.extend(tickles)
        first_time = False

    # 4. Create Instants (Shaded OR Images)
    if isinstance(inst_specs, InstantShadedTicket):
        tickies, nons_pool = create_instant_winner_shaded_tickets(
            inst_specs, nons_pool, gi.AddImages.NoneAdded, num_count, is_first=first_time
        )
        ceedee_tier = inst_specs.cd_tier
        tickets.extend(tickies)
        first_time = False

    elif isinstance(inst_specs, InstantImagesTicket):
        if inst_specs.total_quantity > 0:
            tickets.extend(create_instant_winner_image_tickets(
                inst_specs, gi.AddImages.NoneAdded, num_count, is_first=first_time
            ))
            ceedee_tier = inst_specs.cd_tier
            first_time = False

    # 5. Create NonWinners (Numbers)
    if isinstance(nw_specs, NonWinnerNumbersTicket):
        tickets.extend(create_nonwinner_numbers(
            nw_specs, nons_pool, gi.AddImages.NoneAdded, num_count, is_first=first_time
        ))
        first_time = False

    # 6. Output
    tio.write_tickets_to_file(filename, tickets, output_folder)

    game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacity, True, 0)

    ceedees, blankets = tio.write_game_stacks_to_file(
        filename, game_stacks, ups, sheets, capacity, output_folder
    )

    if len(ceedees) > 0:
        tio.write_cd_positions_to_csv_file(
            partname, filename, ceedees, ceedee_tier, output_folder
        )

    return f"Successfully created {len(tickets) * ups} tickets."


if __name__ == "__main__":
    # MOCK TEST DATA
    # Based on "Twice Fifty" config from original legacy code
    mock_game = GameInfo(
        ups=20, permutations=1, sheets=100, window_structure='3-1',
        capacity=([80, 80]), reset_pool=False, subflats=0, schisms=0, image_suffix='.pdf'
    )

    # NonWinner Numbers
    mock_nw = NonWinnerNumbersTicket(
        quantity=346, spots=8, first_num=101, last_num=999,
        exclusions='00,50,33,22,11', base_image='base'
    )

    # Instant Winners (Shaded)
    # Tier 1: 33s
    t1 = ShadedTier(numbers=[33, 133, 233], suffix='33', color='RED', is_full=False, base_image='winner01')
    # Tier 2: 22s
    t2 = ShadedTier(numbers=[22, 122, 222], suffix='22', color='RED', is_full=False, base_image='winner02')
    # Tier 3: 11s
    t3 = ShadedTier(numbers=[11, 111, 211], suffix='11', color='RED', is_full=False, base_image='winner03')

    mock_inst = InstantShadedTicket(
        tiers=[t1, t2, t3],
        first_num=101, last_num=999, spots=6, cd_tier=0, exclusions='50,00'
    )

    # Hold Tickets (Shaded)
    # Tier 1: 50s (PI enabled in original, logic implies image swaps)
    h1 = ShadedTier(
        numbers=[50, 150, 250], suffix='50', color='RED', is_full=True, base_image='hold01', pi_enabled=True
    )
    # Tier 2: 00s
    h2 = ShadedTier(
        numbers=[100, 200, 300], suffix='00', color='RED', is_full=True, base_image='hold01', pi_enabled=True
    )

    mock_hold = HoldShadedTicket(
        tiers=[h1, h2],
        first_num=101, last_num=999, spots=6, exclusions='33,22,11', image_holds=[]
    )

    # Pick Tickets (Empty)
    mock_pick = PickImagesTicket(tiers=[])

    mock_names = NamesData(base_part='992-016', file_name='TwiceFifty-31885')

    bundle = [mock_game, mock_nw, mock_inst, mock_pick, mock_hold, mock_names, '']

    print("--- Running Test: Twice Fifty (Mock) ---")
    create_game(bundle)