import re
import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from .helpers import create_label_and_field


class NonWinnersNumbersTab(TicketingNotebookTab):
    """
    A tab for managing number-related non-winners ticketing data within a ticketing notebook.

    This class provides a user interface for entering and validating non-winners number data,
    such as quantity, spots, first/last numbers, exclusions, and base values. It inherits from
    `TicketingNotebookTab` and implements the required abstract methods. (Nonwinners -> Numbers)

    Attributes:
        name (str): The name of the tab, set to "Numbers".
    """

    def __init__(self, parent):
        """
        Initializes the NonWinnersNumbersTab.

        Args:
            parent: The parent widget.
        """

        super().__init__(parent)
        self.name = "Numbers"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        """
        Adds widgets to the current GUI layout.

        This method creates several labeled entry fields and their associated labels, which
        are added to the layout. For each widget added, the method utilizes helper functions
        to construct the label and input field, then collects and organizes these widgets
        to integrate them into the user interface. The widget configurations include position,
        default values, and specific grid alignments.
        """

        # Add Quantity label and entry box and add the box to the collections.
        label, input_field = create_label_and_field("Quantity", ttk.Entry(self, width=10),
                                                    0, 0, self, "0")
        self.populate_data_collections_with_label(input_field, label)

        # Add Spots (number of integers per tickets) label and entry box
        # and add the box to the collections.
        label, input_field = create_label_and_field("Spots", ttk.Entry(self, width=10),
                                                    0, 2, self, "0")
        self.populate_data_collections_with_label(input_field, label)

        # Add First (lowest nonwinning number) label and entry box and
        # add the box to the collections.
        label, input_field = create_label_and_field("First", ttk.Entry(self, width=10),
                                                    1, 0, self, "101")
        self.populate_data_collections_with_label(input_field, label)

        # Add Last (highest nonwinning number) label and entry box and
        # add the box to the collections.
        label, input_field = create_label_and_field("Last", ttk.Entry(self, width=10),
                                                    1, 2, self, "9999")
        self.populate_data_collections_with_label(input_field, label)

        # Add exclusions (suffixes that indicate which numbers need to be removed from the pool
        # of numbers produced (pertinent when shaded numbers are used for instants or holds)) label
        # and entry box and add the box to the collections.
        label, input_field = create_label_and_field("Exclusions", ttk.Entry(self),
                                                    2, 0, self, "", 3)
        label.grid(sticky="e")
        self.populate_data_collections_with_label(input_field, label)

        # Add Base image name label and entry box and add the box to the collections.
        label, input_field = create_label_and_field("Base", ttk.Entry(self, width=10),
                                                    2, 4, self, "")
        self.populate_data_collections_with_label(input_field, label)

    def validate_data(self) -> list:
        """
        Validates the data contained in the tab.

        Checks for various input errors, including:
        - Quantity and Spots: Must be non-negative integers.
        - First and Last: Must be positive integers.
        - Exclusions: Must be a comma-separated list of two-digit integers.

        Returns:
            list: A list of error messages. An empty list indicates no errors.
        """

        messages = []
        self.create_data_dictionary()
        # Cycle through the dictionary entries.
        # See method description for validation details.
        for key in self.field_dictionary:
            if key in ['Quantity', 'Spots']:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 0):
                    messages.append(f"Nonwinners -> Numbers: '{key}' must contain a non-negative integer.")
            elif key in ['Exclusions']:
                if self.data_dictionary[key] != "":
                    pattern = r"^(\d{2},)*\d{2}$"
                    if not re.match(pattern, self.data_dictionary[key]):
                        messages.append(f"Nonwinners -> Numbers: '{key}' must contain a"
                                        f" comma-separated list of 2-digit numbers.")
            elif key in ['Base']:
                pass
            else:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 1):
                    messages.append(f"Nonwinners -> Numbers: '{key}' must contain a positive integer.")
        return messages

    def create_data_dictionary(self):
        """
        Populates the data_dictionary with the current values from the input fields.
        """

        self.data_dictionary.clear()
        for key in self.field_dictionary:
            self.data_dictionary[key] = (
                self.field_dictionary[key].get())

    def create_defaults(self):
        """
        Populates the defaults dictionary with default values for the input fields.
        """

        self.defaults = {'Quantity': '0', 'Spots': '0', 'First': '101', 'Last': '9999', 'Exclusions': '', 'Base': ''}

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their default values.
        """

        for key, value in self.defaults.items():
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, value)

    def retrieve_data(self) -> list:
        """
        Retrieves and processes data from input fields.

        Returns:
            list: A list containing the retrieved data in the format:
                  [
                      self.name,
                      quantity,
                      spots,
                      first,
                      last,
                      exclusions,
                      base
                  ]
        """

        return [
            self.name,
            int(self.data_dictionary['Quantity']),
            int(self.data_dictionary['Spots']),
            int(self.data_dictionary['First']),
            int(self.data_dictionary['Last']),
            self.data_dictionary['Exclusions'],
            self.data_dictionary['Base']
        ]
