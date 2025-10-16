import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk

from ticketing import game_info as gi

from .result_message_box import ResultMessageBox

from .game__info_frame import GameInfoFrame
from .holds__frame import HoldsFrame
from .instants__frame import InstantsFrame
from .names__frame import NamesFrame
from .nonwinners__frame import NonwinnersFrame
from .picks__frame import PicksFrame
from .helpers import select_game_method
from .shaded_spread_gui import create_gui as shaded_gui

gui_frames = {}
gui_frame_labels = []
game_specs = []
nw_specs = []
inst_specs = []
pick_specs = []
hold_specs = []
name_specs = []
nw_type = ""
inst_type = ""
pick_type = ""
hold_type = ""

output_folder = ''
DEBUG = True


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


def submit_data(root):
    """
    Processes the provided root object to validate, manipulate, and manage game
    specifications and run the appropriate game creation logic based on the provided
    specifications.

    :param root: The root object that provides the necessary initial data, usually
        representing a GUI structure or a configuration source.
    :return: None
    :raises ValueError: May raise if data validation or processing encounters issues.

    Detailed Steps:
    1. Validates the input data through `validate_data`.
    2. Retrieves game data if validation passes.
    3. Extracts type specifications for game parameters like non-winners, instant
       winners, picks, and holds.
    4. Handles debugging to display initial information based on global DEBUG variable.
    5. Performs verification on specifications and, if successful, re-inserts processed
       type information into corresponding global lists.
    6. Handles complex cases for "Bingos" and "Balls" hold types by adjusting types
       based on additional specifications or flags.
    7. Selects the appropriate game creation method dynamically based on game type
       and calls it with processed specifications.
    8. Displays results or error messages depending on the outcome.
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, \
        nw_type, inst_type, pick_type, hold_type, output_folder
    valley = validate_data(root)
    game_data = []
    if valley:
        game_data = retrieve_data()
    nw_type = nw_specs.pop(0)
    inst_type = inst_specs.pop(0)
    pick_type = pick_specs.pop(0)
    hold_type = hold_specs.pop(0)

    if DEBUG:
        print_initial_data_gathering(game_data, hold_type, inst_type, nw_type, pick_type)
    proceed, result = verify_all_specifications()

    if proceed:
        inst_specs.insert(0, inst_type[:1])
        nw_specs.insert(0, nw_type[:1])
        pick_specs.insert(0, pick_type[:1])
        hold_specs.insert(0, hold_type[:1])

        # # # The following block of code is a little messy, but it's to account for
        # # # special cases that require additional processing. There will probably
        # # # be additional special cases in the future, so I'm leaving it in for now.

        # If the holds are bingos but the representation will be bingo ball images,
        # set the hold type to BBalls and remove the 'BB' list element. (The hold
        # type for actual bingo balls is "Balls". This is confusing, and I should find
        # another way to represent this type of situation.)
        if hold_type == "Bingos" and 'BB' in hold_specs:
            hold_type = "BBalls"
            hold_specs.remove('BB')
        # If the holds are bingo balls, check if the images or the numbers will be used.
        # The gist of this is that the methods used to generate the winners are the same,
        # but, if the 'non-image' checkbox was checked, the 'balls' will be represented
        # as numbers rather than images. The hold type will be changed to reflect that.
        # (The boolean value in the last element of the third list is the item of interest
        # here.) Either way, delete the last element of the third list.
        elif hold_type == "Balls":
            if hold_specs[2][5]:
                hold_type = "BNumbers"
            hold_specs[2].pop()

        # Call the select_game_method, which will return a reference to the appropriate
        # create_game method from the various ticket creation modules. For the moment,
        # this is determined with the ticket types, but it could be updated to take the
        # window structure into account as well.
        create_method = select_game_method(nw_type[:1].upper(), inst_type[:1].upper(),
                                           pick_type[:1].upper(), hold_type[:2].upper())
        # If the method is not found, display an error message.
        if create_method is None:
            error_message = "Invalid game type selected.\n"
            error_message += (f"A game that uses nonwinner '{nw_type}', instant winners '{inst_type}',"
                              f" pick '{pick_type}', and {hold_type} hold tickets is not yet supported."
                              f" You need to tell John to add it to the program. Thanks! :-).")
            ResultMessageBox(root, "Error", error_message)
            return

        create_method([game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, output_folder])

    ResultMessageBox(root, "Results", result)


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
    Verifies all specifications for a gaming environment by checking instants, picks, and holds
    based on their respective types and specifications. The method first processes various types
    to ensure the correct number of tickets will be used to verify expected vs. actual ticket
    counts. It utilizes global parameters and passes them to a validation method. Outputs the
    results and whether the process should proceed.

    :return: Tuple containing a boolean `proceed` flag and the result of the
        parameter checks.
    :rtype: Tuple[bool, Any]
    """
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, \
        inst_type, pick_type, hold_type, nw_type
    # Check the instants' type, grab the appropriate number of tickets, and store it in a list.
    inst_check = []
    if inst_type == "Images":
        for inst in inst_specs[0]:
            inst_check.append(inst[0])
    elif inst_type == "Cannons":
        inst_check = [inst_specs[0]]
    elif inst_type == "Shaded":
        inst_check = []
        for inst in inst_specs[0]:
            inst_check.append(len(inst[0]))
        if len(inst_check) == 0:
            inst_check = [0]
    # Check the picks' type, grab the appropriate number of tickets, and store it in a list.
    pick_check = []
    if pick_type == "Images":
        for pick in pick_specs[0]:
            pick_check.append(pick[0])
    # Check the holds' type, grab the appropriate number of tickets, and store it in a list.'
    hold_check = []
    if hold_type in ["Images"]:
        hold_check = sum(hold_specs[0])
    elif hold_type in ["Cannons", "Flashboard", "Matrix"]:
        hold_check = hold_specs[0]
    elif hold_type == "Shaded":
        hold_check = 0
        for hold in hold_specs[0]:
            hold_check += len(hold[0])
        if len(hold_specs[5]) > 0:
            for hold_spec in hold_specs[5]:
                hold_check += int(hold_spec[1])
    elif hold_type == "Balls":
        hold_check = hold_specs[0][0] + hold_specs[2][0]
    elif hold_type == "Bingos":
        hold_check = 0
        for i in range(4):
            hold_check += sum(hold_specs[i])
        for hold in hold_specs[4]:
            hold_check += hold[0]

    # Send the values off to the validation method to verify expected vs. actual ticket counts.
    proceed, result = gi.check_game_parameters(game_specs, nw_specs, [inst_check], [pick_check],
                                               hold_check, True, True)
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
