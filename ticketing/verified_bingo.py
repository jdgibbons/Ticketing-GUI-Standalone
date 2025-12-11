import itertools as iters

from numpy import matrix
import random as rn

from .bingo_face_list import BingoFaceList

total_rejects = 0


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
    global total_rejects
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
    total_rejects += d_rejects
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
    global total_rejects
    indent = ''
    for i in range(size):
        indent += '  '
    print(f"{indent}Usable faces array contains {faces.length()} members.")
    print(f"{indent}There are {faces.calculate_remaining_bingo_lines()} discrete bingo lines remaining.")
    print(f"{indent}{faces.number_of_paths_taken()} discrete winning paths have been taken.")
    print(f"{indent}{total_rejects} faces have been rejected due to duplicate winning paths.\n")


def create_all_bingo_permutations_without_reset(bingo_amts: list, perms: int, csv_rows: int,
                                                v_size=False, verbose=False) -> list:
    """
    Generates bingo permutations WITHOUT resetting the face list.

    CONCEPT:
    We have a single 'deck' of bingo faces (usable9000.csv). We must generate
    multiple permutations of tickets without ever reusing a face across ANY
    permutation.

    STRATEGY:
    1. Organize tickets by complexity (Highest winning paths -> Lowest).
    2. Generate the specific ticket type for ALL permutations at once.
    3. Store them in temporary bins.
    4. Flatten the bins into the final list at the end.
    """
    global total_rejects

    # --- 1. SETUP & INITIALIZATION ---

    # Initialize the face list OUTSIDE the main loop.
    # This state persists for the entire function execution.
    # Once a face is used, it is gone forever.
    face_list = BingoFaceList(v_size)
    face_list.shuffle_usable_faces()

    # List Unpacking:
    # 'bingo_amts' contains 5 sub-lists. We unpack them into named variables for clarity.
    # Example: q_ns_double might be [90, 25, 10, 5] meaning:
    # 90 tickets with 0 free spaces, 25 with 1 free, 10 with 2 free, etc.
    [q_ns_double, q_stag_double, q_ns_single, q_stag_single, q_sloe] = bingo_amts[0:5]

    if verbose:
        print_usable_face_info_to_screen(face_list)
        print(f"----------> Creating {perms} perms without resetting faces. <----------")

    # --- 2. STORAGE BINS (The "Buckets") ---

    # We need a place to hold the tickets before we organize them.
    # Since we generate "All Permutation 1 Double-Lines", then "All Permutation 2 Double-Lines",
    # we need complex storage to keep them sorted until the end.

    # This creates a list of empty lists, one for each permutation.
    permutations = [[] for _ in range(perms)]

    # 3D List Construction for Standard Tickets:
    # Structure: [Permutation_Index] -> [Free_Space_Count_Index] -> [List_Of_Tickets]
    # We need this because we need to know exactly where to put a ticket based on
    # which permutation it belongs to and how many free spaces it has.
    # We use list comprehensions to instantiate fresh lists for every slot.
    ns_double_holds = [[[] for _ in range(4)] for _ in range(perms)]
    stag_double_holds = [[[] for _ in range(4)] for _ in range(perms)]
    ns_single_holds = [[[] for _ in range(4)] for _ in range(perms)]
    stag_single_holds = [[[] for _ in range(4)] for _ in range(perms)]

    # Dictionary Storage for Either-Or Tickets.
    # Structure: [Permutation_Index][Key_String] -> List_of_Tickets
    sloe_holds = [{} for _ in range(perms)]
    q_either_ors = {}

    # Pre-calculate the Either-Or keys.
    # Example Key: "sloef2d2" (Single Line, Either-Or, Free:2, Doubles:2)
    if q_sloe and q_sloe[0][0] != 0:
        for sloe in q_sloe:
            # sloe structure is [Quantity, Frees, Doubles]
            key = f"sloef{sloe[1]}d{sloe[2]}"
            q_either_ors[key] = sloe
            # Initialize the list for this key in every permutation bucket
            for i in range(perms):
                sloe_holds[i][key] = []

    # --- 3. THE PROCESSING QUEUE (The "Work Order") ---

    # CRITICAL: Resource Management --> Processing Order Matters!
    # We have a finite number of bingo lines. Tickets with the highest number of possible winning
    # paths must be processed first. This means that tickets with free or double spaces will have
    # higher priority than tickets with only single spaces, since free spots are the equivalent of
    # having all 15 possible values in that position. The possibility of finding a ticket with that
    # many winning paths becomes more remote as tickets are added to the list.

    # There are some situations that with eithe/or tickets that should never be processed. Any
    # ticket that doesn't contain both single and double spaces should be handled by one of the
    # single or double, staggered or non-staggered tiers. I'm not checking for it yet, but I will
    # add it in the future.

    # TUPLE FORMAT:
    # ('STD', Storage_Ref, Exact_Qty_Integer, Free_Spaces, Lines, Staggered_Bool, Description)
    # ('SLOE', Exact_Qty_Integer, Key_String, Description)

    # The index of the quantity lists indicates the number of free spaces, so we can use it to
    # determine which tier to process this ticket in. We then pass the value at that index to the
    # factory function to generate the tickets.
    processing_queue = [
        # --- TIER 1: Double-Line, 3 Free Spaces (13,500 winning paths) ---
        # Note: 'q_ns_double[3]' extracts the specific integer count needed for 3 free spaces.
        # We pass the integer, not the list, to the loop.
        ('STD', ns_double_holds, q_ns_double[3], 3, 2, False, "non-staggered double"),
        ('STD', stag_double_holds, q_stag_double[3], 3, 2, True, "staggered double"),

        # --- TIER 2: Single-Line, 3 Free Spaces (3,375 winning paths) ---
        ('STD', ns_single_holds, q_ns_single[3], 3, 1, False, "non-staggered single"),
        ('STD', stag_single_holds, q_stag_single[3], 3, 1, True, "staggered single"),

        # --- TIER 3: Double-Line, 2 Free Spaces (1,800 winning paths) ---
        ('STD', ns_double_holds, q_ns_double[2], 2, 2, False, "non-staggered double"),
        ('STD', stag_double_holds, q_stag_double[2], 2, 2, True, "staggered double"),

        # TUPLE FORMAT FOR SLOE (Either-Or):
        # ('SLOE', Quantity_Integer, Key_String, Description)

        # --- TIER 4: Interleaved Either-Ors, 2 frees; 2 doubles (900 winning paths) ---
        ('SLOE', q_either_ors.get('sloef2d2', [0])[0], 'sloef2d2', "2 free, 2 either-or"),

        # --- TIER 5: Interleaved Either-Ors, 2 frees; 1 double (450 winning paths) ---
        ('SLOE', q_either_ors.get('sloef2d1', [0])[0], 'sloef2d1', "2 free, 1 either-or"),

        # --- TIER 6: Double-Line, 1 Free Space (240 winning paths) ---
        ('STD', ns_double_holds, q_ns_double[1], 1, 2, False, "non-staggered double"),
        ('STD', stag_double_holds, q_stag_double[1], 1, 2, True, "staggered double"),

        # --- TIER 7: Single-Line, 2 Free Spaces (225 winning paths) ---
        ('STD', ns_single_holds, q_ns_single[2], 2, 1, False, "non-staggered single"),
        ('STD', stag_single_holds, q_stag_single[2], 2, 1, True, "staggered single"),  # Single line, 2 frees

        # --- TIER 8: Interleaved Either-Ors, 1 free, 2 doubles (60 winning paths) ---
        ('SLOE', q_either_ors.get('sloef1d2', [0])[0], 'sloef1d2', "1 free, 2 either-or"),

        # --- TIER 9: Double-Line, 0 Free Spaces (32 winning paths) ---
        ('STD', ns_double_holds, q_ns_double[0], 0, 2, False, "non-staggered double"),
        ('STD', stag_double_holds, q_stag_double[0], 0, 2, True, "staggered double"),

        # --- TIER 10: Interleaved Either-Ors, 1 free, 1 double (30 winning paths) ---
        ('SLOE', q_either_ors.get('sloef1d1', [0])[0], 'sloef1d1', "1 free, 1 either-or"),

        # --- TIER 11: Single-Line, 1 Free Space (15 winning paths) ---
        ('STD', stag_single_holds, q_stag_single[1], 1, 1, True, "staggered single"),  # Single line, 1 free
        ('STD', ns_single_holds, q_ns_single[1], 1, 1, False, "non-staggered single"),  # Single line, 1 free

        # --- TIER 12: Interleaved Either-Ors, 0 frees, 3 doubles (8 winning paths) ---
        ('SLOE', q_either_ors.get('sloef0d3', [0])[0], 'sloef0d3', "0 free, 3 either-or"),

        # --- TIER 13: Interleaved Either-Ors, 0 frees, 2 doubles (4 winning paths) ---
        ('SLOE', q_either_ors.get('sloef0d2', [0])[0], 'sloef0d2', "0 free, 2 either-or"),

        # --- TIER 14: Interleaved Either-Ors, 0 frees, 1 double (2 winning paths) ---
        ('SLOE', q_either_ors.get('sloef0d1', [0])[0], 'sloef0d1', "0 free, 1 either-or"),

        # --- TIER 15: Single-Line, 0 Free Spaces (1 winning path) ---
        ('STD', ns_single_holds, q_ns_single[0], 0, 1, False, "non-staggered single"),
        ('STD', stag_single_holds, q_stag_single[0], 0, 1, True, "staggered single"),
    ]

    # --- 4. THE EXECUTION ENGINE ---

    # We iterate through the job queue. Each 'job' represents a specific ticket type.
    for job in processing_queue:
        job_type = job[0]  # Identifies if this is 'STD' or 'SLOE'

        # === HANDLER FOR STANDARD TICKETS ===
        if job_type == 'STD':
            # Unpack the tuple. 'target_store' is a reference to one of our big lists (e.g. ns_double_holds).
            # 'qty_needed' is the value we extracted from the config list earlier.
            _, target_store, qty_needed, free_space_idx, lines, staggered, desc = job

            # Since qty_needed is an explicit integer (e.g., 90, 25, 5), we use it directly.
            if qty_needed > 0:
                if verbose:
                    print(f"  Creating {perms} permutations of {desc} with {free_space_idx} free spaces.")

                # Inner Loop: We must generate this specific ticket type for *every* permutation
                # before moving to the next ticket type in the queue.
                for i in range(perms):
                    face_list.shuffle_usable_faces()
                    if verbose: print(f"    Perm #{i + 1}: Creating {qty_needed} tickets.")

                    # Call the Factory Function to get new faces
                    temp_list = create_pseudo_faces(face_list, qty_needed, free_space_idx, lines, csv_rows, staggered)

                    # Error Handling: The factory returns [None, ErrorMsg] if it runs out of faces.
                    if temp_list[0] is None:
                        return temp_list

                    # Storage:
                    # We access the specific bucket: [Permutation_i] -> [Free_Space_Count]
                    target_store[i][free_space_idx].append(temp_list)

                    if verbose:
                        print('    Done.')
                        print_usable_face_info_to_screen(face_list, 2)
                if verbose: print('  Done.')

        # === HANDLER FOR EITHER-OR TICKETS ===
        elif job_type == 'SLOE':
            # Handle Either-Or tickets (Same logic, different factory function)
            _, qty_needed, key, desc = job

            # Check if the quantity needed is greater than 0 and the key exists in the dictionary.
            # I have no reason to believe that this will ever be false, but just in case ...
            if qty_needed > 0 and key in q_either_ors:
                params = q_either_ors[key]  # [qty, frees, doubles]

                if verbose:
                    print(f"  Creating {perms} permutations of {desc}.")

                # Inner Loop: We must generate this specific ticket type for *every* permutation
                # before moving to the next ticket type in the queue.
                for i in range(perms):
                    face_list.shuffle_usable_faces()
                    if verbose:
                        print(f"    Perm #{i + 1}: Creating {qty_needed} tickets.")

                    # Call the Factory Function to get new faces
                    temp_list = create_single_line_either_or_faces(face_list, params)

                    if temp_list[0] is None: return temp_list

                    # Storage: Use the dictionary key to access the specific bucket: [Permutation_i] -> [Key]
                    sloe_holds[i][key] = temp_list

                    if verbose:
                        print('    Done.')
                        print_usable_face_info_to_screen(face_list, 2)
                if verbose: print('  Done.')

    # --- 5. FLATTEN RESULTS ---
    # At this point, our tickets are scattered across 'ns_double_holds', 'sloe_holds', etc.
    # We need to gather them all into the single 'permutations' list, respecting the
    # specific export order (usually the greatest number of free spaces first).
    for i in range(perms):
        # 1. Flatten Either-Ors
        sloe_keys = ['sloef2d2', 'sloef2d1', 'sloef1d2', 'sloef1d1', 'sloef0d3', 'sloef0d2', 'sloef0d1']
        for key in sloe_keys:
            if key in sloe_holds[i] and sloe_holds[i][key]:
                permutations[i].extend(sloe_holds[i][key])

        # 2. Flatten Standard Tickets
        # We group the storage lists...
        groups = [ns_double_holds[i], stag_double_holds[i], ns_single_holds[i], stag_single_holds[i]]
        for group in groups:
            # ...and iterate them in Reverse.
            # 'group' contains [[0_free], [1_free], [2_free], [3_free]].
            # reversed() ensures we add the 3-free tickets to the final list before the 0-free tickets.
            for free_space_list in reversed(group):
                for batch in free_space_list:
                    permutations[i].extend(batch)

    if verbose: print('Done.')
    total_rejects = 0
    return permutations


