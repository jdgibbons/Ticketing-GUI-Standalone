from .bonanza_ticket import BonanzaTicket


class BingoTicket(BonanzaTicket):
    """
    This ticket should be able to handle a wide variety of bingo-styles. It can accept up to five separate number
    lists (and maybe more, someday). It automatically creates a csv field list to match the quantity of number lines
    and places the row positions contiguously on the line. For example, if there are three bingo lines, the csv numbers
    fields would be in the format:\n
    'N1A','N1B','N1C','N2A','N2B','N2C','N3A','N3B','N3C','N4A','N4B','N4C','N5A','N5B','N5C'\n
    Number fields should be passed as a list of lists, with each list representing an individual bingo line.
    IMPORTANT: is_first must be set to true for at least one ticket. The best/easiest way is to set the is_first
    member to True with the first ticket, then false for every other.
    ticket
    """

    def __init__(self, tick_no: str | int, ver: str | int, numbers: list[list[str | int]], imgs: list[str],
                 zeroes: bool = False, p: int = 1, u: int = 1, is_first: bool = False, lottos: int = 0):
        """
        Create a generic bingo ticket that can use (or not) any of the data\
        structures to allow for maximum flexibility. Bingo numbers and images
        are both optional, but can also handle five separate arrays each. The
        csv fields are created based on the number and size of the arrays.
        Permutations and ups aren't really set here at the moment. Maybe later.

        :param tick_no: ticket number (can be an empty string or an integer)
        :type tick_no: str | int
        :param numbers: list containing lists of bingo numbers
        :type numbers: list[list[str | int]]
        :param imgs: lists of images
        :type imgs: list[str]
        :param zeroes: do bingo numbers have leading zeroes
        :type zeroes: bool
        :param p: permutation: all of them are set to one during creation for now (they're changed later, if necessary).
        :type p: int
        :param u: current up: this is set to one during creation for now (they're changed later, if necessary)
        :type u: int
        :param is_first: is this the first ticket to be created?
        :type is_first: bool
        :param lottos: number of lotto slots--this will almost always be zero
        :type lottos: int
        """
        # Ticket number, permutation, and up are part of the superclass
        super().__init__(tick_no, p, u)
        self.verification = ver
        self.numbers = numbers
        self.images = imgs
        self.zeroes = zeroes
        self.free_type = 'I'
        self.bingo_type = 'N'  # 'S'taggered, 'N'onstaggered, or 'O'ther (for non-bingo tickets)
        # Only set the csv_fields on the first pass. It is a static variable, so there is
        # no need to repeatedly set it. One and done.
        if is_first:
            # Create the csv field headings, starting with ticket number
            slots = ['TKT', 'VER']
            # Verify that the number lists are all the same length.
            if not check_list_lengths(self.numbers, 'numbers', self.ticket_number):
                exit(-1)
            # Use letters to specify disparate lists in the csv by cycling through the spots and appending
            # the letter associated with each list. For example, if there were three different number lists,
            # the headings for the columns would look like:
            # 'N1A', 'N1B', 'N1C', 'N2A', 'N2B', 'N2C', 'N3A', 'N3B', 'N3C', etc.
            endings = ['A', 'B', 'C', 'D', 'E']
            for j in range(len(self.numbers[0])):
                # Add the corresponding letter for each location to the column header.
                for i, numbs in enumerate(self.numbers):
                    slots.append(f'N{j + 1}{endings[i]}')
            # Add the necessary number of csv columns for images and lottos
            for i in range(len(self.images)):
                slots.append(f'I{i + 1}')
            for i in range(lottos):
                slots.append(f'L{i + 1}')
            # Add 'P' and 'U' for permutation and up, respectively.
            slots += ['P', 'U']
            # Set the superclass's static csv_fields variable to the list we just created.
            BonanzaTicket.csv_fields = slots

    def csv_line(self) -> str:
        """
        Gather all the information associated with this ticket and send it back to the caller as a
        comma-delimited string. Ticket number, all images, all numbers, permutation, up
        :return: comma-delimited string representing the ticket's values
        """
        numbs = []
        img_count = 1
        # Cycle through each bingo path and place it in its proper position for the csv file.
        # If the position is blank and free_type is required, add the appropriate image.
        # Add a check to account for leading zeroes and add them to the front of the number
        # if necessary.

        # If this is a non-staggered bingo card, add the correct free space type
        if self.bingo_type == 'N':
            # Check whether this is a single- or double-line bingo. Singles are found
            # in the first list, while doubles are found in the second and third. Set
            # the check_line to the first list, then check if the first line is empty.
            # If it is, then reset the check_line to the second list.
            check_line = 0
            if len(''.join(self.numbers[0])) == 0:
                check_line = 1
            # Cycle through the bingo positions and check if there are empty spaces in the
            # relevant spots. If there are and images are needed, add them at the next
            # available image slots. Then add all three spaces to the numbs list.
            for i in range(len(self.numbers[0])):
                if self.free_type == 'I':
                    if self.numbers[check_line][i] == '':
                        self.images[img_count] = f'free{str(i + 1).zfill(2)}.ai'
                        img_count += 1
                for numb in self.numbers:
                    numbs.append(numb[i])
        # This will use all three columns, so there is less logic to unravel.
        elif self.bingo_type == 'E':
            for i in range(len(self.numbers[0])):
                if not self.numbers[0][i].strip() and not self.numbers[1][i].strip() and not self.numbers[2][i].strip():
                    self.images[img_count] = f'free{str(i + 1).zfill(2)}.ai'
                    img_count += 1
                elif not self.numbers[0][i].strip() and self.numbers[1][i].strip() and self.numbers[2][i].strip():
                    self.images[img_count] = f'eeyore{str(i + 1).zfill(2)}.ai'
                    img_count += 1
                numbs.extend([self.numbers[0][i], self.numbers[1][i], self.numbers[2][i]])
            if self.zeroes:
                for j in range(3):
                    self.numbers[j][0] = self.numbers[j][0].zfill(2)
        elif self.bingo_type == 'S':
            for i in range(len(self.numbers[0])):
                if not self.numbers[1][i].strip() and self.numbers[2][i].strip():
                    self.images[img_count] = f'free{str(i + 1).zfill(2)}_a.ai'
                    img_count += 1
                elif self.numbers[1][i].strip() and not self.numbers[2][i].strip():
                    self.images[img_count] = f'free{str(i + 1).zfill(2)}_b.ai'
                    img_count += 1
                numbs.extend([self.numbers[0][i], self.numbers[1][i], self.numbers[2][i]])
        elif self.bingo_type == 'O':
            for i in range(len(self.numbers[0])):
                sub_numbs = []
                for x in range(len(self.numbers)):
                    sub_numbs.append(self.numbers[x][i])
                # numbs.extend([self.numbers[0][i], self.numbers[1][i], self.numbers[2][i]])
                numbs.extend(sub_numbs)

        # Return a string containing all values to the caller. Add lotto numbers if necessary.
        if len(self.lotto) > 0:
            return (f"{self.ticket_number},{self.verification},{','.join(numbs)},{','.join(self.images)},"
                    f"{','.join(self.lotto)},{self.permutation},{self.up}")
        else:
            return (f"{self.ticket_number},{self.verification},{','.join(numbs)},{','.join(self.images)},"
                    f"{self.permutation},{self.up}")

    def set_free_type(self, free_type: str):
        if free_type not in ['B', 'I', 'T', 'N']:
            return
        else:
            self.free_type = free_type

    def insert_free_text(self):
        for index in range(len(self.numbers)):
            free_the_text = False
            for val in self.numbers[index]:
                if val != '':
                    free_the_text = True
                    break
            if free_the_text:
                for indy, value in enumerate(self.numbers[index]):
                    if value == '':
                        self.numbers[index][indy] = 'FREE'

    def get_numbers_length(self):
        """
        Return the number of bingo rows
        :return: the number of bingo rows
        :rtype: int
        """
        return len(self.numbers)

    def get_bingo_type(self):
        """
        Retrieve the flag denoting which type of bingo ticket this is: (N)onstaggered, (S)taggered,
        or (E)ither/Or.

        :return: True if free spaces are staggered, False otherwise.
        :rtype: str
        """
        return self.bingo_type

    def set_bingo_type(self, bingo_type: str):
        """
        Set the flag indicating if free spaces in the bingo number lists are staggered or not.

        :param bingo_type: Letter indicating whether this is (N)onstaggered, (S)taggered, or (E)ither/Or.
        :type bingo_type: str
        """
        self.bingo_type = bingo_type


