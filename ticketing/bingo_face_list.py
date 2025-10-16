import csv
import random as rn
from typing import Set, Tuple, Any

from numpy import matrix
from itertools import product
from itertools import cycle
from itertools import permutations
import time


from .full_bingo_face import FullBingoFace

spots = [0, 1, 2, 3, 4]

spots_distribution = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]]


class BingoFaceList(object):
    """
    This class holds the available bingo faces imported from an industry-standardized list.
    The list contains instances of the FullBingoFace class, each comprised of the verification
    (face) number and its associated winning bingo lines. There are two different files available:
    the standard file containing 9,000 faces, and an extended file that contains an additional
    18,000 faces. (The csvs may appear incomplete on inspection, but there were duplicate lines
    and faces throughout, and I was obliged to remove them.)

    All list-based methods are implemented in this class.
    """

    def __init__(self, extended: bool = False):
        """
        Represents a container for managing usable faces and paths in a system.

        Usable faces are those generated from the industry-standardized face list; paths taken are the possible winning
        paths that result from combining every achievable bingo combination from a given face; path replacements are
        the five ranges of numbers for each bingo letter; and d_discards are the number of faces that have been
        thrown out when there aren't enough paths remaining.

        :ivar usable_faces: List of faces that can be used in the system.
        :ivar paths_taken: Set of paths that have been traversed.
        :ivar path_replacements: List of replacements for paths.
        :ivar d_discards: Counter for discarded paths.

        :param extended: Whether to use the extended, usable-faces list. Defaults to False.
        :type extended: bool
        """
        self.usable_faces = []
        self.paths_taken = set()
        self.import_usable_faces(extended)
        self.path_replacements = []
        self.populate_path_replacements()
        self.d_discards = 0
        self.debug = False

    def import_usable_faces(self, extended: bool = False, reset_paths_taken: bool = False) -> None:
        """
        Imports usable faces from the correct CSV file, then processes and appends them to a list.
        Optionally resets paths taken if the permutations will not be played together.

        :param extended: Specifies whether to use an extended set of faces. If True,
                         use 'usable27000.csv'. Otherwise, use 'usable9000.csv'.
        :type extended: bool
        :param reset_paths_taken: If True, clears the paths_taken list after processing faces.
        :type reset_paths_taken: bool
        :return: None
        :rtype: None
        """
        self.usable_faces = []
        filename = 'usable9000.csv' if not extended else 'usable27000.csv'
        # Open usable quotes file for reading
        file = open(f'./ticketing/{filename}', 'r')
        lines = file.readlines()
        temp_face = ''
        previous_line_id = ''
        # Cycle through each line of the file
        for line in lines:
            # Split the line into a list. The first element contains the face id plus the
            # location of the line on that face (i.e., 10.1 represents face 10, line 1).
            # The face id is the only value we care about. The remaining elements represent
            # the five bingo spots.
            temp_array = line.strip().split(',')
            temp_id = temp_array.pop(0).split('.')[0].replace('"', '')
            # Check if this bingo line belongs to the same face as the previous line.
            # If it does, add the line to the current face. Otherwise, create a new
            # face with the new id and current line.
            if temp_id != previous_line_id:
                # Update the previous line id to the new id
                previous_line_id = temp_id
                # If this isn't the very first iteration and there are more than two
                # lines on the previous face, append it to the list of usable faces.
                if temp_face != '' and temp_face.number_of_paths() >= 2:
                    temp_face.shuffle_paths()
                    self.usable_faces.append(temp_face)
                # This is a whole new face, so create it already.
                temp_face = FullBingoFace(temp_id, temp_array)
            else:
                temp_face.add_path(temp_array)
        if reset_paths_taken:
            self.paths_taken.clear()

    def shuffle_usable_faces(self) -> None:
        """
        Shuffle the usable face list between 4 and 25 times.
        :return None
        :rtype: None
        """
        shuffles = rn.randint(4, 25)
        for x in range(shuffles):
            rn.shuffle(self.usable_faces)

    def populate_path_replacements(self) -> None:
        """
        Fill the path replacements list with five lists of bingo numbers that encompass every possible
        value on a bingo card:\n
         [['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'], \n
         ['16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30'], \n
         ['31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45'], \n
         ['46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60'], \n
         ['61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75']]

        :return None
        :rtype: None
        """
        # Cycle through the bingo positions
        for index in range(5):
            path = []
            # Cycle through each
            for value in range(1, 16):
                path.append(f"{((index * 15) + value)}")
            self.path_replacements.append(path)

    def paths_collision_free(self, combos: set[list[str]] | set[tuple[str]]) -> bool:
        """
        Check if the passed bingo paths contain any collisions with previously used paths.

        :param combos: set of all paths to be checked
        :type combos: set[list[str]] or set[tuple[str]]
        :return: True if no collisions are found; false if one is found.
        :rtype: bool
        """
        # Cycle through the passed paths
        for combo in combos:
            # If a path is already present in the paths-taken set, return False.
            if tuple(combo) in self.paths_taken:
                return False
        # Didn't find a collision, so return True.
        return True

    def add_combos_to_paths_taken(self, combos: set[tuple[str]]) -> None:
        """
        Add the passed winning paths to the bingo paths taken. This is kind
        of excessive, but whatever.

        :param combos: set of bingo paths to be added to the bingo paths taken
        :type combos: set[list[str]]
        :return: None
        :rtype: None
        """
        for combo in combos:
            self.paths_taken.add(combo)

    def get_two_unique_paths_with_verification(self) -> list[str | list[str]] | None:
        """
        Grabs two rows from a face and makes sure that it doesn't contain two of the
        same numbers. It should never happen, but for some reason I'm checking anyway.

        :return: [verification, path1, path2]
        :rtype: list[str | list[str]] | None
        """
        go_again = True
        # Set these here so PyCharm will shut the hell up.
        temp_face, temp_path1, temp_path2 = [None] * 3
        while go_again:
            # shuffle_usable_faces()
            go_again = False
            try:
                temp_face = self.usable_faces.pop()
            except IndexError:
                return [None, "!!!!! ERROR: WE'VE RUN OUT OF BINGO FACES! !!!!!"]
            # If this face has fewer than two paths, it's of no use.
            # Go on to the next one.
            if temp_face.number_of_paths() < 2:
                go_again = True
                self.d_discards += 1
            else:
                # We've got to shuffle them paths
                temp_face.shuffle_paths()
                # Grab the last two paths in the face's paths' list
                temp_path1 = temp_face.paths.pop()
                temp_path2 = temp_face.paths.pop()
                # Check the uniqueness of the spaces. This should never be true, but there are a lot
                # of things that shouldn't be true about the master face list yet somehow are. If there
                # are any matches, reshuffle the faces array and try again. I'm not deleting it outright
                # because it could have other rows that work.
                if self.contains_common_item(temp_path1, temp_path2):
                    temp_face.add_path(temp_path1)
                    temp_face.add_path(temp_path2)
                    temp_face.shuffle_paths()
                    go_again = True
                #
                if temp_face.number_of_paths() > 2:
                    self.usable_faces.insert(0, temp_face)
        return [temp_face.verification(), temp_path1, temp_path2]

    def create_verification_lists(self, pseudo_face: list[str | list[str]]) -> list[list[str]]:
        """
        Take a pseudo-bingo face and transpose the paths from a one or two dimension
        array into five dimensions. Replace any paths that contain an empty member
        with the full complement of numbers associated with that position. So, the
        pseudo-face \n
         ['1111', ['1', '16', '31', '46', '61'], ['2', '17', '32', '47', '62']] \n
        would return \n
         [['1', '2'], \n
         ['16', '17'], \n
         ['31', '32'], \n
         ['46', '47'], \n
         ['61', '62']]. \n
        A pseudo-face with free spaces like this: \n
         ['1111', ['1', '', '31', '46', ''], ['2', '', '32', '47', '']]\n
        would return\n
         [['1', '2'], \n
         ['16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30'], \n
         ['31', '32'], \n
         ['46', '47'], \n
         ['61', '62', '63', '64', '65', '66', '67', '68', '69', '70', '71', '72', '73', '74', '75']\n
        Staggered spots clear out the entire row as well. The staggered, two-line pseudo-face \n
         ['1111', ['1', '', '31', '46', '61'], ['2', '17', '32', '47', '']]\n
        would produce exactly the same list as the one above.

        :param pseudo_face: pseudo bingo ticket with one or two paths
        :type pseudo_face: list[list[str] | str]
        :return: list containing all possible numbers for each column
        :rtype: list[list[str]]
        """
        # Check for the number of paths on this face, then transpose the paths to five lists.
        # A length of two means there's only one path on this face.
        if len(pseudo_face) == 2:
            spots_list = matrix(pseudo_face[1]).transpose().tolist()
        elif len(pseudo_face) == 3:
            spots_list = matrix([pseudo_face[1], pseudo_face[2]]).transpose().tolist()
        # THE FOLLOWING AREN'T USED RIGHT NOW, BUT THEY MAY BE IN THE FUTURE.
        elif len(pseudo_face) == 4:
            spots_list = matrix([pseudo_face[1], pseudo_face[2], pseudo_face[3]]).transpose().tolist()
        elif len(pseudo_face) == 5:
            spots_list = matrix([pseudo_face[1], pseudo_face[2], pseudo_face[3], pseudo_face[4]]).transpose().tolist()
        # THIS SITUATION ISN'T EVEN POSSIBLE GIVEN THE NATURE OF THE BINGO FACES (there are only four usable
        # lines per face (the center face is missing a number (free space))), BUT I'M JUST KEEPING MY OPTIONS OPEN.
        elif len(pseudo_face) == 6:
            spots_list = matrix([pseudo_face[1], pseudo_face[2], pseudo_face[3],
                                 pseudo_face[4], pseudo_face[5]]).transpose().tolist()
        else:
            spots_list = []
        # Replace any free spaces with the full range of values for the associated columns.
        for i in range(len(spots_list)):
            if '' in spots_list[i]:
                spots_list[i] = self.path_replacements[i]
        return spots_list

    def calculate_remaining_bingo_lines(self) -> int:
        """
        Cycle through the usable faces, add the number of remaining bingo lines together, and return the total.

        :return: total number of remaining bingo lines
        :rtype: int
        """
        remaining_lines = 0
        for face in self.usable_faces:
            remaining_lines += face.number_of_paths()
        return remaining_lines

    def number_of_paths_taken(self) -> int:
        """
        Return the number of possible winning paths that have already been reserved.

        :return: number of paths taken
        :rtype: int
        """
        return len(self.paths_taken)

    def get_usable_faces_size(self) -> int:
        """
        Return the total number of usable faces that still contain bingo paths.

        :return: usable faces in list
        :rtype: int
        """
        return len(self.usable_faces)

    def length(self) -> int:
        """
        The same as 'get_usable_faces_size' with a different name.
        No idea why I have it here. Probably makes code more readable
        somewhere else.

        :return: usable faces in list
        :rtype: int
        """
        return len(self.usable_faces)

    def get_first_face(self) -> FullBingoFace:
        """
        Remove the first face from the usable faces list and return it to the caller.

        :return: the first FullBingoFace object
        :rtype: FullBingoFace
        """
        return None if len(self.usable_faces) == 0 else self.usable_faces.pop(0)

    def get_random_face(self) -> FullBingoFace:
        """
        Remove a random face from the usable faces list and return it to the caller.

        :return: a random FullBingoFace object
        :rtype: FullBingoFace
        """
        return None if len(self.usable_faces) == 0 \
            else self.usable_faces.pop(rn.randint(0, self.get_usable_faces_size() - 1))

    def insert_face_randomly(self, face: FullBingoFace) -> None:
        """
        Insert a FullBingoFace into the usable faces list at a random location.

        :param face: FullBingoFace to insert
        :type face: FullBingoFace
        :return: None
        :rtype: None
        """
        if self.usable_faces is not None:
            x = rn.randint(0, self.get_usable_faces_size() - 1)
            self.usable_faces.insert(x, face)

    def append_face(self, face: FullBingoFace) -> None:
        """
        Append a FullBingoFace to the usable faces list.

        :param face: FullBingoFace to append
        :type face: FullBingoFace
        :return: None
        :rtype: None
        """
        if self.usable_faces is not None:
            self.usable_faces.append(face)

    def reset_paths_taken(self) -> None:
        """
        Clear all elements from the paths taken set.

        :return: None
        :rtype: None
        """
        if self.paths_taken is not None:
            self.paths_taken.clear()

    @staticmethod
    def contains_common_item(path1: list[str], path2: list[str]) -> bool:
        """
        Check each spot in both paths to see if they are the same number. This should
        never happen, but the master bingo list has proven itself to be unreliable.

        :param path1: list of integers as strings
        :type path1: list[str]
        :param path2: list of integers as strings
        :type path2: list[str]
        :return: True if there are common numbers in the list
        """
        # Cycle through the bingo spots and compare their values. Seems almost
        # impossible for this to ever be true, but weirder things have happened
        # with this stupid list.
        for i in range(len(path1)):
            if path1[i] == path2[i]:
                return True
        return False

    @staticmethod
    def create_winning_combinations(paths: list[list[str]], sorta: bool = False) -> set[tuple[Any, ...]]:
        """
        Create every possible five-number combination from the passed list(s).

        :param paths: Five arrays of bingo space numbers
        :type paths: list[list[str]]
        :param sorta: Do the combinations need to be sorted?
        :type sorta: bool
        :return: possible winning combinations using the provided numbers
        :type paths: set[tuple[str]]
        """
        combos = set(product(*paths))
        if sorta:
            sortees = []
            for combo in combos:
                lobo = list(combo)
                lobo.sort()
                sortees.append(tuple(lobo))
            combos = set(sortees)
        return combos

    @staticmethod
    def fisher_yates_shuffle(arr):
        """Shuffles the given list in-place using the Fisher-Yates algorithm."""
        for i in range(len(arr) - 1, 0, -1):
            j = rn.randint(0, i)
            arr[i], arr[j] = arr[j], arr[i]

    @staticmethod
    def add_free_spaces(face: list[str | list[str]], frees: int, staggered=True) -> list[str | list[str]]:
        """
        Insert the correct number of free spots into the passed face at random locations.
        Also, stagger the free spaces when necessary: if there are two lines, the free
        spaces apply to EITHER the top OR the bottom. The free spots are not connected to
        one another. A two-free spot face with two lines would look something like this:\n
         [['1', '16', '31', '', '61'],\n
         ['2', '', '36', '54', '65']]\n
        whereas a nonstaggered, two-line, two-free-spot face would look something like:\n
         [['1', '', '31', '', '61'],\n
         ['2', '', '36', '', '65']]\n
        Ultimately, there number of paths is the same, it just presents differently.

        :param face: pseudo-bingo face with verification and one or two bingo lines
        :type face: list[str | list[str]]
        :param frees: frees number of free spots
        :type frees: int
        :param staggered: True if free spots are in different columns
        :type staggered: bool
        :return: pseudo-bingo face with free spaces added
        :rtype: list[str | list[str]]
        """
        global spots_distribution
        free_marker = ''
        # spots array represents the columns
        # Shuffle the columns and use the first and second
        # positions to randomize the placement of free spaces.
        # rn.seed(int(time.time()))

        # for i in range(rn.randint(2, 6)):
        for _ in range(7):
            rn.shuffle(spots_distribution)

        spots_distribution.sort(key=lambda x: x[1], reverse=False)
        # Figure out how many paths there are and act accordingly
        match len(face) - 1:
            case 1:
                # A single path will be handled the same way, regardless of
                # its staggered status.
                # Add the desired number of free spaces
                for j in range(frees):
                    # Use the shuffled spots array to ascertain which space will
                    # receive the free space marker
                    face[1][spots_distribution[j][0]] = free_marker
                    spots_distribution[j][1] += 1
            case 2:
                # If the spots are staggered, treat the two lines separately.
                # Otherwise, put free spaces in the same spots on both lines.
                if staggered:
                    # If there are two paths, choose how to handle 1 or 2 free spouts.
                    match frees:
                        case 1:
                            # For one free spot, pick a random row then set the first random column to empty.
                            row = rn.randint(1, 2)
                            face[row][spots_distribution[0][0]] = free_marker
                            spots_distribution[0][1] += 1
                        case 2:
                            # For two spots, cycle through the rows and use the first two positions to assign empties.
                            for row in range(1, 3):
                                face[row][spots_distribution[row - 1][0]] = free_marker
                                spots_distribution[row - 1][1] += 1
                        case 3:
                            starter = rn.randint(0, 1)
                            for row in range(1, 4):
                                face[starter + 1][spots_distribution[row - 1][0]] = free_marker
                                starter = 1 if starter == 0 else 0
                else:
                    # For non-staggered free spaces, blank out the spots on both paths.
                    for free in range(frees):
                        face[1][spots_distribution[free][0]] = free_marker
                        face[2][spots_distribution[free][0]] = free_marker
                        spots_distribution[free][1] += 1
        return face

    def set_debug(self, bugging):
        self.debug = bugging

    # def import_usable_faces_csv(self, extended: bool = False, reset_paths_taken: bool = False) -> None:
    #     """
    #     Import the usable bingo faces from a file and place them into a list. The data
    #     includes the verification (face id) number and available bingo paths. Use the
    #     csv library for code clarity.
    #
    #     :param extended: use extended (27,000) instead of the standard (9,000) face csv file
    #     :type extended: bool
    #     :param reset_paths_taken: Should the paths-taken set be cleared?
    #     :type reset_paths_taken: bool
    #     :return: None
    #     :rtype: None
    #     """
    #     self.usable_faces = []
    #     filename = 'usable9000.csv' if not extended else 'usable27000.csv'
    #
    #     with open(f'./ticketing/{filename}') as file:
    #         reader = csv.reader(file)
    #         temp_face = ''
    #         previous_line_id = ''
    #
    #         for row in reader:
    #             temp_id = row[0].split('.')[0].replace('"', '')  # Extract face id
    #
    #             if temp_id != previous_line_id:
    #                 previous_line_id = temp_id
    #                 if temp_face != '' and temp_face.number_of_paths() >= 2:
    #                     temp_face.shuffle_paths()
    #                     self.usable_faces.append(temp_face)
    #                 temp_face = FullBingoFace(temp_id, row[1:])  # Pass remaining elements as bingo spots
    #             else:
    #                 temp_face.add_path(row[1:])
    #
    #     if reset_paths_taken:
    #         self.paths_taken.clear()
