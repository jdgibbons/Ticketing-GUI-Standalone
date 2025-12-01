import re
import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from ticketing.ticket_models import PickImagesTicket, ImageTier


class PicksImagesTab(TicketingNotebookTab):
    """
    A tab for managing image-related image ticketing data within the picks notebook.
    (Picks -> Images)

    This class provides a user interface for entering and validating image-specific data
    for instant tickets, such as tier quantities and uniqueness flags. It inherits from
    `TicketingNotebookTab` and implements the required abstract methods.

    Attributes:
        name (str): The name of the tab, set to "Images".
    """

    def __init__(self, parent):
        """
        Initializes the InstantsImagesTab.

        Args:
            parent: The parent widget.
        """

        super().__init__(parent)
        self.name = "Images"
        self.add_widgets()

    def add_widgets(self):
        """
        Adds widgets to the tab for entering image-related picks ticket data.

        This method creates a grid of labels, entry fields, and checkboxes for entering
        tier quantities and uniqueness flags. It also includes a field for the CD Tier.
        """

        # Create two columns of labels for tier, quantity, and uniqueness
        for i in range(3):
            tier_label = ttk.Label(self, text=f"Tier")
            tier_label.grid(row=0, column=(i * 3) + 0, padx=5, pady=5)
            entry_label = ttk.Label(self, text=f"Quantity")
            entry_label.grid(row=0, column=(i * 3) + 1, padx=5, pady=5, sticky="w")
            unique_label = ttk.Label(self, text=f"Unique")
            unique_label.grid(row=0, column=(i * 3) + 2, padx=5, pady=5)

        # Create  tiers for instant images, including quantity and uniqueness
        # (maybe add more later on--I haven't seen picks heavily tiered).
        for i in range(15):
            # Create the label for this tier, calculate its column and row positions,
            # then add it to the grid.
            row_label = ttk.Label(self, text=str(i + 1))
            col = i // 5 * 3
            row = i % 5
            row_label.grid(row=row + 1, column=col, padx=5, pady=5)

            # Add entry box for quantity and add it to the collections with
            # 'tier' plus the tier's value as the name.
            entry = ttk.Entry(self, width=10)
            entry.grid(row=row + 1, column=col + 1, padx=5, pady=5)
            entry.insert(0, "0")
            field_name = f'tier{str(i + 1).zfill(2)}'
            self.populate_data_collections_with_text(entry, field_name)

            # Add checkbox for uniqueness and add it to the collections with
            # 'unique' plus the tier's value as the name.
            checkbox = ttk.Checkbutton(self)
            checkbox.grid(row=row + 1, column=col + 2, padx=5, pady=5)
            field_name = f'unique{str(i + 1).zfill(2)}'
            self.populate_data_collections_with_text(checkbox, field_name)

    def validate_data(self) -> list:
        """
        Validates the data contained within the tab. Ensures that all quantity
        fields contain non-negative integers.

        Returns:
            list: A list of error messages. An empty list indicates no errors.
        """

        self.create_data_dictionary()
        messages = []
        box_match = r'tier'
        # Cycle through the all the data widgets, but only check the contents
        # of the entry boxes to verify they contain non-negative numbers.
        for label in self.labels:
            if re.search(box_match, label):
                if (not self.data_dictionary[label].isdigit()
                        or int(self.data_dictionary[label]) < 0):
                    messages.append(f"Picks -> Images: '{label.title()}' must contain a non-negative integer.")
        return messages

    def create_data_dictionary(self):
        """
        Populates the data_dictionary with the current values from the input fields.
        """
        self.data_dictionary.clear()
        checkbox_match = r'unique'
        for label in self.labels:
            if re.search(checkbox_match, label):
                self.data_dictionary[label] = self.field_dictionary[label].instate(['selected'])
            else:
                self.data_dictionary[label] = self.field_dictionary[label].get()

    def create_defaults(self):
        """
        Populates the defaults' dictionary. Currently, no defaults are explicitly set
        in this class, so this method does nothing. If you wanted to set defaults,
        you would do it here.
        """

        pass

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their initial values.
        """

        box_match = r'tier'
        checkbox_match = r'unique'
        # Cycle through the data fields and reset them
        for label in self.labels:
            # Reset the quanity fields to '0'.
            if re.search(box_match, label):
                self.field_dictionary[label].delete(0, ttk.END)
                self.field_dictionary[label].insert(0, "0")
            # Deselect the checkboxes.
            elif re.search(checkbox_match, label):
                self.field_dictionary[label].state(['!selected'])
            # I have no clue why it would get here, but . . .
            else:
                self.field_dictionary[label].delete(0, ttk.END)
                self.field_dictionary[label].insert(0, "0")

    def retrieve_data(self) -> PickImagesTicket:
        tier_list = []
        for i in range(15):
            q_key = f'tier{str(i + 1).zfill(2)}'
            u_key = f'unique{str(i + 1).zfill(2)}'
            qty = int(self.data_dictionary[q_key])

            if qty != 0:
                tier_list.append(ImageTier(
                    number=i + 1,
                    quantity=qty,
                    is_unique=self.data_dictionary[u_key]
                ))
            else:
                break

        if not tier_list:
            tier_list.append(ImageTier(0, 0, False))

        return PickImagesTicket(tiers=tier_list)
