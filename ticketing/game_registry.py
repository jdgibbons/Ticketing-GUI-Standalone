from ticketing.ticket_models import (
    NonWinnerNumbersTicket, NonWinnerImagesTicket,
    InstantCannonsTicket, InstantImagesTicket, InstantShadedTicket,
    PickImagesTicket,
    HoldCannonsTicket, HoldImagesTicket, HoldMatrixTicket,
    HoldBallsTicket, HoldBingosTicket, HoldShadedTicket, HoldFlashboardTicket
)

# --- LEGACY MODULES ---
from ticketing.games.game_numbs_imgs_imgs_imgs import create_game as game_numbs_imgs_imgs_imgs_cg
from ticketing.games.game_imgs_imgs_imgs_matrix import create_game as game_imgs_imgs_imgs_matrix_cg
from ticketing.games.game_numbs_imgs_imgs_flash import create_game as game_numbs_imgs_imgs_flash_cg
from ticketing.games.game_imgs_imgs_imgs_bingos import create_game as game_imgs_imgs_imgs_bingos_cg
from ticketing.games.game_imgs_imgs_imgs_vballs import create_game as game_imgs_imgs_imgs_vballs_cg
from ticketing.games.game_imgs_imgs_imgs_bnumbs import create_game as game_imgs_imgs_imgs_bnumbs_cg
from ticketing.games.game_numbs_imgs_imgs_balls import create_game as game_numbs_imgs_imgs_balls_cg

# --- NEW ORCHESTRATORS ---
from ticketing.games.orchestrators.numbers_cannons_orchestrator import create_game as create_cannons_game
from ticketing.games.orchestrators.numbers_shaded_orchestrator import create_game as create_ns_game
from ticketing.games.orchestrators.all_images_orchestrator import create_game as create_images_game
from ticketing.games.orchestrators.images_balls_orchestrator import create_game as create_balls_game


# ==============================================================================
# THE REGISTRY
# ==============================================================================

GAME_REGISTRY = {
    # --- NEW ORCHESTRATORS ---

    # "NSISH" / "NIISH" - Shaded Games
    (NonWinnerNumbersTicket, InstantShadedTicket, PickImagesTicket, HoldShadedTicket): create_ns_game,
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket, HoldShadedTicket): create_ns_game,

    # "IIIIM" - All Images
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldImagesTicket): create_images_game,

    # "NCICA" - Cannons
    (NonWinnerNumbersTicket, InstantCannonsTicket, PickImagesTicket, HoldCannonsTicket): create_cannons_game,

    # "IIIBA" - Images, Images, Images, Balls
    # UPDATED: Now points to your new orchestrator
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldBallsTicket): create_balls_game,

    # --- LEGACY MODULES ---

    # "NIIIM" - Numbers, Images, Images, Images
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket, HoldImagesTicket): game_numbs_imgs_imgs_imgs_cg,

    # "NIIBA" - Numbers, Images, Images, Balls (NOT YET REFACTORED)
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket, HoldBallsTicket): game_numbs_imgs_imgs_balls_cg,

    # "IIIMA" - Images, Images, Images, Matrix
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldMatrixTicket): game_imgs_imgs_imgs_matrix_cg,

    # "NIIFL" - Numbers, Images, Images, Flashboard
    (NonWinnerNumbersTicket, InstantImagesTicket, PickImagesTicket,
     HoldFlashboardTicket): game_numbs_imgs_imgs_flash_cg,

    # "IIIBI" - Images, Images, Images, Bingos
    (NonWinnerImagesTicket, InstantImagesTicket, PickImagesTicket, HoldBingosTicket): game_imgs_imgs_imgs_bingos_cg,
}


def get_game_creator(game_specs, nw_obj, inst_obj, pick_obj, hold_obj):
    """
    Determines the correct game creation function based on the TYPES of the objects passed.
    """
    nw_type = type(nw_obj)
    inst_type = type(inst_obj)
    pick_type = type(pick_obj)
    hold_type = type(hold_obj)

    # --- SPECIAL LOGIC FOR VARIATIONS ---

    # 1. Bingos -> Verified Balls (IIIBB)
    if isinstance(hold_obj, HoldBingosTicket) and hold_obj.use_bingo_balls:
        return game_imgs_imgs_imgs_vballs_cg

    # 2. Balls -> Bingo Numbers (IIIBN)
    # This remains legacy unless you want to refactor 'game_imgs_imgs_imgs_bnumbs' too.
    if isinstance(hold_obj, HoldBallsTicket) and hold_obj.non_image_mode:
        return game_imgs_imgs_imgs_bnumbs_cg

    # --- STANDARD LOOKUP ---
    key = (nw_type, inst_type, pick_type, hold_type)

    return GAME_REGISTRY.get(key)