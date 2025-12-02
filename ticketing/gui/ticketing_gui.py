import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from typing import Optional
from ticketing.ticket_models import GameInfo, Ticket, NamesData

from ticketing import game_info_gui as gi
from ticketing.game_registry import get_game_creator

from .result_message_box import ResultMessageBox

from .game__info_frame import GameInfoFrame
from .holds__frame import HoldsFrame
from .instants__frame import InstantsFrame
from .names__frame import NamesFrame
from .nonwinners__frame import NonwinnersFrame
from .picks__frame import PicksFrame
# from .helpers import select_game_method
from .shaded_spread_gui import create_gui as shaded_gui
from ticketing.ticket_models import (
    # Categories
    InstantImagesTicket, InstantCannonsTicket, InstantShadedTicket,
    PickImagesTicket,
    HoldImagesTicket, HoldCannonsTicket, HoldFlashboardTicket, HoldMatrixTicket,
    HoldShadedTicket, HoldBallsTicket, HoldBingosTicket,
    NonWinnerImagesTicket, NonWinnerNumbersTicket
)

gui_frames = {}
gui_frame_labels = []

game_specs: Optional[GameInfo] = None
nw_specs: Optional[Ticket] = None
inst_specs: Optional[Ticket] = None
pick_specs: Optional[Ticket] = None
hold_specs: Optional[Ticket] = None
name_specs: Optional[NamesData] = None

nw_type = ""
inst_type = ""
pick_type = ""
hold_type = ""

output_folder = ''
DEBUG = False


def create_gui():
    """
    Creates and initializes the graphical user interface (GUI) for the
    Multi-Purpose CSV Generator application.

    This function sets up the main application window, applies global
    default styles for the UI, initializes GUI frames, and adds buttons such
    as Clear and Submit with appropriate commands and styling. It also
    incorporates a menu bar and sets the main event loop to keep the
    application running.

    :return: None
    """
    global gui_frames, gui_frame_labels
    root = ttk.Window(themename="superhero")
    root.title("Multi-Purpose CSV Generator")
    # Configure default styles to increase font size globally
    style = ttk.Style()
    style.configure('.', font=('Helvetica', 10))

    add_menubar(root)

    # Create Gui Frames
    add_frames(root)

    # Create a Clear button with padding and styling
    clear_button = ttk.Button(root, text="Clear", command=lambda: clear_fields(root))
    clear_button.grid(row=6, column=0, columnspan=2, pady=10)

    # Create the Submit button with padding and styling
    submit_button = ttk.Button(root, text="Submit", command=lambda: submit_data(root) if validate_data(root) else None)
    submit_button.grid(row=7, column=0, columnspan=2, pady=10)

    root.mainloop()


def add_menubar(root):
    """
    Adds a menu bar to the given tkinter root window. The menu bar includes various
    file menu options such as selecting an output directory, opening the Shade Helper
    tool, and exiting the application.

    :param root: The root tkinter window where the menu bar will be added.
    :type root: tkinter.Tk
    """

    def select_output_directory():
        global output_folder
        directory = filedialog.askdirectory()
        if directory:
            # Do something with the selected directory, e.g., store it in a variable
            output_folder = directory
            print("Selected output directory:", directory)
        else:
            output_folder = ''

    menubar = tk.Menu(root)
    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Select Output Directory", command=select_output_directory)
    file_menu.add_command(label="Open Shade Helper", command=shaded_gui)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=file_menu)
    root.config(menu=menubar)
    # --- End of Menu Bar Creation ---


def add_frames(root):
    """
    Adds multiple frames to the root widget using the `create_frame` function.

    This function is responsible for initializing and placing several specific
    frames within the given root widget. Each frame represents a distinct section
    or component in the application UI.

    :param root: The root widget where the frames will be added.
    :type root: tkinter.Widget
    :return: None
    """
    create_frame(root, GameInfoFrame, "Game Information", 0, 0)
    create_frame(root, NonwinnersFrame, "Nonwinners", 0, 1)
    create_frame(root, InstantsFrame, "Instant Winners", 1, 0)
    create_frame(root, PicksFrame, "Pick Tickets", 1, 1)
    create_frame(root, HoldsFrame, "Hold Tickets", 2, 0)
    create_frame(root, NamesFrame, "Names", 2, 1)


