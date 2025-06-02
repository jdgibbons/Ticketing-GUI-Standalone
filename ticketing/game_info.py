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


sheet_capacities = {
    '1': [96, 96], 'O1': [96, 96], 'N1': [168, 168],
    '3': [240, 80], 'O3': [240, 80], 'N3': [120, 120],
    '3-1': [80, 80], 'O3-1': [80, 80], 'N3-1': [-1, -1],
    '4': [256, 64], 'O4': [256, 64], 'N4': [96, 96],
    '4-1': [64, 64], 'O4-1': [64, 64], 'N4-1': [-1, -1],
    '5': [56, 56], 'O5': [56, 56], 'N5': [84, 84],
    '7': [42, 42], 'O7': [42, 42], 'N7': [-1, -1],
    'S': [240, 240], 'OS': [240, 240], 'NS': [300, 300],
    'C': [113, 113], 'OC': [113, 113], 'NC': [168, 168],
    'BC': [33, 33], 'OBC': [33, 33], 'NBC': [-1, -1]}

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


def get_game_parameters(sheets: bool, no_win: bool, inst: bool, pick: bool, holders: HoldEnum,
                        names: bool, new_size=False, do_perm=False) -> list:
    """
    Provides a generic function that collects the most commonly used game parameters and returns
    them in a consistent and predictable format.
    :param sheets: gather sheet information? [Ups, Perms, Sheets, [BI Capacity, BO Capacity]]
    :type sheets: bool
    :param no_win: gather nonwinner information? [Count, Pool Size, Images/Ticket]
    :type no_win: bool
    :param inst: gather instant winner information? [[tickets/tier], CD Tier, Subimages?]
    :type inst: bool
    :param pick: gather pick ticket information?
    :type pick: bool
    :param holders: gather hold information and type
    :type holders: HoldEnum
    :param names: gather part and file name information?
    :type names: str
    :param new_size: does this game use the new, larger sheet size?
    :type new_size: bool
    :param do_perm: gather parameter information?
    :type do_perm: bool
    :return: [sheet_specs, nw_specs, instant_specs, pick_specs, hold_specs, names_specs]
    :rtype: list
    """
    params = []
    # Sheet specs returns [Ups, Permutations, Sheets, [Bottom-In CD Capacity, Bottom-Out Ticket Count]]
    if sheets:
        params.append(get_up_sheet_ticket_perms(new_size, do_perm))
    # Nonwinner specs returns [Count, Image Pool Size, Images per Ticket]
    if no_win:
        params.append(get_nonwinner_image_info())
    else:
        # Create a list with zero values to indicate there are no nonwinners in this game.
        params.append([0] * 3)
    # Instant winners returns [[Tickets per Tier], CD Tier Level, Are Subimages Used?]
    if inst:
        params.append(get_instant_winner_info())
    else:
        # Create a list that indicates there are no instant winners in this game.
        params.append([[0], 0, False])
    # Pick specs returns [[Tickets per Tier], (I)mage or (N)umber]
    if pick:
        params.append(get_pick_tickets_info())
    else:
        # Create a list that indicates there are no pick tickets in this game.
        params.append([[0], False])
    # Hold specs returns various lists based on need.
    if holders != HoldEnum.ZERO:
        # Get a single integer
        if holders == HoldEnum.SINGLE:
            params.append(get_single_integer('holds', 15))
        # Get the number of holds and the number of spots on the ticket
        elif holders == HoldEnum.SINGLE_SPOTS:
            params.append([get_single_integer('holds', 15),
                           get_single_integer('spots', 3)])
        elif holders == HoldEnum.SUFFIXED:
            params.append(get_single_window_suffix_hold_info())
        elif holders == HoldEnum.BINGO:
            params.append(get_bingo_number_parameters())
    else:
        params.append(0)
    if names:
        params.append(get_part_and_file_names())
    else:
        params.append([''] * 2)
    return params


