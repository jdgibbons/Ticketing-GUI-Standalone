import copy
import random as rn

from ticketing import game_info as gi
from ticketing import image_generator as ig
from ticketing import number_generator as ng

DEBUG = True

nw_type, insta_type, pick_type, hold_type = '', '', '', ''


def extract_ticket_types(game_specs):
    return [game_specs[1].pop(0), game_specs[2].pop(0), game_specs[3].pop(0), game_specs[4].pop(0)]


def create_matrix_hold_tickets(amt: int, pattern: list[int], base: str, zeroes: bool, addl_imgs: gi.AddImages,
                               is_first: bool = False, permits: int = 1, tkt_no: int = 1):
    bingo_values = []
    perms = []
    number_total = sum(pattern)
    tiered_totals = copy.deepcopy(pattern)
    tiered_totals.sort(reverse=True)

    paths_taken = set()

    imgs = ig.add_additional_image_slots(addl_imgs, [base])
    first_one = is_first
    while len(perms) < permits:
        tkt = tkt_no
        ticks = []
        while len(ticks) < amt:
            if not check_column_lengths(tiered_totals, bingo_values):
                bingo_values = ng.create_bingo_positions(False, False, zeroes, True, True)
            for _ in range(rn.randint(2, 4)):
                rn.shuffle(bingo_values)
            bingo_values.sort(key=len, reverse=True)
            bings = []


def check_column_lengths(sizes: list[int], numbers: list[list[int | str]]):
    """
    Check if the lengths of the columns in the given data match or exceed the required sizes.

    This function verifies that the lengths of the individual sublists (columns) in the
    provided list of lists `numbers` are not smaller than the corresponding values
    in the `sizes` list. It ensures that the dimensions of the data comply with
    expected minimum column sizes.

    :param sizes: A list of integers representing the minimum required sizes for each column.
    :type sizes: list[int]
    :param numbers: A list of sublists, where each sublist represents one column containing
        integers or strings.
    :type numbers: list[list[int | str]]
    :return: Boolean value indicating whether the column lengths meet the required sizes.
    :rtype: bool
    """
    if len(sizes) > len(numbers):
        return False
    for i in range(len(sizes)):
        if len(numbers[i]) < sizes[i]:
            return False
    return True


def create_game(game_specs):
    """
    Initializes and generates a bingo-ball style work order based on specifications from a gui-based form. This
    function supports different types of tickets including pick and instant winners, shaded or imaged holds, and
    imaged or shaded non-winners. Finally, it writes the generated tickets and game stacks to specified output files.

    :param game_specs: A tuple containing specifications for creating the game. The tuple typically consists of:
                       - sheets_specs: Specifications related to sheet configurations.
                       - nowin_specs: Specifications for non-winner tickets.
                       - instant_specs: Specifications for instant win tickets.
                       - picks_specs: Specifications for pick winner tickets.
                       - holds_specs: Specifications for hold tickets.
                       - names_specs: Contains party and file name information.
                       - output_folder: The folder where output files are stored.
    :type game_specs: tuple
    :return: A status message indicating that all items have been successfully written to the files.
    :rtype: str
    """
    global nw_type, insta_type, pick_type, hold_type
    if DEBUG:
        print(game_specs)
    nw_type, insta_type, pick_type, hold_type = extract_ticket_types(game_specs)
    if DEBUG:
        print("\n\n")
        print(game_specs)
    first_timer = True
    mix_flat = True
    tickets = []
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder = game_specs
    part_name, file_name = name_specs


if __name__ == '__main__':
    specs = [
        [4, 1, 66, [56, 56], False, 0, 0],
        ['I', 691, 9, 3],
        ['I', [[1, False], [2, False], [10, False], [90, False]], 0],
        ['I', [[0, False]]],
        ['M', 130, [3, 2, 3, 2, 3], 'base01.ai', True],
        ['993-246', 'TripleDouble-53685'],
        ''
    ]
    create_game(*specs)
