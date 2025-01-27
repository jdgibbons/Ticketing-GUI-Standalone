import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk

from game_info_frame import GameInfoFrame
from nonwinners_frame import NonwinnersFrame

gui_frames = {}
gui_frame_labels = []


def create_gui():
    global gui_frames, gui_frame_labels
    root = ttk.Window(themename="superhero")
    root.title("Multi-Purpose CSV Generator")
    # Configure default styles to increase font size globally
    style = ttk.Style()
    style.configure('.', font=('Helvetica', 10))

    # Game Information Frame
    game_info_frame = GameInfoFrame(root, text="Game Information", padding=40)
    game_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    gui_frames["Game Information"] = game_info_frame
    gui_frame_labels.append("Game Information")

    # Nonwinners Frame
    nonwinners_frame = NonwinnersFrame(root, text="Nonwinners", padding=40)
    nonwinners_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
    gui_frames["Nonwinners"] = nonwinners_frame
    gui_frame_labels.append("Nonwinners")

    # Create Clear button with padding and styling
    clear_button = ttk.Button(root, text="Clear", command=lambda: clear_fields(root))
    clear_button.grid(row=6, column=0, columnspan=2, pady=10)

    # Create Submit button with padding and styling
    submit_button = ttk.Button(root, text="Submit", command=lambda: submit_data(root) if validate_data(root) else None)
    submit_button.grid(row=7, column=0, columnspan=2, pady=10)

    root.mainloop()


def submit_data(root):
    pass


def validate_data(root):
    global gui_frames
    for label in gui_frame_labels:
        errors = gui_frames[label].validate_data()
        for error in errors:
            print(error)
    pass


def clear_fields(root):
    pass


if __name__ == "__main__":
    create_gui()
