import random as rn
import copy
import itertools as itty
from typing import List, Tuple


def create_number_pools(first_number: int, last_number: int, winner_suffix: list[str], smallest_nw: int,
                        biggest_winner: int, dm_tag_name: str, color_all_letters=False) -> list[list[str] | list[int]]:
    """
    Create a pool of numbers between p_first and p_last. Place the results in two lists
    (winners and nonwinners) and return them to the caller. Winners are determined by
    a numeric string compared against the ending numbers for each integer. Any number
    that has the string as a suffix is placed in the winners' list if it falls between
    the smallest and biggest winning numbers. Any number of suffixes can be used, with
    each discrete string's associated numbers placed in their own lists. All other numbers
    containing the strings are discarded to avoid confusion.

    :param first_number: lowest number in pool
    :type first_number: int
    :param last_number: the highest number in pool
    :type last_number: int
    :param winner_suffix: number endings to set aside for winning tickets
    :type winner_suffix: list[str]
    :param biggest_winner: the highest possible winning number
    :type biggest_winner: int
    :param smallest_nw: lowest nonwinning number (allows a winning number to be smaller than least nonwinner)
    :type smallest_nw: int
    :param dm_tag_name: tag to be used in DesignMerge to change font
    :type dm_tag_name: str
    :param color_all_letters: are all digits in a winner to be changed to a new font or just the suffix?
    :type color_all_letters: bool
    :return: two lists: one for winners and another for nonwinners, i.e. [winners, nonwinners]
    :rtype: list[list[str] | list[int]]
    """
    print(f"Creating number pools with the range {first_number} - {last_number}, with the suffix(es)"
          f" {winner_suffix} below {biggest_winner} being set aside for the winners, and {smallest_nw}"
          f" as the smallest possible nonwinner.")
    # Create winning and losing number lists
    win_numbers = []
    nw_numbers = []
    # Cycle through the numbers from the lowest to the highest to be used
    for i in range(first_number, last_number + 1):
        # Convert each to a string for easy comparison goodness
        num = str(i)
        # If the last two numerals match the passed suffix, check if it should be added to the winner list
        if num[len(num) - 2:len(num)] in winner_suffix:
            # We only care about winners up to the biggest value. If this falls below the threshold, add it
            # to the winner list. Otherwise, discard it. We don't want any values that match the suffix
            # to become part of the nonwinner list and create confusion with end users.
            if i <= biggest_winner:
                # If we need to use the DM tag to change the entire string, place it at the front
                # of the string. Otherwise, insert the tag the suffix and the rest of the string.
                num = num.zfill(3)
                if color_all_letters:
                    num = f'<@{dm_tag_name}>{num}'
                else:
                    num = num[:len(num) - 2] + f'<@{dm_tag_name}>' + num[len(num) - 2:]
                win_numbers.append(num)
        # If this nonwinning number is greater than or equal to the lower limit, add it to the list of nonwinners
        # JUST MADE THIS REJECT TWO-DIGIT NUMBERS--CHECK THIS IF YOU WANT TO INCLUDE THEM
        # elif i >= smallest_nw and i > 100:
        elif i >= smallest_nw and i >= 0:
            nw_numbers.append(num)
    # Shuffle both lists 5 to 10 times
    for _ in range(rn.randint(5, 10)):
        # rn.shuffle(win_numbers)
        rn.shuffle(nw_numbers)
    # return [list[str], list[int]]
    return [win_numbers, nw_numbers]


