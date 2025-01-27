import tkinter as tk
import ttkbootstrap as ttk

from ticketing import game_info as gi

from helpers import create_label_and_field
from ticketing_frame import TicketingFrame


class GameInfoFrame(TicketingFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # self.widgets = {}
        self.field_dictionary = {}
        self.input_fields = []
        self.labels = []
        self.data_dictionary = {}
        self.add_widgets()

    def add_widgets(self):
        # Window Structure
        combo_struct = ttk.Combobox(self,
                                    values=['1', '3', '3-1', '4', '4-1', '5', '7', 'S', 'NS', 'C', 'BC', 'NC'],
                                    state="readonly")
        label, input_field = create_label_and_field("Window Structure", combo_struct, 0, 0, self)
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

        # Ups
        label, input_field = create_label_and_field("Ups", ttk.Entry(self), 0, 2,
                                                    self, "1")
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

        # Permutations
        label, input_field = create_label_and_field("Permutations", ttk.Entry(self), 1, 0,
                                                    self, "1")
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

        # Sheets
        label, input_field = create_label_and_field("Sheets", ttk.Entry(self), 1, 2,
                                                    self, "1")
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

        # Subflats
        label, input_field = create_label_and_field("Subflats", ttk.Entry(self), 2, 0,
                                                    self, "1")
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

        # Schisms
        label, input_field = create_label_and_field("Schisms", ttk.Entry(self), 2, 2,
                                                    self, "0")
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

        # Reset
        label, input_field = create_label_and_field("Reset", ttk.Checkbutton(self), 3, 2,
                                                    self)
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

    def validate_data(self) -> list[str]:
        """
        Validates the data in a form or configuration context and returns a list of error
        messages if the provided data does not meet specified constraints. This includes
        ensuring that required fields are non-empty, numeric constraints on integer values
        are satisfied, and specific logical relationships between form values are adhered
        to (e.g., divisibility requirements).

        :raises RuntimeError: If `create_data_dictionary` or any external dependencies
            such as `gi.get_sheet_capacity` or `gi.sheet_columns` fail unexpectedly.
        :param self: Implicit parameter representing the instance of the class, used to
            access instance attributes and methods such as `self.data_dictionary` and
            `self.labels`.

        :return: A list of error messages indicating validation failures. If no validation
            errors occur, an empty list is returned.
        :rtype: list[str]
        """
        messages = []
        self.create_data_dictionary()
        # Verify that a window structure has been selected.
        if not self.data_dictionary["Window Structure"]:
            messages.append("Window Structure cannot be empty. Please select a valid option.")

        # Verify that all number entry fields contain valid integers
        for label_text in self.labels:
            if label_text in ['Ups', 'Permutations', 'Sheets']:
                if not self.data_dictionary[label_text].isdigit() or int(self.data_dictionary[label_text]) < 1:
                    messages.append(f"{label_text} must contain a positive integer.")
            elif label_text in ['Schisms', 'Subflats']:
                if not self.data_dictionary[label_text].isdigit() or int(self.data_dictionary[label_text]) < 0:
                    messages.append(f"{label_text} must contain a non-negative integer.")

        # If there's already an error, pitch this back to the caller with the descriptions.
        if len(messages) > 0:
            return messages

        # Validate that the window capacity is evenly divisible by the number of ups.
        win_capacity = gi.get_sheet_capacity(self.data_dictionary["Window Structure"])[1]
        ups = int(self.data_dictionary["Ups"])
        if win_capacity % ups != 0:
            messages.append(f"Window capacity ({win_capacity}) must be evenly divisible by the number of ups ({ups}).")
            return messages

        # Validate the number of ups is evenly divisible by the number of permutations.
        perms = int(self.data_dictionary["Permutations"])
        if perms != 0 and ups % perms != 0:
            messages.append(f"Ups ({ups}) must be evenly divisible by the number of permutations ({perms}).")
            return messages

        # Validate that schisms is used only with new snaps and is evenly divisible into
        # the number of columns per up.
        schisms = int(self.data_dictionary["Schisms"])
        if schisms != 0:
            if self.data_dictionary["Window Structure"] != "NS":
                messages.append("Schisms can only be used with window structure 'NS' right now.")
                return messages
            columns = gi.sheet_columns(self.data_dictionary["Window Structure"])
            columns_per_up = win_capacity / ups
            if columns_per_up % schisms != 0:
                messages.append(f"Schisms ({schisms}) must be evenly divisible by "
                                f"the number of columns per up ({columns_per_up}).")
                return messages

        # Validate the number of subflats is evenly divisible into the number of sheets.
        subflats = int(self.data_dictionary["Subflats"])
        sheets = int(self.data_dictionary["Sheets"])
        if sheets != 0 and subflats % sheets != 0:
            messages.append(f"Subflats ({subflats}) must be evenly divisible by the number of sheets ({sheets}).")
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
        pass

    def retrieve_data(self) -> list:
        pass
