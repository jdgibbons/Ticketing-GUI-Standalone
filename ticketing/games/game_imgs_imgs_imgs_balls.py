"""
Nonwinners: images
Instants: images
Picks: images
Holds: bingo balls

This module is called from the CSV Generator when the nonwinners, instants, and picks are composed of simple images,
but the holds are composed of bingo balls.
"""
import copy
import random as rn
import itertools as it

from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi
from ticketing import ticket_io as tio

# IMPORT DATA MODELS
from ticketing.ticket_models import (
    GameInfo, NamesData,
    NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldBallsTicket
)

DEBUG = True
suffix = ''


def create_imaged_nonwinner_tickets(nw_ticket: NonWinnerImagesTicket,
                                    add_imgs: list[gi.AddImages], first: bool, numerals: int = 0) -> list[uTick]:
    """
    Create a list of nonwinner tickets consisting of one or more images.
    """
    global suffix

    amt = nw_ticket.quantity
    q_nw_image_pool = nw_ticket.pool_size
    pics_per_ticket = nw_ticket.images_per_ticket

    numbs = [''] * numerals

    nw_image_lines = ig.create_image_lists_from_pool(1, q_nw_image_pool, 'nonwinner', amt,
                                                     pics_per_ticket, suffix)
    ticks = []
    for nw in nw_image_lines:
        pics = nw
        for add in add_imgs:
            pics = ig.add_additional_image_slots(add, list(pics))

        ticks.append(uTick('', pics, numbs, 1, 1, first))
        first = False
    return ticks


def create_instant_winners(inst_ticket: InstantImagesTicket, tkt: int | str,
                           addl_imgs: list[gi.AddImages], nummies: int, first=True) -> list[uTick]:
    """
    Create a list of instant winner tickets.
    """
    global suffix

    cd_tier = inst_ticket.cd_tier
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]

    imgs = ig.create_tiered_image_list_augmented(amt_list, 'winner', suffix)

    nums = [''] * nummies
    ticks = []
    cull_ticket = first

    for img in imgs:
        pics = [img[0]]
        for add in addl_imgs:
            pics = ig.add_additional_image_slots(add, pics)

        tick = uTick(tkt, pics, nums, 1, 1, cull_ticket)

        if img[1] <= cd_tier:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')

        ticks.append(tick)
        cull_ticket = False

        if tkt != '' and isinstance(tkt, int):
            tkt += 1

    return ticks


