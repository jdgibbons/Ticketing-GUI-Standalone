import itertools as iters

from numpy import matrix
import random as rn

from .bingo_face_list import BingoFaceList


def create_pseudo_faces(face_list: BingoFaceList, amt: int, frees: int, size: int, csv_rows: int,
                        staggered: bool = True) -> list[list[str | list[str]]]:
    """
    Create hold tickets of varying sizes and free spaces. Use this method when the free spaces are not
    confined to the same column in both rows (i.e., they are placed single spots rather than full columns).
    This method assumes there are one or two lines with one or two possible free spaces. Staggered lines
    adhere to the following convention: \n
    |  Staggered: \n
    |  [1,  F, 31, 46, 61] \n
    |  [2, 17, 32,  F, 62] \n
    |  Non-Staggered: \n
    |  [1,  F, 31,  F, 61] \n
    |  [2,  F, 32,  F, 62] \n

    :param amt: number of tickets needed
    :type amt: int
    :param frees: number of free spaces
    :type frees: int
    :param size: number of lines on each ticket
    :type size: int
    :param csv_rows: number of rows needed for csv ticket (not currently used)
    :type csv_rows: int
    :param staggered: If free spaces are in the same spot for both paths
    :type staggered: bool
    :param face_list: list of available bingo faces
    :type face_list: BingoFaceList
    :return: list of pseudo bingo faces
    :rtype: list[list[str | list[str]]]
    """
    d_rejects = 0  # List to hold created tickets
    temp_faces = []
    # KEEPING THIS BECAUSE I'LL NEED THE EXPLANATION LATER ON.
    # If the base image needs to be included in the csv, change the value to the appropriate name (convention is "base"
    # + the number of lines padded with zeroes + the extension "ai"), otherwise, simply set it to an empty string.
    # base_file = f"base{str(size).zfill(2)}.ai" if add_base_file else ''

    while len(temp_faces) < amt:
        face = face_list.get_two_unique_paths_with_verification()
        if face[0] is None:
            return face
        # If only one path is needed, delete the second one
        if size == 1:
            face.pop()
        face = face_list.add_free_spaces(face, frees, staggered)
        # Get a list representing all possible bingo values then check if there are any collisions.
        # Next, line takes one or two five-member bingo lines and creates five arrays using the one
        # or two values in each spot as members. If there is a free spot, *all* 15 numbers for that
        # spot will be injected it.
        temp_list = face_list.create_verification_lists(face)
        # Use the five-member list created above to
        # calculate the possible winning combinations.
        combos = face_list.create_winning_combinations(temp_list)

        # Check if there are any possible collisions with previously used paths. If not, create a new
        # ticket and add it to the ticket array. Otherwise, do nothing.
        if face_list.paths_collision_free(combos):
            if len(temp_faces) == 0:
                print('      ', end='')
            # ticker = create_one_hold_ticket(base_file, combos, face, size, staggered)
            # Add these possible winning paths to the paths taken list
            face_list.add_combos_to_paths_taken(combos)
            very = face.pop(0)
            new_face = [very, face]
            new_face += [size, frees, staggered]
            temp_faces.append(new_face)
            print(f"{len(temp_faces)}", end=" ")
            if len(temp_faces) % 30 == 0:
                print('')
                print('      ', end='')
        else:
            d_rejects += 1
    print('')
    return temp_faces