def create_number_pools_from_suffix_list(first_nw: int, last_nw: int, flags: list[str], mixed: bool = True):
    """
    Create a list of numbers to be used as nonwinners for shaded (or other number) ticketing_games between the
    first and last values. Throw out any numbers that contain significant suffixes or where all the
    digits are the same.

    :param first_nw: first nonwinning number
    :type first_nw: int
    :param last_nw: last nonwinning number
    :type last_nw: int
    :param flags: a list of suffixes to be thrown out
    :type flags: list[str]
    :param mixed: does the list need to be shuffled
    :type mixed: bool
    :return: a list of nonwinning integers
    :rtype: list[int]
    """
    nw_numbers = []

    def all_same_digits(numero):
        """
        Sub function to determine if all the digits in a given number are the same.

        :param numero: the number to check
        :type numero: int
        :return: true if all the digits are the same, false otherwise
        :rtype: bool
        """
        str_num = str(numero)
        return all(digit == str_num[0] for digit in str_num)

    # We'd rather not have any double zeroes at the end of any nonwinning integer,
    # so add it to the list of suffixes if it's not already there.
    if '00' not in flags:
        flags.append('00')

    # Cycle through the range of numbers between the first and last integers.
    # Add them to the list if they aren't reserved.
    for num in range(first_nw, last_nw + 1):
        # Check if the number has a reserved suffix or its digits
        # are all the same. If so, skip this one.
        if str(num)[-2:] in flags or all_same_digits(num):
            continue
        else:
            nw_numbers.append(str(num))
    # Shuffle the numbers if necessary.
    if mixed:
        for _ in range(rn.randint(5, 10)):
            rn.shuffle(nw_numbers)
    return nw_numbers


def create_ten_column_spread(first_number: int, last_number: int, fill_size: int,
                             shuffle: bool = False) -> list[list[int]] | list[list[str]]:
    """
    Create a list of ten elements that each contain numbers in the specified range whose
    first number corresponds to the zero-filled first numeral.

    :param first_number:
    :param last_number:
    :param fill_size:
    :param shuffle:
    :return:
    """
    columns = []
    last_length = len(str(last_number))
    bundle_divisor = 10 ** fill_size
    for _ in range(10):
        columns.append([])
    for i in range(first_number, last_number + 1):
        index = i // bundle_divisor
        columns[index].append(i) if fill_size == 0 else columns[index].append(str(i).zfill(last_length))
    if shuffle:
        for column in columns:
            for _ in range(rn.randint(5, 10)):
                rn.shuffle(column)
        for _ in range(rn.randint(5, 10)):
            rn.shuffle(columns)
    return columns


def create_number_pools_multi(first_number: int, last_number: int, winner_suffix: list[str], smallest_nw: int,
                              biggest_winner: int, dm_tag_name: str, color_all_letters=False) \
        -> list[list[str] | list[int]]:
    """
    I'M NOT SURE WHY THIS WAS CREATED. NOTHING CALLS THIS METHOD. I MAY HAVE INITIALLY HAD A SEPARATE METHOD FOR
    MULTIPLE WINNING STRINGS, BUT REALIZED IT WASN'T NECESSARY. I'M KEEPING THIS AROUND UNTIL I'M SURE ABOUT IT.
    Create a pool of numbers between p_first and p_last. Place the results in two lists (winners and nonwinners)
    and return them to the caller. Winners are determined by a list of numeric strings being compared against the
    ending numbers for each integer. Any number that has the string as a suffix is placed in a winners' list if
    it falls between the smallest and biggest winning numbers. Any number of suffixes can be used, with
    each discrete string's associated numbers placed in their own lists. All other numbers
    containing the strings are discarded to avoid confusion.

    :param first_number: lowest number in pool
    :type first_number: int
    :param last_number: highest number in pool
    :type last_number: int
    :param winner_suffix: number endings to set aside for winning tickets
    :type winner_suffix: list[str]
    :param biggest_winner: highest possible winning number
    :type biggest_winner: int
    :param smallest_nw: lowest nonwinning number (allows a winning number to be smaller than least nonwinner)
    :type smallest_nw: int
    :param dm_tag_name: tag to be used in DesignMerge to change font
    :type dm_tag_name: str
    :param color_all_letters: are all digits in a winner to be changed to a new font or just the suffix?
    :type color_all_letters: bool
    :return: two lists: one for winners and another for nonwinners, i.e. [winners, nonwinners]
    :rtype: list[list[str] | list[int]]
    """
    print(f"Creating number pools with the range {first_number} - {last_number}, with the suffix(es)"
          f" {winner_suffix} below {biggest_winner} being set aside for the winners, and {smallest_nw}"
          f" as the smallest possible nonwinner.")
    # Create winning and losing number lists
    nw_numbers = []
    win_numbers = []
    for _ in range(len(winner_suffix)):
        win_numbers.append([])
    # Cycle through the numbers from the lowest to the highest to be used
    for i in range(first_number, last_number + 1):
        # Convert each to a string for easy comparison goodness
        num = str(i)
        # If the last two numerals match the passed suffix, check if it should be added to the winner list
        if num[len(num) - 2:len(num)] in winner_suffix:
            # We only care about winners up to the biggest value. If this falls below the threshold, add it
            # to the winner list. Otherwise, discard it. We don't want any values that match the suffix
            # to become part of the nonwinner list and create confusion with end users.
            if i <= biggest_winner:
                # If we need to use the DM tag to change the entire string, place it at the front
                # of the string. Otherwise, insert the tag the suffix and the rest of the string.
                if color_all_letters:
                    num = f'<@{dm_tag_name}>{num}'
                else:
                    num = num[:len(num) - 2] + f'<@{dm_tag_name}>' + num[len(num) - 2:]
                for index, suffer in enumerate(winner_suffix):
                    if num[len(num) - 2:len(num)] == suffer:
                        win_numbers[index].append(num)
        # If this nonwinning number is greater than or equal to the lower limit, add it to the list of nonwinners
        elif i >= smallest_nw:
            nw_numbers.append(num)
    # Shuffle both lists 5 to 10 times
    for _ in range(rn.randint(5, 10)):
        for i in range(len(win_numbers)):
            rn.shuffle(win_numbers[i])
        rn.shuffle(nw_numbers)
    # return [list[str], list[int]]
    return [win_numbers, nw_numbers]


