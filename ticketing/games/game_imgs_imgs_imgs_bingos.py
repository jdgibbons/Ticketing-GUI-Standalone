"""
Nonwinners: images
Instants: images
Picks: images
Holds: verified bingos

Refactored to use Ticket Models.
"""
import copy
import re

from ticketing import game_info_gui as gi
from ticketing.bingo_ticket import BingoTicket as bTick
from ticketing import verified_bingo as vb
from ticketing import image_generator as ig
from ticketing import ticket_io as tio

# NEW IMPORTS
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
    Create the various either/or bingo tickets required by the game.
    Refactored to accept HoldBingosTicket object.
    """
    # Extract lists from the object
    needs = [
        hold_ticket.dns_counts,
        hold_ticket.ds_counts,
        hold_ticket.sns_counts,
        hold_ticket.ss_counts,
        hold_ticket.either_ors
    ]

    zeroes = hold_ticket.leading_zeroes
    free_type = hold_ticket.free_type

    # "Standard" vs "Extended" logic from legacy code (S vs E)
    is_extended = hold_ticket.extended_csv == 'E' or hold_ticket.extended_csv is True

    # If there is only one permutation or the list can be reset...
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

    base = ['base01.ai']
    is_first = True
    permies = []

    for index, verse in enumerate(versions):
        tkt = 1
        ticks = []
        for face in verse:
            b_type = 'N'

            # --- Logic for determining Base Image and Rows ---
            if csv_rows == 3:
                if len(face[1]) == 1:
                    face[1] += [['', '', '', '', ''], ['', '', '', '', '']]
                    base = ['base01.ai']
                elif len(face[1]) == 2:
                    b_type = determine_b_type(face)
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

            tick = bTick(tkt, face[0], face[1], images, zeroes, index + 1, 1, is_first)
            tick.set_free_type(free_type)
            tick.set_bingo_type(copy.deepcopy(b_type))
            ticks.append(tick)

            is_first = False
            tkt += 1

        permies.append(ticks)

    return permies


def determine_b_type(facial):
    """
    Determines the bingo type (Staggered/Nonstaggered).
    """
    for a, b in zip(facial[1][0], facial[1][1]):
        if bool(a.strip()) ^ bool(b.strip()):
            return 'S'
    return 'N'


def create_instant_winners_refined(inst_ticket: InstantImagesTicket, cd_level: int,
                                   addl_imgs: gi.AddImages, bingo_rows: int,
                                   permits: int) -> list[list[bTick]]:
    """
    Create a list of instant winner tickets (permutations).
    Refactored to accept InstantImagesTicket.
    """
    permies = []
    digits = []
    for _ in range(bingo_rows):
        digits.append(['', '', '', '', ''])

    # Convert Ticket Object data to list for generator
    amt_list = [[tier.quantity, tier.is_unique] for tier in inst_ticket.tiers]

    imgs = ig.create_tiered_image_list_augmented(amt_list, 'winner')
    ticks = []

    for img in imgs:
        img_padded = ig.add_additional_image_slots(addl_imgs, [img[0]])

        tick = bTick('', '', digits, img_padded, False, 1, 1, False)

        if img[1] <= cd_level and img[1] != 0:
            tick.reset_cd_tier(img[1])
            tick.reset_cd_type('I')

        tick.set_bingo_type('O')
        ticks.append(tick)

    permies.append(ticks)

    # Copy for remaining permutations
    for j in range(1, permits):
        temp_ticks = copy.deepcopy(ticks)
        for tick in temp_ticks:
            tick.reset_permutation(j + 1)
        permies.append(temp_ticks)

    return permies


def calculate_image_slots(hold_ticket: HoldBingosTicket, nw_ticket: NonWinnerImagesTicket,
                          free_image: bool):
    """
    Calculates prefix/suffix padding.
    Refactored to use Objects.
    """
    non_base_image_slots = 0
    prefix_value = 0

    if free_image:
        # Check the 4 standard lists (DNS, DS, SNS, SS)
        holders_lists = [
            hold_ticket.dns_counts,
            hold_ticket.ds_counts,
            hold_ticket.sns_counts,
            hold_ticket.ss_counts
        ]

        for sublist in holders_lists:
            for indie, x in enumerate(reversed(sublist)):
                if x != 0:
                    non_base_image_slots = max(non_base_image_slots, len(sublist) - indie - 1)
                    break

        # Check Either/Ors
        if hold_ticket.either_ors and hold_ticket.either_ors[0][0] > 0:
            for hold in hold_ticket.either_ors:
                # hold is [qty, frees, eithers]
                if len(hold) >= 3:
                    frees = hold[1]
                    eithers = hold[2]
                    non_base_image_slots = max(non_base_image_slots, frees + eithers)

        # Check NonWinners
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
    Create a list of nonwinning tickets (permutations).
    Refactored to accept NonWinnerImagesTicket.
    """
    permies = []
    digits = []
    is_first = firstly
    for _ in range(bingo_rows):
        digits.append(['', '', '', '', ''])

    for j in range(permits):
        if nw_ticket.images_per_ticket == 1:
            # Logic wasn't explicit in original for single-image perms, assuming standard pool logic
            nws_perms = ig.create_image_lists_from_pool_perms(
                1, nw_ticket.pool_size, 'nonwinner', nw_ticket.quantity, nw_ticket.images_per_ticket
            )
        else:
            nws_perms = ig.create_image_lists_from_pool_perms(
                1, nw_ticket.pool_size, 'nonwinner', nw_ticket.quantity, nw_ticket.images_per_ticket
            )

        ticks = []
        for nws_perm in nws_perms:
            imgs = ig.add_additional_image_slots(addl_imgs, nws_perm)
            tick = bTick('', '', digits, imgs, False, j + 1, 1, is_first)
            tick.set_bingo_type('O')
            is_first = False
            ticks.append(tick)

        permies.append(ticks)

    return permies


def create_game(data_bundle):
    """
    Main Entry Point.
    Refactored to accept list of Data Objects.
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
    permits = create_hold_tickets(
        hold_specs, bingrows, hold_addls, perms, perm_reset=reset_perms
    )

    if permits is None:
        return "Error creating Bingo Permutations (Check VerifiedBingo logic)."

    # 4. Create Instant Winners (Append to Permutations)
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