def create_single_line_either_or_faces(face_list: BingoFaceList, deets: list[int],
                                       verbose: bool = False) -> list[list[list[str | list[str]]]]:
    """
    Create a list of single-line bingos with possible either-or and/or free spots.
    (Any tickets that have no either-or spots will probably be handled by other methods.)

    This function generates a specified quantity of either-or bingo faces, where each face is represented
    by a verification number and three lines fitting depicting bingo ticket format in the CSV. It utilizes
    helper functions to construct each face and ensures the faces conform to given specs.

    :param face_list: Specific list of Bingo faces to use in construction.
    :type face_list: BingoFaceList
    :param deets: Specifications for face creation, where deets[0] is the quantity of faces, deets[1] is
                  the number of free spaces, and deets[2] is the number of either-or spaces.
    :type deets: list[int]
    :param verbose: Flag to control whether detailed information is printed during the process.
    :type verbose: bool
    :return: List of created bingo faces, each with several structured lines.
    :rtype: list[list[list[str | list[str]]]]
    """
    faces = []
    # Loop until there are the required faces (deets[0] = quantity).
    while len(faces) < deets[0]:
        # Print info to console if desired.
        if verbose:
            if len(faces) == 0:
                print('      ', end='')
        # Get a single either-or bingo face based on specs.
        temp_face = create_single_line_pseudo_either_or(face_list, deets[1], deets[2])
        # If we got none, we're screwed. So, just bail and return None.
        if temp_face[0] is None:
            return temp_face
        # Create a list for the face with the validation number at the zero index.
        face = [temp_face[0]]
        # Create a list with three elements that represent the csv columns used to properly place
        # the numbers on the bingo ticket. Single-number spots are placed in the zero element list
        # and double-number spots are placed at indexes one and two.
        lines = [[], [], []]
        # Cycle through the bingo spots
        for index, spot in enumerate(temp_face[1]):
            # If there's only one number, this is a single spot. Set the zero
            # element to the number and add blanks to the other columns.
            if len(spot) == 1:
                lines[0].append(spot[0])
                lines[1].append('')
                lines[2].append('')
            # If there are two numbers, this is a double spot. Add a blank to
            # the zero element and set the other columns to the number values.
            if len(spot) == 2:
                lines[0].append('')
                lines[1].append(spot[0])
                lines[2].append(spot[1])
        # Add the lines to the face and the face to the faces list.
        face.append(lines)
        faces.append(face)
        # Print info to console if desired.
        if verbose:
            print(f"{len(faces)}", end=" ")
            if len(faces) % 30 == 0:
                print('')
                print('      ', end='')
    # Return the faces list.
    return faces