def create_multi_suffixed_number_pools(first_number: int, last_number: int, suffixes: dict[str, list[str | int | bool]],
                                       smallest_nw: int, biggest_nw: int) -> list[list[str] | list[int]]:
    """
    Create a pool of numbers between first_number and last_number and add them to winning and nonwinning lists.
    The nonwinners will fall between smallest_nw and biggest_nw, excluding integers that contain any of the
    specified suffixes. Suffix parameters are contained within a dictionary, with each suffix being used as
    its index. Its value consists of a list containing the first and last winners, DesignMerge tag, and tag
    placement flag. Each suffix's winning numbers will appear as its own list in the returned winners' list.

    :param first_number: lowest number in pool
    :type first_number: int
    :param last_number: the highest number in pool
    :type last_number: int
    :param suffixes: dictionary containing suffixes and their associated information
    :type suffixes: dict[str, list[str | int| bool]]
    :param smallest_nw: lowest nonwinning number (allows a winning number to be smaller than least nonwinner)
    :type smallest_nw: int
    :param biggest_nw: highest nonwinning number
    :type biggest_nw: int
    :return: two lists: one for winners and another for nonwinners, i.e. [winners, nonwinners]
    :rtype: list[list[str] | list[int]]
    """
    # Create a list containing zfilled (2) strings of every integer between first_number and last_number.
    big_pool = list(str(item).zfill(2) for item in range(first_number, last_number + 1))
    # Create a list of the suffixes
    endings = list(suffixes.keys())
    print(f"Creating number pools within the range {first_number} - {last_number}. The suffix(es)"
          f" {suffixes} are being placed in their own list(s) for the winners, and the nonwinners"
          f" will contain the remaining numbers between {smallest_nw} and {biggest_nw}.")
    # Create lists to contain the winning and nonwinning numbers
    nw_numbers = []
    win_numbers = []
    for _ in range(len(endings)):
        win_numbers.append([])
    # Cycle through the range of integers and add them to the appropriate list.
    for i in big_pool:
        # Check if the final two digits of this integer are in the list of suffixes.
        if i[len(i) - 2:len(i)] in endings:
            # Get the position of this suffix in the list of suffixes and use it to add this suffix
            # to the correct winner's list if it falls within the first and last parameter.
            index = endings.index(i[len(i) - 2:len(i)])
            bottom = suffixes[i[len(i) - 2:len(i)]][0]
            top = suffixes[i[len(i) - 2:len(i)]][1]
            # Add the string to the appropriate list
            if bottom <= int(i) <= top:
                if suffixes[i[len(i) - 2:len(i)]][3]:
                    num = f'<@{suffixes[i[len(i) - 2:len(i)]][2]}>{i}'
                else:
                    num = i[:len(i) - 2] + f'<@{suffixes[i[len(i) - 2:len(i)]][2]}>' + i[len(i) - 2:]
                win_numbers[index].append(num)
        else:
            if smallest_nw <= int(i) <= biggest_nw:
                nw_numbers.append(i)
    return [win_numbers, nw_numbers]


