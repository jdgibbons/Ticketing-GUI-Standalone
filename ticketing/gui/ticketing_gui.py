"""
Ticketing GUI Application
=========================

This module serves as the primary graphical user interface (GUI) entry point for the
Multi-Purpose CSV Generator. It orchestrates the entire ticket generation workflow:

1.  **UI Construction:** Builds the main window with specialized frames for collecting user input.
2.  **Data Retrieval:** Collects raw inputs from GUI fields and converts them into structured Data Objects (`Ticket` models).
3.  **Validation:** Ensures all inputs are valid (integers are positive, strings are non-empty, etc.).
4.  **Verification:** Performs mathematical checks to ensure the requested ticket quantities match the physical sheet capacity.
5.  **Execution:** dynamically selects the appropriate backend generation module based on the ticket configuration and runs it.

Dependencies:
    - tkinter / ttkbootstrap: For the window and widgets.
    - ticketing.ticket_models: For structured data transfer objects.
    - ticketing.game_registry: For mapping ticket types to backend logic.
"""

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from typing import Optional, List, Tuple, Any

# --- Internal Imports ---
from ticketing.ticket_models import GameInfo, Ticket, NamesData
from ticketing import game_info_gui as gi
from ticketing.game_registry import get_game_creator

# --- GUI Components ---
from .result_message_box import ResultMessageBox
from .game__info_frame import GameInfoFrame
from .holds__frame import HoldsFrame
from .instants__frame import InstantsFrame
from .names__frame import NamesFrame
from .nonwinners__frame import NonwinnersFrame
from .picks__frame import PicksFrame
from .shaded_spread_gui import create_gui as shaded_gui

# --- Ticket Models for Type Hinting and Checks ---
from ticketing.ticket_models import (
    # Categories
    InstantImagesTicket, InstantCannonsTicket, InstantShadedTicket,
    PickImagesTicket,
    HoldImagesTicket, HoldCannonsTicket, HoldFlashboardTicket, HoldMatrixTicket,
    HoldShadedTicket, HoldBallsTicket, HoldBingosTicket,
    NonWinnerImagesTicket, NonWinnerNumbersTicket
)

# --- Global State ---
# Stores references to the instantiated frames to allow data retrieval across functions.
gui_frames = {}
gui_frame_labels = []

# --- Data Containers ---
# These hold the structured data objects retrieved from the UI.
# They are initialized to None and populated when the user clicks 'Submit'.
game_specs: Optional[GameInfo] = None
nw_specs: Optional[Ticket] = None
inst_specs: Optional[Ticket] = None
pick_specs: Optional[Ticket] = None
hold_specs: Optional[Ticket] = None
name_specs: Optional[NamesData] = None

# --- Configuration Strings ---
# Used primarily for debugging to print the "Type" of game (e.g., "Images", "Cannons").
# Probably going away soon.
nw_type = ""
inst_type = ""
pick_type = ""
hold_type = ""

output_folder = ''
DEBUG = True


def create_gui():
    """
    Initializes and launches the main application window.

    This function performs the following setup steps:
    1.  Initializes the `ttkbootstrap` Window with the 'superhero' theme.
    2.  Configures global styles (e.g., font sizes).
    3.  Builds the Menu Bar (File > Exit, etc.).
    4.  Calls `add_frames()` to instantiate and grid the data input sections.
    5.  Adds the persistent 'Clear' and 'Submit' buttons at the bottom.
    6.  Starts the main event loop (`root.mainloop()`).
    """
    global gui_frames, gui_frame_labels
    root = ttk.Window(themename="superhero")
    root.title("Multi-Purpose CSV Generator")

    # Configure default styles to increase font size globally
    style = ttk.Style()
    style.configure('.', font=('Helvetica', 10))

    add_menubar(root)

    # Create the specialized input frames
    add_frames(root)

    # --- Control Buttons ---

    # CLEAR: Resets all fields in every frame to their default values.
    clear_button = ttk.Button(root, text="Clear", command=lambda: clear_fields(root))
    clear_button.grid(row=6, column=0, columnspan=2, pady=10)

    # SUBMIT: Triggers the validation -> retrieval -> execution pipeline.
    # Logic: It only calls `submit_data` if `validate_data` returns True.
    submit_button = ttk.Button(
        root,
        text="Submit",
        command=lambda: submit_data(root) if validate_data(root) else None
    )
    submit_button.grid(row=7, column=0, columnspan=2, pady=10)

    root.mainloop()


