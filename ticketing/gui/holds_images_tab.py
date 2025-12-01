import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from ticketing.ticket_models import HoldImagesTicket


class HoldsImagesTab(TicketingNotebookTab):
    """
    A tab for managing image-type hold ticketing data within a ticketing notebook.
     (Holds -> Images)

    This tab allows users to input the quantity of different image tiers.
    It provides 16 entry fields that allow the user to specify the quantity
    of each tier.

    Attributes:
    None (inherits attributes from TicketingNotebookTab)
    """

    def __init__(self, parent):
        """
        Initializes the HoldsImagesTab. Sets the name and adds widgets.

        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        self.name = "Images"
        self.add_widgets()

    def add_widgets(self):
        """
        Adds widgets to the tab for entering image-related data.

        This method creates a grid of labels and entry fields for entering quantities
        for different image types. The grid consists of three rows of four columns, each
        representing a specific image tier, for a total of 16 entries.
        """
        for i in range(4):
            # Add Type and Quantity labels
            tier_label = ttk.Label(self, text=f"Type")
            tier_label.grid(row=0, column=(i * 3) + 0, padx=5, pady=5)
            entry_label = ttk.Label(self, text=f"Quantity")
            entry_label.grid(row=0, column=(i * 3) + 1, padx=5, pady=5, sticky="w")

        # Create 16 entries in three rows and four columns. The counting is done
        # vertically, so types 1 - 3 are in column one, 4 - 6 are in column two, etc.
        for i in range(16):
            # Create and add the tier label.
            row_label = ttk.Label(self, text=str(i + 1).zfill(2))
            col = i // 4
            row = i % 4
            row_label.grid(row=row + 1, column=col * 3, padx=5, pady=5)

            # Create and add the entry box.
            entry = ttk.Entry(self, width=10)
            entry.grid(row=row + 1, column=col * 3 + 1, padx=5, pady=5)
            entry.insert(0, "0")
            field_name = f'type{str(i + 1).zfill(2)}'
            self.populate_data_collections_with_text(entry, field_name)

    def validate_data(self) -> list:
        """
        Validates the data within the tab. Ensures that all quantity
        fields contain non-negative integers.

        Returns:
            list: A list of error messages.
        """
        messages = []
        self.create_data_dictionary()
        for i in range(16):
            key = f'type{str(i + 1).zfill(2)}'
            if (not self.data_dictionary[key].isdigit()
                    or int(self.data_dictionary[key]) < 0):
                messages.append(f"Holds '{key}' must contain a non-negative integer.")
        return messages

    def create_data_dictionary(self):
        """
       Populates the data_dictionary with the current values from the input fields.
       """
        self.data_dictionary.clear()
        for i in range(16):
            key = f'type{str(i + 1).zfill(2)}'
            self.data_dictionary[key] = (
                self.field_dictionary[key].get())

    def create_defaults(self):
        """
        Populates the defaults' dictionary. Currently, no defaults are explicitly set
        in this class, so this method does nothing.
        """
        pass

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their default values
        (which is "0" for all fields).
        """
        for label in self.labels:
            self.field_dictionary[label].delete(0, ttk.END)
            self.field_dictionary[label].insert(0, "0")

    def retrieve_data(self) -> HoldImagesTicket:
        type_list = []
        for i in range(16):
            key = f'type{str(i + 1).zfill(2)}'
            val = int(self.data_dictionary[key])
            if val != 0:
                type_list.append(val)
            else:
                break

        if not type_list:
            type_list.append(0)

        return HoldImagesTicket(quantities=type_list)