def get_up_sheet_ticket_perms(new_size=False, do_perms=False) -> list[int | list[int] | bool]:
    """
    Ask the user for the information concerning the number of ups, tickets, sheets,
    and permutations

    :param new_size: is this the new sheet size
    :type new_size: bool
    :param do_perms: are multiple perms required
    :type do_perms: bool
    :return: [ups, permutations, sheets, sheet capacity, perm reset]
    :rtype: list[int | list[int]]
    """
    # Let the user know that 'x' will end the input process and exit at any prompt
    print("Enter parameters for this game. Entering 'X' for any value will exit the program.")
    # Get the WINDOW STRUCTURE from the user.
    structure = input("Basic Window Structure (1, 3, 3-1, 4, 4-1, 5, 7, S, NS, C, BC, NC): ")
    while structure.upper() not in ['1', '3', '3-1', '4', '4-1', '5', '7', 'S', 'NS', 'C', 'BC', 'NC', 'X']:
        print('You must enter an acceptable value for the window structure. Look at the list.')
        structure = input("Basic Window Structure (1, 3, 3-1, 4, 4-1, 5, 7, S, NS, C, BC, NC): ")
    # If this is the NEW SHEET SIZE, prepend 'N' to structure.
    if new_size:
        structure = 'N' + structure
    check_for_exit(structure)
    # Get the SHEET CAPACITY from the window structure.
    q_sheet_capacity = get_sheet_capacity(structure)
    # Get the number of UPS from the user.
    ups = ''
    while not ups.isnumeric() and ups.upper() != 'X':
        ups = input('Number of Ups (<enter> = 1): ')
        if ups == '':
            ups = '1'
    check_for_exit(ups)
    q_ups = int(ups)
    # If the number of ups is incompatible with the sheet capacity,
    # harass the user until they input a proper value.
    while q_sheet_capacity[1] % q_ups != 0:
        print(f"Sheet capacity ({q_sheet_capacity[1]}) is not evenly divisible by the number of ups ({q_ups}).")
        print("That won't work. Try again.")
        ups = ''
        while not ups.isnumeric() and ups.upper() != 'X':
            ups = input('Number of Ups: ')
        check_for_exit(ups)
        q_ups = int(ups)
    # Get the number of PERMUTATIONS, if requested; otherwise, set the
    # number to one. Make sure the number of ups is evenly divisible by
    # the number of permutations.
    p_reset = False
    if do_perms:
        perms = input('Number of Permutations (<enter> = 1): ')
        if perms == '':
            perms = '1'
        check_for_exit(perms)
        q_permutations = int(perms)
        # If the number of perms doesn't fit the number of ups, bug the user
        # to enter a new number until they get it right.
        while q_ups % q_permutations != 0:
            print(
                f"Number of permutations ({q_permutations}) does not divide equally into the number of ups ({q_ups}).")
            print('Those parameters would create a bloodbath. Try again.')
            perms = input('Number of Permutations (<enter> = 1): ')
            if perms == '':
                perms = '1'
            check_for_exit(perms)
            q_permutations = int(perms)
        # This is set to true if the permutations cannot have duplicates
        # across the entire collection of tickets.
        if q_permutations > 1:
            if input("Will permutations be played simultaneously? (y/n) (<enter> = 'Y') ").upper() == 'N':
                p_reset = True
    else:
        q_permutations = 1
    # Get the TOTAL SHEETS from the user.
    linens = ''
    while not linens.isnumeric() and linens.upper() != 'X':
        linens = input('Number of Sheets: ')
    check_for_exit(linens)
    q_sheets = int(linens)
    # Return all the pertinents.
    return [q_ups, q_permutations, q_sheets, q_sheet_capacity, p_reset]


def get_part_and_file_names() -> list[str]:
    """
    Ask the user to input the game part number and base file name string to be
    used to construct actual csv file names to output game related data. The
    part name is used only when there are cds associated with the game.

    :return: [base part number, base file name]
    :rtype: list[str]
    """
    # Get the PART NAME from the user.
    bn = ''
    while len(bn) == 0:
        bn = input('Base Part Name: ')
    check_for_exit(bn)
    # Get the FILE NAME from the user.
    fn = ''
    while len(fn) == 0:
        fn = input('Base File Name: ')
    check_for_exit(fn)
    # return part name, base file name
    return [bn, fn]


def check_for_exit(value: str) -> None:
    """
    Check if the passed value is 'X' and abort if is.

    :param value: string that was entered by the user
    :type value: str
    :return: None
    :rtype: None
    """
    if value.upper() == 'X':
        print("Good! I didn't want to interact with you anyway!!")
        print("Don't let the screen door hit you on the way out!")
        print('')
        exit(0)


def get_sheet_capacities(structure: str) -> list[int] | None:
    global sheet_capacities
    if structure not in sheet_capacities.keys():
        return None
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
            q_sheet_capacity = [300, 300]
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