def add_menubar(root):
    """
    Attaches the top navigation menu to the main window.

    Menu Options:
    - **Select Output Directory:** Opens a directory picker dialog.
    - **Open Shade Helper:** Launches the standalone Shaded Spread utility.
    - **Exit:** Closes the application.

    :param root: The root tkinter window instance.
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
    Instantiates and places the six primary input frames into the main grid.

    The frames are:
    1.  **Game Information:** General settings (Ups, Sheets, Window Structure).
    2.  **Nonwinners:** Configuration for non-winning tickets.
    3.  **Instant Winners:** Configuration for instant win tickets.
    4.  **Pick Tickets:** Configuration for pick-style tickets.
    5.  **Hold Tickets:** Configuration for hold tickets (Bingos, Balls, etc.).
    6.  **Names:** File output naming conventions.

    :param root: The parent widget to attach the frames to.
    """
    create_frame(root, GameInfoFrame, "Game Information", 0, 0)
    create_frame(root, NonwinnersFrame, "Nonwinners", 0, 1)
    create_frame(root, InstantsFrame, "Instant Winners", 1, 0)
    create_frame(root, PicksFrame, "Pick Tickets", 1, 1)
    create_frame(root, HoldsFrame, "Hold Tickets", 2, 0)
    create_frame(root, NamesFrame, "Names", 2, 1)


def create_frame(root, frame_type, frame_text, row, column):
    """
    Helper function to instantiate a specific frame class and place it on the grid.

    This function also registers the frame in the global `gui_frames` dictionary,
    allowing other functions (like `retrieve_data` or `clear_fields`) to access it later.

    :param root: The parent widget.
    :param frame_type: The class reference of the frame to create (e.g., `GameInfoFrame`).
    :param frame_text: The label text for the frame border.
    :param row: Grid row index.
    :param column: Grid column index.
    """
    global gui_frames, gui_frame_labels
    frame = frame_type(root, text=frame_text, padding=10)
    frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
    gui_frames[frame_text] = frame
    gui_frame_labels.append(frame_text)


