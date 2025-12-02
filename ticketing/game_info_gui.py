import copy
import re

from enum import IntEnum


class HoldEnum(IntEnum):
    """
    This class sole raison d'être is to contain the option values for hold inquiries.
    Apparently classes are the best fit in Python, which seems downright silly to me.
    """
    SINGLE = 1,
    SINGLE_SPOTS = 2,
    SUFFIXED = 3,
    ZERO = 0,
    BINGO = 10


class AddImages(IntEnum):
    """
    This class holds the option values for adding blank-space elements to image lists
    """
    # Insert 'base.ai' at the front of the provided image list
    PreBase = -100,
    # Append 'base.ai' to the list of provided images
    PostBase = 100,
    # Don't add anything to the image list
    NoneAdded = 0,
    # Add the number of spaces equal to the associated
    # absolute value the front of the image list.
    PreOne = -1,
    PreTwo = -2,
    PreThree = -3,
    PreFour = -4,
    PreFive = -5,
    PreSix = -6,
    PreSeven = -7,
    PreEight = -8,
    PreNine = -9
    PreTen = -10
    PreEleven = -11
    PreTwelve = -12
    PreThirteen = -13
    PreFourteen = -14
    PreFifteen = -15
    PreSixteen = -16
    PreSeventeen = -17
    PreEighteen = -18
    PreNineteen = -19
    PreTwenty = -20
    # Append the number of spaces equal to the associated
    # value the front of the image list.
    PostOne = 1,
    PostTwo = 2,
    PostThree = 3
    PostFour = 4,
    PostFive = 5,
    PostSix = 6,
    PostSeven = 7,
    PostEight = 8,
    PostNine = 9
    PostTen = 10
    PostEleven = 11
    PostTwelve = 12
    PostThirteen = 13
    PostFourteen = 14
    PostFifteen = 15
    PostSixteen = 16
    PostSeventeen = 17
    PostEighteen = 18
    PostNineteen = 19
    PostTwenty = 20


sheet_columns = {
    'NS': 10
}


def add_images_lookup(val: int):
    """
    Looks up an AddImages Enum member based on its integer value.

    This function serves as a reverse lookup mechanism for the AddImages Enum.
    It takes an integer and returns the corresponding AddImages member.
    If the provided integer does not match any of the values defined
    in the AddImages Enum, it returns `AddImages.NoneAdded` as a safe default.

    :param val: The integer value potentially corresponding to an AddImages member
                (e.g., -100, 0, 5, -3).
    :type val: int
    :return: The matching AddImages Enum member if `val` is a defined value within
             the Enum. Otherwise, returns `AddImages.NoneAdded`.
    :rtype: AddImages
    """
    # Create a mapping from integer values back to Enum members
    # e.g., {-100: AddImages.PreBase, 100: AddImages.PostBase, 0: AddImages.NoneAdded, -1: AddImages.PreOne, ...}
    val_lookup = {ai.value: ai for ai in AddImages}
    return val_lookup.get(val, AddImages.NoneAdded)


def get_sheet_capacities(structure: str) -> list[int] | int:
    sheet_capacities = {
        '1': [96, 96], 'O1': [96, 96], 'N1': [168, 168],
        '3': [240, 80], 'O3': [240, 80], 'N3': [120, 120],
        '3-1': [80, 80], 'O3-1': [80, 80], 'N3-1': [-1, -1],
        '4': [256, 64], 'O4': [256, 64], 'N4': [96, 96],
        '4-1': [64, 64], 'O4-1': [64, 64], 'N4-1': [-1, -1],
        '5': [56, 56], 'O5': [56, 56], 'N5': [84, 84],
        '7': [42, 42], 'O7': [42, 42], 'N7': [-1, -1],
        'S': [240, 240], 'OS': [240, 240], 'NS': [396, 396],
        'C': [113, 113], 'OC': [113, 113], 'NC': [168, 168],
        'BC': [33, 33], 'OBC': [33, 33], 'NBC': [-1, -1]}

    if structure not in sheet_capacities.keys():
        return 0
    else:
        return sheet_capacities[structure]