def get_nonwinner_image_info() -> list[int]:
    """
    Ask the user for nonwinner image information and return the values in a list.

    :return: [number of nonwinners, size of image pool, images per ticket]
    :rtype: list[int]
    """
    # Get the NUMBER OF NONWINNERS from the users.
    nws = ''
    while not nws.isnumeric() and nws.upper() != 'X':
        nws = input('Number of Nonwinners (<enter> = 0): ')
        if nws == '':
            nws = '0'
    check_for_exit(nws)
    # This will probably always be true, as the user must set the flag to call this function.
    # However, this is just for the 'rare' occasion that I'm an idiot.
    if int(nws) > 0:
        # Get the SIZE OF THE NONWINNER IMAGE POOL from the user.
        # Nine is the default value.
        pool = ''
        while not pool.isnumeric() and pool.upper() != 'X':
            pool = input('Size of Nonwinner-image Pool (<enter> = 9): ')
            if pool == '':
                pool = '9'
        check_for_exit(pool)
        # Get the nonwinner IMAGES PER TICKET from the user.
        ipt = ''
        while not ipt.isnumeric() and ipt.upper() != 'X':
            ipt = input('Number of images on each nonwinning ticket ((1 or 3) <enter> = 1): ')
            if ipt == '':
                ipt = '1'
            elif ipt not in ['1', '3', '9', 'X']:
                print("There are only three choices: 1, 3, or 9.")
                ipt = 'crap'
        check_for_exit(ipt)
    # If there are no nonwinners, just set the pool size to 15 and the number of images
    # per ticket to 1. They're superfluous but keep the list values non-None.
    else:
        pool = '15'
        ipt = '1'
    return [int(nws), int(pool), int(ipt)]


def get_instant_winner_info() -> list[int | bool]:
    """
    Ask user for instant winner information and return it in a list.

    :return: [number of winners, cd tier level, are there subimages]
    :rtype: list[int | bool]
    """
    # Number of instant winners
    inst = ''
    while not re.match('[0-9,]+$', inst) and inst.upper() != 'X':
        inst = input('Number of Instant Winners (separate tiers with commas: 1,5,20 (<enter> = 0)): ')
        if inst == '':
            inst = '0'
    check_for_exit(inst)

    # CD tier level and subimage presence
    subs = 'H'
    ins_cd_tier = ''
    if inst.strip() != '0':
        while not ins_cd_tier.isnumeric() and ins_cd_tier.upper() != 'X':
            ins_cd_tier = input("Instant CD Tier Level (<enter> or '0' = none): ")
            if ins_cd_tier == '':
                ins_cd_tier = '0'
        check_for_exit(ins_cd_tier)

        while not re.match('[YNXynx]', subs):
            subs = input("Do tiers have subimages? ((Y/N) <enter> = 'N'): ")
            if subs == '':
                subs = 'N'
        check_for_exit(subs)
    else:
        subs = 'N'
        ins_cd_tier = '0'
    instants = []
    for insta in inst.split(','):
        instants.append(int(insta))
    return [instants, int(ins_cd_tier), subs.upper() == 'Y']


def get_single_window_suffix_hold_info() -> list[list[int] | str | int | dict[str, [list[int | str | bool]]]]:
    """
    Return a list of information about a single window hold that can include
    number of tickets, type, number of digits, and parameters for creating
    a list of winners and nonwinners from a specified number range.

    :return: [number of holds, type, digits on ticket, number range]
    :rtype: list[list[int] | str | int | dict[str, [list[int | str | bool]]]]
    """
    holdem = ''
    while not re.match('[0-9,]+$', holdem) and holdem.upper() != 'X':
        holdem = input("Number of hold tickets (<enter> or '0'): ")
        if holdem == '':
            holdem = '0'
    check_for_exit(holdem)

    teepee = ''
    while not re.match('[INXinx]', teepee):
        teepee = input("Are the holds [N]umbers or [I]mages? (<enter> = 'I'): ")
        if teepee == '':
            teepee = 'I'
    teepee = teepee.upper()
    check_for_exit(teepee)

    numbness = 'D'
    nws = 'M'
    digits = 'P'
    if teepee == 'N':
        while not digits.isnumeric() and digits.upper() != 'X':
            digits = input("Enter the total number of integers that will be on each ticket (<enter> = 3): ")
            if digits == '':
                digits = '3'
        check_for_exit(digits)

        while not re.match('[0-9,]+$', numbness) and numbness.upper() != 'X':
            numbness = input("Enter the first and last elements in this number range (<enter> = '0,9999'): ")
            if numbness == '':
                numbness = '0,9999'
        check_for_exit(numbness)

        numbness = list(map(int, numbness.split(',')))
        suffix = get_suffix_hold_information_enhanced()
        numbness.append(suffix)

        while not re.match('[0-9,]+$', nws) and nws.upper() != 'X':
            nws = input("Enter the lowest and highest nonwinning integer (<enter> = '101,9999'): ")
            if nws == '':
                nws = '101,9999'
        check_for_exit(nws)
        nws = list(map(int, nws.split(',')))
        numbness.append(nws)
    else:
        numbness = [0]
        digits = '0'

    return [int(holdem), teepee, int(digits), numbness]


