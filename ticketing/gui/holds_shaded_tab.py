import re

import ttkbootstrap as ttk
from .ticketing__notebook_tab import TicketingNotebookTab


class HoldsShadedTab(TicketingNotebookTab):
    """
    A tab for managing shaded ticketing data within the holds ticketing notebook.
    (Holds -> Shaded)

    This class provides a user interface for entering and validating shaded ticket
    data, such as tier numbers, suffixes, colors, and additional settings like
    exclusions and image holds. It inherits from `TicketingNotebookTab` and
    implements the required abstract methods.

    Attributes:
        name (str): The name of the tab, set to "Shaded".
    """

    def __init__(self, parent):
        """
        Initializes the HoldsImagesTab. Sets the name and adds widgets.

        Args:
            parent: The parent widget.
        """

        super().__init__(parent)
        self.name = "Shaded"
        self.add_widgets()
        self.create_defaults()

    def add_widgets(self):
        """
        Adds widgets to the tab for entering shaded ticket data.

        This method creates a grid of labels and input fields for entering data such as
        tier numbers, suffixes, colors, base values, full/partial indicators, and PI settings.
        It also includes fields for first/last numbers, spots, exclusions, and image holds.
        """

        # Add labels for the shaded number columns
        # Tier Label
        tier_label = ttk.Label(self, text="Tier")
        tier_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # Numbers to be shaded
        numbers_label = ttk.Label(self, text="Numbers")
        numbers_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        # Suffix to be shaded
        suffix_label = ttk.Label(self, text="Suffix")
        suffix_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        # Color to be used with MPS tags
        color_label = ttk.Label(self, text="Color")
        color_label.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        # Base image name for the shaded number tickets
        base_label = ttk.Label(self, text="Base")
        base_label.grid(row=0, column=4, sticky="w", padx=5, pady=5)
        # Full number shade or just suffix
        full_label = ttk.Label(self, text="Full")
        full_label.grid(row=0, column=5, sticky="w", padx=5, pady=5)
        # Plus Image? Is an image to be placed on the shaded number?
        pi_label = ttk.Label(self, text="PI")
        pi_label.grid(row=0, column=6, sticky="w", padx=5, pady=5)

        # Create five rows for possible shaded numbers
        for i in range(1, 6):
            # Label for tier number
            tier_label = ttk.Label(self, text=f"{i}")
            tier_label.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            # Numbers entry box
            numbers_entry = ttk.Entry(self, width=20)
            numbers_entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            numbers_entry.insert(0, "")
            field_name = f"numbers{i}"
            self.populate_data_collections_with_text(numbers_entry, field_name)

            # Suffix entry box
            suffix_entry = ttk.Entry(self, width=5)
            suffix_entry.grid(row=i, column=2, sticky="w", padx=5, pady=5)
            field_name = f"suffix{i}"
            self.populate_data_collections_with_text(suffix_entry, field_name)

            # Color entry box 
            color_entry = ttk.Entry(self, width=5)
            color_entry.grid(row=i, column=3, sticky="w", padx=5, pady=5)
            field_name = f"color{i}"
            self.populate_data_collections_with_text(color_entry, field_name)

            # Base image entry box
            base_entry = ttk.Entry(self, width=5)
            base_entry.grid(row=i, column=4, sticky="w", padx=5, pady=5)
            field_name = f"base{i}"
            self.populate_data_collections_with_text(base_entry, field_name)

            # Full shading checkbox
            full_checkbutton = ttk.Checkbutton(self)
            full_checkbutton.grid(row=i, column=5, sticky="w", padx=5, pady=5)
            field_name = f"full{i}"
            self.populate_data_collections_with_text(full_checkbutton, field_name)

            # Plus image checkbox
            pi_checkbutton = ttk.Checkbutton(self)
            pi_checkbutton.grid(row=i, column=6, sticky="w", padx=5, pady=5)
            field_name = f"pi{i}"
            self.populate_data_collections_with_text(pi_checkbutton, field_name)

        # First (lowest) nonwinning number
        first_label = ttk.Label(self, text="First")
        first_label.grid(row=1, column=7, sticky="w", padx=5, pady=5)
        first_entry = ttk.Entry(self, width=7)
        first_entry.grid(row=1, column=8, sticky="w", padx=5, pady=5)
        first_entry.insert(0, "101")
        self.populate_data_collections_with_text(first_entry, "first")

        # Last (highest) nonwinner number
        last_label = ttk.Label(self, text="Last")
        last_label.grid(row=2, column=7, sticky="w", padx=5, pady=5)
        last_entry = ttk.Entry(self, width=7)
        last_entry.grid(row=2, column=8, sticky="w", padx=5, pady=5)
        last_entry.insert(0, "9999")
        self.populate_data_collections_with_text(last_entry, "last")

        # Spots, number of, entry box
        spots_label = ttk.Label(self, text="Spots")
        spots_label.grid(row=3, column=7, sticky="w", padx=5, pady=5)
        spots_entry = ttk.Entry(self, width=5)
        spots_entry.grid(row=3, column=8, sticky="w", padx=5, pady=5)
        spots_entry.insert(0, "5")
        self.populate_data_collections_with_text(spots_entry, "spots")

        # Exclusions entry box
        exclusions_label = ttk.Label(self, text="Exclusions")
        exclusions_label.grid(row=4, column=7, sticky="w", padx=5, pady=5)
        exclusions_entry = ttk.Entry(self, width=15)
        exclusions_entry.grid(row=4, column=8, sticky="w", padx=5, pady=5)
        self.populate_data_collections_with_text(exclusions_entry, "exclusions")

        # Image type holds
        images_label = ttk.Label(self, text="Addl. Holds")
        images_label.grid(row=5, column=7, sticky="w", padx=5, pady=5)
        images_entry = ttk.Entry(self, width=15)
        images_entry.grid(row=5, column=8, sticky="w", padx=5, pady=5)
        self.populate_data_collections_with_text(images_entry, "images")

    def validate_data(self) -> list:
        """
        Validates the data contained in the tab. If the data is in its default state,
        the validator ignores it.

        Checks for various input errors, including:
        - First and Last: Must be non-negative integers.
        - Spots: Must be a non-negative integer.
        - Exclusions: Must be a comma-separated list of two-digit integers.
        - Numbers: Must be a comma-separated list of integers.
        - Suffix: Must be a two-digit integer.
        - Color/Base: Must contain only letters and numbers.
        - Images: Must be a semicolon-separated list of comma-separated
                 hold names and quantities.

        Returns:
            list: A list of error messages. If there are no errors, the list is empty.
        """

        self.create_data_dictionary()
        number_boxes = r"numbers\d+"
        suffix_boxes = r"suffix\d+"
        color_boxes = r"(color|base)\d+"
        messages = []
        for key in self.data_dictionary:
            # Check if FIRST and LAST are valid, non-negative integers
            if key in ["first", "last"]:
                if not self.data_dictionary[key].isdigit() or int(self.data_dictionary[key]) < 0:
                    messages.append(f"Holds -> Shaded: '{key.title()}' must contain a non-negative integer.")

            # If there is data in the SPOTS entry box, make sure it's a non-negative integers
            elif key == "spots":
                if (self.data_dictionary[key] != ""
                        and (not self.data_dictionary[key].isdigit() or int(self.data_dictionary[key]) < 0)):
                    messages.append(f"Holds -> Shaded: '{key.title()}' must contain a non-negative integer.")

            # If there's data in the EXCLUSIONS, make sure it's populated by double-digit entries separated by commas.
            elif key == "exclusions":
                if (self.data_dictionary[key] != ''
                        and not re.fullmatch(r"^(\d{2},)*\d{2}$", self.data_dictionary[key])):
                    messages.append(f"Holds -> Shaded: '{key.title()}' must be integers separated by commas.")

            # If there's data in the NUMBERS boxes, make sure it consists only of numbers separated by commas.
            elif re.match(number_boxes, key):
                if (self.data_dictionary[key] != ""
                        and not re.fullmatch(r'^[0-9,]*$', self.data_dictionary[key])):
                    messages.append(f"Holds -> Shaded: '{key.title()}' must be integers separated by commas.")

            # If there's data in the SUFFIX box, make sure it's a two-digit number.
            elif re.match(suffix_boxes, key):
                if (self.data_dictionary[key] != ""
                        and not re.fullmatch(r"(\d\d)", self.data_dictionary[key])):
                    messages.append(f"Holds -> Shaded: '{key.title()}' must contain a two-integer"
                                    f" suffix, e.g. 00 or 13.")
            # If there's data in the COLOR or BASE entry boxes, make sure its comprised of alphanumeric characters.
            elif re.match(color_boxes, key):
                if (self.data_dictionary[key] != ""
                        and not re.fullmatch(r'([a-zA-Z0-9]*)', self.data_dictionary[key])):
                    messages.append(f"Holds -> Shaded: '{key.title()}' must contain only letters and numbers.")
            # If there's data in the IMAGES entry box, make sure it consists only of
            # alphanumerics, commas, and semicolons.
            elif key == "images":
                if (self.data_dictionary[key] != ''
                        and not re.fullmatch(r'^[a-zA-Z0-9,;]*$', self.data_dictionary[key])):
                    messages.append(f"Holds -> Shaded: '{key.title()}' must be a list of hold names and quantities"
                                    f" separated by commas and multiple entries separated by semicolons.")
        return messages

    def create_data_dictionary(self):
        """
        Populates the data_dictionary with the current values from the input fields.
        """

        self.data_dictionary.clear()
        main_boxes = r"(tier|suffix|color|base)\d+"
        main_checks = r"(full|pi)\d+"
        for key in self.field_dictionary:
            if re.match(main_boxes, key):
                self.data_dictionary[key] = self.field_dictionary[key].get()
            elif re.match(main_checks, key):
                self.data_dictionary[key] = self.field_dictionary[key].instate(['selected'])
            else:
                self.data_dictionary[key] = self.field_dictionary[key].get()

    def create_defaults(self):
        """
        Populates the defaults' dictionary. Currently, no defaults are explicitly set
        in this class, so this method does nothing.
        """
        pass

    def clear_fields(self):
        """
        Clears all input fields in the tab and resets them to their initial values.
        """

        # Cycle through the shaded numbers rows and reset the values to their defaults.
        for i in range(1, 6):
            key = f"numbers{i}"
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, "")
            key = f"suffix{i}"
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, "")
            key = f"color{i}"
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, "")
            key = f"base{i}"
            self.field_dictionary[key].delete(0, ttk.END)
            self.field_dictionary[key].insert(0, "")
            key = f"full{i}"
            self.field_dictionary[key].state(['!selected'])
            key = f"pi{i}"
            self.field_dictionary[key].state(['!selected'])
        # Reset the rest of the fields.
        self.field_dictionary["first"].delete(0, ttk.END)
        self.field_dictionary["first"].insert(0, "101")
        self.field_dictionary["last"].delete(0, ttk.END)
        self.field_dictionary["last"].insert(0, "9999")
        self.field_dictionary["spots"].delete(0, ttk.END)
        self.field_dictionary["spots"].insert(0, "5")
        self.field_dictionary["exclusions"].delete(0, ttk.END)
        self.field_dictionary["exclusions"].insert(0, "")
        self.field_dictionary["images"].delete(0, ttk.END)
        self.field_dictionary["images"].insert(0, "")

    def retrieve_data(self) -> list:
        """
        Retrieves and processes data from input fields.

        Returns:
            list: A list containing the retrieved data in a specific format:
                [
                    self.name,
                    tier_list,
                    first,
                    last,
                    spots,
                    exclusions,
                    image_holds
                ]
                where tier_list is a list of lists, each containing tier data:
                numbers, suffix, color, full, base, pi.
        """

        # Create a list of shaded number values and their associated variables.
        # Cycle through the entries and append the numbers information to the
        # tier list until an empty numbers box is found.
        tier_list = []
        for i in range(1, 6):
            if len(self.data_dictionary[f"numbers{i}"]) > 0:
                tier_list.append([
                    self.data_dictionary[f"numbers{i}"].split(','),
                    self.data_dictionary[f"suffix{i}"],
                    self.data_dictionary[f"color{i}"],
                    self.data_dictionary[f"full{i}"],
                    self.data_dictionary[f"base{i}"],
                    self.data_dictionary[f"pi{i}"]
                ])
            else:
                break

        return [
            self.name,
            tier_list,
            int(self.data_dictionary["first"]),
            int(self.data_dictionary["last"]),
            int(self.data_dictionary["spots"]),
            self.data_dictionary["exclusions"],
            parse_image_holds(self.data_dictionary["images"])
        ]


def parse_image_holds(images_string):
    initial_parse = images_string.split(";")
    image_list = []
    for entry in initial_parse:
        if entry != "":
            image_list.append(entry.split(","))
    return image_list