def create_single_line_pseudo_either_or(face_list: BingoFaceList, frees: int,
                                        doubles: int) -> list[list[str | list[str]] | None]:
    """
    Creates a pseudo either-or bingo face sequence based on specified parameters.

    The function orchestrates the setup of a bingo face, ensuring that it complies with
    certain criteria such as free spaces, double spaces, and unique verification numbers.
    It alters the internal state of the given BingoFaceList and performs validation to
    prevent duplicated winning paths.

    :param face_list: Instance of BingoFaceList that holds and manages the bingo faces
        and paths taken.
    :type face_list: BingoFaceList
    :param frees: Number of free spaces to be included in the bingo face.
    :type frees: int
    :param doubles: Number of spots that will have two numbers.
    :type doubles: int

    :return: A list representing the final bingo face. The list contains two elements:
        1. A single integer string representing the bingo verification number.
        2. A list of lists where each inner list represents a bingo column and contains
           either a single number string, a double number string, or a blank (free) space.
    :rtype: list[list[str | list[str]] | None]
    """
    go_again = True
    final_face = None
    pop_first = True
    while go_again:
        faces = face_list.get_two_unique_paths_with_verification()
        go_again = False
        if faces is None or len(faces) < 2:
            return [None, "!!!!! ERROR: WE'VE RUN OUT OF BINGO FACES! !!!!!"]
        # noinspection PyTypeChecker
        # Transpose the two five-member lists into five two-number lists
        spots_list = matrix([faces[1], faces[2]]).transpose().tolist()
        if spots_list[0] is None:
            return spots_list

        # Create a list representing the indexes of the columns of the bingo face and shuffle it
        # a few times. This will be used to determine where to place either-or and free spots.
        spaces = list(range(5))
        for x in range(rn.randint(4, 10)):
            rn.shuffle(spaces)

        # Create a list of the spots that have two numbers by popping column indexes off of the spaces list.
        # This is really rather superfluous, since no change is effected on these columns. But I may, one day,
        # decide to do things differently and this will be in place.
        combo_spaces = []
        for x in range(doubles):
            combo_spaces.append(spaces.pop())

        # Create a list of the spots that will contain a free space by popping column indexes off the spaces list.
        # These columns will be replaced by lists containing every possible value for the spot, since any value
        # could be called and matched here. This is used to check for possible collisions with previously taken
        # winning paths.
        free_spaces = []
        for x in range(frees):
            free_spaces.append(spaces.pop())

        # The remaining spots will have only one number on them, so traverse the list of
        # spaces and use it as an index to remove the second number at those positions.
        for x in spaces:
            # popper = 1 if pop_first else 0
            spots_list[x].pop(1 if pop_first else 0)
            # spots_list[x].pop(popper)
            pop_first = not pop_first

        # Traverse the list of free space positions and replace the two-number list there with a list
        # of all fifteen possible numbers. This allows the product of the lists to account for every
        # possible winning combination and avoid duplicate winners.
        for x in free_spaces:
            bottom = x * 15
            spot = list(range(bottom + 1, bottom + 16))
            spots_list[x] = [str(s) for s in spot]

        # Use set mathematics to produce a list of possible winning combinations.
        # Cycle through the resulting list and check each value against those in
        # the paths_taken set. If a duplicate is found, chuck this face and try again.
        combos = set(iters.product(*spots_list))
        for combo in combos:
            if combo in face_list.paths_taken:
                go_again = True
                break

        # If there was a collision, don't go beyond this point! Start over, right flippin' now!!
        if go_again:
            continue

        # This face will be used, so add its winning paths to the paths_taken set.
        for combo in combos:
            face_list.paths_taken.add(combo)

        # Create the final faces list which contains two members: the first is a single integer string
        # representing the bingo verification number. The second is a list composed of five lists
        # representing the bingo columns. Those lists contain a single number string, a double number
        # string, or a blank (free) space. The construction is described below.
        final_face = [faces[0], []]
        for spots in spots_list:
            # Sort the list so the lowest number will be at the front.
            spots.sort(key=int)
            # If the length of the list in this position is greater than two, it
            # means this is a free spot. Add a list to final_faces that contains
            # a single blank string.
            if len(spots) > 2:
                final_face[1].append([''])
            # Otherwise, just add the list at this position to final_faces
            else:
                # noinspection PyTypeChecker
                final_face[1].append(spots)
    return final_face


def print_usable_face_info_to_screen(faces: BingoFaceList, size=0):
    """
    Prints detailed information about usable Bingo faces to the screen.

    This function prints the count of usable Bingo faces available in the given
    `faces` object. Additionally, it shows the remaining discrete bingo lines
    and the number of discrete winning paths taken. An optional `size` parameter
    can be provided to indent the printed information.

    :param faces: The list of BingoFace objects to evaluate.
    :type faces: BingoFaceList
    :param size: The indentation size for printed information.
    :type size: int
    :return: None
    """
    indent = ''
    for i in range(size):
        indent += '  '
    print(f"{indent}Usable faces array contains {faces.length()} members.")
    print(f"{indent}There are {faces.calculate_remaining_bingo_lines()} discrete bingo lines remaining.")
    print(f"{indent}{faces.number_of_paths_taken()} discrete winning paths have been taken.\n")