def create_nonwinner_number_tickets(amt: int, spots: int, nw_pool: list[str]) -> list[list[str]]:
    """
    Create a list of lists containing nonwinning number combinations of a specified length
    from an existing pool of numbers.

    :param amt: number of lists needed
    :type amt: int
    :param spots: number of integers in each list
    :type spots: int
    :param nw_pool: pool of numbers used to create the lists
    :type nw_pool: list[str]
    :return: list of lists containing nonwinning number combinations
    :rtype: list[list[str]]
    """
    # Create the top-level list to contain number lists
    nw_tickets = []
    # Repeat for the number of tickets needed
    for _ in range(amt):
        # List to hold nonwinners
        nw_tick = []
        # Add the number of nonwinners needed per ticket
        for _ in range(spots):
            nw_tick.append(nw_pool.pop(0))
        # add the ticket to the top-level list
        nw_tickets.append(nw_tick)
    return nw_tickets


def create_numbered_holds(win_numbs, nw_numbs, spots):
    """
    Create a list of lists containing a winning number plus an indeterminate number of nonwinning numbers.

    :param win_numbs: list of winning numbers
    :type win_numbs: list[str]
    :param nw_numbs: list of nonwinning numbers
    :type nw_numbs: list[str]
    :param spots: number of numbers per ticket
    :type spots: int
    :return: A list of lists containing a winning number and filler nonwinning numbers
    :rtype: list[list[str]]
    """
    winners = []
    # Cycle through the list of winning numbers
    while len(win_numbs) != 0:
        # Pop off the winning number in the first position of the list
        # and use it to create a new list.
        numbs = [win_numbs.pop(0)]
        # Append nonwinning numbers until the ticket contains the required number.
        for _ in range(spots - 1):
            numbs.append(nw_numbs.pop(0))
        # Shuffle 'em up.
        for _ in range(rn.randint(5, 10)):
            rn.shuffle(numbs)
        # Add the list to the list of winners
        winners.append(numbs)
    return winners


def create_varied_numbered_holds(win_numbs: list[str], nw_numbs: list[str], spots: int, win_amts: list[int]):
    """
    Create a list of hold tickets that contain varying numbers of winners. The amounts are
    passed in a list that functions like the free spot lists in other hold tickets.

    :param win_numbs: list of winning numbers
    :type win_numbs: list[str]
    :param nw_numbs: list of nonwinning numbers
    :type nw_numbs: list[str]
    :param spots: number of spots on each ticket
    :type spots: int
    :param win_amts: list where the indexes indicate the number of winning spots and the value is the number of tickets
    :type win_amts: list[int]
    :return: A list of lists containing winning numbers and filler nonwinning numbers
    :rtype: list[list[str]]
    """
    winners = []
    for index, amt in enumerate(win_amts):
        for _ in range(amt):
            tick = []
            for _ in range(index + 1):
                tick.append(win_numbs.pop(0))
            for _ in range(spots - len(tick)):
                tick.append(nw_numbs.pop(0))
            for _ in range(rn.randint(5, 10)):
                rn.shuffle(tick)
            winners.append(tick)
    return winners


def create_numbered_holds_multi(win_numbs: list[list[str]], nw_numbs: list[str], spots):
    """
    Create a list of lists containing a winning number plus an indeterminate number of
    nonwinning numbers. The sublists contain all the numbers associated with a particular
    suffix. The returned list contains all the tickets generated for each sublist.

    :param win_numbs: list of lists containing winning numbers
    :type win_numbs: list[list[str]]
    :param nw_numbs: list of nonwinning numbers
    :type nw_numbs: list[str]
    :param spots: number of spots per ticket
    :type spots: int
    :return: A list of lists containing a winning number and filler nonwinning numbers
    :rtype: list[list[str]]
    """
    winners = []
    for wins in win_numbs:
        win = []
        while len(wins) != 0:
            numbs = [wins.pop(0)]
            for _ in range(spots - 1):
                numbs.append(nw_numbs.pop(0))
            for _ in range(rn.randint(5, 10)):
                rn.shuffle(numbs)
            win.append(numbs)
        winners.append(win)
    return winners