def get_pick_tickets_info() -> list[int]:
    """
    Ask the user for pick tickets information and return it to the caller.
    This can be a single integer or a list of integers, but either value
    will be returned as a list.

    :return: list of ints representing the number of pick tickets
    :rtype: list[int]
    """
    picket = ''
    while not re.match('[0-9,]+$', picket) and picket.upper() != 'X':
        picket = input('Number of Pick Winners (separate tiers with commas: 1,5,20'
                       ' (or a single number if tiers are irrelevant)): ')
        if picket == '':
            picket = '0'
    check_for_exit(picket)
    q_picks = []
    numbs = []
    for val in picket.split(','):
        numbs.append(int(val))
    q_picks.append(numbs)
    if len(numbs) == 1 and numbs[0] != 0:
        i_type = 'E'
        while not re.match('[YNXynx]', i_type):
            i_type = input("Does each image have a unique name? (<enter> = 'N') ")
            if i_type == '':
                i_type = 'N'
        check_for_exit(i_type)
        q_picks.append(i_type == 'Y')
    else:
        q_picks.append(False)
    return q_picks


def get_single_integer(ticket_type: str, preset: int) -> int:
    """
    Ask the user for a single integer for ticket count and set it
    to a default value if <enter> is pressed without an entry.

    :param ticket_type: name of the ticket type
    :type ticket_type: str
    :param preset: default value
    :type preset: int
    :return: user provided integer value
    :rtype: int
    """
    val = ''
    while not val.isnumeric() and val.upper() != 'X':
        val = input(f"Number of {ticket_type} (<enter> = {preset}): ")
        if val == '':
            val = str(preset)
    check_for_exit(val)
    return int(val)


def get_integer_list(ticket_type: str, deafen: int) -> list[int]:
    """
    Ask the user for a list of integers to be used for ticket counts. Set
    the list to a default value if <enter> is pressed without an entry.

    :param ticket_type: name of the ticket type
    :type ticket_type: str
    :param deafen: default value for the list
    :return: user provided list of integers
    :rtype: list[int]
    """
    val = ''
    while not re.match('[0-9,]+$', val) and val.upper() != 'X':
        val = input(f'Number of {ticket_type} (separate tiers with commas: 1,5,20: ')
        if val == '':
            val = f'{deafen}'
    check_for_exit(val)
    q_picks = []
    for val in val.split(','):
        q_picks.append(int(val))
    return q_picks


def get_suffix_hold_information() -> list[int | list[str] | str | bool]:
    """
    Ask the user to enter the pertinent information for the numbers game that uses
    suffixes to create a list of winning integers and another list with (almost) all
    the numbers not contained in the list of winners.

    :return: [starting number, ending number, suffixes, smallest winning integer, largest winning integer, \
    text of DesignMerge tag (without the <@>), color all characters in the winning numbers?]
    :rtype: list[int | list[str] | str | bool]
    """
    # Input the lowest number in the entire integer range
    first = ''
    while not first.isnumeric() and first.upper() != 'X':
        first = input('First number in entire range (<enter> = 1): ')
        if first == '':
            first = '1'
    check_for_exit(first)
    q_first = int(first)
    # Input the highest number in the entire integer range
    last = ''
    while not last.isnumeric() and last.upper() != 'X':
        last = input('Last number in entire range (<enter> = 9999): ')
        if last == '':
            last = '9999'
    check_for_exit(last)
    q_last = int(last)
    # Input a list of suffixes to be used to indicate winners separated by a comma
    suffix = ''
    while len(suffix) == 0:
        suffix = input('Enter any suffix(es) to be segregated (separate by commas: 00, 10, 33 (<enter> = 00)): ')
        if suffix == '':
            suffix = '00'
    check_for_exit(suffix)
    suffixes = []
    for suff in suffix.split(','):
        suffixes.append(suff)
    # Input the smallest winning number
    smallest = ''
    while not smallest.isnumeric() and smallest.upper() != 'X':
        smallest = input('Enter the smallest winner in hold range (<enter> = 1): ')
        if smallest == '':
            smallest = '1'
    check_for_exit(smallest)
    q_smallest = int(smallest)
    # Input the largest winning number
    largest = ''
    while not largest.isnumeric() and largest.upper() != 'X':
        largest = input('Enter the largest winner in hold range (<enter> = 1500): ')
        if largest == '':
            largest = '1500'
    check_for_exit(largest)
    q_largest = int(largest)

    dm_tag = ''
    while len(dm_tag) == 0:
        dm_tag = input('Enter the DesignMerge tag for the holds (<enter> = REDFONT): ')
        if dm_tag == '':
            dm_tag = 'REDFONT'
    check_for_exit(dm_tag)

    all_chars = ''
    while len(all_chars) == 0:
        all_chars = input('Apply DesignMerge tag to suffix only? Y/N (<enter> = Y): ')
        if all_chars == '':
            all_chars = 'Y'
    color_all_chars = all_chars.upper() != 'Y'
    check_for_exit(all_chars)

    return [q_first, q_last, suffixes, q_smallest, q_largest, dm_tag, color_all_chars]


