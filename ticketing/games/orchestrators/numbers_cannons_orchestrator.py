import ticketing.ticket_io as tio
import ticketing.game_info_gui as gi
from ticketing.games.generators.cannons_game_generator import CannonsGameGenerator
from ticketing.games.generators.number_game_generator import NumberGameGenerator
from ticketing.games.generators.image_game_generator import ImageGameGenerator
from ticketing.games.generators.shaded_game_generator import ShadedGameGenerator


def create_game(data_bundle):
    """
    Orchestrator for Games:
    NW: Numbers | Inst: Cannons/Shaded/Images | Pick: Images | Hold: Cannons
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

    # Calculate Max Spots (for CSV columns)
    max_spots = 0
    if hasattr(nw_specs, 'spots'): max_spots = max(max_spots, nw_specs.spots)
    if hasattr(inst_specs, 'spots'): max_spots = max(max_spots, inst_specs.spots)
    if hasattr(hold_specs, 'spots'): max_spots = max(max_spots, hold_specs.spots)

    # 3. Padding Defaults
    nw_padding = [gi.AddImages.NoneAdded]
    inst_padding = [gi.AddImages.NoneAdded]
    hold_padding = [gi.AddImages.NoneAdded]
    pick_padding = [gi.AddImages.NoneAdded]

    # --- GENERATION PHASE ---

    # A. Generate PICKS (Images)
    pick_batches = []
    if hasattr(pick_specs, 'total_quantity') and pick_specs.total_quantity > 0:
        gen = ImageGameGenerator(game_info, pick_padding, pick_specs, max_spots)
        gen.set_start_state([], is_first)
        pick_batches, _ = gen.generate()
        is_first = False

    # B. Generate HOLDS (Cannons)
    hold_batches = []
    if hasattr(hold_specs, 'total_quantity') and hold_specs.total_quantity > 0:
        gen = CannonsGameGenerator(game_info, hold_padding, hold_specs, max_spots)
        gen.set_start_state(nw_pool, is_first)
        hold_batches, nw_pool = gen.generate()
        is_first = False

        # C. Generate INSTANTS (Cannons OR Shaded OR Images)
    inst_batches = []
    if hasattr(inst_specs, 'total_quantity') and inst_specs.total_quantity > 0:

        # 1. CHECK FOR CANNONS (Iterative)
        # We detect Cannons by checking the class name string for 'Cannons'
        if 'Cannons' in type(inst_specs).__name__:
            gen = CannonsGameGenerator(game_info, inst_padding, inst_specs, max_spots)
            gen.set_start_state(nw_pool, is_first)
            inst_batches, nw_pool = gen.generate()
            is_first = False

        # 2. CHECK FOR SHADED
        # Shaded tickets have tiers with a color attribute
        elif hasattr(inst_specs, 'tiers') and len(inst_specs.tiers) > 0 and \
                hasattr(inst_specs.tiers[0], 'color') and inst_specs.tiers[0].color:

            gen = ShadedGameGenerator(game_info, inst_padding, inst_specs, max_spots, 1)
            gen.set_start_state(nw_pool, is_first)
            inst_batches, nw_pool = gen.generate()
            is_first = False

        # 3. DEFAULT TO IMAGES (Tiered)
        else:
            gen = ImageGameGenerator(game_info, inst_padding, inst_specs, max_spots)
            gen.set_start_state([], is_first)
            inst_batches, _ = gen.generate()
            is_first = False

    # D. Generate NON-WINNERS (Numbers)
    nw_batches = []
    if hasattr(nw_specs, 'total_quantity') and nw_specs.total_quantity > 0:
        gen = NumberGameGenerator(game_info, nw_padding, nw_specs, max_spots)
        gen.set_start_state(nw_pool, is_first)
        nw_batches, nw_pool = gen.generate()
        is_first = False

    # --- MERGE PHASE ---
    final_permutations = []
    perms = game_info.permutations

    for i in range(perms):
        current_perm = []
        if i < len(pick_batches):
            current_perm.extend(pick_batches[i])
        elif len(pick_batches) == 1:
            current_perm.extend(pick_batches[0])

        if i < len(hold_batches): current_perm.extend(hold_batches[i])

        if i < len(inst_batches):
            current_perm.extend(inst_batches[i])
        elif len(inst_batches) == 1:
            current_perm.extend(inst_batches[0])

        if i < len(nw_batches): current_perm.extend(nw_batches[i])

        final_permutations.append(current_perm)

    # --- OUTPUT PHASE ---
    filename = name_specs.file_name
    tio.write_permutations_to_files(filename, final_permutations, False, output_folder)

    ups = game_info.ups
    sheets = game_info.sheets
    capacity = game_info.capacity[1] if isinstance(game_info.capacity, (tuple, list)) else game_info.capacity

    game_stacks = tio.create_game_stacks_from_permutations(final_permutations, ups, sheets, capacity)
    cd_positions, _ = tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets, capacity, output_folder)

    if len(cd_positions) > 0:
        cd_tier = getattr(inst_specs, 'cd_tier', 0)
        tio.write_cd_positions_to_csv_file(name_specs.base_part, filename, cd_positions, cd_tier, output_folder)
        tio.write_cd_positions_to_xml_file(name_specs.base_part, filename, cd_positions, cd_tier, ups, output_folder)

    return f"Successfully generated {len(final_permutations)} permutations (Cannons)."
