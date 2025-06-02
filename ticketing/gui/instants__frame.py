import ttkbootstrap as ttk

from .instants_cannons_tab import InstantsCannonsTab
from .instants_images_tab import InstantsImagesTab
from .instants_shaded_tab import InstantsShadedTab
from .ticketing__frame import TicketingFrame


class InstantsFrame(TicketingFrame):
    """
    A specific ticketing frame for managing different instant winner tickets tabs (e.g., images, shaded).

    This class inherits from TicketingFrame and uses a ttk.Notebook to organize
    different instant win tabs, such as Images, Shaded, and Cannons.

    Attributes:
        instants_shaded_tab (InstantsShadedTab): An instance of the InstantsShadedTab.
        instants_cannons_tab (InstantsCannonsTab): An instance of the InstantsCannonsTab.
        instants_images_tab (InstantsImagesTab): An instance of the InstantsImagesTab.
        notebook (ttk.Notebook): The notebook widget to hold the tabs.
        tab_selected_index (int): The index of the currently selected tab.

    Methods:
        add_widgets(): Adds the notebook and creates the tabs for each instant win type.
        validate_data() -> list: Validates the data in the currently selected tab.
        clear_fields(): Clears the input fields in all tabs.
        retrieve_data() -> list: Retrieves the data from the currently selected tab.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the InstantsFrame.

        Args:
            parent: The parent widget for this frame.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.
        """
        super().__init__(parent, *args, **kwargs)
        self.instants_shaded_tab = None
        self.instants_cannons_tab = None
        self.instants_images_tab = None
        self.tab_selected_index = 0
        self.notebook = None
        self.add_widgets()

    def add_widgets(self):
        """
        Adds tab widgets to the InstantsFrame.
        """
        # Create a Notebook widget to manage tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

        # Add Instants->Images tab
        self.instants_images_tab = InstantsImagesTab(self.notebook)  # Change to LabelFrame
        self.notebook.add(self.instants_images_tab, text='Images')
        self.tab_names.append('Images')
        self.tabs['Images'] = self.instants_images_tab

        # Add Instants->Shaded tab
        self.instants_shaded_tab = InstantsShadedTab(self.notebook)
        self.notebook.add(self.instants_shaded_tab, text='Shaded')
        self.tab_names.append('Shaded')
        self.tabs['Shaded'] = self.instants_shaded_tab

        # Add Instants->Cannons tab
        self.instants_cannons_tab = InstantsCannonsTab(self.notebook)
        self.notebook.add(self.instants_cannons_tab, text='Cannons')
        self.tab_names.append('Cannons')
        self.tabs['Cannons'] = self.instants_cannons_tab

        def tab_instant_selected(event):
            """
            Callback method to handle tab selection events.

            Args:
                event: The event object passed by the <<NotebookTabChanged>> event.
            """
            self.tab_selected_index = self.notebook.index(self.notebook.select())

        # Bind the tab change event to the tab_instant_selected method
        self.notebook.bind('<<NotebookTabChanged>>', tab_instant_selected)

    def validate_data(self) -> list:
        """
        Invokes the data validation method for the currently selected tab.

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
