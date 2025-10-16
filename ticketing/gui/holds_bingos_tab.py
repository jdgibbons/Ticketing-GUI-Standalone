import re
import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from .helpers import create_label_and_field


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

    def retrieve_data(self) -> list:
        """
        Retrieves and processes data from the input fields.

        Returns:
            list: A list containing the retrieved data, including bingo values, either-or options,
                  leading zeroes setting, free type, and extended CSV setting.
        """
        values = []
        # Create four lists for the different standard bingos, then cycle through the
        # entry boxes and append their data to their associated lists.
        for i in range(4):
            values.append([])
        for i in range(4):
            key = f'dns{i + 1}'
            values[0].append(int(self.data_dictionary[key]))
            key = f'ds{i + 1}'
            values[1].append(int(self.data_dictionary[key]))
            key = f'sns{i + 1}'
            values[2].append(int(self.data_dictionary[key]))
            key = f'ss{i + 1}'
            values[3].append(int(self.data_dictionary[key]))
        # Parse the string in the Either-Ors box and create a list for each type present within the text.
        # The list is expected to contain quantity, free spaces, and doubles. Multiple types can be entered
        # if they are divided by semicolons. So, an entry of 100,0,1;50,1,1;30,0,2;20,1,2 would equal:
        # a list of four elements representing 100 tickets with 0 free and 1 double column; 50 tickets with
        # 1 free and 1 double columns; 30 tickets with 0 free and 2 double columns; and 20 tickets with
        # 1 free and 2 double columns -----> [[100, 0, 1], [50, 1, 1], [30, 0, 2], [20, 1, 2]]
        bungee = []
        if len(self.data_dictionary['Either-Ors']) > 0:
            # Split each bingo spec, then cycle through them.
            bings = self.data_dictionary['Either-Ors'].split(';')
            for bing in bings:
                # Split the spec into its constituent parts, then
                # append the int equivalent to a list.
                binkie = bing.split(',')
                bunk = []
                for val in binkie:
                    bunk.append(int(val))
                # Add this bingo spec info to the
                bungee.append(bunk)
        else:
            bungee.append([0, 0, 0])
        # Append either-ors, leading zeroes, and how to handle free spaces (free type)
        values.append(bungee)
        values.append(self.data_dictionary['Leading Zeroes'])
        values.append(self.data_dictionary['Free Type'])
        # If the Bingo Balls value is True, add 'BB' to the values list.
        # Otherwise, just ignore it.
        if self.data_dictionary['Bingo Balls']:
            values.append('BB')
        # Append 'E' or 'S' to indicate whether to use the standard or
        # extended version of the bingo lines csv.
        if self.data_dictionary['Extended CSV']:
            values.append('E')
        else:
            values.append('S')
        values.insert(0, self.name)

        # Calculate the number of rows needed to accommodate the bingo styles used by the game.
        # (Single-line, double-line, or a combination of the two. (If both single- and double-line
        # bingos are present, three rows are needed (since the text frames will need to be different
        # in DesignMerge).). Either-Ors require three rows for the same reason.)
        # columns_needed indexes translate to: [0] single-line is needed, [1] double-line is needed,
        # [2] three rows are needed (either-ors).
        columns_needed = [False] * 3
        columns = 0
        # Double-line nonstaggered; at least two lines needed
        if sum(values[1]) > 0:
            columns_needed[1] = True
        # Double-line staggered; at least two lines needed
        if sum(values[2]) > 0:
            columns_needed[1] = True
        # Single-line nonstaggered; at least one line needed
        if sum(values[3]) > 0:
            columns_needed[0] = True
        # Single-line staggered; at least one line needed
        if sum(values[4]) > 0:
            columns_needed[0] = True
        # Either-Ors; three lines needed
        if values[5][0][0] > 0:
            columns_needed[2] = True
        # If either-ors are present or both single- and double-line bingos
        # are present, set the columns needed to 3.
        if columns_needed[2] or (columns_needed[0] and columns_needed[1]):
            columns = 3
        # If only single-line bingos are present, set the columns needed to 1.
        elif columns_needed[0]:
            columns = 1
        # If only double-line bingos are present, set the columns needed to 2.
        elif columns_needed[1]:
            columns = 2
        values.append(columns)
        return values


def parse_either_ors(eeyore):
    value = []
    if eeyore == '':
        value.append([0, 0, 0])
    return value
