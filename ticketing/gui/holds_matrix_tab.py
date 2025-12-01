import re
import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from .helpers import create_label_and_field
from ticketing.ticket_models import HoldMatrixTicket


class HoldsMatrixTab(TicketingNotebookTab):
    """
    A tab within the ticketing notebook specifically for handling data related
    to Cannon holds. (Holds -> Matrix)

    This class provides a user interface for entering and validating matrix-specific
    hold data, such as quantity and pattern. It inherits from `TicketingNotebookTab`
    and implements the required abstract methods.

    Attributes:
        name (str): The name of the tab, set to "Matrix".
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Matrix"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        """
        Adds widgets to the tab for entering cannons-related data.

        This method creates labels and entry fields for entering the quantity and iterations
        of cannons. It uses the `create_label_and_field` helper function to simplify the creation
        of label-field pairs.
        """

        # Add the Quantity entry box and add it to the collections.
        label, input_field = create_label_and_field("Quantity", ttk.Entry(self, width=10),
                                                    0, 0, self, "0")
        self.populate_data_collections_with_label(input_field, label)

        # Add the Pattern entry box and add it to the collections.
        label, input_field = create_label_and_field("Pattern", ttk.Entry(self, width=15),
                                                    0, 2, self, "")
        self.populate_data_collections_with_label(input_field, label)

        # Add the Base image entry box and add it to the collections.
        label, input_field = create_label_and_field("Base", ttk.Entry(self, width=15),
                                                    0, 4, self, "")
        self.populate_data_collections_with_label(input_field, label)

        # Add the Leading Zeroes checkbutton and add it to the collections as zeroes.
        label, input_field = create_label_and_field("Leading Zeroes", ttk.Checkbutton(self),
                                                    1, 0, self)
        self.populate_data_collections_with_text(input_field, "zeroes")

    def validate_data(self) -> list:
        """
        Validates the data entered into the tab's input fields.

        This method checks that the entered data is valid, ensuring that the quantity field
        contains a non-negative integer and the pattern field is empty or contains single
        digits separated by commas.

        Returns:
            list: A list of error messages. An empty list indicates no errors.
        """
        messages = []
        self.create_data_dictionary()
        for key in self.field_dictionary:
            # Check Quantity for non-zero integer
            if key in ['Quantity']:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 0):
                    messages.append(f"Holds -> Matrix: '{key}' must contain a non-negative integer.")
            elif key in ['Pattern']:
                # Check if Pattern is not empty
                if self.data_dictionary[key] != "":
                    # Check if Pattern has single digits separated by commas.
                    if not re.fullmatch(r"^(\d,)*\d$", self.data_dictionary[key]):
                        messages.append(f"Holds -> Matrix: '{key}' must contain single digits separated by commas.")
                    # Make sure a properly formatted list contains no more than 5 members.
                    elif len(self.data_dictionary[key].split(',')) > 5:
                        messages.append(f"Holds -> Matrix: '{key}' must contain no more than 5 digits.")
            elif key in ['Base']:
                if self.data_dictionary[key] != "":
                    if re.search(r'[<>:"/\\|?*\x00-\x1F]', self.data_dictionary[key]):
                        messages.append(f"Holds -> Matrix: '{key}' file name must not contain special characters.")
                    elif self.data_dictionary[key] == '.ai':
                        messages.append(f"Holds -> Matrix: '{key}' file name must"
                                        f" contain more than its extension (.ai).")

        return messages

    def create_defaults(self):
        """
        Populates the defaults dictionary with default values for the input fields.
        """

        self.defaults = {'Quantity': '0', 'Pattern': '', 'Base': ''}

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their default values.
        """

        for key, value in self.defaults.items():
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, value)
        self.field_dictionary['zeroes'].state(['!selected'])

    def retrieve_data(self) -> HoldMatrixTicket:
        pattern_str = self.data_dictionary['Pattern']
        pattern_list = [int(x) for x in pattern_str.split(',')] if pattern_str else []

        filename = self.data_dictionary['Base']
        if filename and not filename.endswith('.ai'):
            filename += '.ai'
        elif not filename:
            filename = 'base.ai'

        return HoldMatrixTicket(
            quantity=int(self.data_dictionary['Quantity']),
            pattern=pattern_list,
            base_image=filename,
            leading_zeroes=self.data_dictionary['zeroes']
        )

    def create_data_dictionary(self):
        """
        Populates the data_dictionary with the current values from the input fields.
        """
        self.data_dictionary.clear()
        for key in self.field_dictionary:
            if key in ['zeroes']:
                self.data_dictionary[key] = self.field_dictionary[key].instate(['selected'])
            else:
                self.data_dictionary[key] = self.field_dictionary[key].get()
