import random
from typing import List, Tuple, Any

# Inherit from your new base class
from .base_game_generator import BaseGameGenerator

# Import your Data Models and Game Info
import ticketing.game_info_gui as gi  # Assuming this is where AddImages enum lives
import ticketing.image_generator as ig
# You may need to adjust these imports based on where you store these specific functions now
from ticketing.ticket_creation import create_shaded_ticket, generate_balanced_positions, uTick


class ShadedGameGenerator(BaseGameGenerator):
    """
    Generator logic for Shaded Tickets (Hold/Instant/Pick).
    Handles both Vertical (Stacked) and Standard (Horizontal) generation modes.
    """

    def __init__(self, game_info, addl_imgs_tracker, ticket_data, num_slots: int, num_nw_images: int = 1):
        """
        Args:
            game_info: Global game settings object.
            addl_imgs_tracker: The 'gi.AddImages' object used to TRACK available images.
            ticket_data: The HoldShadedTicket data model containing tiers, colors, etc.
            num_slots: Total number of slots (Spots + Filler).
            num_nw_images: The count of images on a standard Non-Winning ticket.
                           Required to calculate padding for shaded tickets.
        """
        super().__init__(game_info, addl_imgs_tracker)

        self.ticket_data = ticket_data
        self.num_slots = num_slots
        self.num_nw_images = num_nw_images

        # Calculate 'Additional Numbers' (Filler spots)
        # This is separate from 'Additional Images'
        self.addl_nums = num_slots - ticket_data.spots

        # Suffix logic (Defaults to "13" or derived dynamically if needed)
        self.suffix = getattr(game_info, 'image_suffix', '')

        self.exclusions = []
        self.initialize_batches()

    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        """
        Main execution flow.
        Returns:
            Tuple containing:
            1. The batches of tickets (one list per permutation)
            2. The updated pool of non-winning numbers
        """
        self._prepare_exclusions()

        # 1. Generate the main Ticket Batches
        if self.ticket_data.vertical_layout and self.ticket_data.tiers:
            self._generate_vertical()
        else:
            self._generate_standard()

        # 2. Add Fixed 'Additional Image Holds' (The static ones defined in the 'Images' box)
        self._generate_fixed_image_holds()

        return self.batches, self.nw_pool

    def _prepare_exclusions(self):
        """Parses the exclusions string and appends tier suffixes."""
        raw = self.ticket_data.exclusions
        self.exclusions = raw.split(',') if raw else []

        for tier in self.ticket_data.tiers:
            if tier.suffix:
                self.exclusions.append(tier.suffix)

        # Clean up the list ---
        # 1. Filter empty strings (x for x in exclusions if x)
        # 2. Convert to set to remove duplicates
        # 3. Convert back to list (and sort for consistent debugging order)
        self.exclusions = sorted(list(set(x for x in self.exclusions if x)))

    def _generate_vertical(self):
        """
        Logic for Vertical (Stacked) Tiers.
        - Validates that Tier 1 contains the Master Pool.
        - Shuffles and splits the pool across tiers for each permutation.
        """
        tiers = self.ticket_data.tiers
        # In validation, we ensured all tiers have the same numbers.
        # We take the pool from Tier 1.
        master_pool = list(tiers[0].numbers)
        perms = self.ticket_data.game_perms
        num_tiers = len(tiers)

        for perm_index in range(perms):
            # A. Shuffle the master pool so distribution changes every perm
            current_pool = master_pool[:]
            random.shuffle(current_pool)

            # B. Calculate split size
            chunk_size = len(current_pool) // num_tiers

            # C. Split the pool into chunks
            chunks = [current_pool[i:i + chunk_size]
                      for i in range(0, len(current_pool), chunk_size)]

            # D. Assign chunks to Tiers
            for i, tier in enumerate(tiers):
                if i >= len(chunks):
                    break

                self._create_ticket_batch(perm_index, tier, chunks[i])

    def _generate_standard(self):
        """
        Logic for Standard (Horizontal) Tiers.
        - Iterates through all tiers.
        - Splits numbers across permutations if 'split_tiers' is checked.
        """
        perms = self.ticket_data.game_perms

        for tier in self.ticket_data.tiers:
            all_numbers = tier.numbers

            # Distribution Logic
            if self.ticket_data.split_tiers:
                # Split the 'all_numbers' list into 'perms' chunks
                dist = [[] for _ in range(perms)]
                for i, num in enumerate(all_numbers):
                    dist[i % perms].append(num)
            else:
                # No split: Every permutation gets the FULL list
                dist = [all_numbers for _ in range(perms)]

            for perm_index in range(perms):
                self._create_ticket_batch(perm_index, tier, dist[perm_index])

    def _calculate_padding_values(self) -> Tuple[Any, Any]:
        """
        Calculates the 'Prior' and 'Post' padding values for image slots.

        Logic:
        - Shaded tickets (Instants/Holds) generally have 1 image slot.
        - Prior: Always NoneAdded.
        - Post: If the game uses >1 NW image, we need padding (Post = Num_NW_Images).
                Otherwise NoneAdded.
        """
        prior = gi.AddImages.NoneAdded
        post = gi.AddImages.NoneAdded

        if self.num_nw_images > 1:
            post = self.num_nw_images

        return prior, post

    def _create_ticket_batch(self, perm_index: int, tier, numbers: List[str]):
        """
        Creates tickets for a specific tier and set of numbers.
        Calculates image padding dynamically based on NW image count.
        """
        # 1. Define Base Image
        base_name = f"{tier.base_image}{self.suffix}" if tier.base_image else ""
        active_images = [base_name] if base_name else []

        # 2. Calculate Padding
        prior, post = self._calculate_padding_values()

        # 3. Generate Image Slots (Using the NEW list method)
        imgs = ig.add_additional_image_slots_list(
            [prior, post],
            active_images
        )

        # 4. Calculate Positions
        position_list = generate_balanced_positions(len(numbers), self.ticket_data.spots)

        # 5. Generate Tickets
        for i, shade_val in enumerate(numbers):
            pos = position_list[i]

            self.nw_pool, ticket = create_shaded_ticket(
                self.addl_nums, tier.color, self.exclusions,
                self.ticket_data.first_num, tier.is_full, imgs,
                self.is_first, self.ticket_data.last_num,
                self.nw_pool, shade_val, self.ticket_data.spots,
                forced_position=pos, pi=tier.pi_enabled
            )

            self.is_first = False
            self.batches[perm_index].append(ticket)

    def _generate_fixed_image_holds(self):
        """
        Handles the 'Addl. Holds' box (bottom of UI).
        These are standard image blocks appended to every permutation.
        """
        nummies = [''] * (self.addl_nums + self.ticket_data.spots)
        perms = self.ticket_data.game_perms

        for hold in self.ticket_data.image_holds:
            # hold format: ['Name', 'Quantity', 'etc...']
            if len(hold) >= 2:
                base_name = hold[0]
                amt = int(hold[1])

                for perm_index in range(perms):
                    for i in range(amt):
                        img_name = f'{base_name}{str(i + 1).zfill(2)}{self.suffix}'

                        prior, post = self._calculate_padding_values()

                        # Using the NEW list method
                        imgs = ig.add_additional_image_slots_list(
                            [prior, post],
                            [img_name]
                        )

                        tick = uTick('', imgs, nummies, 1, 1, self.is_first)
                        self.batches[perm_index].append(tick)
                        self.is_first = False