def check_game_parameters(sheet: list[list[int] | int], nws: list[int], insts: list[list[int] | int | bool],
                          picks: list[list[int] | bool], holds: int | list[list[int] | str | bool],
                          verbose=False, gui=False):
    """
    Verify the number of tickets expected equals the number that would be generated
    given the passed parameters.

    :param sheet: list containing sheet layout/quantity information
    :type sheet: list[list[int] | int]
    :param nws: list containing nonwinner info (quantity in field 0)
    :type nws: list[int]
    :param insts: list containing instant winner info (quantity list in field 0)
    :type insts: list[list[int] | int | bool]
    :param picks: list containing pick quantities
    :type picks: list[int]
    :param holds: number of hold ticket
    :type holds: int | list[list[int] | str | bool]
    :param verbose: should debug/reporting information be displayed to the screen
    :type verbose: bool
    :param gui: is this being called from a GUI?
    :type gui: bool
    :return: True if the math checks out, False otherwise
    :rtype: bool
    """
    # Break up the sheet parameters and subdivide the sheet capacity to
    # use the ticket count
    if len(sheet) == 5:
        q_ups, q_permutations, q_sheets, q_sheet_capacity, p_reset = sheet
    else:
        q_ups, q_permutations, q_sheets, q_sheet_capacity, p_reset, subflats, schisms = sheet
    q_sheet_capacity = q_sheet_capacity[1]

    q_nonwinners, q_instants, q_picks, q_holds, ticket_total = get_ticket_total(nws, insts, picks, holds)
    ticket_total *= q_ups

    running_total = copy.deepcopy(ticket_total)
    # Multiply the number of sheets by sheet capacity
    expected_total = q_sheets * q_sheet_capacity

    # The two totals should match.
    if ticket_total != expected_total:
        if verbose:
            output_string = ('!!!!!  TICKET TOTAL ERROR  !!!!!\n'
                             f"Expected {expected_total} tickets, "
                             f"but {ticket_total} would be produced with current parameters:\n"
                             f"Number of Ups: {q_ups}\n"
                             f"Non-winners: {q_nonwinners}\n"
                             f"Number of Instants: {q_instants}\n"
                             f"Number of Picks: {q_picks[0]}\n"
                             f"Number of Holds: {q_holds}\n"
                             f"Number of Tickets per Up Expected: {int(expected_total / q_ups)}\n"
                             f"Total Tickets per Up from Input Parameters: {int(running_total / q_ups)}\n")
            if gui:
                return [False, output_string]
            else:
                print(output_string)
        return False
    else:
        if verbose:
            output_string = ("The math works out!\n"
                             f"Number of Ups: {q_ups}\n"
                             f"Number of permutations: {q_permutations}\n"
                             f"Non-winners: {q_nonwinners}\n"
                             f"Number of Instants: {q_instants}\n"
                             f"Number of Picks: {q_picks[0]}\n"
                             f"Number of Holds: {q_holds}\n"
                             + (f"    Number of Non-staggered, Double-line Holds: {holds[0]}\n"
                                f"    Number of Staggered, Double-line Holds: {holds[1]}\n"
                                f"    Number of Non-staggered, Single-line Holds: {holds[2]}\n"
                                f"    Number of Staggered, Single-line Holds:"
                                f" {holds[3]}\n" if not isinstance(q_holds, int) else "")
                             + f"Total tickets per up: {int(running_total / q_ups)}\n"
                             + (f"Total tickets per permutation: "
                                f"{int(expected_total / q_permutations)}\n" if q_permutations != 1 else "")
                             + "Verified the 'number of sheets multiplied by tickets per sheet' "
                               "equals 'number of ups multiplied by ticket count' . . .\n"
                             + f"Expected {expected_total} tickets, producing {ticket_total}\n"
                             + f"Creating {q_sheets} sheets with {q_ups} ups and "
                               f"{int(q_sheet_capacity / q_ups)} tickets per up on each sheet.\n")
            if gui:
                return [True, output_string]
            else:
                print(output_string)
        return True


