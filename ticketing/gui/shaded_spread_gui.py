"""
Shaded List Generator

This script creates a GUI application using Tkinter and ttkbootstrap 
that generates a list of numbers based on user-provided start, end, 
suffix, and leading zero values.  The generated list is displayed in a 
separate window and can be copied to the clipboard.
"""

import tkinter as tk
import ttkbootstrap as ttk


def create_gui():
    """
    Creates the main GUI window and its components.
    """

    def create_shaded_list():
        """
        Generates the shaded list based on user input and displays it
        in a new window. Handles input validation and error messages.
        """
        try:
            # Get values from the input fields
            start = int(start_entry.get())
            end = int(end_entry.get())
            suffix = int(suffix_entry.get())
            zeroes = zeroes_entry.get()

            # Input validation: Suffix must be between 0 and 99
            if not (0 <= suffix <= 99):
                result_label.config(text="Suffix must be between 0 and 99")  # Display error in main window
                return  # Stop execution if invalid

            # Generate the shaded list
            result_list = []
            for number in range(start, end + 1):
                new_number = number * 100 + suffix
                result_list.append(str(new_number).zfill(int(zeroes)))

            # --- Result Window Handling ---
            # Check if the result window already exists and is open
            if hasattr(create_shaded_list, "result_window") and create_shaded_list.result_window.winfo_exists():
                result_window = create_shaded_list.result_window  # Reuse existing window
                result_text = create_shaded_list.result_text
            else:  # Create a new result window
                result_window = tk.Toplevel(root)  # Create a new top-level window
                result_window.title("Shaded List Result")
                result_text = ttk.Text(result_window)  # Use themed Text widget
                result_text.pack(padx=10, pady=10)

                # --- Copy to Clipboard Function ---
                def copy_to_clipboard():
                    """Copies the generated list to the clipboard."""
                    result_window.clipboard_clear()  # Clear previous clipboard content
                    result_window.clipboard_append(result_string)  # Add current string to clipboard
                    result_window.update()  # Update clipboard
                    copy_button.config(text="Copied!")  # Visual feedback
                    copy_button.after(2000, lambda: copy_button.config(text="Copy"))  # Reset button text

                copy_button = ttk.Button(result_window, text="Copy", command=copy_to_clipboard)
                copy_button.pack(pady=(0, 10))

                # Store window and text widget as attributes of the function for reuse
                create_shaded_list.result_window = result_window
                create_shaded_list.result_text = result_text

            # Update the text box content in the result window
            result_string = f"{','.join([str(num) for num in result_list])}" # Store comma-separated string
            result_text.delete("1.0", tk.END)  # Clear previous content
            result_text.insert(tk.END, result_string)  # Insert the new list

        except ValueError:
            result_label.config(text="Invalid input. Please enter numbers.") # Display error in main window

    # --- Main Window Setup ---
    root = ttk.Window(themename="superhero")  # Use ttkbootstrap for styling
    root.title("Shaded List Generator")

    style = ttk.Style()  # Style configuration
    style.configure('.', font=('Helvetica', 10)) # Set default font for all widgets

    # --- Input Fields ---
    start_label = ttk.Label(root, text="Start:")
    start_label.grid(row=0, column=0, padx=5, pady=5)
    start_entry = ttk.Entry(root)
    start_entry.grid(row=0, column=1, padx=5, pady=5)

    end_label = ttk.Label(root, text="End:")
    end_label.grid(row=1, column=0, padx=5, pady=5)
    end_entry = ttk.Entry(root)
    end_entry.grid(row=1, column=1, padx=5, pady=5)

    suffix_label = ttk.Label(root, text="Suffix (2 digits):")
    suffix_label.grid(row=2, column=0, padx=5, pady=5)
    suffix_entry = ttk.Entry(root)
    suffix_entry.grid(row=2, column=1, padx=5, pady=5)

    zeroes_label = ttk.Label(root, text="Leading Zeroes Length")
    zeroes_label.grid(row=3, column=0, padx=5, pady=5)
    zeroes_entry = ttk.Entry(root)
    zeroes_entry.grid(row=3, column=1, padx=5, pady=5)

    # --- Button ---
    generate_button = ttk.Button(root, text="Generate", command=create_shaded_list)
    generate_button.grid(row=4, column=0, columnspan=2, pady=10)

    # --- Result Label (for error messages) ---
    result_label = ttk.Label(root, text="")  # Used to display error messages
    result_label.grid(row=5, column=0, columnspan=2, pady=5)

    root.mainloop()


if __name__ == "__main__":
    create_gui()