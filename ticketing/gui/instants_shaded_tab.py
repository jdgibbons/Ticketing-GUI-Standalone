import re
import ttkbootstrap as ttk

from .ticketing__notebook_tab import TicketingNotebookTab
from ticketing.ticket_models import InstantShadedTicket, ShadedTier


class InstantsShadedTab(TicketingNotebookTab):
    """
        A tab for managing shaded ticketing data within the instants ticketing notebook.
        (Instants -> Shaded)

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
        tier numbers, suffixes, colors, base values, and full/partial indicators.
        It also includes fields for first/last numbers, spots, CD Tier, and exclusions.
        """

        # Create labels for the tiered, shaded number data
        # Tier
        tier_label = ttk.Label(self, text="Tier")
        tier_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # Numbers (numbers to be shaded)
        numbers_label = ttk.Label(self, text="Numbers")
        numbers_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        # Suffix of the shaded numbers
        suffix_label = ttk.Label(self, text="Suffix")
        suffix_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        # Color (font color of shading)
        color_label = ttk.Label(self, text="Color")
        color_label.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        # Base (name of base image, if any)
        base_label = ttk.Label(self, text="Base")
        base_label.grid(row=0, column=4, sticky="w", padx=5, pady=5)
        # Full shading or not (suffix only)
        full_label = ttk.Label(self, text="Full")
        full_label.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        # Create tier-specific input fields
        for i in range(1, 6):
            # Label containing tier level
            tier_label = ttk.Label(self, text=f"{i}")
            tier_label.grid(row=i, column=0, sticky="w", padx=5, pady=5)

            # Add Numbers entry box and add as 'numbers' + tier level to the collections
            numbers_entry = ttk.Entry(self, width=20)
            numbers_entry.grid(row=i, column=1, sticky="w", padx=5, pady=5)
            numbers_entry.insert(0, "")
            field_name = f"numbers{i}"
            self.populate_data_collections_with_text(numbers_entry, field_name)

            # Add Suffix entry box and add as 'suffix' + tier level to the collections
            suffix_entry = ttk.Entry(self, width=5)
            suffix_entry.grid(row=i, column=2, sticky="w", padx=5, pady=5)
            field_name = f"suffix{i}"
            self.populate_data_collections_with_text(suffix_entry, field_name)

            # Add Color entry box and add as 'color' + tier level to the collections
            color_entry = ttk.Entry(self, width=5)
            color_entry.grid(row=i, column=3, sticky="w", padx=5, pady=5)
            field_name = f"color{i}"
            self.populate_data_collections_with_text(color_entry, field_name)

            # Add Base entry box and add as 'base' + tier level to the collections
            base_entry = ttk.Entry(self, width=5)
            base_entry.grid(row=i, column=4, sticky="w", padx=5, pady=5)
            field_name = f"base{i}"
            self.populate_data_collections_with_text(base_entry, field_name)

            # Add Full checkbox and add as 'full' + tier level to the collections
            full_checkbutton = ttk.Checkbutton(self)
            full_checkbutton.grid(row=i, column=5, sticky="w", padx=5, pady=5)
            field_name = f"full{i}"
            self.populate_data_collections_with_text(full_checkbutton, field_name)

        # Additional labels and fields
        # Add First label and entry box (lowest nonwinning number) and add the box
        # as 'first' to the collections.
        first_label = ttk.Label(self, text="First")
        first_label.grid(row=1, column=6, sticky="w", padx=5, pady=5)
        first_entry = ttk.Entry(self, width=7)
        first_entry.grid(row=1, column=7, sticky="w", padx=5, pady=5)
        first_entry.insert(0, "101")
        self.populate_data_collections_with_text(first_entry, "first")

        # Add Last label and entry box (highest nonwinning number) and add the box
        # as 'last' to the collections.
        last_label = ttk.Label(self, text="Last")
        last_label.grid(row=2, column=6, sticky="w", padx=5, pady=5)
        last_entry = ttk.Entry(self, width=7)
        last_entry.grid(row=2, column=7, sticky="w", padx=5, pady=5)
        last_entry.insert(0, "9999")
        self.populate_data_collections_with_text(last_entry, "last")

        # Add Spots label and entry box (total number of integers per ticket)
        # and add the box as 'spots' to the collections.
        spots_label = ttk.Label(self, text="Spots")
        spots_label.grid(row=3, column=6, sticky="w", padx=5, pady=5)
        spots_entry = ttk.Entry(self, width=5)
        spots_entry.grid(row=3, column=7, sticky="w", padx=5, pady=5)
        spots_entry.insert(0, "5")
        self.populate_data_collections_with_text(spots_entry, "spots")

        # Add CD Tier label and entry box (highest tier level a cd is needed)
        # and add the box as 'cd_tier' to the collections.
        cd_tier_label = ttk.Label(self, text="CD Tier")
        cd_tier_label.grid(row=4, column=6, sticky="w", padx=5, pady=5)
        cd_tier_entry = ttk.Entry(self, width=5)
        cd_tier_entry.grid(row=4, column=7, sticky="w", padx=5, pady=5)
        cd_tier_entry.insert(0, "0")
        self.populate_data_collections_with_text(cd_tier_entry, "cd_tier")

        # Add Exclusions label and entry box (suffixes to be excluded from nonwinning
        # numbers) and add the box as 'spots' to the collections.
        exclusions_label = ttk.Label(self, text="Exclusions")
        exclusions_label.grid(row=5, column=6, sticky="w", padx=5, pady=5)
        exclusions_entry = ttk.Entry(self, width=15)
        exclusions_entry.grid(row=5, column=7, sticky="w", padx=5, pady=5)
        self.populate_data_collections_with_text(exclusions_entry, "exclusions")

    def validate_data(self) -> list:
        """
        Validates the data contained in the tab.

        Checks for various input errors, including:
        - First, Last, CD Tier: Must be non-negative integers.
        - Spots: Must be a non-negative integer.
        - Exclusions: Must be a comma-separated list of two-digit integers.
        - Numbers: Must be a comma-separated list of integers.
        - Suffix: Must be a two-digit integer.
        - Color/Base: Must contain only letters, numbers, and hyphens.

        Returns:
            list: A list of error messages. If there are no errors, the list is empty.
        """

        self.create_data_dictionary()
        number_boxes = r"numbers\d+"
        suffix_boxes = r"suffix\d+"
        color_boxes = r"(color|base)\d+"
        messages = []
        for key in self.data_dictionary:
            # Check first, last, or cd tier
            if key in ["first", "last", "cd_tier"]:
                if not self.data_dictionary[key].isdigit() or int(self.data_dictionary[key]) < 0:
                    messages.append(f"Instants -> Shaded: '{key.title().replace('_', ' ')}'"
                                    f" must contain a non-negative integer.")
            # Check spots
            elif key in ["spots"]:
                if (self.data_dictionary[key] == ""
                        or (not self.data_dictionary[key].isdigit() or int(self.data_dictionary[key]) < 0)):
                    messages.append(f"Instants -> Shaded: '{key.title()}' must contain a non-negative integer.")
            # Check exclusions
            elif key == "exclusions":
                if (self.data_dictionary[key] != ''
                        and not re.fullmatch(r"^(\d{2},)*\d{2}$", self.data_dictionary[key])):
                    messages.append(f"Instants -> Shaded: '{key.title()}' must be numbers separated by commas.")
            # Check shaded numbers
            elif re.match(number_boxes, key):
                if (self.data_dictionary[key] != ""
                        and not re.fullmatch(r'^[0-9,]*$', self.data_dictionary[key])):
                    messages.append(f"Instants -> Shaded: '{key.title()}' must be integers separated by commas.")
            # Check suffix
            elif re.match(suffix_boxes, key):
                if (self.data_dictionary[key] != ""
                        and not re.fullmatch(r"^(\d\d)", self.data_dictionary[key])):
                    messages.append(f"Instants -> Shaded: '{key.title()}' must contain"
                                    f" a two-integer suffix, e.g. 00 or 13.")
            # Check color
            elif re.match(color_boxes, key):
                if (self.data_dictionary[key] != ""
                        and not re.fullmatch(r'([a-zA-Z0-9\-]*)', self.data_dictionary[key])):
                    messages.append(f"Instants -> Shaded: '{key.title()}' must contain only"
                                    f" letters, numbers, and hyphens.")
        # Return error messages.
        return messages

    def create_data_dictionary(self):
        """
        This method updates the `data_dictionary` with the current values from the input fields,
        including checkboxes and entry fields.
        """

        self.data_dictionary.clear()
        main_checks = r"(full)\d+"
        for key in self.field_dictionary:
            if re.match(main_checks, key):
                self.data_dictionary[key] = self.field_dictionary[key].instate(['selected'])
            else:
                self.data_dictionary[key] = self.field_dictionary[key].get()

    def create_defaults(self):
        """
        Populates the defaults dictionary. Currently, no defaults are explicitly set
        in this class, so this method does nothing. If you wanted to set defaults,
        you would do it here.
        """

        pass

    def clear_fields(self):
        """
        This method resets all input fields, including tier numbers, suffixes, colors, and other settings,
        to their default values.
        """

        # Cycle through the tiers and reset the related values.
        for i in range(1, 6):
            # Reset entry boxes to empty.
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
            # Set full checkbox to unselected.
            key = f"full{i}"
            self.field_dictionary[key].state(['!selected'])
        # Reset other entry boxes to their initial values.
        self.field_dictionary["first"].delete(0, ttk.END)
        self.field_dictionary["first"].insert(0, "101")
        self.field_dictionary["last"].delete(0, ttk.END)
        self.field_dictionary["last"].insert(0, "9999")
        self.field_dictionary["spots"].delete(0, ttk.END)
        self.field_dictionary["spots"].insert(0, "5")
        self.field_dictionary["cd_tier"].delete(0, ttk.END)
        self.field_dictionary["cd_tier"].insert(0, "0")
        self.field_dictionary["exclusions"].delete(0, ttk.END)
        self.field_dictionary["exclusions"].insert(0, "")

    def retrieve_data(self) -> InstantShadedTicket:
        tier_list = []
        for i in range(1, 6):
            num_str = self.data_dictionary[f"numbers{i}"]
            if num_str:
                tier_list.append(ShadedTier(
                    numbers=[int(x) for x in num_str.split(",")],
                    suffix=self.data_dictionary[f"suffix{i}"],
                    color=self.data_dictionary[f"color{i}"],
                    is_full=self.data_dictionary[f"full{i}"],
                    base_image=self.data_dictionary[f"base{i}"],
                    pi_enabled=False  # Not used in Instants
                ))

        return InstantShadedTicket(
            tiers=tier_list,
            first_num=int(self.data_dictionary["first"]),
            last_num=int(self.data_dictionary["last"]),
            spots=int(self.data_dictionary["spots"]),
            cd_tier=int(self.data_dictionary["cd_tier"]),
            exclusions=self.data_dictionary["exclusions"]
        )


def parse_suffixes(images_string):
    """
    This function splits the suffixes string into a list of lists, where each sublist
    contains the parsed suffix data.

    Args:
        images_string (str): The suffixes string to parse.

    Returns:
        list: A list of lists containing parsed suffix data.
    """
    initial_parse = images_string.split(";")
    image_list = []
    for entry in initial_parse:
        if entry != "":
            image_list.append(entry.split(","))
    return image_list