def create_basic_number_pool(first: int, last: int) -> list[str]:
    """
    Take a beginning and ending number and create a list
    containing string representations of the numbers.

    :param first: beginning number
    :type first: int
    :param last: ending number
    :return: a list of strings ranging from first to last number
    :rtype: list[str]
    """
    # Take all numbers in the first/last range, convert them to strings, and add them to a list
    numbs = [str(i) for i in range(first, last + 1)]
    # Shuffle the list
    for _ in range(rn.randint(5, 10)):
        rn.shuffle(numbs)
    return numbs


def create_winning_pools(pools: list[str], suffixes: list[list[str | int | bool]]) -> list[list[str]]:
    # Go to the input for suffixes and add functionality for specifying
    # first and last for each suffix

    pass


def create_winning_number_pool(pool: list[str], first: int, last: int, suffix: str,
                               tag: str, all_numbers: bool) -> list[str]:
    # Create a list to hold the winning numbers
    winners = []
    for index in reversed(range(len(pool))):
        if pool[index][len(pool[index]) - 2:len(pool[index])] == suffix:
            whiner = pool.pop(index)
            if first <= int(whiner) <= last:
                if all_numbers:
                    whiner = f'<@{tag}>{whiner}'
                else:
                    whiner = whiner[:len(whiner) - 2] + f'<@{tag}>' + whiner[len(whiner) - 2:]
                winners.append(whiner)
    return winners


def create_bingo_downlines(spots: int, letters: bool, hyphen: bool,
                           zeroes: bool, mixers: bool = False) -> list[list[str]]:
    """
    Creates bingo downlines of given number of spots.

    :param spots: number of spots in the downline
    :type spots: int
    :param letters: include bingo letters?
    :type letters: bool
    :param hyphen: include a hyphen in the downline spots? (ignored if letters is False)
    :type hyphen: bool
    :param zeroes: include leading zeroes?
    :type zeroes: bool
    :param mixers: shuffle the downlines?
    :type mixers: bool
    :return: list of bingo downlines
    :rtype: list[list[str]]
    """
    # Create the bingo positions and DO NOT have them shuffled! They'll be mixed
    # further down if
    bingos = create_bingo_positions(letters, hyphen, zeroes, True, False)
    downers = []
    for index in range(len(bingos[0])):
        bingo = []
        for bins in bingos:
            bingo.append(bins[index])
        combos = itty.combinations(bingo, spots)
        for combo in combos:
            downers.append(list(combo))
    if mixers:
        for _ in range(rn.randint(4, 11)):
            rn.shuffle(downers)
    return downers


def create_bingo_numbers(letters: bool = False, hyphen: bool = False, zeroes: bool = False, mixers: bool = True):
    alphabet = ['B', 'I', 'N', 'G', 'O']
    bingos = []
    for i in range(len(alphabet)):
        bingo = []
        for j in range(1, 16):
            spot = ''
            if letters:
                spot += alphabet[i]
            if hyphen:
                spot += '-'
            spot += str((i * 15) + j).zfill(2) if zeroes else str((i * 15) + j)
            # spot += str((i * 15) + j)
            bingo.append(spot)
        bingos.append(bingo)
    if mixers:
        for _ in range(rn.randint(5, 10)):
            for i in range(len(bingos)):
                rn.shuffle(bingos[i])
            rn.shuffle(bingos)
    return bingos