def get_sheet_capacity(structure: str) -> list[int]:
    """
    Set the sheet capacity variables based on the window structure, and whether this
    is the new sheet size or old.

    :param structure: Window structure to be used
    :type structure: str
    :return: [bottom in capacity, bottom out capacity]
    :rtype: list[int]
    """
    q_sheet_capacity = 0
    # Set the sheet capacity according to window structure
    match structure.upper():
        case '1':
            q_sheet_capacity = [96, 96]
        case 'O1':
            q_sheet_capacity = [96, 96]
        case 'N1':
            q_sheet_capacity = [-1, -1]
        case '3':
            q_sheet_capacity = [240, 80]
        case 'O3':
            q_sheet_capacity = [240, 80]
        case 'N3':
            q_sheet_capacity = [-1, -1]
        case '3-1':
            q_sheet_capacity = [80, 80]
        case 'O3-1':
            q_sheet_capacity = [80, 80]
        case 'N3-1':
            q_sheet_capacity = [-1, -1]
        case '4':
            q_sheet_capacity = [256, 64]
        case 'O4':
            q_sheet_capacity = [256, 64]
        case 'N4':
            q_sheet_capacity = [-1, -1]
        case '4-1':
            q_sheet_capacity = [64, 64]
        case 'O4-1':
            q_sheet_capacity = [64, 64]
        case 'N4-1':
            q_sheet_capacity = [-1, -1]
        case '5':
            q_sheet_capacity = [56, 56]
        case 'O5':
            q_sheet_capacity = [56, 56]
        case 'N5':
            q_sheet_capacity = [-1, -1]
        case '7':
            q_sheet_capacity = [42, 42]
        case 'O7':
            q_sheet_capacity = [42, 42]
        case 'N7':
            q_sheet_capacity = [-1, -1]
        case 'S':
            q_sheet_capacity = [240, 240]
        case 'OS':
            q_sheet_capacity = [240, 240]
        case 'NS':
            q_sheet_capacity = [396, 396]
        case 'C':
            q_sheet_capacity = [113, 113]
        case 'OC':
            q_sheet_capacity = [113, 113]
        case 'NC':
            q_sheet_capacity = [-1, -1]
        case 'BC':
            q_sheet_capacity = [33, 33]
        case 'OBC':
            q_sheet_capacity = [33, 33]
        case 'NBC':
            q_sheet_capacity = [-1, -1]

    return q_sheet_capacity


def check_game_parameters(sheet, nws, insts, picks, holds, verbose=False, gui=False):
    """
    Verify that the number of tickets expected (Sheets * Capacity) equals the
    number of tickets generated (Ups * (NW + Inst + Pick + Hold)).

    Accepts both new Data Objects (GameInfo, Ticket classes) and legacy Lists.
    """

    # 1. PARSE SHEET / GAME INFO
    if hasattr(sheet, 'ups'):
        # Data Class (GameInfo)
        q_ups = sheet.ups
        q_permutations = sheet.permutations
        q_sheets = sheet.sheets
        q_sheet_capacity = sheet.capacity[1]
    else:
        # Legacy List: [ups, perms, sheets, [cap_in, cap_out], ...]
        q_ups = sheet[0]
        q_permutations = sheet[1]
        q_sheets = sheet[2]
        q_sheet_capacity = sheet[3][1]

    # 2. PARSE TICKET QUANTITIES

    # Non-Winners
    if hasattr(nws, 'total_quantity'):
        q_nws = nws.total_quantity
    else:
        q_nws = nws[0]  # Legacy: [quantity, pool, images_per_ticket]

    # Instants
    q_inst = 0
    if insts:
        # New GUI passes [total_int]. Legacy passes [[qty1, qty2], ...].
        if isinstance(insts[0], list):
            q_inst = sum(insts[0])
        else:
            q_inst = insts[0]

    # Picks
    q_pick = 0
    if picks:
        if isinstance(picks[0], list):
            q_pick = sum(picks[0])
        else:
            q_pick = picks[0]

    # Holds
    q_hold = 0
    if isinstance(holds, int):
        # New GUI passes the pre-calculated total as an integer
        q_hold = holds
    elif hasattr(holds, 'total_quantity'):
        # Just in case the object itself was passed
        q_hold = holds.total_quantity
    elif isinstance(holds, list):
        # Legacy List Logic (Bingos, etc.)
        # Attempt to sum the first 4 standard lists (DNS, DS, SNS, SS)
        try:
            for i in range(min(4, len(holds))):
                if isinstance(holds[i], list):
                    q_hold += sum(holds[i])

            # Add Either-Ors (Index 4) if present
            # Legacy Either-Ors are [[qty, free, double], ...]
            if len(holds) > 4 and isinstance(holds[4], list):
                # Sum the first element (quantity) of each inner list
                q_hold += sum(x[0] for x in holds[4] if x)
        except (TypeError, IndexError):
            # Fallback for simple list of ints
            if all(isinstance(x, int) for x in holds):
                q_hold = sum(holds)

    # 3. DO THE MATH
    tickets_per_up = q_nws + q_inst + q_pick + q_hold
    total_generated = tickets_per_up * q_ups
    total_expected = q_sheets * q_sheet_capacity

    # 4. REPORTING
    is_match = (total_generated == total_expected)

    if verbose:
        if is_match:
            output_string = (
                "The math works out!\n"
                f"Number of Ups: {q_ups}\n"
                f"Number of Permutations: {q_permutations}\n"
                f"Non-winners: {q_nws}\n"
                f"Instants: {q_inst}\n"
                f"Picks: {q_pick}\n"
                f"Holds: {q_hold}\n"
                f"---------------------------\n"
                f"Tickets Per Up: {tickets_per_up}\n"
                f"Total Generated: {total_generated}\n"
                f"Total Expected (Sheets * Capacity): {total_expected}\n"
            )
        else:
            output_string = (
                '!!!!!  TICKET TOTAL ERROR  !!!!!\n'
                f"Expected {total_expected} tickets, but {total_generated} would be produced.\n"
                f"Ups: {q_ups} | Sheets: {q_sheets} | Capacity: {q_sheet_capacity}\n"
                f"---------------------------\n"
                f"Non-winners: {q_nws}\n"
                f"Instants: {q_inst}\n"
                f"Picks: {q_pick}\n"
                f"Holds: {q_hold}\n"
                f"---------------------------\n"
                f"Tickets Per Up: {tickets_per_up}\n"
                f"Expected Per Up: {int(total_expected / q_ups) if q_ups else 0}\n"
            )

        if gui:
            return [is_match, output_string]
        else:
            print(output_string)

    return is_match