def get_ticket_total(nws: list[int], inst: list[list[int] | int | bool],
                     pick: list[list[int] | bool], holds: int | list[list[int] | str | bool]) -> list[list[int] | int]:
    """
    Verify the number of tickets expected equals the number that would be generated
    given the passed parameters.

    :param nws: list containing nonwinner info (quantity in field 0)
    :type nws: list[int]
    :param inst: list containing instant winner info (quantity list in field 0)
    :type inst: list[list[int] | int | bool]
    :param pick: list containing pick quantities
    :type pick: list[int]
    :param holds: number of hold ticket
    :type holds: int | list[list[int] | str | bool]
    :return: Total number of tickets
    :rtype: list[int]
    """

    # Get quantities from nonwinner and instant lists
    q_nonwinners = nws[0]
    q_instants = inst[0]
    q_picks = pick
    if isinstance(holds, int):
        q_holds = holds
    else:
        q_holds = 0
        for i in range(4):
            q_holds += sum(holds[i])
        q_holds += sum(list(zip(*holds[4]))[0])

    ticket_total = 0
    # Cycle through instant and pick lists to add their values
    for val in q_instants:
        ticket_total += val
    for val in q_picks[0]:
        ticket_total += val
    # Add the rest of the tickets
    ticket_total += q_nonwinners
    ticket_total += q_holds

    return [q_nonwinners, q_instants, q_picks, q_holds, ticket_total]


def get_suffix_hold_information_enhanced() -> dict[str, [list[int | str | bool]]] | None:
    """
    Ask the user to enter the pertinent information for the numbers game that uses
    suffixes to create a list of winning integers and another list with (almost) all
    the numbers not contained in the list of winners.

    :return: [starting number, ending number, suffixes, smallest winning integer, largest winning integer, \
    text of DesignMerge tag (without the <@>), color all characters in the winning numbers?]
    :rtype: dict[str, list[int | str | bool]]
    """
    suffix = ''
    while len(suffix) == 0:
        print('Enter suffixes in the following format: Suffix, First, Last, Tag, All Digits (T/F)')
        suffix = input('Separate multiple suffixes with semicolons: ')
        if suffix == '':
            suffix = '00,100,1500,REDFONT,T'
    check_for_exit(suffix)
    # suffixes = parse_suffix_entries(suffix)
    suffixes = parse_suffixes(suffix)

    return suffixes


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


def parse_suffixes(suffixes: str) -> dict[str, list[int | str | bool]] | None:
    """
    Parses a semicolon-separated string into a dictionary where each entry
    corresponds to suffix details. This function expects the `suffixes` string to
    include values subdivided by commas. Each entry should have 5 or 6 components
    specifying index, numeric identifiers, a DesignMerge tag, a character indicating
    the scope of influence, and an optional extra string.

    :param suffixes: A string that consists of one or more suffix descriptions,
                     separated by semicolons. Each suffix description is expected
                     to have 5 or 6 comma-separated parts.
    :return: A dictionary with parsed suffix information where the keys are suffix
             indices and the values are lists containing processed components such
             as integers, strings, and a boolean indicating the scope of influence.
    """
    stuffix = {}
    entries = suffixes.split(';')
    for entry in entries:
        temp = entry.split(',')
        if len(temp) not in (5, 6):
            print(f"Expected 5 or 6 entries, got {len(temp)}.")
            exit(0)
        # Set index to suffix
        index = temp[0]
        value = []
        # Add first and last suffixed entries
        for i in range(1, 3):
            if not temp[i].isnumeric():
                print(f"Expected integer but got '{temp[i]}'.")
                break
            else:
                value.append(int(temp[i]))
        # Add DesignMerge tag--no way I can check its validity.
        if re.fullmatch(r'\w+', temp[3]):
            value.append(f'<@{temp[3]}FONT>')
        else:
            print(f"Design merge tags should only have numbers and letters. '{temp[3]}' doesn't qualify.")
            break
        # Add whether the DM tag will affect the whole number (T) or just the suffix (F).
        if temp[4].upper() not in ['T', 'F']:
            print(f"Expected 'T' or 'F' but got '{temp[4]}'.")
            break
        else:
            value.append(True) if temp[4].upper() == 'T' else value.append(False)
        if len(temp) == 5:
            value.append('')
        else:
            value.append(temp[5])
        stuffix[index] = value
    return stuffix