def create_bingo_positions(letters: bool = False, hyphen: bool = False, zeroes: bool = False,
                           multi: bool = False, mix: bool = False) -> list[str] | list[list[str]]:
    """
    Create a list (or a list of lists) of bingo numbers based on the traditional positions:\n
     B-1 — B-15, I-16 — I-30, N-31 — N-45, G-46 — G-60, O-61 — 0-75\n
    The positions can contain (or not) the letters, a hyphen between letter and number, and leading
    zeroes on single digits. The resulting strings can be returned as a single list of strings containing
    all 75 spots, or a list of five lists, each containing all the values corresponding to a particular
    letter.

    :param letters: If True, a letter corresponding to the column is prepended to the numerical value
    :type letters: bool
    :param hyphen: If True, a hyphen will divide the number and letter. Only significant if letters is true.
    :type hyphen: bool
    :param zeroes: If True, zeroes will be added to those letters contain only one digit
    :type zeroes: bool
    :param multi: If True, values are contained in five lists. If False, values are contained in one large list.
    :type multi: bool
    :param mix: If True, values are shuffled.
    :type mix: bool
    :return: 75 spots, as either five, 15-spot lists, or one, 75-spot list.
    :rtype: list[str | list[str]]
    """
    # Letters for each column, if needed
    alphabet = ['B', 'I', 'N', 'G', 'O']
    bingos = []
    # Cycle through the bingo columns
    for i in range(len(alphabet)):
        # Create a list and fill it with the numbers for this column, plus any desired decoration
        bingo = []
        for j in range(1, 16):
            # Create a string and populate it with all the desired pieces
            spot = ''
            # Add the letter to the string and the hyphen if indicated
            if letters:
                spot += alphabet[i]
                # Hyphen is only checked if letters are added
                if hyphen:
                    spot += '-'
            # Add this spot's numerical value and zero-fill if necessary
            spot += str((i * 15) + j).zfill(2) if zeroes else str((i * 15) + j)
            bingo.append(spot)
        bingos.append(bingo)
    # If this needs to be one big list, create a temp list, cycle through every spot in
    # bingos, add them to the temp list, then assign the list to bingos.
    if not multi:
        temp = []
        for bingo in bingos:
            for spot in bingo:
                temp.append(spot)
        bingos = temp
    # Shuffle either version of list
    if mix:
        for i in range(rn.randint(5, 10)):
            # If we're dealing with five lists, cycle through each list, shuffle it,
            # then shuffle the list that contains them.
            if len(bingos) == 5:
                for bingo in bingos:
                    rn.shuffle(bingo)
                rn.shuffle(bingos)
            # Otherwise, just shuffle the one list
            else:
                rn.shuffle(bingos)
    # Return the randomized list
    return bingos


def count_remaining_numbers(bingos: list[list[int]]):
    """

    :param bingos:
    :return:
    """
    return sum(len(b) for b in bingos)


def create_potential_bingos_letters(letters: bool, hyphen: bool, zeroes: bool, multi: bool,
                                    mix: bool) -> list[list[str | int]] | None:
    """
    Create a list of lists containing bingo spots with no more than two from any
    given column. Bail if it looks like there isn't a varied enough set
    of spots to generate the whole list.

    :return: list of lists containing bingo numbers
    """
    # Grab a single list of all seventy-five bingo numbers
    pool = create_bingo_positions(letters, hyphen, zeroes, multi, mix)
    cards = []
    # Attempt to create 15 bingo lists
    for _ in range(15):
        card = []
        # Use this dictionary to prevent more than 2 of any column from being used.
        totals = {
            'B': 0,
            'I': 0,
            'N': 0,
            'G': 0,
            'O': 0
        }
        count = 0
        while len(card) < 5:
            count += 1
            candy = pool.pop(0)
            if totals[candy[:1]] == 2:
                pool.append(candy)
                rn.shuffle(pool)
            else:
                card.append(candy)
                totals[candy[:1]] += 1
            if count == 25:
                return None
        cards.append(card)
    return cards


def create_unique_lines_with_bingo_spots(letters: bool, hyphen: bool, zeroes: bool, dm_tag: str,
                                         taken=None) -> [list[list[str | int]], set[list[str]]]:
    """

    :param letters:
    :param hyphen:
    :param zeroes:
    :param dm_tag:
    :param taken:
    :return:
    """
    if taken is None:
        taken = set()
    bingos = []
    undented = False
    potentials = []
    while not undented:
        potentials = create_potential_bingos_letters(letters, hyphen, zeroes, False, True)
        if potentials is not None:
            undented, taken = check_winning_bingo_paths(potentials, taken)
    for dots in potentials:
        spotters = []
        for dot in dots:
            if dm_tag is not None and dm_tag != '':
                dot = f'{dm_tag}{dot}'
            spotters.append(dot)
        bingos.append(spotters)
    return [bingos, taken]