def create_all_bingo_permutations_without_reset(bingo_amts: list[list[int] | list[list[int]] | bool | str],
                                                perms, csv_rows: int, v_size=False,
                                                verbose=False) -> list[list[str | list[str]]] | None:
    """
    This method creates the total number of tickets needed for all permutations for each ticket specification based on
    the number of possible winning paths generated (by combining its free, double, and single spaces), before moving on
    to the next most-demanding ticket type. This differs from the traditional method of creating all the tickets for a
    given permutation before moving on to the next. Doing this makes it easier to find less demanding tickets as the
    method progresses and has been shown to provide a better chance of generating all the desired tickets.

    :param bingo_amts: list containing the number of bingo faces needed for each type of face: lines and free spaces
    :type bingo_amts: list[list[int] | | list[list[int]] | bool | str]
    :param perms: the number of permutations needed
    :type perms: int
    :param csv_rows: number of rows needed for the csv file
    :type csv_rows: int
    :param v_size: Should the standard or extended usable faces be read?
    :type v_size: bool
    :param verbose: should status info be printed to the screen
    :type verbose: bool
    :return list of info for bingo faces
    :rtype: list[list[str | list[str]]]
    """
    sloes = ['f2d2', 'f2d1', 'f1d2', 'f1d1', 'f0d2', 'f0d1', 'f0d3']
    # Create and shuffle a new list of usable faces
    face_list = BingoFaceList(v_size)
    face_list.shuffle_usable_faces()
    numbs = []
    for i in range(5):
        numbs.append(bingo_amts[i])

    # Break up the bingo requirements by type (single- or double-lines staggered or not, plus either-ors)
    [q_nonstaggered_double_holds, q_staggered_double_holds,
     q_nonstaggered_single_holds, q_staggered_single_holds, q_single_line_either_ors] = numbs
    if verbose:
        print_usable_face_info_to_screen(face_list)
        print(f"----------> Creating {perms} permutations without resetting the usable faces array. <----------")

    # Create lists to hold the faces for each type and add a sublist for each permutation.
    nonstaggered_double_holds = [[] for _ in range(perms)]
    staggered_double_holds = [[] for _ in range(perms)]
    nonstaggered_single_holds = [[] for _ in range(perms)]
    staggered_single_holds = [[] for _ in range(perms)]
    single_line_either_ors = [{} for _ in range(perms)]

    # Create a dictionary to hold faces for either/ors, using their parameters
    # to create the keys: an either/or with 1 free space and 2 either/or spots
    # would be referred to by the key 'sloef1d2'.
    q_either_ors = {}
    if q_single_line_either_ors[0][0] != 0:
        for sloe in q_single_line_either_ors:
            q_either_ors[f"sloef{sloe[1]}d{sloe[2]}"] = sloe

    # Create the permutations list and a list for each permutation. Also, create a list in each
    # for the number of possible free spots (0 - 3). The index represents the number of free spots,
    # and the list will contain all the tickets for that slot.
    permutations = []
    for i in range(perms):
        permutations.append([])
        nonstaggered_double_holds[i] = [[] for _ in range(4)]
        staggered_double_holds[i] = [[] for _ in range(4)]
        nonstaggered_single_holds[i] = [[] for _ in range(4)]
        staggered_single_holds[i] = [[] for _ in range(4)]
        for eeyore in q_either_ors:
            single_line_either_ors[i][eeyore] = []

    # BEGIN TICKET GENERATION (in order of the number of possible winning paths)
    # Two-line tickets with three-nonstaggered free spots (13500 winning paths)
    if q_nonstaggered_double_holds[3] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, double-line hold with three free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[3]} non-staggered, "
                      f"double-line holds with three free spaces.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_double_holds[3], 3, 2, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_double_holds[i][3].append(temp_list)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Two-line tickets with three-staggered free spots (13500 winning paths)
    if q_staggered_double_holds[3] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of staggered, double-line hold with three free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[3]} staggered, double-line "
                      f"holds with three free spaces.")
            temp_list = create_pseudo_faces(face_list, q_staggered_double_holds[3], 3, 2, csv_rows, True)
            if temp_list[0] is None:
                return temp_list
            staggered_double_holds[i][3].append(temp_list)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # One-line tickets with three-nonstaggered free spots (3375 winning paths)
    if q_nonstaggered_single_holds[3] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, single-line hold with three free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[3]} staggered, single-line "
                      f"tickets with three free spaces.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_single_holds[3],
                                            3, 1, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_single_holds[i][3].append(temp_list)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Two-line tickets with two-nonstaggered free spots (1800 winning paths)
    if q_nonstaggered_double_holds[2] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, double line hold with two free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[2]} non-staggered, double-line "
                      f"tickets with two free spaces.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_double_holds[2], 2, 2, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_double_holds[i][2].append(temp_list)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Two-line tickets with two-staggered free spots (1800 winning paths)
    if q_staggered_double_holds[2] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of staggered, double line hold with two free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[2]} staggered, double-line "
                      f"tickets with two free spaces.")
            temp_list = create_pseudo_faces(face_list, q_staggered_double_holds[2], 2, 2, csv_rows, True)
            if temp_list[0] is None:
                return temp_list
            staggered_double_holds[i][2].append(temp_list)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with two free spaces and two either/or spots (900 winning paths)
    if 'sloef2d2' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with two free and two either/or spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef2d2'][0]} single-line "
                      f"tickets with two free spaces and two either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef2d2'])
            if temp_list[0] is None:
                return temp_list
            single_line_either_ors[i]['sloef2d2'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with two free spaces and two either/or spots (450 winning paths)
    if 'sloef2d1' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with two free and one either/or space.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef2d1'][0]} single-line "
                      f"tickets with two free spaces and two either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef2d1'])
            if temp_list[0] is None:
                return temp_list
            single_line_either_ors[i]['sloef2d1'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Two-line tickets with one nonstaggered free spot (240 winning paths)
    if q_nonstaggered_double_holds[1] > 0:
        face_list.shuffle_usable_faces()
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, double line hold with one free space.")
        for i in range(perms):
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[1]} non-staggered, double-line "
                      f"tickets with one free space.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_double_holds[1], 1, 2, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_double_holds[i][1].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Two-line tickets with one staggered free spot (240 winning paths)
    if q_staggered_double_holds[1] > 0:
        face_list.shuffle_usable_faces()
        if verbose:
            print(f"  Creating {perms} permutations of staggered, double line hold with one free space.")
        for i in range(perms):
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[1]} non-staggered, double-line "
                      f"tickets with one free space.")
            temp_list = create_pseudo_faces(face_list, q_staggered_double_holds[1], 1, 2, csv_rows, True)
            if temp_list[0] is None:
                return temp_list
            staggered_double_holds[i][1].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line tickets with two-nonstaggered free spots (225 winning paths)
    if q_nonstaggered_single_holds[2] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of nonstaggered, single-line hold with two free space.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[2]} nonstaggered, single-line "
                      f"tickets with two free spaces.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_single_holds[2], 2, 1, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_single_holds[i][2].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line tickets with two staggered free spots (225 winning paths)
    if q_staggered_single_holds[2] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of staggered, single-line hold with two free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_single_holds[2]} staggered, single-line "
                      f"tickets with two free spaces.")
            temp_list = create_pseudo_faces(face_list, q_staggered_single_holds[2], 2, 1, csv_rows, True)
            if temp_list[0] is None:
                return temp_list
            staggered_single_holds[i][2].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Double-line tickets with no free spaces. (Nonstaggered, but that's irrelevant.) (32 winning paths)
    if q_nonstaggered_double_holds[0] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of nonstaggered, double-line hold with no free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[0]} nonstaggered, double-line "
                      f"tickets with no free spaces.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_double_holds[0], 0, 2, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_double_holds[i][0].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with one free space and two either/or spot (60 winning paths)
    if 'sloef1d2' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with one free and two either/or spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef1d2'][0]} single-line "
                      f"tickets with two free spaces and two either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef1d2'])
            if temp_list[0] is None:
                return temp_list
            single_line_either_ors[i]['sloef1d2'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Double-line tickets with no free spaces. (Staggered, but that's irrelevant.) (32 winning paths)
    if q_staggered_double_holds[0] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of staggered, double-line hold with no free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[0]} staggered, double-line "
                      f"tickets with no free spaces.")
            temp_list = create_pseudo_faces(face_list, q_staggered_double_holds[0], 0, 2, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            staggered_double_holds[i][0].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line tickets with one staggered free space. (15 winning paths)
    if q_staggered_single_holds[1] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of staggered, single-line hold with one free space.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_single_holds[1]} staggered, single-line "
                      f"tickets with one free space.")
            temp_list = create_pseudo_faces(face_list, q_staggered_single_holds[1],
                                            1, 1, csv_rows, True)
            if temp_list[0] is None:
                return temp_list
            staggered_single_holds[i][1].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line tickets with one nonstaggered free space. (15 winning paths)
    if q_nonstaggered_single_holds[1] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, single-line hold with one free space.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[1]} non-staggered, single-line "
                      f"tickets with one free space.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_single_holds[1], 1, 1, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_single_holds[i][1].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with one free space and one either/or spot (15 winning paths)
    if 'sloef1d1' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with one free and one either/or spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef1d1'][0]} single-line "
                      f"tickets with no free spaces and one either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef1d1'])
            if temp_list[0] is None:
                return temp_list
            single_line_either_ors[i]['sloef1d1'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with zero free spaces and three either/or spot (8 winning paths)
    if 'sloef0d3' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with zero free and two either/or spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef0d3'][0]} single-line "
                      f"tickets with no free spaces and one either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef0d3'])
            if temp_list[0] is None:
                return temp_list
            single_line_either_ors[i]['sloef0d3'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with zero free spaces and two either/or spot (4 winning paths)
    if 'sloef0d2' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with zero free and two either/or spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef0d2'][0]} single-line "
                      f"tickets with no free spaces and one either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef0d2'])
            if temp_list[0] is None:
                return temp_list
            single_line_either_ors[i]['sloef0d2'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line ticket with zero free spaces and one either/or spot (2 winning paths)
    if 'sloef0d1' in q_either_ors:
        if verbose:
            print(f"  Creating {perms} permutations of single-line hold with one free and one either/or spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef0d1'][0]} single-line "
                      f"tickets with no free spaces and one either-or spots.")
            temp_list = create_single_line_either_or_faces(face_list, q_either_ors['sloef0d1'])
            if temp_list is None:
                return temp_list
            single_line_either_ors[i]['sloef0d1'] = temp_list
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line nonstaggered tickets with no free spaces. (1 winning path)
    if q_nonstaggered_single_holds[0] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, single-line hold with no free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[0]} non-staggered, single-line "
                      f"tickets with one free space.")
            temp_list = create_pseudo_faces(face_list, q_nonstaggered_single_holds[0], 0, 1, csv_rows, False)
            if temp_list[0] is None:
                return temp_list
            nonstaggered_single_holds[i][0].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    # Single-line staggered tickets with no free spaces. (1 winning path)
    if q_staggered_single_holds[0] > 0:
        if verbose:
            print(f"  Creating {perms} permutations of non-staggered, single-line hold with no free spaces.")
        for i in range(perms):
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_single_holds[0]} non-staggered, single-line "
                      f"tickets with one free space.")
            temp_list = create_pseudo_faces(face_list, q_staggered_single_holds[0], 0, 1, csv_rows, True)
            if temp_list[0] is None:
                return temp_list
            staggered_single_holds[i][0].append(temp_list)
            if verbose:
                print('  Done.')
                print_usable_face_info_to_screen(face_list, 2)
        if verbose:
            print('  Done.')

    for i in range(perms):
        for sloe in sloes:
            if f'sloe{sloe}' in single_line_either_ors[i].keys():
                for ticket in single_line_either_ors[i][f'sloe{sloe}']:
                    permutations[i].append(ticket)

        nonstaggered_double_holds[i].reverse()
        for frees in nonstaggered_double_holds[i]:
            for free in frees:
                for ticket in free:
                    permutations[i].append(ticket)

        staggered_double_holds[i].reverse()
        for frees in staggered_double_holds[i]:
            for free in frees:
                for ticket in free:
                    permutations[i].append(ticket)

        nonstaggered_single_holds[i].reverse()
        for frees in nonstaggered_single_holds[i]:
            for free in frees:
                for ticket in free:
                    permutations[i].append(ticket)

        staggered_single_holds[i].reverse()
        for frees in staggered_single_holds[i]:
            for free in frees:
                for ticket in free:
                    permutations[i].append(ticket)

    if verbose:
        print('Done.')
    return permutations


