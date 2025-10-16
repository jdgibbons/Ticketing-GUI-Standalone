import random

# --- Configuration ---
BINGO_RANGES = {
    'B': (1, 15),
    'I': (16, 30),
    'N': (31, 45),
    'G': (46, 60),
    'O': (61, 75)
}
COLUMNS = list(BINGO_RANGES.keys())  # ['B', 'I', 'N', 'G', 'O']

NUM_CARDS_TO_GENERATE = 400

# Distribution of free spaces
FREE_SPACE_DISTRIBUTION = {
    3: 40,  # 40 cards with 3 free spaces
    2: 60,  # 60 cards with 2 free spaces
    1: 100,  # 100 cards with 1 free space
    0: 200  # 200 cards with 0 free spaces
}


# --- Helper Functions ---

def get_column_numbers(column_name, count):
    """Generates 'count' unique numbers for a given Bingo column, sorted."""
    start, end = BINGO_RANGES[column_name]
    available_numbers = list(range(start, end + 1))
    if count > len(available_numbers):
        raise ValueError(f"Cannot select {count} unique numbers from {column_name} column range {start}-{end}")

    selected = random.sample(available_numbers, count)
    selected.sort()  # Ensure numbers within a column are sorted
    return selected


def generate_card_layout_and_numbers(num_free_spaces):
    """
    Generates a card with 10 slots (numbers or None for free spaces).
    Free spaces are correctly placed such that no more than one appears per column.
    All actual numbers are sorted ascendingly across the entire card.
    """
    card_template = [None] * 10  # Initialize 10 slots for the card

    # Map each slot index to its corresponding column
    # Slot 0,1 -> B; 2,3 -> I; 4,5 -> N; 6,7 -> G; 8,9 -> O
    slot_to_column_map = [
        'B', 'B', 'I', 'I', 'N', 'N', 'G', 'G', 'O', 'O'
    ]

    # 1. Randomly select the 'num_free_spaces' columns that will contain a free space.
    # This automatically enforces "no more than one free space per column".
    fs_cols = random.sample(COLUMNS, num_free_spaces)

    # 2. For each column selected for a free space, randomly choose one of its two slots
    # to place the 'None'. The other slot will be for a number.

    # Keep track of which slots are already designated as None
    fs_slot_indices = []

    for col_name in fs_cols:
        # Find the two possible slot indices for this column
        possible_slots = [i for i, col in enumerate(slot_to_column_map) if col == col_name]

        # Randomly choose one of these two slots to be the free space
        chosen_fs_slot = random.choice(possible_slots)
        fs_slot_indices.append(chosen_fs_slot)
        card_template[chosen_fs_slot] = None  # Place None directly in the template

    # 3. Populate the remaining slots with numbers
    numbers_for_sorting = []

    for i, col_name in enumerate(COLUMNS):
        # Find the two possible slot indices for this column
        col_slot1_idx = i * 2
        col_slot2_idx = i * 2 + 1

        if col_name in fs_cols:
            # This column has one free space; it needs 1 number.
            numbers = get_column_numbers(col_name, 1)
            # Place the number in the slot that was NOT chosen for None
            if card_template[col_slot1_idx] is None:  # If slot1 is None, put number in slot2
                card_template[col_slot2_idx] = numbers[0]
            else:  # If slot2 is None, put number in slot1
                card_template[col_slot1_idx] = numbers[0]

            numbers_for_sorting.append(numbers[0])  # Add the number for global sorting

        else:
            # This column has no free space; it needs 2 numbers.
            numbers = get_column_numbers(col_name, 2)
            card_template[col_slot1_idx] = numbers[0]
            card_template[col_slot2_idx] = numbers[1]
            numbers_for_sorting.extend(numbers)  # Add both numbers for global sorting

    # 4. Sort all numbers globally.
    numbers_for_sorting.sort()

    # 5. Reconstruct the final card with sorted numbers inserted into non-None slots.
    final_card = []
    num_idx = 0
    for i in range(10):
        if card_template[i] is None:
            final_card.append(None)
        else:
            # This spot is a number. Take the next sorted number.
            final_card.append(numbers_for_sorting[num_idx])
            num_idx += 1

    return tuple(final_card)  # Use tuple for hashability for uniqueness check


# --- Main Generation Logic (Remains mostly the same) ---

