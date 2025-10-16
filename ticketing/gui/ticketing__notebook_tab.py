import ttkbootstrap as ttk

from abc import ABC, abstractmethod


class TicketingNotebookTab(ttk.Frame):
    """
    Abstract base class for tabs within a ticketing notebook.

    This class provides a common structure and interface for all tabs that
    manage ticketing data.  Subclasses must implement the abstract methods.

    Attributes:
        name (str): The name of the tab.
        data_dictionary (dict): Stores the current data entered in the tab's fields.
        field_dictionary (dict): Maps labels or text identifiers to their corresponding input fields.
        input_fields (list): A list of all input fields in the tab.
        defaults (dict): Stores the default values for each input field.
        labels (list): A list of the labels associated with the input fields (not necessarily all).
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the TicketingNotebookTab.

        Args:
            parent: The parent widget.
            *args: Additional positional arguments for the ttk.Frame constructor.
            **kwargs: Additional keyword arguments for the ttk.Frame constructor.
        """
        super().__init__(parent, *args, **kwargs)
        self.name = ''
        self.data_dictionary = {}
        self.field_dictionary = {}
        self.input_fields = []
        self.defaults = {}
        self.labels = []

    @abstractmethod
    def add_widgets(self):
        """
        Abstract method to add widgets (labels, entry fields, etc.) to the tab.
        Subclasses must implement this method to create the tab's UI. Must be
        implemented by subclasses.
        """
        pass

    @abstractmethod
    def validate_data(self) -> list:
        """
        Abstract method to validate data entered into the input fields.
        Must be implemented by subclasses.

        Returns:
            list: A list of error messages.  An empty list indicates no errors.
        """
        pass

    @abstractmethod
    def clear_fields(self):
        """
        Abstract method to clear all input fields in the tab and reset them to
        their default values. Must be implemented by subclasses.
        """

    @abstractmethod
    def retrieve_data(self) -> list:
        """
        Abstract method to retrieve and process data from input fields. Must be
        implemented by subclasses.

        Returns:
            list: A list containing the retrieved data. The specific structure
                  of the list is determined by the subclass.
        """
        pass

    @abstractmethod
    def create_data_dictionary(self):
        """
        Abstract method to populate the data_dictionary with the current values
        from the input fields. Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def create_defaults(self):
        """
        Abstract method to populate the defaults dictionary with the default values
        for the input fields. Must be implemented by subclasses.
        """
        pass

    def populate_data_collections_with_label(self, input_field, label: ttk.Label):
        """
        Adds an input field and its associated label to the data collections.

        Args:
            input_field: The input field widget (e.g., ttk.Entry, ttk.Checkbutton).
            label (ttk.Label): The label widget associated with the input field.
        """
        self.field_dictionary[label.cget("text")] = input_field
        self.input_fields.append(input_field)
        self.labels.append(label.cget("text"))

    def populate_data_collections_with_text(self, input_field, text: str):
        """
        Adds an input field with a text identifier to the data collections.
        Used when an input field doesn't have a visible label (e.g., free spots).

        Args:
            input_field: The input field widget.
            text (str): The text identifier for the input field.
        """
        self.field_dictionary[text] = input_field
        self.input_fields.append(input_field)
        self.labels.append(text)