def create_all_bingo_permutations_with_reset(bingo_amts: list[list[int] | bool | str],
                                             perms: int, csv_rows: int, v_size=False, verbose=False):
    """
    This method creates each permutation of bingo numbers in its entirety and resets the usable faces list for
    successive iterations. It creates the bingo faces in order of the greatest number of possible winning paths.

    :param bingo_amts: list containing the number of bingo faces for each type of face: lines and free spaces
    :type bingo_amts: list[list[int] | bool | str]
    :param perms: the number of permutations needed
    :type perms: int
    :param csv_rows: number of rows needed for the csv file
    :type csv_rows: int
    :param v_size: Should the standard or extended usable faces be read?
    :type v_size: bool
    :param verbose: should status info be printed to the screen
    :type verbose: bool
    """
    # Create a list to hold the permutations
    permutations = []
    for i in range(perms):
        permutations.append([])

    # I'LL PROBABLY TAKE THIS OUT. I'M JUST PARANOID. ----------------------------------------------------------------
    # Take the first five
    # numbs = []
    # for i in range(5):
    #     numbs.append(bingo_amts[i])
    # Break up the bingo requirements by type (single- or double-lines staggered or not, plus either-ors)
    # [q_nonstaggered_double_holds, q_staggered_double_holds,
    #  q_nonstaggered_single_holds, q_staggered_single_holds, q_single_line_either_ors] = numbs
    # ----------------------------------------------------------------------------------------------------------------

    # Break up the bingo requirements by type (single- or double-lines staggered or not, plus either-ors)
    [q_nonstaggered_double_holds, q_staggered_double_holds,
     q_nonstaggered_single_holds, q_staggered_single_holds, q_single_line_either_ors] = bingo_amts
    # Create a dictionary to hold faces for either/ors, using their parameters
    # to create the keys: an either/or with 1 free space and 2 either/or spots
    # would be referred to by the key 'sloef1d2'.
    q_either_ors = {}
    if q_single_line_either_ors[0][0] != 0:
        for sloe in q_single_line_either_ors:
            q_either_ors[f"sloef{sloe[1]}d{sloe[2]}"] = sloe

    if verbose:
        print(f"==========> Creating {perms} permutations resetting the usable faces array for each one. <==========")

    # Create the faces needed for each permutation, resetting the faces list with each iteration. Call
    # create_pseudo_faces for regular bingos and create_single_line_either_or_faces for either/or tickets.
    for i in range(perms):
        if verbose:
            print(f"  Creating PERMUTATION #{i + 1}")
            print("    Creating and shuffling usable faces list.")
        # Create a new list of bingo faces.
        face_list = BingoFaceList(v_size)
        face_list.shuffle_usable_faces()
        if verbose:
            print_usable_face_info_to_screen(face_list, 2)

        # Two-line tickets with three nonstaggered free spots (13,500) (let's hope it never happens)
        if q_nonstaggered_double_holds[3] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[3]} non-staggered, double-line "
                      "tickets with three free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_double_holds[3],
                                                   3, 2, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Two-line tickets with three staggered free spots (13,500)
        if q_staggered_double_holds[3] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[3]} staggered, double-line "
                      "tickets with three free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_double_holds[3],
                                                   3, 2, csv_rows, True)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # One-line tickets with three nonstaggered free spots (3375 winning paths)
        if q_nonstaggered_single_holds[3] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[3]} non-staggered, double-line "
                      f"tickets with three free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_single_holds[3],
                                                   3, 1, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Two-line tickets with two-nonstaggered free spots (1800 winning paths)
        if q_nonstaggered_double_holds[2] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[2]} non-staggered, double-line "
                      f"tickets with two free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_double_holds[2],
                                                   2, 2, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Two-line tickets with two-staggered free spots (1800 winning paths)
        if q_staggered_double_holds[2] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[2]} staggered, double-line "
                      f"tickets with two free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_double_holds[2],
                                                   2, 2, csv_rows, True)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with two free spaces and two either/or spots (900 winning paths)
        if 'sloef2d2' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef2d2'][0]} single-line "
                      f"tickets with two free spaces and two either-or spots.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef2d2'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with two free spaces and one either/or spot (450 winning paths)
        if 'sloef2d1' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef2d1'][0]} single-line "
                      f"tickets with two free spaces and one either-or spot.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef2d1'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Two-line tickets with one nonstaggered free spot (240 winning paths)
        if q_nonstaggered_double_holds[1] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[1]} non-staggered, double-line "
                      f"tickets with one free space.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_double_holds[1],
                                                   1, 2, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Two-line tickets with one staggered free spot (240 winning paths)
        if q_staggered_double_holds[1] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[1]} non-staggered, double-line "
                      f"tickets with one free space.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_double_holds[1],
                                                   1, 2, csv_rows, True)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line tickets with two staggered free spots (225 winning paths)
        if q_staggered_single_holds[2] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_single_holds[2]} staggered, single-line "
                      f"tickets with two free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_single_holds[2],
                                                   2, 1, csv_rows, True)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line tickets with two-nonstaggered free spots (225 winning paths)
        if q_nonstaggered_single_holds[2] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[2]} nonstaggered, single-line "
                      f"tickets with two free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_single_holds[2],
                                                   2, 1, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with one free space2 and two either/or spots (60 winning paths)
        if 'sloef1d2' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef1d2'][0]} single-line "
                      f"tickets with two free spaces and one either-or spot.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef1d2'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Double-line tickets with no free spaces. (Nonstaggered, but that's irrelevant.) (32 winning paths)
        if q_nonstaggered_double_holds[0] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_double_holds[0]} nonstaggered, double-line "
                      f"tickets with no free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_double_holds[0],
                                                   0, 2, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Double-line tickets with no free spaces. (Staggered, but that's irrelevant.) (32 winning paths)
        if q_staggered_double_holds[0] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_double_holds[0]} staggered, double-line "
                      f"tickets with no free spaces.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_double_holds[0],
                                                   0, 2, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with one free space and one either/or spot (15 winning paths)
        if 'sloef1d1' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef1d1'][0]} single-line "
                      f"tickets with one free space and one either-or spot.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef1d1'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line tickets with one staggered free space. (15 winning paths)
        if q_staggered_single_holds[1] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_single_holds[1]} staggered, single-line "
                      f"tickets with one free space.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_single_holds[1],
                                                   1, 1, csv_rows, True)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line tickets with one nonstaggered free space. (15 winning paths)
        if q_nonstaggered_single_holds[1] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[1]} non-staggered, single-line "
                      f"tickets with one free space.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_single_holds[1],
                                                   1, 1, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with no free spaces and three either/or spots (8 winning paths)
        if 'sloef0d3' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef0d3'][0]} single-line "
                      f"tickets with no free space spaces and two either-or spots.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef0d3'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with no free spaces and two either/or spots (4 winning paths)
        if 'sloef0d2' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef0d2'][0]} single-line "
                      f"tickets with no free space spaces and two either-or spots.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef0d2'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line ticket with no free spaces and one either/or spot (2 winning paths)
        if 'sloef0d1' in q_either_ors:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_either_ors['sloef0d1'][0]} single-line "
                      f"tickets with no free space spaces and one either-or spot.")
            permutations[i] += create_single_line_either_or_faces(face_list, q_either_ors['sloef0d1'])
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line nonstaggered tickets with no free spaces. (1 winning path)
        if q_nonstaggered_single_holds[0] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_nonstaggered_single_holds[0]} non-staggered, single-line "
                      f"tickets with one free space.")
            permutations[i] += create_pseudo_faces(face_list, q_nonstaggered_single_holds[0],
                                                   0, 1, csv_rows, False)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        # Single-line staggered tickets with no free spaces. (1 winning path)
        if q_staggered_single_holds[0] > 0:
            face_list.shuffle_usable_faces()
            if verbose:
                print(f"    Permutation #{i + 1}: Creating {q_staggered_single_holds[0]} non-staggered, single-line "
                      f"tickets with one free space.")
            permutations[i] += create_pseudo_faces(face_list, q_staggered_single_holds[0],
                                                   0, 1, csv_rows, True)
            if verbose:
                print('    Done.')
                print_usable_face_info_to_screen(face_list, 2)

        print('  Done.')
    print('Done.')
    return permutations
