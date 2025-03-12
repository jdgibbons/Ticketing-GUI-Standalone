import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk

from ticketing import game_info as gi

from result_message_box import ResultMessageBox

from game__info_frame import GameInfoFrame
from holds__frame import HoldsFrame
from instants__frame import InstantsFrame
from names__frame import NamesFrame
from nonwinners__frame import NonwinnersFrame
from picks__frame import PicksFrame
from helpers import select_game_method
from shaded_spread_gui import create_gui as shaded_gui

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
    global gui_frames, gui_frame_labels
    root = ttk.Window(themename="superhero")
    root.title("Multi-Purpose CSV Generator")
    # Configure default styles to increase font size globally
    style = ttk.Style()
    style.configure('.', font=('Helvetica', 10))

    add_menubar(root)

    # Create Gui Frames
    add_frames(root)

    # Create Clear button with padding and styling
    clear_button = ttk.Button(root, text="Clear", command=lambda: clear_fields(root))
    clear_button.grid(row=6, column=0, columnspan=2, pady=10)

    # Create Submit button with padding and styling
    submit_button = ttk.Button(root, text="Submit", command=lambda: submit_data(root) if validate_data(root) else None)
    submit_button.grid(row=7, column=0, columnspan=2, pady=10)

    root.mainloop()


def add_menubar(root):
    # --- Menu Bar Creation ---
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
        if hold_type == "Bingos" and 'BB' in hold_specs:
            hold_type = "BBalls"
            hold_specs.remove('BB')
        create_method = select_game_method(nw_type[:1].upper(), inst_type[:1].upper(),
                                           pick_type[:1].upper(), hold_type[:2].upper())
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
    print(f'Nonwinners: {now_type}')
    print(f'Instant Winners: {insta_type}')
    print(f'Pick Tickets: {picky_type}')
    print(f'Hold Tickets: {holding_type}')
    for data in gamey_data:
        print(data)


def verify_all_specifications():
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs, \
        inst_type, pick_type, hold_type, nw_type
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
    pick_check = []
    if pick_type == "Images":
        for pick in pick_specs[0]:
            pick_check.append(pick[0])

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

    proceed, result = gi.check_game_parameters(game_specs, nw_specs, [inst_check], [pick_check],
                                               hold_check, True, True)
    print(result)
    print(proceed)
    return proceed, result


def validate_data(root):
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
    gui_frames["Game Information"].clear_fields()
    gui_frames["Nonwinners"].clear_fields()
    gui_frames["Instant Winners"].clear_fields()
    gui_frames["Pick Tickets"].clear_fields()
    gui_frames["Hold Tickets"].clear_fields()
    gui_frames["Names"].clear_fields()


def retrieve_data():
    global game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs
    game_specs = gui_frames["Game Information"].retrieve_data()
    nw_specs = gui_frames["Nonwinners"].retrieve_data()
    inst_specs = gui_frames["Instant Winners"].retrieve_data()
    pick_specs = gui_frames["Pick Tickets"].retrieve_data()
    hold_specs = gui_frames["Hold Tickets"].retrieve_data()
    name_specs = gui_frames["Names"].retrieve_data()
    return [game_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs]


if __name__ == "__main__":
    create_gui()