def get_ticket_total(nws: list[int], inst: list[list[int] | int | bool],
                     pick: list[list[int] | bool], holds: int | list[list[int] | str | bool]) -> list[list[int] | int]:
    """
    Simplified helper to sum tickets.
    """
    q_nonwinners = nws[0]

    if isinstance(inst[0], list):
        q_instants = sum(inst[0])
    else:
        q_instants = inst[0]

    if isinstance(pick[0], list):
        q_picks = sum(pick[0])
    else:
        q_picks = pick[0]

    if isinstance(holds, int):
        q_holds = holds
    else:
        q_holds = 0
        # Attempt legacy bingo sum
        try:
            for i in range(4):
                q_holds += sum(holds[i])
            q_holds += sum(list(zip(*holds[4]))[0])
        except:
            pass

    ticket_total = q_nonwinners + q_instants + q_picks + q_holds
    return [q_nonwinners, q_instants, q_picks, q_holds, ticket_total]


def parse_shaded_numbers(shady: str) -> dict[str, list[int | str | bool]] | None:
    """
    Parse a string of numbers and options for creating tickets with shaded numbers. The
    string is expected to contain a list of numbers, the color of the shading, and the
    description of the shading: 'S' for suffix or 'F' for full, followed by the suffix
    used.

    :param shady: numbers and options for shaded tickets
    :type: shady: str
    :return: dictionary containing the lists of numbers and options for shaded tickets
    :rtype: dict[str, list[int | str | bool] | None
    """
    if shady.strip() in ['', '0']:
        return {'ZYXW': ['0']}
    shades = {}
    # Split the shaded string at semicolons if there is more than one shaded type.
    entries = shady.split(';')
    # Create a dictionary entry for each shaded type.
    for entry in entries:
        # Split the string into a list.
        temp = entry.split(',')
        # Take the rule from the end of the newly created list.
        rule = temp.pop()
        # Take the font rule name from the list's end
        fob = temp.pop()
        # Verify the remaining list elements as digits.
        for t in temp:
            if not t.isdigit():
                return None
        # Use the font rule name as the key for this item and the number list as the value.
        shades[fob] = temp
        # Insert the suffix and its descriptor at the front of the value list.
        shades[fob].insert(0, rule)
    return shades
