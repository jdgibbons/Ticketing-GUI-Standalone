from abc import ABC, abstractmethod

import ttkbootstrap as ttk


class TicketingFrame(ABC, ttk.LabelFrame):
    """
       Abstract base class for ticketing frames.

       This class provides a common structure and methods for frames used in a
       ticketing application.  It manages data dictionaries, input fields,
       and labels, and defines abstract methods that subclasses must implement.

       Attributes:
           data_dictionary (dict): A dictionary to store data from data widgets.
           field_dictionary (dict): A dictionary mapping label text to input fields.
           input_fields (list): A list of input fields.
           labels (list): A list of label names for input fields.
           tabs (dict): A dictionary mapping tab names to tab instances (if using tabs).
           tab_names (list): A list of tab names.

       Methods:
           add_widgets(): Abstract method to add widgets to the frame. Subclasses must implement this.
           validate_data() -> list: Abstract method to validate data entered into the frame. Returns a
                                    list of error messages. Subclasses must implement this.
           clear_fields(): Abstract method to clear all input fields in the frame. Subclasses must
                           implement this.
           retrieve_data() -> list: Abstract method to retrieve data from the input fields. Returns
                                    a list of data values. Subclasses must implement this.
           populate_data_collections(input_field, label): Populates the field_dictionary, input_fields,
                                                          and labels attributes.
       """

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # These fields are required by subclasses.
        self.data_dictionary = {}
        self.field_dictionary = {}
        self.input_fields = []
        self.labels = []
        self.tabs = {}
        self.tab_names = []

    @abstractmethod
    def add_widgets(self):
        """
        Abstract method to add widgets (e.g., input fields, labels, tabs) to the frame.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def validate_data(self) -> list:
        """
        Abstract method to validate data entered into form input fields. Must be implemented
        by subclasses.

        Returns:
            A list of validation results (e.g., errors or warnings).
        """
        pass

    @abstractmethod
    def clear_fields(self):
        """
        Abstract method to clear all input fields in the frame and reset the values to
        their defaults. Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def retrieve_data(self) -> list:
        """
        Abstract method to retrieve data entered into form input fields. Must be
        implemented by subclasses.

        Returns:
            A list of retrieved data.
        """
        pass

    def populate_data_collections(self, input_field, label):
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))
