import ttkbootstrap as ttk
import tkinter as tk
from ticketing__frame import TicketingFrame
from helpers import create_label_and_field


class NamesFrame(TicketingFrame):
    """
    A frame for managing game and file name information in the ticketing application.

    This class inherits from TicketingFrame and provides input fields for
    entering the "Base Part" and "File Name" related to a game.

    Methods:
        add_widgets(): Adds the input fields for "Base Part" and "File Name".
        validate_data() -> list: Validates the entered data and returns a list of error messages.
        clear_fields(): Clears the input fields.
        retrieve_data() -> list: Retrieves the entered data as a list.
        create_data_dictionary(): Populates the data_dictionary with values from the input fields.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the NamesFrame.

        Args:
            parent: The parent widget for this frame.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.
        """
        super().__init__(parent, *args, **kwargs)
        self.add_widgets()

    def add_widgets(self):
        """
        Adds label and input widgets to the NamesFrame.
        """
        # Names: base part name
        label, input_field = create_label_and_field("Base Part", ttk.Entry(self), 0, 0, self)
        self.populate_data_collections(input_field, label)

        # Names: file name
        label, input_field = create_label_and_field("File Name", ttk.Entry(self), 1, 0, self)
        self.populate_data_collections(input_field, label)

    def validate_data(self) -> list:
        """
        Validates the data entered in the form fields.

        Returns:
            A list of error messages if validation fails. If no errors are found,
            an empty list is returned.
        """
        messages = []
        self.create_data_dictionary()
        if len(self.data_dictionary['Base Part']) == 0:
            messages.append("Names: Base Part cannot contain an empty string.")

        if len(self.data_dictionary['File Name']) == 0:
            messages.append("Names: File Name cannot contain an empty string.")

        return messages

    def clear_fields(self):
        """
        Clears all input fields in the frame.
        """
        for label, input_field in self.field_dictionary.items():
            input_field.delete(0, tk.END)

    def retrieve_data(self) -> list:
        """
        Retrieves and returns the current data from the form fields.

        Returns:
            A list containing the following data:
            - Base Part (str)
            - File Name (str)
        """
        self.create_data_dictionary()
        return [self.data_dictionary['Base Part'], self.data_dictionary['File Name']]

    def create_data_dictionary(self):
        """
        Updates the `data_dictionary` with current values from the input fields.
        """
        for label, input_field in self.field_dictionary.items():
            self.data_dictionary[label] = input_field.get()

