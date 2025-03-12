import ttkbootstrap as ttk

from picks_images_tab import PicksImagesTab
from ticketing__frame import TicketingFrame


class PicksFrame(TicketingFrame):
    """
    A frame for managing pick options tabs in the ticketing application.

    This class inherits from TicketingFrame and uses a ttk.Notebook to organize
    different pick options, such as Images. Currently, it only contains
    an Images tab.

    Attributes:
        notebook (ttk.Notebook): The notebook widget to hold the tabs.
        tab_selected_index (int): The index of the currently selected tab.

    Methods:
        add_widgets(): Adds the notebook and creates the tabs for pick options.
        validate_data() -> list: Validates the data in the currently selected tab.
        clear_fields(): Clears the input fields in all tabs.
        retrieve_data() -> list: Retrieves the data from the currently selected tab.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the PicksFrame.

        Args:
            parent: The parent widget for this frame.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.
        """
        super().__init__(parent, *args, **kwargs)
        self.tab_selected_index = 0
        self.notebook = None
        self.add_widgets()

    def add_widgets(self):
        """
        Adds tab widgets to the PicksFrame.
        """
        # Create a Notebook widget to manage tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

        # Add Picks->Images tab
        nw_images_frame = PicksImagesTab(self.notebook)  # Change to LabelFrame
        self.notebook.add(nw_images_frame, text='Images')
        self.tab_names.append('Images')
        self.tabs['Images'] = nw_images_frame

        def tab_picks_selected(event):
            """
            Callback method to handle tab selection events.

            Args:
                event: The event object passed by the <<NotebookTabChanged>> event.
            """
            self.tab_selected_index = self.notebook.index(self.notebook.select())

        # Bind the tab change event to the tab_instant_selected method
        self.notebook.bind("<<NotebookTabChanged>>", tab_picks_selected)

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