def generate_bingo_cards():
    generated_cards = set()
    cards_by_free_space_count = {
        0: [],
        1: [],
        2: [],
        3: []
    }

    # Generate cards for each free space category
    for num_fs, target_count in FREE_SPACE_DISTRIBUTION.items():
        print(f"Generating {target_count} cards with {num_fs} free spaces...")
        current_count = 0
        attempts = 0
        max_attempts_per_card_type = target_count * 5000  # Increased attempts as uniqueness becomes harder

        while current_count < target_count and attempts < max_attempts_per_card_type:
            card = generate_card_layout_and_numbers(num_fs)

            # Additional check: If card generated with wrong number of FS due to logic error, skip.
            # (Shouldn't happen with current logic, but good as a safety net)
            if card.count(None) != num_fs:
                attempts += 1
                continue

            if card not in generated_cards:
                generated_cards.add(card)
                cards_by_free_space_count[num_fs].append(card)
                current_count += 1
            attempts += 1

            if attempts % 10000 == 0:
                print(f"  Attempts for {num_fs} FS: {attempts}, found: {current_count}/{target_count}")

        if current_count < target_count:
            print(
                f"WARNING: Could only generate {current_count} of {target_count} cards for {num_fs} free spaces within {max_attempts_per_card_type} attempts.")
        print(f"Finished generating {current_count} cards with {num_fs} free spaces.")

    all_cards_list = []
    for fs_count in sorted(cards_by_free_space_count.keys()):
        all_cards_list.extend(cards_by_free_space_count[fs_count])

    print(f"\nTotal unique cards generated: {len(generated_cards)}")
    return all_cards_list


# --- Execution (Remains the same, just better verification) ---

if __name__ == "__main__":
    cards = generate_bingo_cards()

    # Display some sample cards and verify properties
    print("\n--- Sample Generated Cards ---")

    # Get a few from each category if available
    sample_counts_to_display = {0: 2, 1: 2, 2: 2, 3: 2}  # How many samples to show per category

    displayed_card_counter = 0
    # Iterate through each free space count category
    for num_fs in sorted(FREE_SPACE_DISTRIBUTION.keys(), reverse=True):  # Show 3FS first for impact
        cards_in_category = [c for c in cards if c.count(None) == num_fs]

        if sample_counts_to_display[num_fs] > 0 and len(cards_in_category) > 0:
            print(f"\nCards with {num_fs} Free Spaces ({len(cards_in_category)} generated):")

            for i in range(min(sample_counts_to_display[num_fs], len(cards_in_category))):
                card = cards_in_category[i]
                print(f"  Card {displayed_card_counter + 1}: {list(card)}")
                displayed_card_counter += 1

                # --- Verification ---
                # 1. Verify ascending order of numbers
                nums_on_card = [x for x in card if x is not None]
                if not all(nums_on_card[j] <= nums_on_card[j + 1] for j in range(len(nums_on_card) - 1)):
                    print("    [ERROR: Numbers not strictly ascending!]")

                # 2. Verify no more than 1 free space per column
                fs_col_check = {}  # {col_char: count_of_fs_in_col}
                for k in range(5):  # First 5 elements of 'conceptual' first line
                    if card[k] is None:
                        col_char = COLUMNS[k]  # This index maps to column 0-4
                        fs_col_check[col_char] = fs_col_check.get(col_char, 0) + 1
                for k in range(5):  # Next 5 elements of 'conceptual' second line
                    if card[k + 5] is None:
                        col_char = COLUMNS[k]  # This index maps to column 0-4
                        fs_col_check[col_char] = fs_col_check.get(col_char, 0) + 1

                for col_char, fs_count_in_col in fs_col_check.items():
                    if fs_count_in_col > 1:
                        print(f"    [ERROR: More than one free space in column {col_char}! ({fs_count_in_col})]")

                # 3. Verify correct number of free spaces for the category
                if card.count(None) != num_fs:
                    print(f"    [ERROR: Incorrect number of free spaces! Expected {num_fs}, got {card.count(None)}]")

    print(f"\nTotal unique cards generated: {len(cards)}")
    # Double-check total count
    expected_total = sum(FREE_SPACE_DISTRIBUTION.values())
    if len(cards) != expected_total:
        print(f"WARNING: Expected {expected_total} cards but generated {len(cards)}")