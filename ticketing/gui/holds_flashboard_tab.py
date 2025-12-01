import re
import ttkbootstrap as ttk

from .helpers import create_label_and_field
from .ticketing__notebook_tab import TicketingNotebookTab
from ticketing.ticket_models import HoldFlashboardTicket


class HoldsFlashboardTab(TicketingNotebookTab):
    """
    (See Bluecoats - 4854)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.name = "Flashboard"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        # Add 'Quantity' label and entry box and add the box to the collections as 'quantity'.
        label, input_field = create_label_and_field("Quantity", ttk.Entry(self, width=5),
                                                    0, 0, self, "0")
        self.populate_data_collections_with_text(input_field, 'quantity')

        # Add spacers.
        label = ttk.Label(self, text="     ")
        label.grid(row=0, column=2, padx=15, pady=5)

        label = ttk.Label(self, text="     ")
        label.grid(row=0, column=3, padx=15, pady=5)

        # Add 'Spots per Ticket' label and entry box and add it to the collections as 'spots'.
        label, input_field = create_label_and_field("Spots per Ticket", ttk.Entry(self, width=5),
                                                    0, 4, self, "0")
        self.populate_data_collections_with_text(input_field, 'spots')

        # Add spacers.
        label = ttk.Label(self, text="     ")
        label.grid(row=0, column=6, padx=15, pady=5)

        label = ttk.Label(self, text="     ")
        label.grid(row=0, column=7, padx=15, pady=5)

        # Add a frame to hold the checkboxes, so they don't appear janky.
        check_layout_frame = ttk.Frame(self)
        check_layout_frame.grid(row=1, column=0, columnspan=8, padx=25, pady=5)

        # Add 'Leading Zeroes' label and checkbox and add the checkbox to the collections as 'zeroes'.
        label, input_field = create_label_and_field("Leading Zeroes", ttk.Checkbutton(check_layout_frame),
                                                    0, 0, check_layout_frame)
        self.populate_data_collections_with_text(input_field, 'zeroes')

        # Add 'Letters' label and checkbox and add the checkbox to the collections as 'letters'.
        label, input_field = create_label_and_field("Letters", ttk.Checkbutton(check_layout_frame),
                                                    0, 2, check_layout_frame)
        self.populate_data_collections_with_text(input_field, 'letters')

        # Add 'Hyphen' label and checkbox and add the checkbox to the collections as 'hyphen'.
        label, input_field = create_label_and_field("Hyphen", ttk.Checkbutton(check_layout_frame),
                                                    0, 4, check_layout_frame)
        self.populate_data_collections_with_text(input_field, 'hyphen')

        # Add a frame to hold the checkboxes, so they don't appear janky.
        color_layout_frame = ttk.Frame(self)
        color_layout_frame.grid(row=2, column=0, columnspan=8, padx=25, pady=5)

        # Add 'Color' label.
        label = ttk.Label(color_layout_frame, text="Colors")
        label.grid(row=0, column=0, padx=5, pady=5)
        # Add five entry boxes to hold the color strings and add them to the collections as 'color1' - 'color5'.
        for i in range(1, 6):
            entry = ttk.Entry(color_layout_frame, width=10, name=f"color{i}")
            entry.grid(row=0, column=i, padx=15, pady=5)
            self.populate_data_collections_with_text(entry, f"color{i}")

    def validate_data(self):
        """
        Validates the data in the entry boxes of the "Flashboard" tab in the holds frame.

        Returns:
            list: A list of error messages.  An empty list indicates no errors.
        """
        self.create_data_dictionary()
        messages = []
        for key in self.data_dictionary:
            if key in ['quantity', 'spots']:
                if (not self.data_dictionary[key].isdigit()
                        or int(self.data_dictionary[key]) < 0):
                    messages.append(f"Holds -> Flashboard: '{key}' must contain a non-negative integer.")
            elif re.search(r'color[1-5]', key):
                if (not re.search(r'^[0-9a-zA-Z-]+$', self.data_dictionary[key])
                        and self.data_dictionary[key] != ''):
                    messages.append(f"Holds -> Flashboard: '{key}' must contain only numbers, letters, and hyphens.")
        return messages

    def create_data_dictionary(self):
        """
        Create a dictionary mapping field names to their values.
        Handles both text-based input fields and checkbuttons.
        """
        self.data_dictionary.clear()
        for key in self.field_dictionary:
            if key in ['zeroes', 'letters', 'hyphen']:
                self.data_dictionary[key] = self.field_dictionary[key].instate(['selected'])
            else:
                self.data_dictionary[key] = (self.field_dictionary[key].get())

    def create_defaults(self):
        self.defaults = {'quantity': '0', 'spots': '0', 'color1': '', 'color2': '',
                         'color3': '', 'color4': '', 'color5': ''}

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their default values.
        """
        # Reset the entry boxes
        for key, value in self.defaults.items():
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, value)
        # Reset the checkboxes
        self.field_dictionary['zeroes'].state(['!selected'])
        self.field_dictionary['letters'].state(['!selected'])
        self.field_dictionary['hyphen'].state(['!selected'])

    def retrieve_data(self)-> HoldFlashboardTicket:
        colors_list = [self.data_dictionary[f'color{i}'] for i in range(1, 6) if self.data_dictionary[f'color{i}']]

        return HoldFlashboardTicket(
            quantity=int(self.data_dictionary['quantity']),
            spots=int(self.data_dictionary['spots']),
            leading_zeroes=self.data_dictionary['zeroes'],
            use_letters=self.data_dictionary['letters'],
            use_hyphen=self.data_dictionary['hyphen'],
            colors=colors_list
        )