def get_type_from_object(obj) -> str:
    """
    Debug Utility: Converts a Ticket Object back into a readable string identifier.

    This is primarily used for console logging to show the user (developer) what
    kind of ticket configuration was detected (e.g., "Images", "Numbers", "Cannons").

    :param obj: A Ticket Data Object (e.g., `InstantImagesTicket`).
    :return: A string representing the ticket category (e.g., "Images").
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
    The Core Workflow Function.

    Triggered when the user clicks 'Submit'. It performs the following sequence:
    1.  **Validation:** Checks fields for basic errors (empty fields, negative numbers).
    2.  **Retrieval:** Pulls data from GUI frames into `Ticket` objects.
    3.  **Debug Logging:** Prints the gathered configuration to the console.
    4.  **Verification:** Calculates totals to ensure Ticket Count == Sheet Capacity.
    5.  **Selection:** Uses the `Game Registry` to find the correct backend module for this configuration.
    6.  **Execution:** Runs the selected game module to generate the files.
    7.  **Reporting:** Displays the final results (success or error) in a popup.

    :param root: The root window (used for parenting message boxes).
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder, \
        hold_type, inst_type, pick_type, nw_type

    # 1. Validate Data (Basic field checks)
    if not validate_data(root):
        return  # Stop if validation fails (popup already shown in `validate_data`)

    # 2. Retrieve Data (Convert GUI inputs to Data Objects)
    data_bundle = retrieve_data()
    game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs = data_bundle

    # 3. Debug Printing (Console output)
    if DEBUG:
        nw_type_str = get_type_from_object(nw_specs)
        inst_type_str = get_type_from_object(inst_specs)
        pick_type_str = get_type_from_object(pick_specs)
        hold_type_str = get_type_from_object(hold_specs)
        print_initial_data_gathering(data_bundle, hold_type_str, inst_type_str, nw_type_str, pick_type_str)

    # 4. Verify Specifications (Math/Logic Checks)
    # Checks if ticket quantities match sheet layouts and if Cannon iterations match permutations.
    proceed, verification_output = verify_all_specifications()

    if not proceed:
        ResultMessageBox(root, "Verification Failed", verification_output)
        return

    # 5. Select the Game Method (The Registry Lookup)
    # This determines WHICH python module (e.g., game_imgs_imgs_imgs_imgs.py) handles this specific
    # combination of ticket types.
    create_method = get_game_creator(game_specs, nw_specs, inst_specs, pick_specs, hold_specs)

    if create_method is None:
        # If no matching module is found in the registry, warn the user.
        config_desc = (f"NW: {type(nw_specs).__name__}\n"
                       f"INST: {type(inst_specs).__name__}\n"
                       f"PICK: {type(pick_specs).__name__}\n"
                       f"HOLD: {type(hold_specs).__name__}")

        ResultMessageBox(root, "Error", f"No game engine found for configuration:\n{config_desc}")
        return

    # 7. Execute Creation
    try:
        # Pass the bundle of Objects + Output Folder to the backend logic.
        creation_output = create_method([
            game_specs,
            nw_specs,
            inst_specs,
            pick_specs,
            hold_specs,
            name_specs,
            output_folder
        ])

        # Combine the verification breakdown with the success message
        final_message = f"{verification_output}\n\n{'-' * 30}\n\n{creation_output}"
        ResultMessageBox(root, "Results", str(final_message))
    except Exception as e:
        # If DEBUG is True, crash so we can see the Traceback in the IDE.
        # Otherwise, show a friendly error popup.
        if DEBUG:
            raise e
        ResultMessageBox(root, "Execution Error", f"An error occurred during generation:\n{str(e)}")


def print_initial_data_gathering(gamey_data, holding_type, insta_type, now_type, picky_type):
    """
    Console Helper: Prints a summary of the collected data types.
    """
    print(f'Nonwinners: {now_type}')
    print(f'Instant Winners: {insta_type}')
    print(f'Pick Tickets: {picky_type}')
    print(f'Hold Tickets: {holding_type}')
    for data in gamey_data:
        print(data)


def verify_all_specifications():
    """
    The Mathematical Gatekeeper.

    This function performs two critical checks:
    1.  **Logical Consistency:** Ensures that if 'Cannons' are used, the number of iterations
        matches the number of Game Permutations.
    2.  **Capacity Verification:** Calculates the total number of tickets (NonWinners + Instants + Picks + Holds)
        and multiplies by the number of Ups. It checks if this number equals the physical capacity
        of the requested Sheets (Sheets * Tickets per Sheet).

    :return: A tuple (Boolean, String).
             - True + Success Message if checks pass.
             - False + Error Message if checks fail.
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs

    # Safety check
    if not game_specs or not inst_specs or not pick_specs or not hold_specs:
        return False, "Data has not been retrieved properly."

    # === 1. LOGIC CHECK: CANNONS VS PERMUTATIONS ===
    game_perms = game_specs.permutations

    # Check Instant Cannons
    if isinstance(inst_specs, InstantCannonsTicket):
        if inst_specs.iterations != game_perms:
            error_msg = (
                "Configuration Error:\n"
                f"Game Permutations: {game_perms}\n"
                f"Instant Cannon Iterations: {inst_specs.iterations}\n\n"
                "For Cannons, these values must be equal."
            )
            return False, error_msg

    # Check Hold Cannons
    if isinstance(hold_specs, HoldCannonsTicket):
        if hold_specs.iterations != game_perms:
            error_msg = (
                "Configuration Error:\n"
                f"Game Permutations: {game_perms}\n"
                f"Hold Cannon Iterations: {hold_specs.iterations}\n\n"
                "For Cannons, these values must be equal."
            )
            return False, error_msg

    # === 2. CALCULATE TOTALS ===
    # We ask the Ticket Objects to calculate their own total quantities now.
    inst_check = [inst_specs.total_quantity]
    pick_check = [pick_specs.total_quantity]
    hold_check = hold_specs.total_quantity

    # === 3. VALIDATE MATH (Capacity vs Quantity) ===
    # Delegates the final math check to the logic in game_info_gui.py
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
    Iterates through every active GUI Frame and calls its specific `validate_data` method.

    If any frame reports an error (e.g., negative numbers, missing fields), this function
    collects those errors into a single list and displays them in a popup window.

    :return: True if NO errors were found, False otherwise.
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
    Resets the interface. Calls `.clear_fields()` on every registered frame.
    """
    gui_frames["Game Information"].clear_fields()
    gui_frames["Nonwinners"].clear_fields()
    gui_frames["Instant Winners"].clear_fields()
    gui_frames["Pick Tickets"].clear_fields()
    gui_frames["Hold Tickets"].clear_fields()
    gui_frames["Names"].clear_fields()


def retrieve_data():
    """
    Collects the current state of the application.

    Calls `.retrieve_data()` on every registered frame to get the latest `Ticket` objects.
    Updates the global variables (game_specs, nw_specs, etc.) and returns them as a list.

    :return: A list of Data Objects [GameInfo, NW, Inst, Pick, Hold, Names].
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