def create_full_bingo_line_permutations(amt: int, letters: bool, hyphen: bool, zeroes: bool, dm_tag: str):
    taken = set()
    perms = []
    while len(perms) < amt:
        numbers, taken = create_unique_lines_with_bingo_spots(letters, hyphen, zeroes, dm_tag, taken)
        if numbers is not None:
            perms.append(numbers)
    return perms


def check_winning_bingo_paths(bingos: list[list[str | int]], taken: set) -> [bool, set[list[str | int]]]:
    """
    Check a list of potential winning bingo paths against the set of those already taken.

    :param bingos: list of potential winning bingo paths
    :type bingos: list[list[str | int]]
    :param taken: set of tuples containing previously taken winning bingo paths
    :type taken: set[tuple[str | int]]
    :return: success (true or false) and set of taken winning bingo paths
    :rtype: tuple[bool, set[list[str | int]]]
    """
    c_lists = copy.deepcopy(bingos)
    dd = False
    for c_list in c_lists:
        if dd:
            print(f"c_list before sorting: {c_list}")
        c_list.sort()
        if dd:
            print(f"c_list after sorting: {c_list}")
        if tuple(c_list) in taken:
            if dd:
                print("\n\n!!!!!!!!!!!! Houston? Problem. COLLISION. Meteor! !!!!!!!!!!!")
                return [False, taken]
    for c_list in c_lists:
        taken.add(tuple(c_list))
    return [True, taken]


def create_unique_bingo_line_permutations(q_perms: int, amt: int, spots: int, zeroes: bool, letters: bool,
                                          hyphen: bool) -> list[list[list[str | int]]]:
    """
    Create a list of list of lists containing unique bingo paths that have the required number of spots
    and any decoration the numbers need: leading zeroes, column letters, and hyphens.

    :param q_perms: the number of perms needed
    :type q_perms: int
    :param amt: number of bingo paths in each perm
    :type amt: int
    :param spots: number of spots in each bingo path
    :type spots: int
    :param zeroes: Are leading zeroes needed?
    :type zeroes: bool
    :param letters: Are the column letters (BINGO) needed?
    :type letters: bool
    :param hyphen: Is a hyphen needed between the letters and numbers (only relevant when 'letters' is True).
    :type hyphen: bool
    :return: a list of lists containing lists of bingo paths
    :rtype: list[list[list[str | int]]]
    """
    taken = set()
    perms = []
    while len(perms) < q_perms:
        potential = create_unique_bingo_lines(amt, spots, zeroes, letters, hyphen, taken)
        if potential is not None:
            perms.append(potential)
    return perms


def create_unique_bingo_lines(amt: int, spots: int, zeroes: bool, letters: bool,
                              hyphen: bool, taken=None) -> list[list[str | int]] | None:
    """
    Create a list of unique bingo paths containing the number required and any
    decoration the numbers need: leading zeroes, column letters, and hyphens.

    :param amt: number of bingo lines needed
    :type amt: int
    :param spots: number of spots in each bingo line
    :type spots: int
    :param zeroes: Are leading zeroes needed?
    :type zeroes: bool
    :param letters: Are the column letters (BINGO) needed?
    :type letters: bool
    :param hyphen: Is a hyphen needed between the letters and numbers (only relevant when 'letters' is True).
    :type hyphen: bool
    :param taken: set of tuples containing previously taken bingo paths
    :type taken: set[tuple[str | int]]
    :return: a list of lists containing bingo lines
    :rtype: list[list[str | int]]
    """
    bingos = []
    numbers = []
    # Create a new set for winning paths if one doesn't already exist
    if taken is None:
        paths_taken = set()
    else:
        paths_taken = taken
    # Cycle through until we get the number we came for.
    while len(bingos) < amt:
        numbs = []
        # If there aren't enough numbers remaining in the master list,
        # create a new list.
        if count_remaining_numbers(numbers) < spots:
            numbers = create_bingo_numbers(letters, hyphen, zeroes)
        # Add the required number of spots and sort them by value.
        for i in range(spots):
            numbs.append(numbers[i].pop(0))
        if hyphen:
            numbs.sort(key=lambda x: int(x.split('-')[1]), reverse=False)
        else:
            numbs.sort(key=lambda x: int(x), reverse=False)
        # Make sure the path isn't already taken and add it if it isn't.
        if tuple(numbs) not in paths_taken:
            paths_taken.add(tuple(numbs))
            bingos.append(numbs)
        else:
            # Apparently we're bailing if this
            print(f'Rejected: {numbs}')
            return None
        for _ in range(rn.randint(2, 4)):
            rn.shuffle(numbers)
        numbers.sort(key=len, reverse=True)
    return bingos