def create_frame(root, frame_type, frame_text, row, column):
    """
  Creates and places a frame of the specified type in the grid.

  Args:
    root: The parent widget.
    frame_type: The type of frame to create (e.g., GameInfoFrame, NonwinnersFrame).
    frame_text: The text to display in the frame's label.
    row: The grid row to place the frame in.
    column: The grid column to place the frame in.
  """
    global gui_frames, gui_frame_labels
    frame = frame_type(root, text=frame_text, padding=10)
    frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
    gui_frames[frame_text] = frame
    gui_frame_labels.append(frame_text)


def get_type_from_object(obj) -> str:
    """
    Maps Ticket Objects to the string identifiers expected by select_game_method.
    Returns strings like 'Images', 'Numbers', 'Cannons', 'Bingos', etc.
    """
    # NonWinners
    if isinstance(obj, NonWinnerImagesTicket): return "Images"
    if isinstance(obj, NonWinnerNumbersTicket): return "Numbers"

    # Instants
    if isinstance(obj, InstantImagesTicket): return "Images"
    if isinstance(obj, InstantCannonsTicket): return "Cannons"
    if isinstance(obj, InstantShadedTicket): return "Shaded"

    # Picks
    if isinstance(obj, PickImagesTicket): return "Images"

    # Holds
    if isinstance(obj, HoldImagesTicket): return "Images"
    if isinstance(obj, HoldCannonsTicket): return "Cannons"
    if isinstance(obj, HoldFlashboardTicket): return "Flashboard"
    if isinstance(obj, HoldMatrixTicket): return "Matrix"
    if isinstance(obj, HoldShadedTicket): return "Shaded"
    if isinstance(obj, HoldBallsTicket): return "Balls"
    if isinstance(obj, HoldBingosTicket): return "Bingos"

    return "Unknown"


def submit_data(root):
    """
    Orchestrates the data collection and game generation.
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder, \
        hold_type, inst_type, pick_type, nw_type

    # 1. Validate Data
    if not validate_data(root):
        return  # validate_data handles the error popup

    # 2. Retrieve Data (These are now Objects, not lists!)
    # Note: retrieve_data() updates the global variables automatically,
    # but we assign them here for clarity.
    data_bundle = retrieve_data()
    game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs = data_bundle

    # 3. Debug Printing
    # We use the helper to get readable strings because we can't just pop index 0 anymore.
    if DEBUG:
        nw_type_str = get_type_from_object(nw_specs)
        inst_type_str = get_type_from_object(inst_specs)
        pick_type_str = get_type_from_object(pick_specs)
        hold_type_str = get_type_from_object(hold_specs)
        print_initial_data_gathering(data_bundle, hold_type_str, inst_type_str, nw_type_str, pick_type_str)

    # 4. Verify Specifications (Math Checks)
    proceed, verification_output = verify_all_specifications()

    if not proceed:
        ResultMessageBox(root, "Verification Failed", verification_output)
        return

    # 5. Select the Game Method
    # We pass the full objects. The logic for "Bingos -> BBalls" is now handled inside this function.
    # We also pass game_specs as requested for future logic (e.g. checking Window Structure).
    create_method = get_game_creator(game_specs, nw_specs, inst_specs, pick_specs, hold_specs)

    if create_method is None:
        # Generate a readable error message describing the configuration
        config_desc = (f"NW: {type(nw_specs).__name__}\n"
                       f"INST: {type(inst_specs).__name__}\n"
                       f"PICK: {type(pick_specs).__name__}\n"
                       f"HOLD: {type(hold_specs).__name__}")

        ResultMessageBox(root, "Error", f"No game engine found for configuration:\n{config_desc}")
        return

    # 7. Execute Creation
    # CRITICAL NOTE: We are now passing OBJECTS, not LISTS.
    # Your 'create_method' (the backend logic) must be updated to handle these objects,
    # OR we need an adapter here to convert them back to lists.
    # Assuming we are moving forward with Objects:
    try:
        creation_output = create_method([
            game_specs,
            nw_specs,
            inst_specs,
            pick_specs,
            hold_specs,
            name_specs,
            output_folder
        ])
        final_message = f"{verification_output}\n\n{'-' * 30}\n\n{creation_output}"
        ResultMessageBox(root, "Results", str(final_message))
    except Exception as e:
        # Catch unexpected crashes (likely due to backend not expecting Objects yet)
        if DEBUG:
            raise e
        ResultMessageBox(root, "Execution Error", f"An error occurred during generation:\n{str(e)}")


def print_initial_data_gathering(gamey_data, holding_type, insta_type, now_type, picky_type):
    """
    Prints initial data gathering information including details about nonwinners,
    instant winners, pick tickets, hold tickets, and iterates over game data to print each item.

    :param gamey_data: A collection of data elements related to the game.
    :type gamey_data: list
    :param holding_type: The type of tickets that are on hold.
    :type holding_type: str
    :param insta_type: The type of instant winning tickets.
    :type insta_type: str
    :param now_type: The type of nonwinning tickets.
    :type now_type: str
    :param picky_type: The type of pick tickets.
    :type picky_type: str
    :return: None
    """
    print(f'Nonwinners: {now_type}')
    print(f'Instant Winners: {insta_type}')
    print(f'Pick Tickets: {picky_type}')
    print(f'Hold Tickets: {holding_type}')
    for data in gamey_data:
        print(data)


def verify_all_specifications():
    """
    Verifies all specifications for a gaming environment using Data Class objects.
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs

    # --- 1. CALCULATE TOTALS ---
    # We simply ask the objects for their calculated totals.
    # We wrap them in lists (e.g. [inst_total]) because that is
    # what gi.check_game_parameters currently expects.

    inst_check = [inst_specs.total_quantity]
    pick_check = [pick_specs.total_quantity]
    hold_check = hold_specs.total_quantity

    # --- 2. VALIDATE ---
    proceed, result = gi.check_game_parameters(
        game_specs,
        nw_specs,
        [inst_check],
        [pick_check],
        hold_check,
        True,
        True
    )

    print(result)
    print(proceed)
    return proceed, result


