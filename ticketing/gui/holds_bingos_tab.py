import re
import ttkbootstrap as ttk

from ticket_models import HoldBingosTicket
from .ticketing__notebook_tab import TicketingNotebookTab
from .helpers import create_label_and_field
from ticketing.ticket_models import HoldBingosTicket


class HoldsBingosTab(TicketingNotebookTab):
    """
    A tab within the ticketing notebook specifically for handling data related
    to Bingo holds. (Holds -> Bingos)

    This class provides a user interface tab for entering and validating bingo-specific
    data, such as bingo types (Double Staggered, Single Nonstaggered, etc.), as well as
    "Either-Or" options, and additional settings like leading zeroes and extended CSV-file.
    It inherits from `TicketingNotebookTab` and implements the required abstract methods.

    Attributes:
        bingo_fields (dict): A dictionary mapping Bingo type names to their
                             corresponding short codes (e.g., 'Double Nonstaggered' to 'dns').
    """

    def __init__(self, parent):
        """
        Initializes the HoldsBingoTab. This method sets the name variable and
        calls the add_widgets method to populate the tab.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        self.bingo_fields = None
        self.name = "Bingos"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        """
        Adds the UI elements (labels, entry fields, checkboxes, combobox) to the tab.
        """
        spots = 4  # How deep the list indicating free spots will be.
        # Abbreviations for bingo types to be used a reference names
        self.bingo_fields = {
            'Double Nonstaggered': 'dns',
            'Double Staggered': 'ds',
            'Single Nonstaggered': 'sns',
            'Single Staggered': 'ss'
        }
        # Create and position the bingo columns and add them to the collections
        # with their abbreviated names (plus their free space position).
        for index, (key, value) in enumerate(self.bingo_fields.items()):
            label = ttk.Label(self, text=key)
            label.grid(row=index, column=0, padx=5, pady=5)
            for j in range(spots):
                entry = ttk.Entry(self, width=5, name=f'{value}{j + 1}')
                entry.grid(row=index, column=(j + 1), padx=5, pady=5)
                entry.insert(0, '0')
                if value == 'ss':
                    entry.config(state='readonly')
                self.populate_data_collections_with_text(entry, f'{value}{j + 1}')
        # Add the Either-Or entry box and add it to collections.
        label = ttk.Label(self, text="Either-Ors")
        label.grid(row=4, column=0, padx=5, pady=5)
        entry = ttk.Entry(self, width=60)
        entry.grid(row=4, column=1, columnspan=6, padx=5, pady=5)
        entry.insert(0, '')
        self.populate_data_collections_with_text(entry, 'Either-Ors')

        # Add the Leading Zeroes checkbox and add it to the collections.
        label, input_field = create_label_and_field("Leading Zeroes", ttk.Checkbutton(self),
                                                    0, 5, self)
        self.populate_data_collections_with_label(input_field, label)

        # Add the Extended CSV checkbox and add it to the collections.
        label, input_field = create_label_and_field("Extended CSV", ttk.Checkbutton(self),
                                                    1, 5, self)
        self.populate_data_collections_with_label(input_field, label)

        # Add the Bingo Balls checkbox and add it to the collections. This allows the production
        # of bingo ball style tickets with verified bingo paths.
        label, input_field = create_label_and_field("Bingo Balls", ttk.Checkbutton(self),
                                                    2, 5, self)
        self.populate_data_collections_with_label(input_field, label)

        # Add "Free Type" combobox and label with an empty column in between. Add it
        # to the collections.
        free_type_options = ['Images', 'Text', 'Both', 'Neither']
        free_type_combobox = ttk.Combobox(self, values=free_type_options, state="readonly", width=8)
        free_type_combobox.current(0)
        free_type_label = ttk.Label(self, text="Free Type")

        # Position the label and combobox in the last two columns
        free_type_label.grid(row=3, column=5, padx=5, pady=5, sticky="e")  # Shifted to column 5
        free_type_combobox.grid(row=3, column=6, padx=5, pady=5, sticky="w")  # Shifted to column 6
        self.populate_data_collections_with_text(free_type_combobox, 'Free Type')

    def validate_data(self) -> list:
        """
        Validates the data present in the tab's input fields.

        This method checks that the data is valid, ensuring that bingo fields contain non-negative
        integers and that the either-or field contains only letters, numbers, and semicolons.

        Returns:
            list: A list of error messages. An empty list indicates no errors.
        """
        self.create_data_dictionary()
        messages = []
        bingo_match = r'(dns|ds|sns|ss)\d+'
        # Cycle through the data fields.
        for key in self.field_dictionary:
            # If this is a bingo field, make sure it contains a non-negative integer.
            if re.search(bingo_match, key):
                if (self.data_dictionary[key] == '' or not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 0):
                    messages.append(f"Holds -> Bingos: '{key.upper()}' must contain a non-negative integer.")
            # If this is the Either-Or field, make sure there are no unrecognized characters. It's not a
            # complete validation, but ain't nobody got time for that right now.
            if key in ['Either-Ors']:
                test_values = True
                if ((self.data_dictionary[key]) != ''
                        and not re.match(r"^\d+,\d+,\d+(;\d+,\d+,\d+)*$", self.data_dictionary[key])):
                    messages.append(f"Holds -> Bingos: '{key}' must contain only sets of three comma-separated integers"
                                    f" separated by semicolons.")
                    test_values = False
                elif self.data_dictionary[key] == '':
                    test_values = False
                if test_values:
                    temps = self.data_dictionary[key].split(';')
                    for temp in temps:
                        pints = [int(pint.strip()) for pint in temp.split(',')]
                        if pints[1] > 3 or (pints[1] + pints[2]) > 4:
                            messages.append(f"Holds -> Bingos: '{key}' column totals violate specs. You cannot have "
                                            f"more than three free columns or a total of four double-line "
                                            f"plus free columns.")
        # Bingo ball checkbox validation.
        first_text = ("Holds -> Bingo: Only nonstaggered, single values may be"
                      " used if the Bingo Balls option is selected.")
        first_time = True
        if self.data_dictionary['Bingo Balls']:
            for i in range(1, 5):
                if self.data_dictionary[f'dns{i}'] != '0':
                    if first_time:
                        messages.append(first_text)
                        first_time = False
                    messages.append(f"--> Holds -> Bingos: 'dns{i}' must be zero if Bingo Balls option is selected.")
                if self.data_dictionary[f'ds{i}'] != '0':
                    if first_time:
                        messages.append(first_text)
                        first_time = False
                    messages.append(f"--> Holds -> Bingos: 'ds{i}' must be zero if Bingo Balls option is selected.")
                if self.data_dictionary[f'ss{i}'] != '0':
                    if first_time:
                        messages.append(first_text)
                        first_time = False
                    messages.append(f"--> Holds -> Bingos: 'ss{i}' must be zero if Bingo Balls option is selected.")
            if self.data_dictionary['Either-Ors'] != '':
                if first_time:
                    messages.append(first_text)
                    messages.append(f"--> Holds -> Bingos: 'Either-Ors' must be "
                                    f"blank if Bingo Balls option is selected.")
        return messages

    def create_data_dictionary(self):
        """
        Populates the data_dictionary with the current values from the input fields,
        checkboxes, and the combobox.
        """
        self.data_dictionary.clear()
        # Cycle through the tab's fields.
        for key in self.field_dictionary:
            # If this is a checkbox, get its selected value.
            if key in ['Leading Zeroes', 'Extended CSV', 'Bingo Balls']:
                self.data_dictionary[key] = self.field_dictionary[key].instate(['selected'])
            # Otherwise, just set the value to the box's content.
            else:
                self.data_dictionary[key] = (self.field_dictionary[key].get())

    def create_defaults(self):
        """
        Creates the default values for the input fields.

        This method is currently a placeholder and does not implement any functionality.
        """
        self.defaults = {'Either-Ors': ''}
        for i in range(1, 5):
            self.defaults[f'dns{i}'] = '0'
            self.defaults[f'ds{i}'] = '0'
            self.defaults[f'sns{i}'] = '0'
            self.defaults[f'ss{i}'] = '0'

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their default values ('0' for
        bingo entries,
        unchecked for checkbuttons, and 'Images' for the combobox).
        """
        # Reset the entry boxes
        for key, value in self.defaults.items():
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, value)

        # Reset checkboxes
        self.field_dictionary['Leading Zeroes'].state(['!selected'])
        self.field_dictionary['Extended CSV'].state(['!selected'])
        self.field_dictionary['Bingo Balls'].state(['!selected'])
        # Reset combobox
        self.field_dictionary['Free Type'].set('Images')

    def retrieve_data(self) -> HoldBingosTicket:
        """
        Retrieves data and returns a HoldBingosTicket object.
        """
        # 1. Gather Counts
        dns_counts = [int(self.data_dictionary[f'dns{i+1}']) for i in range(4)]
        ds_counts = [int(self.data_dictionary[f'ds{i+1}']) for i in range(4)]
        sns_counts = [int(self.data_dictionary[f'sns{i+1}']) for i in range(4)]
        ss_counts = [int(self.data_dictionary[f'ss{i+1}']) for i in range(4)]

        # 2. Parse Either-Ors
        either_ors = []
        raw_eo = self.data_dictionary['Either-Ors']
        if raw_eo:
            bings = raw_eo.split(';')
            for bing in bings:
                parts = [int(val.strip()) for val in bing.split(',')]
                either_ors.append(parts)
        else:
            # Default empty state logic from original code, though list is preferred empty
            either_ors.append([0, 0, 0])

        # 3. Calculate Columns Needed (Preserving original logic)
        columns_needed = 0
        has_single = False
        has_double = False
        has_triple = False # For Either-Ors

        # Check Double-line
        if sum(ds_counts) > 0 or sum(dns_counts) > 0:
            has_double = True
        # Check Single-line
        if sum(sns_counts) > 0 or sum(ss_counts) > 0:
            has_single = True
        # Check Either-Ors
        if either_ors[0][0] > 0:
            has_triple = True

        if has_triple or (has_single and has_double):
            columns_needed = 3
        elif has_double:
            columns_needed = 2
        elif has_single:
            columns_needed = 1

        return HoldBingosTicket(
            dns_counts=dns_counts,
            ds_counts=ds_counts,
            sns_counts=sns_counts,
            ss_counts=ss_counts,
            either_ors=either_ors,
            leading_zeroes=self.data_dictionary['Leading Zeroes'],
            free_type=self.data_dictionary['Free Type'],
            use_bingo_balls=self.data_dictionary['Bingo Balls'],
            extended_csv=self.data_dictionary['Extended CSV'],
            columns_needed=columns_needed
        )

def parse_either_ors(eeyore):
    value = []
    if eeyore == '':
        value.append([0, 0, 0])
    return value
