import ttkbootstrap as ttk

from .nonwinners_images_tab import NonWinnersImagesTab
from .nonwinners_numbers_tab import NonWinnersNumbersTab
from .ticketing__frame import TicketingFrame


class NonwinnersFrame(TicketingFrame):
    """
    A frame for managing non-winning options tabs in the ticketing application.

    This class inherits from TicketingFrame and uses a ttk.Notebook to organize
    different non-winning options, such as Images and Numbers.

    Attributes:
        nw_numbers_frame (NonWinnersNumbersTab): An instance of the NonWinnersNumbersTab.
        nw_images_frame (NonWinnersImagesTab): An instance of the NonWinnersImagesTab.
        notebook (ttk.Notebook): The notebook widget to hold the tabs.
        tab_selected_index (int): The index of the currently selected tab.

    Methods:
        add_widgets(): Adds the notebook and creates the tabs for each non-winning option.
        validate_data() -> list: Validates the data in the currently selected tab.
        clear_fields(): Clears the input fields in all tabs.
        retrieve_data() -> list: Retrieves the data from the currently selected tab.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the NonwinnersFrame.

        Args:
            parent: The parent widget for this frame.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.
        """
        super().__init__(parent, *args, **kwargs)
        self.nw_numbers_frame = None
        self.nw_images_frame = None
        self.notebook = None
        self.tab_selected_index = 0
        self.add_widgets()

    def add_widgets(self):
        # Create a Notebook widget to manage tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

        # Add Nonwinners->Images tab
        self.nw_images_frame = NonWinnersImagesTab(self.notebook)  # Change to LabelFrame
        self.notebook.add(self.nw_images_frame, text='Images')
        self.tab_names.append('Images')
        self.tabs['Images'] = self.nw_images_frame

        # Add Nonwinners->Numbers Tab
        self.nw_numbers_frame = NonWinnersNumbersTab(self.notebook)  # Change to LabelFrame
        self.notebook.add(self.nw_numbers_frame, text='Numbers')
        self.tab_names.append('Numbers')
        self.tabs['Numbers'] = self.nw_numbers_frame

        def tab_nonwinner_selected(event):
            """
            Callback method to handle tab selection events.

            Args:
                event: The event object passed by the <<NotebookTabChanged>> event.
            """
            self.tab_selected_index = self.notebook.index(self.notebook.select())

        # Bind the tab change event to the tab_instant_selected method
        self.notebook.bind("<<NotebookTabChanged>>", tab_nonwinner_selected)

    def validate_data(self) -> list:
        """
        Validates the data in the currently selected tab.

        Returns:
            A list of validation results from the selected tab.
        """
        return self.tabs[self.tab_names[self.tab_selected_index]].validate_data()

    def clear_fields(self):
        """
        Clears the data fields in all tabs and reset them to their default values.
        """
        for tab in self.tab_names:
            self.tabs[tab].clear_fields()

    def retrieve_data(self) -> list:
        """
        Retrieves data from the currently selected tab.

        Returns:
            A list of retrieved data from the selected tab.
        """
        return self.tabs[self.tab_names[self.tab_selected_index]].retrieve_data()
