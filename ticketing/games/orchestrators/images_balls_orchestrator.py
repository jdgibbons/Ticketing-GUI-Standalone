import ticketing.ticket_io as tio
import ticketing.game_info_gui as gi
from ticketing.games.generators.image_game_generator import ImageGameGenerator
from ticketing.games.generators.balls_game_generator import BallsGameGenerator


def create_game(data_bundle):
    """
    Orchestrator for Games:
    NW: Images | Inst: Images | Pick: Images | Hold: Bingo Balls
    """
    # 1. Unpack Data
    game_info = data_bundle[0]
    nw_specs = data_bundle[1]
    inst_specs = data_bundle[2]
    pick_specs = data_bundle[3]
    hold_specs = data_bundle[4]
    name_specs = data_bundle[5]
    output_folder = data_bundle[6]

    # 2. Setup Shared State
    is_first = True

    # 3. Calculate Padding (Specific to Balls Logic)
    addl_nw, addl_hold, addl_inst = _calculate_padding(nw_specs, hold_specs)

    # --- GENERATION PHASE ---

    # A. Generate PICKS (Images)
    pick_batches = []
    if hasattr(pick_specs, 'total_quantity') and pick_specs.total_quantity > 0:
        # Use ImageGameGenerator (treating picks as standard images)
        # Note: Pick tickets usually start at Ticket #1
        gen = ImageGameGenerator(game_info, addl_inst, pick_specs, 0)
        gen.set_start_state([], is_first)
        gen.start_ticket_number = 1
        pick_batches, _ = gen.generate()
        is_first = False

    # B. Generate HOLDS (Balls)
    hold_batches = []
    if hasattr(hold_specs, 'total_quantity') and hold_specs.total_quantity > 0:
        # Holds start at Ticket #1 (if no picks/instants/etc, or logical sequence)
        # In legacy, 'hold_tkt_int' = True, usually reset to 1
        gen = BallsGameGenerator(game_info, addl_hold, hold_specs, hold_specs.spots_per_ticket)
        gen.set_start_state([], is_first)
        gen.start_ticket_number = 1
        hold_batches, _ = gen.generate()
        is_first = False

    # C. Generate INSTANTS (Images)
    inst_batches = []
    if hasattr(inst_specs, 'total_quantity') and inst_specs.total_quantity > 0:
        # Instants usually Ticket #0 or ''
        gen = ImageGameGenerator(game_info, addl_inst, inst_specs, 0)
        gen.set_start_state([], is_first)
        gen.start_ticket_number = ''
        inst_batches, _ = gen.generate()
        is_first = False

    # D. Generate NON-WINNERS (Images)
    nw_batches = []
    if hasattr(nw_specs, 'total_quantity') and nw_specs.total_quantity > 0:
        gen = ImageGameGenerator(game_info, addl_nw, nw_specs, 0)
        gen.set_start_state([], is_first)
        # Non-Winners usually don't have ticket numbers
        gen.start_ticket_number = ''
        nw_batches, _ = gen.generate()
        is_first = False

    # --- MERGE PHASE ---
    final_permutations = []
    perms = game_info.permutations

    # The merge order in legacy was: Holds + Instants + Picks + NWs
    # We loop through Perms and append.
    for i in range(perms):
        current_perm = []

        # 1. Holds (Base)
        if i < len(hold_batches):
            current_perm.extend(hold_batches[i])

        # 2. Instants (Copied if less perms than Holds)
        if i < len(inst_batches):
            current_perm.extend(inst_batches[i])
        elif len(inst_batches) == 1:
            current_perm.extend(inst_batches[0])

        # 3. Picks
        if i < len(pick_batches):
            current_perm.extend(pick_batches[i])
        elif len(pick_batches) == 1:
            current_perm.extend(pick_batches[0])

        # 4. Non-Winners
        if i < len(nw_batches):
            current_perm.extend(nw_batches[i])
        # Note: NonWinners might already be unique per perm if generated that way.

        final_permutations.append(current_perm)

    # --- OUTPUT PHASE ---
    filename = name_specs.file_name
    partname = name_specs.base_part

    # Write Permutations
    tio.write_permutations_to_files(filename, final_permutations, False, output_folder)

    # Stacking
    ups = game_info.ups
    sheets = game_info.sheets
    # Handling capacity tuple (bi, bo)
    capacities = game_info.capacity
    if isinstance(capacities, int): capacities = [capacities, capacities]
    bo_capacity = capacities[0]

    game_stacks = tio.create_game_stacks_from_permutations(
        final_permutations, ups, sheets, bo_capacity, True, game_info.subflats
    )

    cd_positions, _ = tio.write_game_stacks_to_file(
        filename, game_stacks, ups, sheets, bo_capacity, output_folder
    )

    if len(cd_positions) > 0:
        cd_tier = getattr(inst_specs, 'cd_tier', 0)
        tio.write_cd_positions_to_csv_file(partname, filename, cd_positions, cd_tier, output_folder)
        tio.write_cd_positions_to_xml_file(partname, filename, cd_positions, cd_tier, ups, output_folder)

    return "Successfully generated Images/Balls game."


def _calculate_padding(nw_ticket, hold_ticket):
    """
    Replicated padding logic from legacy game_imgs_imgs_imgs_balls.py
    """
    nws_needed = nw_ticket.images_per_ticket
    holds_needed = hold_ticket.spots_per_ticket

    holds_supplemental = 0
    if hold_ticket.shazams > 0:
        holds_supplemental += 1

    nw_pre = 0;
    nw_post = 0
    hold_pre = 0;
    hold_post = 0
    inst_pre = 0;
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

    return add_nw, add_hold, add_inst