# ========================================================================================#

def get_bingo_number_parameters() -> list[list[list[int] | list[list[int]]] | bool | str | int]:
    """
    Get the count of the various types of bingo combinations and return the values in a list to the user. Each type will
    consist of a list of integers whose index value represents the number of free spots in the bingo line. For example,
    a list of 50, 25, 10 would represent 50 lines with zero free-spots, 25 lines with one free-spot, and 10 lines with
    two free-spots. For the double-line tickets, there is a choice of 'staggered' and 'non-staggered.' This refers to
    how the free-spaces are handled: in a non-staggered ticket, the free-spaces for both rows occur in the same column;
    in a staggered ticket, the free-spaces for each row occur in different columns. As for single columns, I don't
    remember the reason why the staggered vs. non-staggered options exist. I think it's necessary for naming conventions
    when used in combination with staggered double-lines: the two staggered rows each have a list of images indicating
    their positions, and the single staggered row has a third list. In the case where non-staggered double-lines are
    used, both tickets use the same free images. I haven't encountered this situation in quite some time, so I'll update
    this documentation if I'm wrong about that. The user also provides whether leading zeroes are to be used, as well as
    the type of free space used: images, text, or both. Both come into play when the image for the spot has to be
    changed (or added) to the column along with the text for a free spot. The final information provided by the user is
    which verification list is to be used: the standard (with 9,000 faces) or the extended (with 27,000 faces).

    :return: [[non-staggered doubles], [staggered doubles], [non-staggered singles], [staggered singles],
              [[single either-ors]], zeroes, free type, verification file size, csv rows]
    :rtype: [list[list[int] | list[list[int]] | bool | str | int]
    """
    bingo_parameters = []
    columns_needed = [False] * 3
    #  Non-staggered double-holds (top and bottom free spots appear in the same column)
    non_staggered_double_holds = ''
    while not re.match('[0-9,]+$', non_staggered_double_holds) and non_staggered_double_holds.upper() != 'X':
        non_staggered_double_holds = input('Number of Non-staggered, Double-line hold tickets '
                                           '(separate free spots with commas: 84,42,14) (<enter> = [0]): ')
        if non_staggered_double_holds == '':
            non_staggered_double_holds = '0'
        check_for_exit(non_staggered_double_holds)
    q_nonstaggered_double_holds = []
    for val in non_staggered_double_holds.split(','):
        q_nonstaggered_double_holds.append(int(val))
    while len(q_nonstaggered_double_holds) < 4:
        q_nonstaggered_double_holds.append(0)
    if sum(q_nonstaggered_double_holds) > 0:
        columns_needed[1] = True
    bingo_parameters.append(q_nonstaggered_double_holds)

    # Staggered double-holds (top and bottom free spots appear in different columns)
    staggered_double_holds = ''
    while not re.match('[0-9,]+$', staggered_double_holds) and staggered_double_holds.upper() != 'X':
        staggered_double_holds = input('Number of Staggered, Double-line hold tickets '
                                       '(separate free spots with commas: 84,42,14 (<enter> = [0])): ')
        if staggered_double_holds == '':
            staggered_double_holds = '0'
        check_for_exit(staggered_double_holds)
    q_staggered_double_holds = []
    for val in staggered_double_holds.split(','):
        q_staggered_double_holds.append(int(val))
    while len(q_staggered_double_holds) < 4:
        q_staggered_double_holds.append(0)
    if sum(q_staggered_double_holds) > 0:
        columns_needed[1] = True
    bingo_parameters.append(q_staggered_double_holds)

    # Non-staggered single-holds (I'm not sure of the difference between non_staggered_single holds and
    # staggered_single_holds. I believe staggered has something to do with the names of the images used
    # when dealing with ticketing_games that have double and single line combinations mixed together.)
    non_staggered_single_holds = ''
    while not re.match('[0-9,]+$', non_staggered_single_holds) and non_staggered_single_holds.upper() != 'X':
        non_staggered_single_holds = input('Number of Non-staggered, Single-line hold tickets '
                                           '(separate free spots with commas: 84,42,14) (<enter> = [0]): ')
        if non_staggered_single_holds == '':
            non_staggered_single_holds = '0'
        check_for_exit(non_staggered_single_holds)
    q_non_staggered_single_holds = []
    for val in non_staggered_single_holds.split(','):
        q_non_staggered_single_holds.append(int(val))
    while len(q_non_staggered_single_holds) < 4:
        q_non_staggered_single_holds.append(0)
    if sum(q_non_staggered_single_holds) > 0:
        columns_needed[0] = True
    bingo_parameters.append(q_non_staggered_single_holds)

    # See above non-staggered single hold
    staggered_single_holds = ''
    while not re.match('[0-9,]+$', staggered_single_holds) and staggered_single_holds.upper() != 'X':
        staggered_single_holds = input('Number of Staggered, Single-line hold tickets '
                                       '(separate free spots with commas: 84,42,14) (<enter> = [0]): ')
        if staggered_single_holds == '':
            staggered_single_holds = '0'
        check_for_exit(staggered_single_holds)
    q_staggered_single_holds = []
    for val in staggered_single_holds.split(','):
        q_staggered_single_holds.append(int(val))
    while len(q_staggered_single_holds) < 4:
        q_staggered_single_holds.append(0)
    if sum(q_staggered_single_holds) > 0:
        columns_needed[0] = True
    bingo_parameters.append(q_staggered_single_holds)

    # Single-line bingos with either/or spots
    single_with_either_or_spots = ''
    q_single_with_either_or_spots = []
    go_again = True
    while go_again:
        go_again = False
        while (not re.match('[0-9,;]+$', single_with_either_or_spots)
               and single_with_either_or_spots.upper() != 'X'):
            print('\nNumber of single line, double-spot hold tickets (format: amount,free-spots,double-spots)')
            print('Separate parameters with colon and type with semicolon.')
            single_with_either_or_spots = input('Example: 100,0,1;50,1,1;30,2,0 (<enter> = [0]): ')
            if single_with_either_or_spots == '':
                single_with_either_or_spots = '0,0,0'
            check_for_exit(single_with_either_or_spots.upper())
        q_single_with_either_or_spots = []
        for stuff in single_with_either_or_spots.split(';'):
            vals = stuff.split(',')
            if len(vals) != 3:
                print(f'Wrong number of parameters for single-line, either/or hold tickets: {vals}\n')
                single_with_either_or_spots = ''
                go_again = True
                break
            q_single_with_either_or_spots.append([int(v) for v in vals])
        if go_again:
            q_single_with_either_or_spots.clear()
    if sum(list(zip(*q_single_with_either_or_spots))[0]) > 0:
        columns_needed[2] = True
    bingo_parameters.append(q_single_with_either_or_spots)

    # Are leading zeroes needed for single digit numbers?
    zeroes = ''
    while zeroes.upper() not in ['Y', 'N', 'X']:
        zeroes = input("Do there need to be leading zeroes? ((Y/N) <enter> = 'N') ")
        if zeroes == '':
            zeroes = 'N'
        check_for_exit(zeroes.upper())
    leaders = zeroes.upper() != 'N'
    bingo_parameters.append(leaders)

    # Are free spots composed of images, text, or both?
    freetype = 'L'
    while freetype.upper() not in ['I', 'T', 'B', 'N', 'X']:
        freetype = input("Are free spots (I)mages, (T)ext, (B)oth, or (N)either? (<enter> = 'N'): ")
        if freetype == '':
            freetype = 'N'
    check_for_exit(freetype.upper())
    bingo_parameters.append(freetype.upper())

    # Will the verifiable faces come from the short or extended csv?
    verifiers = 'W'
    while verifiers.upper() not in ['S', 'E', 'X']:
        verifiers = input("Which verification list should be used? "
                          "(S)tandard (9000), (E)xtended (27000) (<enter> = 'S'): ")
        if verifiers == '':
            verifiers = 'S'
        check_for_exit(verifiers.upper())
    bingo_parameters.append(verifiers.upper())

    if columns_needed[2] or (columns_needed[0] and columns_needed[1]):
        columns = 3
    elif columns_needed[0]:
        columns = 1
    elif columns_needed[1]:
        columns = 2
    else:
        print("Number of columns needed is not defined. Not sure what to do, so I'm bailing.")
        exit(-1)
    bingo_parameters.append(columns)

    return bingo_parameters

# Get quantities from nonwinner and instant lists
# q_nonwinners = nws[0]
# q_instants = insts[0]
# q_picks = picks
# if isinstance(holds, int):
#     q_holds = holds
# else:
#     q_holds = 0
#     for i in range(4):
#         q_holds += sum(holds[i])
#     q_holds += sum(list(zip(*holds[4]))[0])
#
# ticket_total = 0
# # Cycle through instant and pick lists to add their values
# for val in q_instants:
#     ticket_total += val
# for val in q_picks[0]:
#     ticket_total += val
# # Add the rest of the tickets and multiply by the number of ups
# ticket_total += q_nonwinners
# ticket_total += q_holds