def create_pick_winners(pick_ticket: PickImagesTicket, tkt: int, addl_imgs: list[gi.AddImages], nummies: int,
                        first: bool = False) -> list[uTick]:
    """
    Create a list of pick winner tickets.
    """
    global suffix
    ticks = []
    img_list = []
    nums = [''] * nummies

    amt_list = [tier.quantity for tier in pick_ticket.tiers]
    uniq = pick_ticket.tiers[0].is_unique if pick_ticket.tiers else False

    if len(amt_list) == 1:
        imgs = ig.create_prefixed_images(1, amt_list[0], 'pick', uniq)
        for img in imgs:
            img_list.append([img, 1])
    else:
        img_list = ig.create_tiered_image_list(amt_list, 'pick', False)

    cull_ticket = first

    for img in img_list:
        pics = [img[0]]
        for add in addl_imgs:
            pics = ig.add_additional_image_slots(add, pics)

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
    Create bingo downlines.
    """
    global suffix
    bingos = ig.create_bingo_downlines(bpt, 'hold', False, suffix)
    if len(bingos) < amt:
        return None
    for _ in range(rn.randint(5, 10)):
        rn.shuffle(bingos)
    return bingos[0: amt]


def create_hold_tickets(hold_ticket: HoldBallsTicket, tkt: int | str,
                        addl_bb_imgs: list[gi.AddImages], addl_sup_imgs: list[gi.AddImages],
                        permits: int, first: bool) -> list[list[uTick]] | None | str:
    """
    Create bingo ball and supplemental hold tickets.
    """
    # Extract properties
    bb_amt = hold_ticket.quantity
    bpt = hold_ticket.bingos_per_ticket
    spt = hold_ticket.spots_per_ticket
    fill_pool = hold_ticket.pool_size

    downs = hold_ticket.use_downlines
    shazams = hold_ticket.shazams
    sortie = hold_ticket.sort_balls
    base = hold_ticket.base_image
    match_bbs = hold_ticket.match_bbs
    iterations = hold_ticket.iterations

    sup_holds_list = []
    sup_holds_total = 0
    for color, amt in hold_ticket.additional_holds:
        sup_holds_list.append([color, amt])
        sup_holds_total += amt

    perms = []

    # 1. Create Bingo Ball Tickets
    if bb_amt > 0:
        # We now pass iterations into the function, so it can handle the
        # "Generate Layout Once -> Apply to Multiple Bases" logic.
        perms = create_bingo_ball_tickets(bb_amt, bpt, spt, downs, permits, first, 0, fill_pool,
                                          addl_bb_imgs, tkt, shazams, base, iterations, sortie)

        # Calculate how many tickets were generated to update tkt_no properly
        # Each perm has (bb_amt * iterations) tickets.
        total_generated_per_perm = bb_amt * iterations

        if isinstance(tkt, int):
            tkt += total_generated_per_perm

        first = False

    # 2. Create Supplemental Holds
    if sup_holds_total > 0:
        if match_bbs:
            ticks = create_bb_match_image_holds(sup_holds_list, addl_bb_imgs, fill_pool, spt, base, first)
        else:
            ticks = create_single_image_holds(sup_holds_list, addl_sup_imgs, first)

        first = False

        if len(perms) == 0:
            perms = [[] for _ in range(permits)]

        for index, perm in enumerate(perms):
            single_copy = copy.deepcopy(ticks)
            for tick in single_copy:
                tick.reset_permutation(index + 1)
                perm.append(tick)

    return perms


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


def create_single_image_holds(suppers: list[list[str | int]], addl_imgs: list[gi.AddImages], first: bool):
    global suffix
    ticks = []
    numbs = []
    for sup in suppers:
        prefix = f'{sup[0]}'
        pics = ig.create_prefixed_images(1, sup[1], prefix, True, suffix)
        for pic in pics:
            imgs = [pic]
            for add in addl_imgs:
                imgs = ig.add_additional_image_slots(add, imgs)
            ticks.append(uTick('', imgs, numbs, 1, 1, first))
            first = False
    return ticks


def create_bingo_ball_tickets(bb_amt, bpt, spt, downs, permits: int, first, nums, nw_pool,
                              addl_bb_imgs, tkt, shazams: int, basic: str, iterations: int, sortie: bool = True):
    """
    Create a list of bingo-ball-type hold-tickets.

    Refactored for Iterations:
    1. Generates the 'Master Layouts' (Balls + Fillers + Shazams) ONCE per permutation.
    2. Then iterates through 'iterations' (Base01, Base02...) applying those layouts.
    """
    global suffix
    perms = []
    numbs = [''] * nums
    tick_places = list(range(bb_amt))

    if downs:
        bangles = [create_downline_image_lists(bb_amt, bpt)]
    else:
        bangles = ig.create_bingo_ball_image_permutations(bb_amt, bpt, permits, 'hold', sortie, suffix)

    for index, bingos in enumerate(bangles):
        # --- STEP 1: PREPARE THE MASTER LAYOUTS ---
        # We modify the 'bingos' list IN PLACE to add Shazams and Fillers.
        # This creates the "Same Numbers/Layout" that will be reused across iterations.

        # Determine Shazam positions
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(tick_places)
        places = tick_places[0: shazams]
        places.sort(reverse=True)
        shizzle = copy.deepcopy(shazams)

        # Insert Non-Winner Fillers if needed (e.g. 3 balls on a 5-spot ticket)
        if bpt != spt:
            nw_imgs = ig.create_image_pool(1, nw_pool, 'nonwinner', True, suffix)
            for _ in range(rn.randint(2, 5)):
                rn.shuffle(nw_imgs)
            nw_cycle = it.cycle(nw_imgs)
            for bingo in bingos:
                while len(bingo) < spt:
                    bingo.insert(rn.randint(0, len(bingo) + 1), next(nw_cycle))

        # Insert Shazams
        positions = list(range(1, spt + 1))
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(positions)
        pos_cycle = it.cycle(positions)

        for innie, bingo in enumerate(bingos):
            # We are building the layout WITHOUT the base image first.
            # Shazams are added to the list.
            if shazams > 0:
                if shizzle > 0:
                    if innie == places[shizzle - 1]:
                        # Insert Shazam
                        bingo.append(f'shazam{str(next(pos_cycle)).zfill(2)}{suffix}')
                        shizzle -= 1
                    else:
                        # Insert Placeholder
                        bingo.append('')
                else:
                    bingo.append('')

        # --- STEP 2: GENERATE TICKETS FOR EACH ITERATION ---
        # Now 'bingos' contains the full layout (Balls + Fillers + Shazams).
        # We loop through iterations, creating tickets by prepending the Base Image.

        perm_ticks = []

        for i in range(iterations):
            tick_no = tkt  # Start ticket numbering
            # Determine Base Name
            # If iterations > 1, assume base01, base02...
            # If iterations == 1, use 'basic' as provided.
            if iterations > 1:
                # Assuming 'basic' is the root name (e.g., 'base')
                current_base_name = f"{basic}{str(i + 1).zfill(2)}{suffix}"
            else:
                # Logic for blank/none base
                if basic in ['', 'none', 'blank', '0', '000']:
                    current_base_name = ''
                else:
                    current_base_name = f"{basic}{suffix}"

            # Create tickets using the PREPARED layouts
            for bingo_layout in bingos:
                # Start with Base Image
                pics = [current_base_name] if current_base_name else ['']

                # Add the prepared layout (Balls/Fillers/Shazams)
                pics.extend(bingo_layout)

                # Apply Padding
                for addl in addl_bb_imgs:
                    pics = ig.add_additional_image_slots(addl, pics)

                # Create Ticket
                perm_ticks.append(uTick(tick_no, pics, numbs, index + 1, 1, first))

                if tick_no != '' and isinstance(tick_no, int):
                    tick_no += 1
                first = False

        perms.append(perm_ticks)

    return perms


def calculate_image_slots(nw_ticket: NonWinnerImagesTicket, hold_ticket: HoldBallsTicket):
    """
    Calculate additional image slots needed for each ticket type.
    """
    nws_needed = nw_ticket.images_per_ticket
    holds_needed = hold_ticket.spots_per_ticket

    holds_supplemental = 0
    if hold_ticket.shazams > 0:
        holds_supplemental += 1

    nw_pre = 0
    nw_post = 0
    hold_pre = 0
    hold_post = 0
    inst_pre = 0
    inst_post = 0

    if nws_needed != 1:
        if holds_needed == nws_needed:
            nw_pre = -1
            inst_post = holds_needed
            if holds_supplemental > 0:
                nw_pre -= 1
                inst_post += 1
        elif holds_needed == 1:
            inst_post = nws_needed
            hold_post = nws_needed
            nw_pre = -1
        else:
            nw_pre = -(holds_needed + 1)
            hold_post = nws_needed
            inst_post = holds_needed + nws_needed
            if holds_supplemental > 0:
                nw_pre -= 1
                inst_post += 1
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


def create_game(data_bundle):
    """
    Main Entry Point.
    """
    global suffix

    # 1. Unpack Objects
    game_info = data_bundle[0]  # type: GameInfo
    nw_specs = data_bundle[1]  # type: NonWinnerImagesTicket
    inst_specs = data_bundle[2]  # type: InstantImagesTicket
    pick_specs = data_bundle[3]  # type: PickImagesTicket
    hold_specs = data_bundle[4]  # type: HoldBallsTicket
    name_specs = data_bundle[5]  # type: NamesData
    output_folder = data_bundle[6]

    if DEBUG:
        print(f"Game: {name_specs.file_name}")

    suffix = game_info.image_suffix
    file_name = name_specs.file_name
    part_name = name_specs.base_part

    ups = game_info.ups
    perms = game_info.permutations
    sheets = game_info.sheets

    # --- CAPACITY LOGIC RESTORED ---
    # We keep this as a list to support differing Bottom-In vs Bottom-Out
    capacities = game_info.capacity

    # Ensure it's a list/tuple (sanity check)
    if isinstance(capacities, int):
        capacities = [capacities, capacities]

    # Explicitly define the two capacities for future logic (5D, 5E, etc.)
    # Legacy code used index 0 for standard stack generation.
    bo_capacity = capacities[0]
    bi_capacity = capacities[1] if len(capacities) > 1 else capacities[0]

    subflats = game_info.subflats

    # Calculate padding
    addl_nw, addl_hold, addl_inst = calculate_image_slots(nw_specs, hold_specs)

    inst_tkt_int = False
    pick_tkt_int = False
    hold_tkt_int = True
    tkt_no = 'unassigned'

    first_timer = True
    instants = []

    # Create Instants
    if inst_specs.total_quantity > 0:
        if inst_tkt_int:
            tkt_no = 0
        else:
            tkt_no = ''
        instants.extend(create_instant_winners(inst_specs, tkt_no, addl_inst, 0, first_timer))
        first_timer = False

    picks = []
    # Create Picks
    if pick_specs.total_quantity > 0:
        if pick_tkt_int:
            tkt_no = 1
        else:
            tkt_no = ''
        picks.extend(create_pick_winners(pick_specs, tkt_no, addl_inst, 0, first_timer))
        first_timer = False

    holds = []
    # Create Holds (Bingo Balls)
    if hold_specs.total_quantity > 0:
        if hold_tkt_int:
            tkt_no = 1

        holds = create_hold_tickets(hold_specs, tkt_no, addl_hold, addl_inst, perms, first_timer)

        if isinstance(holds, str) or holds is None:
            return holds
        first_timer = False

    nonwinners = []
    # Create Non-Winners
    if nw_specs.quantity > 0:
        nonwinners = create_imaged_nonwinner_tickets(nw_specs, addl_nw, first_timer)
        first_timer = False

    # Merge Permutations
    for index, hold_perm_list in enumerate(holds):
        if len(instants) > 0:
            perm_instants = copy.deepcopy(instants)
            for snap in perm_instants:
                snap.reset_permutation(index + 1)
            hold_perm_list.extend(perm_instants)

        if len(picks) > 0:
            perm_picks = copy.deepcopy(picks)
            for snap in perm_picks:
                snap.reset_permutation(index + 1)
            hold_perm_list.extend(perm_picks)

        if len(nonwinners) > 0:
            perm_nws = copy.deepcopy(nonwinners)
            for snap in perm_nws:
                snap.reset_permutation(index + 1)
            hold_perm_list.extend(perm_nws)

    # Output
    # We pass 'bo_capacity' (index 0) to match the legacy logic for standard stacking
    if len(holds) == 1:
        tio.write_tickets_to_file(file_name, holds[0], output_folder)
        game_stacks = tio.create_game_stacks(holds[0], ups, sheets, bo_capacity, True, subflats)
    else:
        tio.write_permutations_to_files(file_name, holds, output_folder)
        game_stacks = tio.create_game_stacks_from_permutations(holds, ups, sheets, bo_capacity,
                                                               True, subflats)

    cds, sheeters = tio.write_game_stacks_to_file(file_name, game_stacks, ups, sheets, bo_capacity, output_folder)

    if len(cds) > 0:
        tio.write_cd_positions_to_csv_file(part_name, file_name, cds, inst_specs.cd_tier)
        # tio.write_cd_positions_to_xml_file(part_name, file_name, cds, inst_specs.cd_tier, ups, output_folder)

    return "CSVs created without incident!"
