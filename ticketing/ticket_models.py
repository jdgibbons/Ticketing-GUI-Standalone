from dataclasses import dataclass, field
from typing import List, Tuple


# ==========================================
# 1. HELPER DATA CLASSES (Tiers, etc.)
# ==========================================

@dataclass
class ImageTier:
    """Used for Instants -> Images and Picks -> Images"""
    number: int
    quantity: int
    is_unique: bool


@dataclass
class ShadedTier:
    """Used for Shaded tabs (Holds and Instants)"""
    suffix: str
    color: str
    is_full: bool
    base_image: str
    pi_enabled: bool = False  # Only used in Holds -> Shaded
    numbers: List[str] = field(default_factory=list)


# ==========================================
# 2. BASE TICKET HIERARCHY
# ==========================================

@dataclass
class Ticket:
    """Base class for all ticket types."""
    quantity: int = 0
    type_name: str = ""

    @property
    def total_quantity(self) -> int:
        return self.quantity


# --- LEVEL 2: FRAME CATEGORIES ---

@dataclass
class NonWinnerTicket(Ticket):
    """Base for items in the NonwinnersFrame."""
    pass


@dataclass
class InstantTicket(Ticket):
    """Base for items in the InstantsFrame."""
    pass


@dataclass
class HoldTicket(Ticket):
    """Base for items in the HoldsFrame."""
    pass


@dataclass
class PickTicket(Ticket):
    """Base for items in the PicksFrame."""
    pass


# ==========================================
# 3. CONCRETE IMPLEMENTATIONS (The Tabs)
# ==========================================

# === HOLD SUBCLASSES ===

@dataclass
class HoldBallsTicket(HoldTicket):
    type_name = "Balls"
    bingos_per_ticket: int = 0
    spots_per_ticket: int = 0
    pool_size: int = 0
    free_spots: List[int] = field(default_factory=list)
    use_downlines: bool = False
    shazams: int = 0
    sort_balls: bool = False
    base_image: str = ""
    match_bbs: bool = False
    non_image_mode: bool = False
    # List of tuples: (color, amount)
    additional_holds: List[Tuple[str, int]] = field(default_factory=list)
    iterations: int = 1

    @property
    def total_quantity(self) -> int:
        """
        Calculates total tickets.
        Logic: (Base Quantity * Iterations) + Sum(Additional Holds)
        """
        # Multiply the base quantity by the number of iterations
        total = self.quantity * self.iterations

        # Add the quantity of every additional hold (these are NOT multiplied by iterations)
        # item is a tuple: (name, quantity)
        for _, amount in self.additional_holds:
            total += amount

        return total


@dataclass
class HoldBingosTicket(HoldTicket):
    # Lists of counts [1, 2, 3, 4] for each type
    dns_counts: List[int] = field(default_factory=list)
    ds_counts: List[int] = field(default_factory=list)
    sns_counts: List[int] = field(default_factory=list)
    ss_counts: List[int] = field(default_factory=list)
    # [quantity, free, double_lines]
    either_ors: List[List[int]] = field(default_factory=list)
    leading_zeroes: bool = False
    free_type: str = "Images"
    use_bingo_balls: bool = False
    extended_csv: bool = False
    columns_needed: int = 0

    @property
    def total_quantity(self) -> int:
        total = sum(self.dns_counts) + sum(self.ds_counts) + \
                sum(self.sns_counts) + sum(self.ss_counts)

        # Add Either-Ors (index 0 is quantity)
        for eo in self.either_ors:
            if eo and len(eo) > 0:
                total += eo[0]
        return total


@dataclass
class HoldCannonsTicket(HoldTicket):
    iterations: int = 0

    @property
    def total_quantity(self):
        """Standardizes the interface so Orchestrators can treat all tickets the same."""
        return self.quantity


@dataclass
class HoldFlashboardTicket(HoldTicket):
    spots: int = 0
    leading_zeroes: bool = False
    use_letters: bool = False
    use_hyphen: bool = False
    colors: List[str] = field(default_factory=list)

    @property
    def total_quantity(self):
        """Standardizes the interface so Orchestrators can treat all tickets the same."""
        return self.quantity