def create_all_bingo_permutations_with_reset(bingo_amts: list, perms: int, csv_rows: int,
                                             v_size=False, verbose=False) -> list:
    """
    Generates permutations WITH a reset of the face list.

    CONCEPT:
    Unlike the previous function, this method treats every permutation as a fresh start.
    Faces used in Permutation 1 ARE allowed to be used again in Permutation 2.

    STRATEGY:
    1. Loop through Permutations (1 to N).
    2. Inside the loop, create a fresh 'BingoFaceList'.
    3. Process the ticket queue for that permutation immediately.
    4. Store results directly (no complex bins needed).
    """
    global total_rejects

    # --- 1. SETUP ---

    # Unpack the config lists.
    [q_ns_double, q_stag_double, q_ns_single, q_stag_single, q_sloe] = bingo_amts[0:5]

    if verbose:
        print(f"==========> Creating {perms} perms WITH RESET. <==========")

    # Simplified Storage:
    # Since we build Permutation 1 start-to-finish, we don't need the 3D storage arrays.
    # We just need a list of lists: [Permutation_1_Tickets, Permutation_2_Tickets, ...]
    permutations = [[] for _ in range(perms)]

    # Setup Either-Or keys for lookup
    # Example Key: "sloef2d2" (Single Line, Either-Or, Free:2, Doubles:2)
    q_either_ors = {}
    if q_sloe and q_sloe[0][0] != 0:
        for sloe in q_sloe:
            key = f"sloef{sloe[1]}d{sloe[2]}"
            q_either_ors[key] = sloe

    # --- 2. THE PROCESSING QUEUE ---
    # Matches the 'Without Reset' queue exactly. We prioritize tickets with high-winning
    # path counts (complexity) first to ensure we don't run out of valid bingo faces.
    #
    # Note: Even though we use the same processing order as seen in the previous method, we
    # don't have to create the tickets for all permutations at every level of complexity.
    # This is because the usable face list is reset for every permutation, so we can
    # simply create the tickets for each level of complexity for the current permutation.
    # The next permutation will have a fresh usable face list. This is generally done in
    # cases where the different ups of a game will never be played at the same time, which
    # eliminates the need to prevent winning paths from being reused across permutations.
    #
    # FORMAT CHANGE:
    # Notice we removed 'Storage_Ref' from the Standard tuple. We don't need to know *where*
    # to store it, as all tickets are stored in the list for the current permutation.
    processing_queue = [
        # === 13,500 Winning Paths ===
        ('STD', q_ns_double[3], 3, 2, False, "non-staggered double (3 free)"),
        ('STD', q_stag_double[3], 3, 2, True, "staggered double (3 free)"),

        # === 3,375 Winning Paths ===
        ('STD', q_ns_single[3], 3, 1, False, "non-staggered single (3 free)"),

        # === 1,800 Winning Paths ===
        ('STD', q_ns_double[2], 2, 2, False, "non-staggered double (2 free)"),
        ('STD', q_stag_double[2], 2, 2, True, "staggered double (2 free)"),

        # === 900 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef2d2', [0])[0], 'sloef2d2', "2 free, 2 either-or"),

        # === 450 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef2d1', [0])[0], 'sloef2d1', "2 free, 1 either-or"),

        # === 240 Winning Paths ===
        # Note: These have 1 Free Space, but are MORE complex than Single lines with 2 Free Spaces
        ('STD', q_ns_double[1], 1, 2, False, "non-staggered double (1 free)"),
        ('STD', q_stag_double[1], 1, 2, True, "staggered double (1 free)"),

        # === 225 Winning Paths ===
        ('STD', q_ns_single[2], 2, 1, False, "non-staggered single (2 free)"),
        ('STD', q_stag_single[2], 2, 1, True, "staggered single (2 free)"),

        # === 60 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef1d2', [0])[0], 'sloef1d2', "1 free, 2 either-or"),

        # === 32 Winning Paths ===
        ('STD', q_ns_double[0], 0, 2, False, "non-staggered double (0 free)"),
        ('STD', q_stag_double[0], 0, 2, True, "staggered double (0 free)"),

        # === 30 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef1d1', [0])[0], 'sloef1d1', "1 free, 1 either-or"),

        # === 15 Winning Paths ===
        ('STD', q_stag_single[1], 1, 1, True, "staggered single (1 free)"),
        ('STD', q_ns_single[1], 1, 1, False, "non-staggered single (1 free)"),

        # === 8 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef0d3', [0])[0], 'sloef0d3', "0 free, 3 either-or"),

        # === 4 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef0d2', [0])[0], 'sloef0d2', "0 free, 2 either-or"),

        # === 2 Winning Paths ===
        ('SLOE', q_either_ors.get('sloef0d1', [0])[0], 'sloef0d1', "0 free, 1 either-or"),

        # === 1 Winning Path ===
        ('STD', q_ns_single[0], 0, 1, False, "non-staggered single (0 free)"),
        ('STD', q_stag_single[0], 0, 1, True, "staggered single (0 free)"),
    ]

    # --- 3. THE EXECUTION LOOP (Inverted Logic) ---

    # OUTER LOOP: We iterate through Permutations (1 to N).
    # This is the opposite of the previous function.
    for i in range(perms):
        if verbose:
            print(f"  Creating PERMUTATION #{i + 1}")

        # CRITICAL RESET STEP:
        # We instantiate 'BingoFaceList' INSIDE the loop.
        # This reloads the CSV and creates a fresh deck of faces.
        face_list = BingoFaceList(v_size)
        face_list.shuffle_usable_faces()

        if verbose:
            print_usable_face_info_to_screen(face_list, 2)

        # INNER LOOP: Process the entire Job Queue for THIS permutation.
        for job in processing_queue:
            job_type = job[0]

            # === HANDLER FOR STANDARD TICKETS ===
            if job_type == 'STD':
                # Unpack without 'target_store'
                _, qty_needed, frees, lines, staggered, desc = job

                if qty_needed > 0:
                    if verbose:
                        print(f"    Perm #{i + 1}: Creating {qty_needed} {desc}.")

                    # Call the Factory Function to get new faces
                    temp_list = create_pseudo_faces(face_list, qty_needed, frees, lines, csv_rows, staggered)

                    # Fail fast on error
                    if temp_list[0] is None:
                        return temp_list

                    # Direct Append:
                    # We add the generated tickets immediately to the current permutation list.
                    permutations[i].extend(temp_list)

                    if verbose:
                        print('    Done.')
                        print_usable_face_info_to_screen(face_list, 2)

            # === HANDLER FOR EITHER-OR TICKETS ===
            elif job_type == 'SLOE':
                _, qty_needed, key, desc = job

                if qty_needed > 0 and key in q_either_ors:
                    params = q_either_ors[key]

                    if verbose:
                        print(f"    Perm #{i + 1}: Creating {qty_needed} {desc}.")

                    # Call the Factory Function to get new faces
                    temp_list = create_single_line_either_or_faces(face_list, params)

                    # Fail fast on error
                    if temp_list[0] is None:
                        return temp_list

                    # Direct Append:
                    # We add the generated tickets immediately to the current permutation list.
                    permutations[i].extend(temp_list)

                    if verbose:
                        print('    Done.')
                        print_usable_face_info_to_screen(face_list, 2)

        if verbose:
            print('  Permutation Done.')

    if verbose:
        print('Done.')
    total_rejects = 0
    return permutations
