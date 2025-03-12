import tkinter as tk  # Import the tkinter module for GUI components
import ttkbootstrap as ttk  # Import ttkbootstrap for themed widgets


class ResultMessageBox(tk.Toplevel):
    """
    A custom Toplevel window that displays a message to the user.

    This class creates a pop-up window with a title, a message, and an "OK" button.
    The message is displayed in a read-only text widget, and the first line of the message
    is formatted in bold.

    Attributes:
        parent (tk.Widget): The parent widget (usually the main application window).
        title (str): The title of the message box window.
        message (str): The message to be displayed in the text widget.
    """

    def __init__(self, parent, title, message):
        """
        Initializes the ResultMessageBox with a parent, title, and message.

        Args:
            parent (tk.Widget): The parent widget (usually the main application window).
            title (str): The title of the message box window.
            message (str): The message to be displayed in the text widget.
        """
        super().__init__(parent)  # Initialize the Toplevel window
        self.title(title)  # Set the title of the window

        # Create a Text widget to display the message
        text_widget = tk.Text(self, wrap="word")  # Wrap text at word boundaries
        text_widget.pack(padx=10, pady=10)  # Add padding around the text widget
        text_widget.insert("end", message)  # Insert the message into the text widget

        # Apply bold formatting to the first line of the message
        text_widget.tag_add("bold", "1.0", "1.end")  # Tag the first line
        text_widget.tag_configure("bold", font=("Helvetica", 12, "bold"))  # Configure the bold tag

        # Set the text widget to read-only mode
        text_widget.config(state="disabled")

        # Create an "OK" button to close the window
        ok_button = ttk.Button(self, text="OK", command=self.destroy)  # Button to destroy the window
        ok_button.pack(pady=10)  # Add padding below the button

        # Set focus to this window and make it modal
        self.focus_set()  # Focus on this window
        self.grab_set()  # Prevent interaction with the parent window
        parent.wait_window(self)  # Wait until this window is closed
        parent.focus_force()  # Return focus to the parent window after closing