@dataclass
class HoldImagesTicket(HoldTicket):
    # Just a list of quantities for the 16 slots
    quantities: List[int] = field(default_factory=list)

    @property
    def total_quantity(self) -> int:
        return sum(self.quantities)


@dataclass
class HoldMatrixTicket(HoldTicket):
    pattern: List[int] = field(default_factory=list)
    base_image: str = ""
    leading_zeroes: bool = False

    # Quantity returned by base class


@dataclass
class HoldShadedTicket(HoldTicket):
    tiers: List[ShadedTier] = field(default_factory=list)
    first_num: int = 0
    last_num: int = 0
    spots: int = 0
    exclusions: str = ""
    # List of lists for image holds
    image_holds: List[List[str]] = field(default_factory=list)

    # Added for permutations
    game_perms: int = 1  # From GameInfoFrame
    split_tiers: bool = False  # New checkbox in HoldsShadedFrame
    vertical_layout: bool = False

    @property
    def total_quantity(self) -> int:
        total = 0

        # Calculate quantity from Number Tiers
        if self.tiers:
            # --- PRIORITY 1: VERTICAL MODE ---
            # Logic: In vertical mode, the total quantity equals the length of
            # a single tier's number list (since the total pool is distributed).
            if self.vertical_layout:
                total = len(self.tiers[0].numbers)

            # --- PRIORITY 2: PERMUTATIONS MODE (Split Tiers) ---
            # Logic: Total values across all tiers divided by the number of permutations.
            elif self.split_tiers and self.game_perms > 0:
                total_numbers = sum(len(t.numbers) for t in self.tiers)
                total = total_numbers / self.game_perms

            # --- PRIORITY 3: STANDARD MODE ---
            # Logic: Simple sum of all values across all tiers.
            else:
                total = sum(len(t.numbers) for t in self.tiers)

        # Add Image Holds (Fixed quantities added on top)
        for img_hold in self.image_holds:
            if len(img_hold) > 1 and img_hold[1].isdigit():
                total += int(img_hold[1])

        return int(total)

# === INSTANT SUBCLASSES ===

@dataclass
class InstantCannonsTicket(InstantTicket):
    iterations: int = 0

    @property
    def total_quantity(self):
        """Standardizes the interface so Orchestrators can treat all tickets the same."""
        return self.quantity


@dataclass
class InstantImagesTicket(InstantTicket):
    tiers: List[ImageTier] = field(default_factory=list)
    cd_tier: int = 0

    @property
    def total_quantity(self) -> int:
        return sum(tier.quantity for tier in self.tiers)


@dataclass
class InstantShadedTicket(InstantTicket):
    tiers: List[ShadedTier] = field(default_factory=list)
    first_num: int = 0
    last_num: int = 0
    spots: int = 0
    cd_tier: int = 0
    exclusions: str = ""

    @property
    def total_quantity(self) -> int:
        return sum(len(tier.numbers) for tier in self.tiers)


# === PICK SUBCLASSES ===

@dataclass
class PickImagesTicket(PickTicket):
    tiers: List[ImageTier] = field(default_factory=list)

    @property
    def total_quantity(self) -> int:
        return sum(tier.quantity for tier in self.tiers)


# === NONWINNER SUBCLASSES ===

@dataclass
class NonWinnerImagesTicket(NonWinnerTicket):
    pool_size: int = 0
    images_per_ticket: int = 0

    @property
    def total_quantity(self):
        """Standardizes the interface so Orchestrators can treat all tickets the same."""
        return self.quantity


@dataclass
class NonWinnerNumbersTicket(NonWinnerTicket):
    spots: int = 0
    first_num: int = 0
    last_num: int = 0
    exclusions: str = ""
    base_image: str = ""

    @property
    def total_quantity(self):
        """Standardizes the interface so Orchestrators can treat all tickets the same."""
        return self.quantity


# ==========================================
# 4. GENERAL CONFIGURATION MODELS
# ==========================================

@dataclass
class GameInfo:
    """Data from GameInfoFrame"""
    ups: int
    permutations: int
    sheets: int
    window_structure: str
    capacity: tuple  # (rows, cols)
    reset_pool: bool
    subflats: int
    schisms: int
    image_suffix: str


@dataclass
class NamesData:
    """Data from NamesFrame"""
    base_part: str
    file_name: str
