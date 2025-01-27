from .bonanza_ticket import BonanzaTicket


class UniversalTicket(BonanzaTicket):
    """
    This class should be able to accommodate a very wide variety of tickets.
    It allows the user to first populate the number and image lists, then uses
    their lengths to create the static csv fields. I wish I'd thought of this
    years ago.\n
    Single/base images should be placed in the first column to allow for easier
    sharing of column space. Distribution can be as efficient as possible by
    remembering to add blank spaces to the lists representing unused DesignMerge
    fields.\n
    Numbers can be handled the same way to allow more complex yet efficient
    distribution by accounting for unused DesignMerge fields with blank spaces.
    """

    def __init__(self, tkt: int | str, imgs: list[str], numbs: list[int | str], p: int = 1, u: int = 1,
                 is_first: bool = False, lottos: int = 0):
        """
        Create a generic ticket that should cover most non-bingo (and some that are bingo)
        situations. It also allows the user to pass in a list of images and a list
        of numbers to represent ticket values and creates a list of csv column headings to
        pass up to the superclass's static csv_fields. The creation is dependent on 'True'
        being passed as the is_first parameter. This is so the static variable isn't set
        every time a new ticket is created.

        :param tkt: ticket number
        :type tkt: int
        :param imgs: list of strings containing image names
        :type imgs: list[str]
        :param numbs: a list of integers or strings containing number values
        :type numbs: list[int | str]
        :param p: this ticket's permutation
        :type p: int
        :param u: this ticket's up
        :type u: int
        :param is_first: Is the first ticket to be created?
        :type is_first: bool
        """
        super().__init__(tkt, p, u)
        self.images = imgs
        self.numbers = numbs
        self.permutation = p
        self.up = u
        # If this is the first ticket created, generate the csv fields to be used when
        # writing out the ticket's values to files. First add the ticket number field,
        # then iterate using the lengths of the number and image lists to create the csv
        # fields. For each iteration, place an 'N' or an 'I' in front of the index value
        # plus one. Add 'P' and 'U' for the permutation  and up, respectively, then assign
        # the result to the superclass's csv field member.
        if is_first:
            # Add the ticket number field
            slots = ['TKT']
            # Add an image field for every spot in the list
            for i in range(len(self.images)):
                slots.append(f'I{i + 1}')
            # Add a number field for every spot in the list
            for i in range(len(self.numbers)):
                slots.append(f'N{i + 1}')
            # Add the number of lotto fields indicated by the lottos parameter
            for i in range(lottos):
                slots.append(f'L{i + 1}')
            # Add 'P' and 'U' for permutation and up, respectively.
            slots += ['P', 'U']
            # If there are subflats, add 'S' to the csv fields
            if self.subflat != 0:
                slots.append('S')
            # Set the superclass's static csv_fields variable
            BonanzaTicket.csv_fields = slots

    def csv_line(self) -> str:
        """
        Gather all the information associated with this ticket and send it back to the
        caller as a comma-delimited string. Ticket number, all images, all numbers, permutation, up

        :return: comma-delimited string representing the ticket's values
        """
        line = f"{self.ticket_number}"
        if len(self.images) > 0:
            line += f",{','.join(self.images)}"
        if len(self.numbers) > 0:
            line += f",{','.join(self.numbers)}"
        line += f",{self.permutation},{self.up}"
        if self.subflat != 0:
            line += f",{self.subflat}"
        return line
        # return f"{self.ticket_number},{','.join(self.images)},{','.join(self.numbers)},{self.permutation},{self.up}"
