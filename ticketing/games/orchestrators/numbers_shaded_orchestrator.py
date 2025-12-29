import ticketing.ticket_io as tio
import ticketing.game_info_gui as gi
from ticketing.games.generators.shaded_game_generator import ShadedGameGenerator
from ticketing.games.generators.number_game_generator import NumberGameGenerator
from ticketing.games.generators.image_game_generator import ImageGameGenerator


def create_game(data_bundle):
    """
    Orchestrator for Games:
    NW: Numbers | Inst: Shaded/Images | Pick: Images | Hold: Shaded
    Replaces: game_numbs_shade_imgs_shade.py
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
    nw_pool = []
    is_first = True

    # Calculate Max Spots (to align CSV columns)
    # This logic assumes simple max() calculation.
    # If your legacy code had complex column logic, replicate it here.
    max_spots = 0
    if hasattr(nw_specs, 'spots'): max_spots = max(max_spots, nw_specs.spots)
    if hasattr(inst_specs, 'spots'): max_spots = max(max_spots, inst_specs.spots)
    if hasattr(hold_specs, 'spots'): max_spots = max(max_spots, hold_specs.spots)

    # 3. Determine Image Padding (Columns)
    # Legacy logic: Holds usually define the structure for Shaded games.
    # For now, we default to NoneAdded, but you can add logic here to compare
    # nw_specs vs hold_specs image counts if needed.
    nw_padding = [gi.AddImages.NoneAdded]
    inst_padding = [gi.AddImages.NoneAdded]
    hold_padding = [gi.AddImages.NoneAdded]
    pick_padding = [gi.AddImages.NoneAdded]

    # --- GENERATION PHASE ---

    # A. Generate PICKS (Images)
    # Picks are processed first or early to ensure image assets are handled
    pick_batches = []
    if hasattr(pick_specs, 'total_quantity') and pick_specs.total_quantity > 0:
        # Picks are typically images, so we use the ImageGameGenerator.
        # We pass 'max_spots' so it adds the correct number of empty CSV columns for the numbers.
        gen = ImageGameGenerator(game_info, pick_padding, pick_specs, max_spots)
        gen.set_start_state([], is_first)
        pick_batches, _ = gen.generate()
        is_first = False

    # B. Generate HOLDS (Shaded)
    hold_batches = []
    if hasattr(hold_specs, 'total_quantity') and hold_specs.total_quantity > 0:
        # Determine number of non-winning images needed for padding logic
        # (This mimics logic from your legacy files)
        num_nw_imgs = 1

        gen = ShadedGameGenerator(game_info, hold_padding, hold_specs, max_spots, num_nw_imgs)
        gen.set_start_state(nw_pool, is_first)
        hold_batches, nw_pool = gen.generate()
        is_first = False  # Once first ticket is done, flag is off forever

    # C. Generate INSTANTS (Shaded or Images)
    inst_batches = []
    if hasattr(inst_specs, 'total_quantity') and inst_specs.total_quantity > 0:
        # 1. CHECK FOR SHADED (Has Tiers AND Color)
        # We check tiers[0].color safely
        is_shaded = False
        if hasattr(inst_specs, 'tiers') and len(inst_specs.tiers) > 0:
            if hasattr(inst_specs.tiers[0], 'color') and inst_specs.tiers[0].color:
                is_shaded = True

        if is_shaded:
            # === SHADED GENERATION ===
            gen = ShadedGameGenerator(game_info, inst_padding, inst_specs, max_spots, 1)
            gen.set_start_state(nw_pool, is_first)
            inst_batches, nw_pool = gen.generate()
            is_first = False
        else:
            # === IMAGE GENERATION ===
            # Used for "NIISH" games (Numbers, Images, Images, Shaded)
            # We use ImageGameGenerator, passing 'max_spots' so it pads the number columns correctly.
            gen = ImageGameGenerator(game_info, inst_padding, inst_specs, max_spots)
            gen.set_start_state([], is_first)
            # Image generation doesn't consume the NW pool, so we ignore the pool return
            inst_batches, _ = gen.generate()
            is_first = False

    # D. Generate NON-WINNERS (Numbers)
    nw_batches = []
    if hasattr(nw_specs, 'quantity') and nw_specs.quantity > 0:
        gen = NumberGameGenerator(game_info, nw_padding, nw_specs, max_spots)
        gen.set_start_state(nw_pool, is_first)
        nw_batches, nw_pool = gen.generate()
        is_first = False

    # --- MERGE PHASE ---
    # Combine all batches into final permutations list
    final_permutations = []
    perms = game_info.permutations

    for i in range(perms):
        current_perm = []

        # Add Picks
        # ImageGameGenerator returns a batch per perm, or duplicates if perms > 1
        if i < len(pick_batches):
            current_perm.extend(pick_batches[i])
        elif len(pick_batches) == 1:
            current_perm.extend(pick_batches[0])

        # Add Holds
        if i < len(hold_batches):
            current_perm.extend(hold_batches[i])

        # Add Instants (Note: Instants often repeat same batch across perms, logic varies)
        if i < len(inst_batches):
            current_perm.extend(inst_batches[i])
        elif len(inst_batches) == 1:
            # If only 1 batch generated, reuse it (common for instants)
            # You might need deepcopy here if modifying tickets
            current_perm.extend(inst_batches[0])

        # Add Non-Winners
        if i < len(nw_batches):
            current_perm.extend(nw_batches[i])

        final_permutations.append(current_perm)

    # --- OUTPUT PHASE ---
    filename = name_specs.file_name

    # Write Raw
    tio.write_permutations_to_files(filename, final_permutations, False, output_folder)

    # Create Stacks
    ups = game_info.ups
    sheets = game_info.sheets
    # Handle tuple capacity vs int
    capacity = game_info.capacity[1] if isinstance(game_info.capacity, tuple) or isinstance(game_info.capacity,
                                                                                            list) else game_info.capacity

    game_stacks = tio.create_game_stacks_from_permutations(final_permutations, ups, sheets, capacity)

    cd_positions, cd_sheets = tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets, capacity, output_folder)

    partname = name_specs.base_part
    if len(cd_positions) > 0:
        tio.write_cd_positions_to_csv_file(
            partname, filename, cd_positions, inst_specs.cd_tier, output_folder
        )

    return f"Successfully generated {len(final_permutations)} permutations using Class-Based logic."