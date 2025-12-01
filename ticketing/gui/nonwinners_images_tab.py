import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from .helpers import create_label_and_field
from ticketing.ticket_models import NonWinnerImagesTicket


class NonWinnersImagesTab(TicketingNotebookTab):
    """
    A tab for managing image-style ticket data within the nonwinner ticketing notebook.

    This class provides a user interface for entering and validating non-winners image data,
    such as quantity, pool size, and images per ticket. It inherits from `TicketingNotebookTab`
    and implements the required abstract methods. (Nonwinners -> Images)

    Attributes:
        name (str): The name of the tab, set to "Images".
    """

    def __init__(self, parent):
        """
        Initializes the NonWinnersImagesTab.

        Args:
            parent: The parent widget.
        """

        super().__init__(parent)
        self.name = "Images"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        """
        Adds widgets to the tab for entering non-winners image data.

        This method creates labels and entry fields for entering the quantity, pool size,
        and images per ticket. It uses the `create_label_and_field` helper function to
        simplify the creation of label-field pairs.
        """

        # Add Quantity label and entry box and add the box to the collections.
        label, input_field = create_label_and_field("Quantity", ttk.Entry(self, width=5),
                                                    0, 0, self, "0")
        self.populate_data_collections_with_label(input_field, label)

        # Add Pool Size label and entry box and add the box to the collections.
        label, input_field = create_label_and_field("Pool Size", ttk.Entry(self, width=5),
                                                    0, 2, self, "9")
        self.populate_data_collections_with_label(input_field, label)

        # Add Images per Ticket label and entry box and add the box to the collections.
        label, input_field = create_label_and_field("Images per Ticket", ttk.Entry(self, width=5),
                                                    0, 4, self, "1")
        self.populate_data_collections_with_label(input_field, label)

    def validate_data(self) -> list:
        """
        Validates the data contained in the tab. Ensures that "Quantity" is a
        non-negative integer and that "Pool Size" and "Images per Ticket"
        are positive integers.

        Returns:
            list: A list of error messages. An empty list indicates no errors.
        """

        messages = []
        self.create_data_dictionary()
        for key in self.field_dictionary:
            if key in ['Quantity']:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 0):
                    messages.append(f"Nonwinners -> Images: '{key}' must contain a non-negative integer.")
            else:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 1):
                    messages.append(f"Nonwinners -> Images: '{key}' must contain a positive integer.")
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
        This method initializes the `defaults` dictionary with default values for the
        quantity, pool size, and images per ticket fields.
        """

        self.defaults = {'Quantity': '0', 'Pool Size': '9', 'Images per Ticket': '1'}

    def clear_fields(self):
        """
        This method resets the quantity, pool size, and images per ticket fields to their
        default values.
        """
        for key, value in self.defaults.items():
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, value)

    def retrieve_data(self) -> NonWinnerImagesTicket:
        return NonWinnerImagesTicket(
            quantity=int(self.data_dictionary['Quantity']),
            pool_size=int(self.data_dictionary['Pool Size']),
            images_per_ticket=int(self.data_dictionary['Images per Ticket'])
        )
