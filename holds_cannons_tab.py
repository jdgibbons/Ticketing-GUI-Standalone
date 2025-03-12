from ticketing__notebook_tab import TicketingNotebookTab
import ttkbootstrap as ttk

from helpers import create_label_and_field


class HoldsCannonsTab(TicketingNotebookTab):
    """
    A tab within the ticketing notebook specifically for handling data related
    to Cannon holds. (Holds -> Cannons)

    This class provides a user interface for entering and validating cannons-specific data,
    such as quantity and iterations. It inherits from `TicketingNotebookTab` and implements
    the required abstract methods.

    Attributes:
        None (inherits attributes from TicketingNotebookTab)
    """

    def __init__(self, parent):
        """
        Initializes the HoldsCannonsTab. This method sets the name variable and
        calls the add_widgets method to populate the tab.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        self.name = "Cannons"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        """
        Adds widgets to the tab for entering cannons-related data.

        This method creates labels and entry fields for entering the quantity and iterations
        of cannons. It uses the `create_label_and_field` helper function to simplify the creation
        of label-field pairs.
        """

        # Add Quantity entry box and add it to the collections.
        label, input_field = create_label_and_field("Quantity", ttk.Entry(self, width=5),
                                                    0, 0, self, "0")
        self.populate_data_collections_with_label(input_field, label)

        # Add Iterations entry box and add it to the collections.
        label, input_field = create_label_and_field("Iterations", ttk.Entry(self, width=5),
                                                    0, 4, self, "0")
        self.populate_data_collections_with_label(input_field, label)

    def validate_data(self) -> list:
        """
        Validates the data entered into the tab's input fields.

        This method checks that the entered data is valid, ensuring that both the quantity
        and iterations fields contain non-negative integers.

        Returns:
            list: A list of error messages. An empty list indicates no errors.
        """
        messages = []
        self.create_data_dictionary()
        for key in self.field_dictionary:
            if (not self.data_dictionary[key].isdigit()
                    or int(self.data_dictionary[key]) < 0):
                messages.append(f"Holds->Cannons: '{key}' must contain a non-negative integer.")
        return messages

    def create_defaults(self):
        """
        Populates the defaults dictionary with default values for the input fields.
        """
        self.defaults = {'Quantity': '0', 'Iterations': '0'}

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
                  [self.name, quantity, iterations]
        """
        return [
            self.name,
            int(self.data_dictionary['Quantity']),
            int(self.data_dictionary['Iterations'])
        ]

    def create_data_dictionary(self):
        """
        Populates the data_dictionary with the current values from the input fields.
        """
        self.data_dictionary.clear()
        for key in self.field_dictionary:
            self.data_dictionary[key] = (
                self.field_dictionary[key].get())