def create_full_bingo_line_permutations_from_full_list(tkt_amt: int, spots: int, perm_qty: int,
                                                       zeroes: bool, letters: bool, hyphen: bool):
    taken = set()
    perms = []
    while len(perms) < perm_qty:
        numbers, taken = create_bingo_lines_from_full_list(tkt_amt, spots, zeroes, letters, hyphen, taken)
        if numbers is not None:
            perms.append(numbers)
    return perms


def create_bingo_lines_from_full_list(amt: int, spots: int, zeroes: bool,
                                      letters: bool, hyphen: bool, taken: set[tuple[str]] = None) -> list[list[str]]:
    """
    Create a list of lists containing bingo numbers that span the entire 1-75 range. Unlike
    traditional bingos, the members of these lists do not need to contain numbers from disparate
    columns--they can be spread across the 75 numbers however the random generator sees fit.

    :param amt: number of bingo lines needed
    :type amt: int
    :param spots: number of spots in each bingo line
    :type spots: int
    :param zeroes: Include leading zeroes?
    :type zeroes: bool
    :param letters: Include column letters?
    :type letters: bool
    :param hyphen: Include a hyphen in between letter and number?
    :type hyphen: bool
    :param taken: Set containing winning bingo lines already taken
    :type taken: set[tuple[str]]
    :return: List of lists containing bingo numbers that span the entire 1-75 range
    :rtype: list[list[str]]
    """
    if taken is None:
        taken = set()
    paths_taken = taken
    bingos = create_bingo_positions(letters, hyphen, zeroes, False, True)
    lines = []
    while len(lines) < amt:
        line = []
        if len(bingos) < spots:
            bingos = create_bingo_positions(letters, hyphen, zeroes, False, True)
        for _ in range(spots):
            line.append(bingos.pop(0))
        sort_line = copy.deepcopy(line)
        sort_line.sort(key=lambda x: int(x), reverse=False)
        if tuple(sort_line) not in paths_taken:
            lines.append(line)
            paths_taken.add(tuple(sort_line))
        else:
            print(f'Duplicate: {sort_line}')
    return [lines, paths_taken]


def create_free_substitutes(zeroes: bool, letters: bool, hyphen: bool):
    bingos = ['B', 'I', 'N', 'G', 'O']
    substitutes = []
    for col in range(5):
        spots = []
        for val in range(1, 16):
            spot = (col * 15) + val
            if zeroes:
                t_spot = str(spot).zfill(2)
            else:
                t_spot = str(spot)
            if letters:
                if hyphen:
                    t_spot = f"{bingos[col]}-{t_spot}"
                else:
                    t_spot = f"{bingos[col]}{t_spot}"
            spots.append(t_spot)
        substitutes.append(spots)
    return substitutes


def create_free_substitutes_refined(zeroes: bool, letters: bool, hyphen: bool):
    bingos = 'BINGO'
    substitutes = []

    for col in range(5):
        spots = [
            (f"{bingos[col]}{'-' if hyphen else ''}" if letters else "") +
            (str(col * 15 + val).zfill(2) if zeroes else str(col * 15 + val))
            for val in range(1, 16)
        ]
        substitutes.append(spots)

    return substitutes


def create_bingo_lines_with_frees(amt: list[int], zeroes: bool, letters: bool, hyphen: bool,
                                  taken: set[tuple[str]] = None) -> list[list[str]]:
    """

    :param amt:
    :param zeroes:
    :param letters:
    :param hyphen:
    :param taken:
    :return:
    """