def validate_data(root):
    """
    Validates the data across multiple GUI frames and displays an error message
    if validation fails. Each frame's individual `validate_data` method is called
    to collect a list of errors. If any errors are found, they are compiled into a
    message and displayed in a result message box.

    :param root: The root window or widget where the result message box
        will be displayed.
    :return: A boolean indicating whether all frames' data passed validation
        (`True`) or not (`False`).
    """
    global gui_frames, DEBUG
    errors = []
    for label in gui_frame_labels:
        errors.extend(gui_frames[label].validate_data())
    if len(errors) > 0:
        message = "Input Errors: \n\n"
        for error in errors:
            if DEBUG:
                print(error)
            message += error + "\n"
        message.rstrip("\n")
        messagebox = ResultMessageBox(root, "Error", message)
    return len(errors) == 0


def clear_fields(root):
    """
    Clears all fields within specific GUI frames.

    This function iterates over specific frames in the graphical user
    interface and clears all fields associated with them. Each frame,
    identified by its respective key in the `gui_frames` dictionary,
    is invoked with its `clear_fields` method.

    :param root: Root element of the GUI application.
    :return: None
    """
    gui_frames["Game Information"].clear_fields()
    gui_frames["Nonwinners"].clear_fields()
    gui_frames["Instant Winners"].clear_fields()
    gui_frames["Pick Tickets"].clear_fields()
    gui_frames["Hold Tickets"].clear_fields()
    gui_frames["Names"].clear_fields()


def retrieve_data():
    """
    Retrieves data from multiple GUI frames and returns a consolidated list.

    Each piece of data is gathered from the respective GUI frame by invoking
    their `retrieve_data()` method. The function globally updates specific
    variables to hold the data from each frame, allowing later access and use.

    :return: A list containing data retrieved from six specific GUI frames. The
        data corresponds to different categories including game information,
        nonwinners, instant winners, pick tickets, hold tickets, and names.
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs
    game_specs = gui_frames["Game Information"].retrieve_data()
    nw_specs = gui_frames["Nonwinners"].retrieve_data()
    inst_specs = gui_frames["Instant Winners"].retrieve_data()
    pick_specs = gui_frames["Pick Tickets"].retrieve_data()
    hold_specs = gui_frames["Hold Tickets"].retrieve_data()
    name_specs = gui_frames["Names"].retrieve_data()
    return [game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs]


if __name__ == "__main__":
    """
    This is the main entry point for the application. It creates and runs the main window.
    It is called when the script is executed directly.
    :return: None
    :rtype: NoneType
    """
    create_gui()
