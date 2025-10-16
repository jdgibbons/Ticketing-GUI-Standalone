import ttkbootstrap as ttk

from .holds_balls_tab import HoldsBallsTab
from .holds_bingos_tab import HoldsBingosTab
from .holds_cannons_tab import HoldsCannonsTab
from .holds_flashboard_tab import HoldsFlashboardTab
from .holds_images_tab import HoldsImagesTab
from .holds_matrix_tab import HoldsMatrixTab
from .holds_shaded_tab import HoldsShadedTab
from .ticketing__frame import TicketingFrame


class HoldsFrame(TicketingFrame):
    """
    A specific ticketing frame for managing different hold tickets tabs (e.g., balls, bingo).

    This class inherits from TicketingFrame and implements its abstract methods
    to create a notebook frame to contain tabs for different hold types. To add a new
    tab, simply create a new tab class and add it to the notebook. Also, add a class
    variable for the tab, create a name for it, add it to the tab_names list, and then
    add the tab to the tabs dictionary using the tab's name as the key. All data input
    and gathering is handled by the tab classes.

    Attributes:
        holds_balls_tab (HoldsBallsTab): An instance of the HoldsBallsTab.
        holds_bingo_tab (HoldsBingosTab): An instance of the HoldsBingoTab.
        holds_shaded_tab (HoldsShadedTab): An instance of the HoldsShadedTab.
        holds_matrix_tab (HoldsMatrixTab): An instance of the HoldsMatrixTab.
        holds_cannons_tab (HoldsCannonsTab): An instance of the HoldsCannonsTab.
        holds_images_tab (HoldsImagesTab): An instance of the HoldsImagesTab.
        notebook (ttk.Notebook): A notebook widget to hold the tabs.
        tab_selected_index (int): The index of the currently selected tab.

    Methods:
        add_widgets(): Adds a notebook and creates tabs for each hold type.
        validate_data() -> list: Validates the data in the currently selected tab.
        clear_fields(): Clears the input fields in all tabs.
        retrieve_data() -> list: Retrieves the data from the currently selected tab.
        set_bb_nw_pool(pool): Sets the ball/no win pool for the Balls tab.  This is a
                             specific method for the Balls tab.
    """

    def __init__(self, parent, *args, **kwargs):
        """
        Initializes the HoldsFrame.

        Args:
            parent: The parent widget for this frame.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.
        """
        super().__init__(parent, *args, **kwargs)
        self.holds_balls_tab = None
        self.holds_bingo_tab = None
        self.holds_shaded_tab = None
        self.holds_matrix_tab = None
        self.holds_cannons_tab = None
        self.holds_images_tab = None
        self.holds_flashboard_tab = None
        self.notebook = None
        self.tab_selected_index = 0
        self.add_widgets()

    def add_widgets(self):
        """
        Adds tab widgets to the HoldsFrame.
        """
        # Create a Notebook widget to manage tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")  # Use grid instead of pack

        # Add Holds -> Images tab
        self.holds_images_tab = HoldsImagesTab(self.notebook)  # Change to LabelFrame
        self.notebook.add(self.holds_images_tab, text='Images')
        self.tab_names.append('Images')
        self.tabs['Images'] = self.holds_images_tab

        # Add Holds -> Balls tab (Bingo Balls)
        self.holds_balls_tab = HoldsBallsTab(self.notebook)
        self.notebook.add(self.holds_balls_tab, text='Balls')
        self.tab_names.append('Balls')
        self.tabs['Balls'] = self.holds_balls_tab

        # Add Holds -> Bingos tab (Bingo Numbers)
        self.holds_bingo_tab = HoldsBingosTab(self.notebook)
        self.notebook.add(self.holds_bingo_tab, text='Bingos')
        self.tab_names.append('Bingo')
        self.tabs['Bingo'] = self.holds_bingo_tab

        # Add Holds -> Shaded tab (Shaded Number Suffixes)
        self.holds_shaded_tab = HoldsShadedTab(self.notebook)
        self.notebook.add(self.holds_shaded_tab, text='Shaded')
        self.tab_names.append('Shaded')
        self.tabs['Shaded'] = self.holds_shaded_tab

        # Add Holds -> Matrix tab
        self.holds_matrix_tab = HoldsMatrixTab(self.notebook)
        self.notebook.add(self.holds_matrix_tab, text='Matrix')
        self.tab_names.append('Matrix')
        self.tabs['Matrix'] = self.holds_matrix_tab

        # Add Holds -> Cannons tab
        self.holds_cannons_tab = HoldsCannonsTab(self.notebook)
        self.notebook.add(self.holds_cannons_tab, text='Cannons')
        self.tab_names.append('Cannons')
        self.tabs['Cannons'] = self.holds_cannons_tab

        # Add Holds -> Flashboard tab
        self.holds_flashboard_tab = HoldsFlashboardTab(self.notebook)
        self.notebook.add(self.holds_flashboard_tab, text='Flashboard')
        self.tab_names.append('Flashboard')
        self.tabs['Flashboard'] = self.holds_flashboard_tab

        def tab_hold_selected(event):
            """
            Callback method to handle tab selection events.

            Args:
                event: The event object passed by the <<NotebookTabChanged>> event.
            """
            self.tab_selected_index = self.notebook.index(self.notebook.select())

        # Bind the tab change event to the tab_instant_selected method
        self.notebook.bind('<<NotebookTabChanged>>', tab_hold_selected)

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

    def set_bb_nw_pool(self, pool):
        """
        Sets the `bb_nw_pool` (size of the nonwinner image pool) attribute in the "Balls"
        tab if it is the currently selected tab. I'll probably remove this method later and
        have the whole

        Args:
            pool: The value to set for the `bb_nw_pool` attribute.
        """
        if self.tab_names[self.tab_selected_index] == 'Balls':
            self.tabs['Balls'].set_bb_nw_pool(pool)
