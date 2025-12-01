import re
import os.path as osp
import ttkbootstrap as ttk

from ticket_models import HoldBallsTicket
from .ticketing__notebook_tab import TicketingNotebookTab
from .helpers import create_label_and_field
from ticketing.ticket_models import HoldBallsTicket


class HoldsBallsTab(TicketingNotebookTab):
    """
    Concrete implementation of TicketingNotebookTab for managing (Bingo) "Balls"
    data for hold tickets. (Holds -> Balls)

    This tab allows users to input information related to the number of balls,
    bingos per ticket, spots per ticket, free spots, additional holds, etc.

    Attributes:
        nw_pool (int): Stores the size of the number pool (used for filler image creation).
    """

    def __init__(self, parent):
        """
        Initialize the HoldsBallsTab instance.

        Args:
            parent: The parent widget (notebook within holds frame).
        """
        super().__init__(parent)
        # self.bingo_fields = None
        self.name = "Balls"
        self.add_widgets()
        self.create_defaults()
        self.nw_pool = 0

    def add_widgets(self):
        """
        Adds all the necessary widgets to the "Balls" tab to collect necessary data.
        Also, add widgets and names to collections.
        """
        # Add 'Quantity' label and entry box.
        label, input_field = create_label_and_field("Quantity", ttk.Entry(self, width=5),
                                                    0, 0, self, "0")
        self.populate_data_collections_with_label(input_field, label)

        # Add 'Bingos per Ticket' label and entry box. Add to collections as 'bingos'.
        label, input_field = create_label_and_field("Bingos per Ticket", ttk.Entry(self, width=5),
                                                    0, 2, self, "0")
        self.populate_data_collections_with_text(input_field, 'bingos')

        # Add 'Spots per Ticket' label and entry box. Add to collections as 'spots'.
        label, input_field = create_label_and_field("Spots per Ticket", ttk.Entry(self, width=5),
                                                    0, 4, self, "0")
        self.populate_data_collections_with_text(input_field, 'spots')

        # Add a frame to hold the checkboxes, so they don't appear janky.
        check_layout_frame = ttk.Frame(self)
        check_layout_frame.grid(row=1, column=0, columnspan=8, padx=25, pady=5)

        # Add 'Downlines' label and checkbox.
        label, input_field = create_label_and_field("Downlines", ttk.Checkbutton(check_layout_frame),
                                                    0, 0, check_layout_frame)
        self.populate_data_collections_with_label(input_field, label)

        # Add 'Sort Bingo Balls' checkbox and add it to the collections as 'sortie'.
        label, input_field = create_label_and_field("Sort Bingo Balls", ttk.Checkbutton(check_layout_frame),
                                                    0, 2, check_layout_frame)
        self.populate_data_collections_with_text(input_field, 'sortie')

        # Add 'Non-Image' checkbox and add it to the collections as 'non-image'.
        # This checkbox indicates the numbers are all that are required in the csv,
        # because they will be placed into a base image. The bingo-ball logic is the
        # same, but the representation doesn't require the images themselves.
        label, input_field = create_label_and_field("Non-Image", ttk.Checkbutton(check_layout_frame),
                                                    0, 4, check_layout_frame)
        self.populate_data_collections_with_text(input_field, 'non-image')

        # Add 'Free Spots' label and five entry boxes for free quantities. Add to
        # collections as 'free1' - 'free5'.
        label = ttk.Label(self, text='Free Spots')
        label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        for i in range(1, 4):
            entry = ttk.Entry(self, width=5, name=f'free{i}')
            entry.grid(row=2, column=i, padx=5, pady=5)
            entry.insert(0, '0')
            self.populate_data_collections_with_text(entry, f'free{i}')

        label, input_field = create_label_and_field("NW Pool Size", ttk.Entry(self, width=5),
                                                    2, 4, self, "0")
        self.populate_data_collections_with_text(input_field, 'pool')

        # Add 'Add Shazam Images' label and checkbox. Add to collections as 'keep'.
        label, input_field = create_label_and_field("Shazams", ttk.Entry(self, width=5),
                                                    3, 0, self, "0")
        self.populate_data_collections_with_text(input_field, 'shazams')

        # Add 'Base' image label and entry box and add it to the collections
        # Leaving the field blank will automatically generate the name 'base.ai'. If the user
        # actually wants the field to be empty, they can enter 'none', 'blank', '0', or '000'.
        label, input_field = create_label_and_field("Base", ttk.Entry(self, width=10),
                                                    3, 4, self, "")
        self.populate_data_collections_with_text(input_field, 'base')

        # Add 'Additional Holds' label and entry box across multiple columns.
        # Add to collections as 'additionals'.
        label = ttk.Label(self, text='Additional Holds')
        label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        entry = ttk.Entry(self, width=50)
        entry.grid(row=4, column=1, columnspan=3, padx=5, pady=5, sticky='w')
        self.populate_data_collections_with_text(entry, 'additionals')

        # Add 'Match BBs' checkbox and add it to the collections as 'match-bbs'.
        # This checkbox indicates how the additional holds should be handled: if checked,
        # the tickets should contain the same number of images as the bingo balls. If
        # not, then treat the additional holds as single-image tickets.
        label, input_field = create_label_and_field("Match BBs", ttk.Checkbutton(self),
                                                    4, 4, self)
        self.populate_data_collections_with_text(input_field, 'match-bbs')

    def validate_data(self) -> list:
        """
        Validates the data in the entry boxes of the "Balls" tab in the holds frame.

        Returns:
            list: A list of error messages.  An empty list indicates no errors.
        """
        self.create_data_dictionary()
        messages = []
        for key in self.field_dictionary:
            if key in ['Quantity', 'bingos', 'spots', 'free1', 'free2', 'free3', 'pool', 'shazams']:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 0):
                    messages.append(f"Holds -> Balls: '{key.title()}' must contain a non-negative integer.")
            elif key == "additionals":
                if (self.data_dictionary[key] != ''
                        and not re.fullmatch(r'^[a-zA-Z0-9,;-]*$', self.data_dictionary[key])):
                    messages.append(f"Holds -> Balls: 'Additional Holds' must be a list of hold names and quantities"
                                    f" separated by commas. Multiple entries must separated by semicolons.")
            elif key in ['base']:
                illegal_char_patter = re.compile(r'[^a-zA-Z0-9.-_]')
                if self.data_dictionary[key] != "":
                    # if re.search(r'[<>:"/\\|?*\x00-\x1F]', self.data_dictionary[key]):
                    if illegal_char_patter.search(self.data_dictionary[key]):
                        messages.append(f"Holds -> Matrix: '{key}' file name contains illegal characters.")
                    elif self.data_dictionary[key] in ['.ai', '.pdf']:
                        messages.append(f"Holds -> Matrix: '{key}' file name must"
                                        f" contain more than an extension (.ai or .pdf).")
        if len(messages) == 0:
            if int(self.data_dictionary['bingos']) > int(self.data_dictionary['spots']):
                messages.append("Holds -> Balls: 'Bingos per Ticket' must be less than or equal to 'Spots per Ticket'.")
        return messages

    def create_data_dictionary(self):
        """
        Create a dictionary mapping field names to their values.
        Handles both text-based input fields and checkbuttons.
        """
        self.data_dictionary.clear()
        for key in self.field_dictionary:
            if key in ['Downlines', 'sortie', 'non-image', 'match-bbs']:
                self.data_dictionary[key] = self.field_dictionary[key].instate(['selected'])
            else:
                self.data_dictionary[key] = (self.field_dictionary[key].get())

    def create_defaults(self):
        """
        Populates the defaults dictionary with the default values for the input fields.
        """
        self.defaults = {'Quantity': '0', 'bingos': '0', 'spots': '0', 'additionals': '',
                         'pool': '0', 'shazams': '0', 'base': ''}
        for i in range(1, 4):
            self.defaults[f'free{i}'] = '0'

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their default values.
        """
        # Reset the entry boxes
        for key, value in self.defaults.items():
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, value)
        # Reset the checkboxes
        self.field_dictionary['Downlines'].state(['!selected'])
        self.field_dictionary['sortie'].state(['!selected'])
        self.field_dictionary['non-image'].state(['!selected'])
        self.field_dictionary['match-bbs'].state(['!selected'])

    def retrieve_data(self) -> HoldBallsTicket:
        """
                Retrieves the data from the tab and returns a HoldBallsTicket object.
                """
        # Retrieve unique integer fields
        quantity = int(self.data_dictionary['Quantity'])
        bingos = int(self.data_dictionary['bingos'])
        spots = int(self.data_dictionary['spots'])
        pool = int(self.data_dictionary['pool'])
        shazams = int(self.data_dictionary['shazams'])

        # Retrieve tiered free space values
        frees = [int(self.data_dictionary[f'free{i}']) for i in range(1, 4)]

        # Retrieve boolean values
        downlines = self.data_dictionary['Downlines']
        non_image = self.data_dictionary['non-image']
        match_bbs = self.data_dictionary['match-bbs']
        sortie = self.data_dictionary['sortie']

        # Handle filename
        filename, extension = osp.splitext(self.data_dictionary['base'])
        # (Optional: Logic to ensure the extension is correct could go here or in validation)

        # Retrieve and parse additional holds
        additionals = []
        temp = self.data_dictionary['additionals']

        if temp:
            adds = temp.split(';')
            for addl in adds:
                if addl.strip():  # Check if not empty string
                    hold_parts = addl.split(',')
                    if len(hold_parts) == 2:
                        color = hold_parts[0].strip()
                        amt = int(hold_parts[1].strip())
                        additionals.append((color, amt))

        return HoldBallsTicket(
            quantity=quantity,
            bingos_per_ticket=bingos,
            spots_per_ticket=spots,
            pool_size=pool,
            free_spots=frees,
            use_downlines=downlines,
            shazams=shazams,
            sort_balls=sortie,
            base_image=filename,
            match_bbs=match_bbs,
            non_image_mode=non_image,
            additional_holds=additionals
        )

    def set_nw_pool(self, pool):
        """
        This is going to go away.
        :param pool:
        :return:
        """
        self.nw_pool = pool

