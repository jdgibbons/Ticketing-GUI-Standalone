import random
from collections import namedtuple
from typing import List, Tuple

import ticketing.game_info_gui as gi
import ticketing.image_generator as ig

# Define the lightweight Ticket object (previously uTick)
uTick = namedtuple('uTick', ['base', 'images', 'numbers', 'p_id', 's_id', 'is_first'])


def generate_balanced_positions(num_items: int, total_spots: int) -> List[int]:
    """
    Generates a list of positions that are relatively balanced across the available spots.
    Used to prevent all shaded numbers from bunching up at the start or end of a ticket.
    """
    if num_items == 0:
        return []

    # Calculate the ideal gap between items
    step = total_spots / num_items
    positions = []

    current_pos = 0.0
    for _ in range(num_items):
        # Add a small random jitter so it doesn't look too perfect/robotic
        jitter = random.uniform(-0.5, 0.5)
        target = int(current_pos + jitter)

        # Clamp to valid range (0 to total_spots - 1)
        target = max(0, min(target, total_spots - 1))

        # Ensure we don't pick the same position twice (simple collision avoidance)
        while target in positions:
            target = (target + 1) % total_spots

        positions.append(target)
        current_pos += step

    # Sort them so they appear in order
    return sorted(positions)


def create_shaded_ticket(addl_nums: int, color: str, exclusions: List[str],
                         first_num: int, is_full: bool, imgs: List[str],
                         is_first: bool, last_num: int, nw_pool: List[str],
                         shade: str, spots: int, forced_position: int = -1,
                         pi: bool = False) -> Tuple[List[str], uTick]:
    """
    Constructs a single Shaded Ticket.

    Args:
        addl_nums: Number of filler (non-winning) numbers needed.
        color: The color code for the shaded number font (e.g. 'RED').
        exclusions: List of suffix strings to avoid in filler numbers.
        first_num: Lowest allowed non-winning number.
        is_full: If True, shades the entire number. If False, usually just suffix.
        imgs: The list of images for this ticket.
        is_first: Boolean flag for the 'is_first' property on uTick.
        last_num: Highest allowed non-winning number.
        nw_pool: The list of already used non-winning numbers (to avoid dupes).
        shade: The specific winning number/suffix to shade (e.g., "013").
        spots: Total number of spots on the ticket.
        forced_position: The specific index where the winning number must go.
        pi: "Plus Image" flag (logic dependent on your specific rules).

    Returns:
        Tuple(updated_nw_pool, uTick_object)
    """

    # 1. Generate Non-Winning (Filler) Numbers
    #    We need (spots - 1) fillers because 1 spot is taken by the winner.
    #    Usually 'addl_nums' refers to extra fillers outside the main spots?
    #    Adjust logic below if addl_nums vs spots calculation differs in your specific logic.
    current_ticket_numbers = []
    required_fillers = spots - 1

    while len(current_ticket_numbers) < required_fillers:
        candidate = str(random.randint(first_num, last_num))

        # Check exclusions (suffix matching)
        excluded = False
        for exc in exclusions:
            if candidate.endswith(exc):
                excluded = True
                break

        if not excluded and candidate not in nw_pool:
            current_ticket_numbers.append(candidate)
            nw_pool.append(candidate)

            # Simple pool management
            if len(nw_pool) > 5000:
                nw_pool.pop(0)

    # 2. Format the Winning (Shaded) Number
    suffix_len = 2
    formatted_winner = ""

    if is_full:
        formatted_winner = f"<@{color}FONT>{shade}"
    else:
        if len(shade) > suffix_len:
            prefix = shade[:-suffix_len]
            suffix = shade[-suffix_len:]
            formatted_winner = f"{prefix}<@{color}FONT>{suffix}"
        else:
            formatted_winner = f"<@{color}FONT>{shade}"

    # 3. Insert the Winner into the List
    if forced_position >= 0 and forced_position < spots:
        current_ticket_numbers.insert(forced_position, formatted_winner)
    else:
        insert_idx = random.randint(0, len(current_ticket_numbers))
        current_ticket_numbers.insert(insert_idx, formatted_winner)

    # 4. Handle "Plus Image" (PI) logic if enabled
    if pi:
        pass

    # 5. Add Empty Strings for "Additional Numbers"
    final_numbers = current_ticket_numbers + [''] * addl_nums

    # 6. Create the Ticket Object
    ticket = uTick(
        base='',
        images=imgs,
        numbers=final_numbers,
        p_id=1,
        s_id=1,
        is_first=is_first
    )

    return nw_pool, ticket
