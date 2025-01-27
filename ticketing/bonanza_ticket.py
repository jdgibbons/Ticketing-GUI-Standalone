from abc import ABC, abstractmethod


class BonanzaTicket(ABC):
    """
    Abstract class to represent a generic ticket and contain methods and members
    that are common to every ticket class.
    3/1/2023: Moved ticket number here because I was adding it to every single subclass
    """
    # This needs to be set by the subclasses
    csv_fields = ['Somebody', 'did', 'not', 'set', 'the', 'class', 'variable',
                  'is_first', 'to', 'True', 'for', 'the', 'first', 'ticket!']

    def __init__(self, ticket_number: str | int = '', p: int = 1, u: int = 1) -> None:
        """
        Set all variables to default values except for ticket number, which may be
        passed from the subclass. If ticket_number is not included, set the field
        to an empty string.
        :param ticket_number:
        """
        self.ticket_number = ticket_number
        self.up = u
        self.permutation = p
        self.cd_tier = 0
        self.cd_type = 'N'
        self.position_on_sheet = 0
        self.position_on_ticket = 0
        self.sheet_number = 0
        self.part_suffix = ''
        self.lotto = []
        self.subflat = 0

    # Each subclass must implement this method to conform to its own csv line
    @abstractmethod
    def csv_line(self) -> str:
        pass

    def position_line(self, part: str) -> str:
        """
        Generates a formatted string composed of values pertaining to CD positions in a
        comma-delimited format: part number (zero-filled sheet number with part prefix),
        up, tier, position on sheet, and cd type.

        :param part: A part identifier that is to be included in the generated position line
                     string at its beginning.
        :return: A formatted string that integrates the part identifier with attributes of
                 the object, following the format
                 'part_sheetNumber,up,cd_tier,position_on_sheet,cd_type'.
        """
        return (f"{part}_{str(self.sheet_number).zfill(3)},{self.up},{self.cd_tier},"
                f"{self.position_on_sheet},{self.cd_type}")

    # Convenience method to make code more readable.
    def __str__(self) -> str:
        return self.csv_line()

    def get_csv_fields(self):
        return self.csv_fields

    # GETTERS AND (RE)SETTERS FOR THIS CLASS'S MEMBERS
    def reset_cd_tier(self, tear) -> None:
        self.cd_tier = tear

    def get_cd_tier(self) -> int:
        return self.cd_tier

    def reset_cd_type(self, typo) -> None:
        self.cd_type = typo

    def get_cd_type(self) -> str:
        return self.cd_type

    def reset_position_on_sheet(self, location):
        self.position_on_sheet = location

    def get_position_on_sheet(self):
        return self.position_on_sheet

    def get_position_on_ticket(self):
        return self.position_on_ticket

    def reset_position_on_ticket(self, pose):
        self.position_on_ticket = pose

    def reset_sheet_number(self, page):
        self.sheet_number = page

    def get_sheet_number(self):
        return self.sheet_number

    def reset_permutation(self, perm):
        self.permutation = perm

    def get_permutation(self):
        return self.permutation

    def reset_up(self, above):
        self.up = above

    def get_up(self):
        return self.up

    def reset_subflat(self, subflat):
        self.subflat = subflat

    def get_subflat(self):
        return self.subflat

    def reset_part_suffix(self, suffix):
        self.part_suffix = suffix

    def get_part_suffix(self):
        return self.part_suffix

    def reset_lotto(self, lotto):
        self.lotto = lotto

    def set_lotto(self):
        return self.lotto

    def add_subflat_to_csv_fields(self):
        self.csv_fields += 'S'