def check_list_lengths(items: list[list[str | int]], name: str, tkt: int) -> bool:
    """
    Cycle through the passed lists and verify that each contains the same number of items.
    If there is a discrepancy, there must be some issue in the code that created the bingo
    ticket and called this function.
    :param items: list of lists containing values for a bingo ticket
    :type items: list[list[str | int]]
    :param name: name of the item types (numbers or images)
    :type name: str
    :param tkt: this ticket's number
    :type tkt: int
    :return: True if all lists have the same number of items, False otherwise
    :rtype: bool
    """
    it = iter(items)
    size = len(next(it))
    success = True
    if not all(len(items) == size for items in it):
        success = False
    if not success:
        print(f"The number of columns in the {name} list is not consistent for ticket {tkt}.")
        for item in items:
            print(item)
    return success

# Cycle through each of the bingo lines and add them to the master list, while
# also adding the necessary free space indicators.
# for i in range(len(self.numbers[0])):
# Cycle through this each bingo line while tracking the index
# for index, indies in enumerate(self.numbers):
#     if self.free_type == 'T' and indies[i] == '':
#         # I DON'T KNOW WHY I'M CHECKING THE FIRST IMAGE. NO CLUE AT ALL.
#         # THE ANSWER WILL ALWAYS BE TRUE, SO I JUST DON'T REMEMBER.
#
#         # THIS NEEDS TO BE REWRITTEN FOR THE TEXT BASED ANSWERS.
#
#         if self.images[0].startswith('base'):
#             numbs.append('FREE')
#         else:
#             numbs.append(indies[i])
#     elif self.free_type == 'B' and indies[i] == '' and index == 0:
#         numbs.append('FREE')
#         if self.images[0].startswith('base'):
#             self.images[img_count] = f'free{str(i + 1).zfill(2)}.ai'
#             img_count += 1
#     elif self.free_type == 'I' and indies[i] == '' and index == 0:
#         if self.images[0].startswith('base'):
#             self.images[img_count] = f'free{str(i + 1).zfill(2)}.ai'
#             img_count += 1
#         numbs.append(indies[i])
#     elif self.zeroes and indies[i].isdigit():
#         numbs.append(str(indies[i]).zfill(2))
#     else:
#         numbs.append(str(indies[i]))
