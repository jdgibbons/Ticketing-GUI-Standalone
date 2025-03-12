import tkinter as tk
import ttkbootstrap as ttk

from ticketing import game_info as gi

from helpers import create_label_and_field
from ticketing__frame import TicketingFrame


class GameInfoFrame(TicketingFrame):
    """
    A specific ticketing frame for entering game information.

    This class inherits from TicketingFrame and implements the abstract methods
    to create a frame with input fields for various game parameters.

    Attributes:
        defaults (dict): A dictionary storing default values for the input fields.

    Methods:
        add_widgets(): Adds widgets (labels and input fields) to the frame.
        validate_data() -> list[str]: Validates the entered data and returns a list of error messages.
        create_data_dictionary(): Populates the data_dictionary with values from the input fields.
        clear_fields(): Clears all input fields and resets them to their default values.
        retrieve_data() -> list: Retrieves the data from the input fields as a list.
        create_defaults(): Initializes the defaults dictionary with default values.
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.add_widgets()
        self.defaults = {}
        self.create_defaults()

    def add_widgets(self):
        # Window Structure Combobox
        combo_struct = ttk.Combobox(self,
                                    values=['1', '3', '3-1', '4', '4-1', '5', '7', 'S', 'NS', 'C', 'BC', 'NC'],
                                    state="readonly",
                                    width=5)
        label, input_field = create_label_and_field("Window Structure", combo_struct, 0, 0, self)
        self.populate_data_collections(input_field, label)

        # Ups Text Entry Box
        label, input_field = create_label_and_field("Ups", ttk.Entry(self, width=5), 0, 2,
                                                    self, "1")
        self.populate_data_collections(input_field, label)

        # Permutations Text Entry Box
        label, input_field = create_label_and_field("Permutations", ttk.Entry(self, width=5), 0, 4,
                                                    self, "1")
        self.populate_data_collections(input_field, label)

        # Sheets Text Entry Box
        label, input_field = create_label_and_field("Sheets", ttk.Entry(self, width=5), 1, 0,
                                                    self, "1")
        self.populate_data_collections(input_field, label)

        # Subflats Text Entry Box
        label, input_field = create_label_and_field("Subflats", ttk.Entry(self, width=5), 1, 2,
                                                    self, "0")
        self.populate_data_collections(input_field, label)

        # Schisms Text Entry Box
        label, input_field = create_label_and_field("Schisms", ttk.Entry(self, width=5), 1, 4,
                                                    self, "0")
        self.populate_data_collections(input_field, label)

        # Reset Checkbox
        label, input_field = create_label_and_field("Reset", ttk.Checkbutton(self), 2, 4,
                                                    self)
        self.populate_data_collections(input_field, label)

    def validate_data(self) -> list[str]:
        """
        Validates the entered game information.

        This method checks for empty fields, valid integer values, and specific
        logical relationships between the inputs (e.g., divisibility requirements).

        Returns:
            list[str]: A list of error messages.  Returns an empty list if no errors are found.
        """
        messages = []
        self.create_data_dictionary()
        # Verify that a window structure has been selected.
        if not self.data_dictionary["Window Structure"]:
            messages.append("Game Information: Window Structure cannot be empty. Please select a valid option.")

        # Verify that all number entry fields contain valid integers
        for label_text in self.labels:
            if label_text in ['Ups', 'Permutations', 'Sheets']:
                if not self.data_dictionary[label_text].isdigit() or int(self.data_dictionary[label_text]) < 1:
                    messages.append(f"Game Information: '{label_text}' must contain a positive integer.")
            elif label_text in ['Schisms', 'Subflats']:
                if not self.data_dictionary[label_text].isdigit() or int(self.data_dictionary[label_text]) < 0:
                    messages.append(f"Game Information: '{label_text}' must contain a non-negative integer.")

        # If there's already an error, pitch this back to the caller with the descriptions.
        if len(messages) > 0:
            return messages

        # Validate that the window capacity is evenly divisible by the number of ups.
        win_capacity = gi.get_sheet_capacity(self.data_dictionary["Window Structure"])[1]
        ups = int(self.data_dictionary["Ups"])
        if win_capacity % ups != 0:
            messages.append(f"Game Information: Window capacity ({win_capacity})"
                            f" must be evenly divisible by the number of ups ({ups}).")
            return messages

        # Validate the number of ups is evenly divisible by the number of permutations.
        perms = int(self.data_dictionary["Permutations"])
        if perms != 0 and ups % perms != 0:
            messages.append(f"Game Information: Ups ({ups}) must be evenly divisible"
                            f" by the number of permutations ({perms}).")
            return messages

        # Validate that schisms is used only with new snaps and is evenly divisible into
        # the number of columns per up.
        schisms = int(self.data_dictionary["Schisms"])
        if schisms != 0:
            if self.data_dictionary["Window Structure"] != "NS":
                messages.append("Game Information: Schisms can only be used with window structure 'NS' right now.")
                return messages
            columns = gi.sheet_columns(self.data_dictionary["Window Structure"])
            columns_per_up = win_capacity / ups
            if columns_per_up % schisms != 0:
                messages.append(f"Game Information: Schisms ({schisms}) must be evenly divisible by "
                                f"the number of columns per up ({columns_per_up}).")
                return messages

        # Validate the number of subflats is evenly divisible into the number of sheets.
        subflats = int(self.data_dictionary["Subflats"])
        sheets = int(self.data_dictionary["Sheets"])
        if sheets != 0 and subflats != 0 and sheets % subflats != 0:
            messages.append(f"Game Information: Subflats ({subflats}) must be evenly"
                            f" divisible by the number of sheets ({sheets}).")
            return messages
        return messages

    def create_data_dictionary(self):
        """
        Clears and populates the `data_dictionary` attribute with updated values
        from `field_dictionary`. This method loops through the available labels
        and updates the corresponding value of each label from the
        `field_dictionary`.

        :raises KeyError: If a label is not found in `field_dictionary`.
        """
        self.data_dictionary.clear()
        for i, label_text in enumerate(self.labels):
            if label_text in ['Reset']:
                self.data_dictionary[label_text] = self.field_dictionary[label_text].instate(['selected'])
            else:
                self.data_dictionary[label_text] = self.field_dictionary[label_text].get()

    def clear_fields(self):
        """
        Clears the data fields in all tabs and reset them to their default values.
        """
        for label_text in self.labels:
            if label_text in ['Reset']:
                self.field_dictionary[label_text].state([self.defaults[label_text]])
            elif label_text in ['Window Structure']:
                self.field_dictionary[label_text].set(self.defaults[label_text])
            else:
                self.field_dictionary[label_text].delete(0, tk.END)
                self.field_dictionary[label_text].insert(0, self.defaults[label_text])

    def retrieve_data(self) -> list:
        """
        Retrieves and returns the current data from the form fields.

        Returns:
            A list containing the following data:
            - Ups (int)
            - Permutations (int)
            - Sheets (int)
            - Sheet capacity (tuple, from `gi.get_sheet_capacity`)
            - Reset status (bool)
            - Subflats (int)
            - Schisms (int)
        """
        return [
            int(self.data_dictionary["Ups"]),
            int(self.data_dictionary["Permutations"]),
            int(self.data_dictionary["Sheets"]),
            gi.get_sheet_capacity(self.data_dictionary["Window Structure"]),
            self.data_dictionary["Reset"],
            int(self.data_dictionary["Subflats"]),
            int(self.data_dictionary["Schisms"])
        ]

    def create_defaults(self):
        """
        Initializes the `defaults` dictionary with default values for each field.
        """
        self.defaults = {"Window Structure": '', "Reset": '!selected', "Schisms": '0', "Subflats": '0'}
        for key in ['Ups', 'Permutations', 'Sheets']:
            self.defaults[key] = '1'
