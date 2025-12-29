import ticketing.ticket_io as tio
import ticketing.game_info_gui as gi
from ticketing.games.generators.image_game_generator import ImageGameGenerator


def create_game(data_bundle):
    """
    Orchestrator for All-Image Games.
    Replaces: game_imgs_imgs_imgs_imgs.py
    """
    game_info, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = data_bundle

    # 1. Calculate Image Padding
    # If NonWinners have >1 image, other tickets need padding.
    nw_imgs_count = getattr(nw_specs, 'images_per_ticket', 1)

    # Define padding rules
    nw_pad = []
    other_pad = []

    if nw_imgs_count > 1:
        # NonWinners get PreOne (-1)
        nw_pad = [gi.add_images_lookup(-1)]
        # Others get Post(NW_Count)
        other_pad = [gi.add_images_lookup(nw_imgs_count)]
    else:
        nw_pad = [gi.AddImages.NoneAdded]
        other_pad = [gi.AddImages.NoneAdded]

    # 2. Generate Batches
    all_batches = []
    is_first = True

    # Helper to run generator and merge results
    def run_gen(ticket_data, padding):
        nonlocal is_first
        if ticket_data.total_quantity > 0:
            gen = ImageGameGenerator(game_info, padding, ticket_data, 0)  # 0 number slots
            gen.set_start_state([], is_first)
            batches, _ = gen.generate()
            is_first = False

            all_batches.extend(batches[0])

    # A. Picks
    run_gen(pick_specs, other_pad)

    # B. Instants
    run_gen(inst_specs, other_pad)

    # C. Holds
    run_gen(hold_specs, other_pad)

    # D. Non-Winners
    run_gen(nw_specs, nw_pad)

    # 3. Output
    filename = name_specs.file_name
    tio.write_tickets_to_file(filename, all_batches, output_folder)

    # Create Stacks
    ups = game_info.ups
    capacity = game_info.capacity[1] if isinstance(game_info.capacity, (list, tuple)) else game_info.capacity

    # Logic: Disable mixer for complex structures
    mixer = game_info.window_structure not in tio.non_shuffles

    game_stacks = tio.create_game_stacks(all_batches, ups, game_info.sheets, capacity, mixer, game_info.subflats)
    cd_positions, cd_sheets = tio.write_game_stacks_to_file(filename, game_stacks, ups, game_info.sheets,
                                                            capacity, output_folder)

    partname = name_specs.base_part
    if len(cd_positions) > 0:
        tio.write_cd_positions_to_csv_file(
            partname, filename, cd_positions, inst_specs.cd_tier, output_folder
        )

    return f"Generated {len(all_batches)} permutations (All Images)."
