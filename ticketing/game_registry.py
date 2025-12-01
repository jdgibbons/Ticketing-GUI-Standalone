from ticketing.ticket_models import (
    NonWinnerNumbersTicket, NonWinnerImagesTicket,
    InstantCannonsTicket, InstantImagesTicket, InstantShadedTicket,
    PickImagesTicket,
    HoldCannonsTicket, HoldImagesTicket, HoldMatrixTicket,
    HoldBallsTicket, HoldBingosTicket, HoldShadedTicket, HoldFlashboardTicket
)

# --- IMPORT YOUR RENAMED GAME MODULES ---
from ticketing.games.game_numbs_cans_imgs_cans import create_game as game_numbs_cans_imgs_cans_cg
from ticketing.games.game_numbs_shade_imgs_shade import create_game as game_numbs_shade_imgs_shade_cg
from ticketing.games.game_numbs_imgs_imgs_imgs import create_game as game_numbs_imgs_imgs_imgs_cg
from ticketing.games.game_imgs_imgs_imgs_imgs import create_game as game_imgs_imgs_imgs_imgs_cg
from ticketing.games.game_imgs_imgs_imgs_balls import create_game as game_imgs_imgs_imgs_balls_cg
from ticketing.games.game_imgs_imgs_imgs_matrix import create_game as game_imgs_imgs_imgs_matrix_cg
from ticketing.games.game_numbs_imgs_imgs_flash import create_game as game_numbs_imgs_imgs_flash_cg
from ticketing.games.game_imgs_imgs_imgs_bingos import create_game as game_imgs_imgs_imgs_bingos_cg
from ticketing.games.game_imgs_imgs_imgs_vballs import create_game as game_imgs_imgs_imgs_vballs_cg
from ticketing.games.game_imgs_imgs_imgs_bnumbs import create_game as game_imgs_imgs_imgs_bnumbs_cg
from ticketing.games.game_numbs_imgs_imgs_balls import create_game as game_numbs_imgs_imgs_balls_cg

# ==============================================================================
# THE REGISTRY
# Keys are tuples of: (NonWinnerType, InstantType, PickType, HoldType)
# Values are the function to call.
# ==============================================================================

GAME_REGISTRY = {
    # FORMAT: (NW, INST, PICK, HOLD) : function

    # "NCICA" - Numbers, Cannons, Images, Cannons
    (NonWinnerNumbersTicket, InstantCannonsTicket, PickImagesTicket, HoldCannonsTicket): game_numbs_cans_imgs_cans_cg,

    # "NSISH" - Numbers, Shaded, Images, Shaded
    (NonWinnerNumbersTicket, InstantShadedTicket, PickImagesTicket, HoldShadedTicket): game_numbs_shade_imgs_shade_cg,

    # "NIIIM" - Numbers, Images, Images, Images
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket, HoldImagesTicket): game_numbs_imgs_imgs_imgs_cg,

    # "IIIIM" - Images, Images, Images, Images
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldImagesTicket): game_imgs_imgs_imgs_imgs_cg,

    # "IIIBA" - Images, Images, Images, Balls
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldBallsTicket): game_imgs_imgs_imgs_balls_cg,

    # "NIIBA" - Numbers, Images, Images, Balls
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket, HoldBallsTicket): game_numbs_imgs_imgs_balls_cg,

    # "IIIMA" - Images, Images, Images, Matrix
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldMatrixTicket): game_imgs_imgs_imgs_matrix_cg,

    # "NIIFL" - Numbers, Images, Images, Flashboard
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket,
     HoldFlashboardTicket): game_numbs_imgs_imgs_flash_cg,

    # "IIIBI" - Images, Images, Images, Bingos
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldBingosTicket): game_imgs_imgs_imgs_bingos_cg,

    # "IIIBB" - Images, Images, Images, BBalls (Bingos converted to Balls with verified numbers)
    # Note: We handle the logic to map this key in the function below

    # "IIIBN" - Images, Images, Images, BNumbs (Balls converted to Numbers (without images))
    # Note: We handle the logic to map this key in the function below
}


# Define special keys for the variations (like 'BNumbers' or 'Verified Balls')
# Since these variations share the same HoldBallsTicket class, we can use
# string constants or specific references to map them manually if they differ
# significantly in logic. However, based on your import list, you have
# separate modules for them. We can use a custom string key override.
def get_game_creator(game_specs, nw_obj, inst_obj, pick_obj, hold_obj):
    """
    Determines the correct game creation function based on the TYPES of the objects passed.

    Args:
        game_specs (GameInfo): General configuration (window structure, ups, etc.)
        nw_obj (Ticket): NonWinner Ticket Object
        inst_obj (Ticket): Instant Ticket Object
        pick_obj (Ticket): Pick Ticket Object
        hold_obj (Ticket): Hold Ticket Object
    """
    nw_type = type(nw_obj)
    inst_type = type(inst_obj)
    pick_type = type(pick_obj)
    hold_type = type(hold_obj)

    # --- FUTURE LOGIC EXAMPLE ---
    # if game_specs.window_structure == "NS":
    #     return special_ns_game_function

    # --- SPECIAL LOGIC FOR VARIATIONS ---

    # 1. Bingos -> Verified Balls (IIIBB)
    if isinstance(hold_obj, HoldBingosTicket) and hold_obj.use_bingo_balls:
        return game_imgs_imgs_imgs_vballs_cg

    # 2. Balls -> Bingo Numbers (IIIBN)
    if isinstance(hold_obj, HoldBallsTicket) and hold_obj.non_image_mode:
        return game_imgs_imgs_imgs_bnumbs_cg

    # --- STANDARD LOOKUP ---
    key = (nw_type, inst_type, pick_type, hold_type)

    return GAME_REGISTRY.get(key)