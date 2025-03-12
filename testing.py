import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import ttkbootstrap as ttk
from enum import Enum
from typing import List, Dict, Tuple
import logging

# Import custom modules for different frames and game information handling
from ticketing import game_info as gi
from game__info_frame import GameInfoFrame
from holds__frame import HoldsFrame
from instants__frame import InstantsFrame
from names__frame import NamesFrame
from nonwinners__frame import NonwinnersFrame
from picks__frame import PicksFrame


class TicketType(Enum):
    """Enum to define ticket types."""
    IMAGES = "Images"
    CANNONS = "Cannons"


class GUIApp:
    """Main application class to manage the GUI and its functionality."""

    def __init__(self):
        """Initialize the application state."""
        self.gui_frames: Dict[str, ttk.Frame] = {}
        self.gui_frame_labels: List[str] = []
        self.game_specs: List = []
        self.nw_specs: List = []
        self.inst_specs: List = []
        self.pick_specs: List = []
        self.hold_specs: List = []
        self.name_specs: List = []
        self.nw_type: TicketType = TicketType.IMAGES
        self.inst_type: TicketType = TicketType.IMAGES
        self.pick_type: TicketType = TicketType.IMAGES
        self.hold_type: TicketType = TicketType.IMAGES
        self.DEBUG: bool = True

        # Configure logging
        logging.basicConfig(level=logging.DEBUG if self.DEBUG else logging.INFO)

    def create_gui(self) -> None:
        """Create and display the main GUI window."""
        root = ttk.Window(themename="superhero")
        root.title("Multi-Purpose CSV Generator")

        # Configure default styles
        style = ttk.Style()
        style.configure('.', font=('Helvetica', 10))

        # Create and place GUI frames
        self.create_frame(root, GameInfoFrame, "Game Information", 0, 0)
        self.create_frame(root, NonwinnersFrame, "Nonwinners", 0, 1)
        self.create_frame(root, InstantsFrame, "Instant Winners", 1, 0)
        self.create_frame(root, PicksFrame, "Pick Tickets", 1, 1)
        self.create_frame(root, HoldsFrame, "Hold Tickets", 2, 0)
        self.create_frame(root, NamesFrame, "Names", 2, 1)

        # Create Clear and Submit buttons
        clear_button = ttk.Button(root, text="Clear", command=lambda: self.clear_fields(root))
        clear_button.grid(row=6, column=0, columnspan=2, pady=10)

        submit_button = ttk.Button(root, text="Submit", command=lambda: self.submit_data(root))
        submit_button.grid(row=7, column=0, columnspan=2, pady=10)

        root.mainloop()

    def create_frame(self, root: ttk.Window, frame_type: type, frame_text: str, row: int, column: int) -> None:
        """
        Create and place a frame of the specified type in the grid.

        Args:
            root: The parent widget.
            frame_type: The type of frame to create (e.g., GameInfoFrame, NonwinnersFrame).
            frame_text: The text to display in the frame's label.
            row: The grid row to place the frame in.
            column: The grid column to place the frame in.
        """
        frame = frame_type(root, text=frame_text, padding=10)
        frame.grid(row=row, column=column, padx=5, pady=5, sticky="nsew")
        self.gui_frames[frame_text] = frame
        self.gui_frame_labels.append(frame_text)

    def submit_data(self, root: ttk.Window) -> None:
        """Handle data submission and validation."""
        if not self.validate_data(root):
            return
        self.retrieve_data()
        self.process_data()
        self.verify_all_specifications()

    def process_data(self) -> None:
        """Process the retrieved data and prepare it for verification."""
        self.nw_type = TicketType(self.nw_specs.pop(0))
        self.inst_type = TicketType(self.inst_specs.pop(0))
        self.pick_type = TicketType(self.pick_specs.pop(0))
        self.hold_type = TicketType(self.hold_specs.pop(0))

        if self.DEBUG:
            self.print_initial_data_gathering(
                [self.game_specs, self.nw_specs, self.inst_specs, self.pick_specs, self.hold_specs, self.name_specs],
                self.hold_type, self.inst_type, self.nw_type, self.pick_type
            )

    def print_initial_data_gathering(self, gamey_data: List, holding_type: TicketType, insta_type: TicketType,
                                     now_type: TicketType, picky_type: TicketType) -> None:
        """Print the initial data gathered from the GUI frames for debugging purposes."""
        self.print_data("Nonwinners", now_type)
        self.print_data("Instant Winners", insta_type)
        self.print_data("Pick Tickets", picky_type)
        self.print_data("Hold Tickets", holding_type)
        for data in gamey_data:
            self.print_data("Game Data", data)

    @staticmethod
    def print_data(title: str, data: any) -> None:
        """Helper function to print data in a consistent format."""
        logging.debug(f"{title}: {data}")

    def verify_all_specifications(self) -> Tuple[bool, str]:
        """Verify all specifications gathered from the GUI frames."""
        inst_check = self._prepare_inst_check()
        pick_check = self._prepare_pick_check()
        hold_check = self._prepare_hold_check()

        proceed, result = gi.check_game_parameters(
            self.game_specs, self.nw_specs, [inst_check], [pick_check], hold_check, True, True
        )
        logging.debug(result)
        logging.debug(f"Proceed: {proceed}")
        return proceed, result

    def _prepare_inst_check(self) -> List:
        """Prepare instant winner data for verification."""
        if self.inst_type == TicketType.IMAGES:
            return [inst[0] for inst in self.inst_specs[0]]
        elif self.inst_type == TicketType.CANNONS:
            return [self.inst_specs[0]]
        return []

    def _prepare_pick_check(self) -> List:
        """Prepare pick ticket data for verification."""
        if self.pick_type == TicketType.IMAGES:
            return [pick[0] for pick in self.pick_specs[0]]
        return []

    def _prepare_hold_check(self) -> List:
        """Prepare hold ticket data for verification."""
        if self.hold_type == TicketType.IMAGES:
            return sum(self.hold_specs[0])
        elif self.hold_type == TicketType.CANNONS:
            return self.hold_specs[0]
        return []

    def validate_data(self, root: ttk.Window) -> bool:
        """Validate data in all GUI frames."""
        errors = []
        for label in self.gui_frame_labels:
            errors.extend(self.gui_frames[label].validate_data())
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
        return len(errors) == 0

    def clear_fields(self, root: ttk.Window) -> None:
        """Clear all fields in the GUI frames."""
        for label in self.gui_frame_labels:
            self.gui_frames[label].clear_fields()

    def retrieve_data(self) -> List[List]:
        """Retrieve data from all GUI frames and store it in instance variables."""
        self.game_specs = self.gui_frames["Game Information"].retrieve_data()
        self.nw_specs = self.gui_frames["Nonwinners"].retrieve_data()
        self.inst_specs = self.gui_frames["Instant Winners"].retrieve_data()
        self.pick_specs = self.gui_frames["Pick Tickets"].retrieve_data()
        self.hold_specs = self.gui_frames["Hold Tickets"].retrieve_data()
        self.name_specs = self.gui_frames["Names"].retrieve_data()
        return [self.game_specs, self.nw_specs, self.inst_specs, self.pick_specs, self.hold_specs, self.name_specs]


if __name__ == "__main__":
    app = GUIApp()
    app.create_gui()