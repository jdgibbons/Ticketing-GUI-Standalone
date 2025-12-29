from typing import List, Tuple, Any
from ticketing.games.generators.base_game_generator import BaseGameGenerator
import ticketing.game_info_gui as gi
import ticketing.image_generator as ig
from ticketing.ticket_creation import uTick


class ImageGameGenerator(BaseGameGenerator):
    """
    Generator for all Image-based tickets (Instants, Picks, Holds, Non-Winners).
    Automatically selects the correct generation strategy based on the ticket_data type.
    """

    def __init__(self, game_info, addl_imgs_tracker, ticket_data, num_slots: int):
        super().__init__(game_info, addl_imgs_tracker)
        self.ticket_data = ticket_data
        self.num_slots = num_slots
        self.suffix = getattr(game_info, 'image_suffix', '')

        # Initialize batches
        self.initialize_batches()

    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        """
        Main entry point. Routes to specific logic based on data attributes.
        """
        # 1. Non-Winners (Pooled Images)
        if hasattr(self.ticket_data, 'pool_size'):
            self._generate_pooled()

        # 2. Instants / Picks (Tiered Images)
        elif hasattr(self.ticket_data, 'tiers'):
            self._generate_tiered()

        # 3. Holds (Simple Quantities)
        elif hasattr(self.ticket_data, 'quantities'):
            self._generate_simple()

        return self.batches, self.nw_pool

    def _generate_pooled(self):
        """Logic for Non-Winners (Randomized from a Pool)."""
        perms = self.game_info.permutations
        qty = self.ticket_data.quantity
        pool_size = self.ticket_data.pool_size
        ipt = self.ticket_data.images_per_ticket

        # Create image lists for ALL permutations at once using the helper
        # This handles the shuffling logic per perm
        perm_image_lists = ig.create_image_lists_from_pool_perms(
            1, pool_size, 'nonwinner', qty, ipt, self.suffix
        )

        # We assume the helper returns a list of lists (one per perm),
        # or a flat list we need to repeat.
        # *Correction based on your legacy code*: 'create_image_lists_from_pool_perms'
        # returns a single list of ticket-images. We need to regenerate or copy for perms.

        for perm_index in range(perms):
            # Regenerate unique randomness for each permutation
            current_batch_images = ig.create_image_lists_from_pool_perms(
                1, pool_size, 'nonwinner', qty, ipt, self.suffix
            )

            for img_set in current_batch_images:
                # Apply Padding
                padded_imgs = ig.add_additional_image_slots_list(self.addl_imgs_tracker, list(img_set))

                # Create Ticket (Numbers are empty for Image tickets)
                numbs = [''] * self.num_slots
                tick = uTick('', padded_imgs, numbs, perm_index + 1, 1, self.is_first)
                self.is_first = False
                self.batches[perm_index].append(tick)

    def _generate_tiered(self):
        """Logic for Instants and Picks (Defined Tiers)."""
        perms = self.game_info.permutations

        # Extract [Quantity, IsUnique] from the Tier objects
        amt_list = [[t.quantity, t.is_unique] for t in self.ticket_data.tiers]

        # Determine prefix based on class name
        cls_name = self.ticket_data.__class__.__name__
        is_pick = 'Pick' in cls_name
        prefix = 'pick' if is_pick else 'winner'

        # Determine prefix ('winner' vs 'pick') based on class name or type
        prefix = 'pick' if 'Pick' in self.ticket_data.__class__.__name__ else 'winner'

        # Generate the master list of images (e.g. winner01, winner02...)
        # This list is usually identical for every permutation (unless unique perms requested)
        master_imgs = ig.create_tiered_image_list_augmented(amt_list, prefix, self.suffix)

        for perm_index in range(perms):
            for img_data in master_imgs:
                # img_data is [image_name, tier_number]
                img_name = img_data[0]
                tier_num = img_data[1]

                padded_imgs = ig.add_additional_image_slots_list(self.addl_imgs_tracker, [img_name])
                numbs = [''] * self.num_slots

                tick = uTick('', padded_imgs, numbs, perm_index + 1, 1, self.is_first)

                # --- CHECK DIGIT (CD) LOGIC ---
                should_assign_cd = False

                # Get the limit from the ticket data (default to 0 if missing)
                cd_limit = getattr(self.ticket_data, 'cd_tier', 0)

                if is_pick:
                    # Picks usually ALWAYS get a CD
                    should_assign_cd = True
                elif cd_limit > 0 and tier_num <= cd_limit:
                    # Instants only get a CD if their tier is within the tracking limit
                    should_assign_cd = True

                if should_assign_cd:
                    tick.reset_cd_tier(tier_num)
                    # Picks get type 'P', Instants get type 'I'
                    cd_type = 'P' if is_pick else 'I'
                    tick.reset_cd_type(cd_type)
                # ------------------------------

                self.is_first = False
                self.batches[perm_index].append(tick)

    def _generate_simple(self):
        """Logic for Holds (Simple Quantities)."""
        perms = self.game_info.permutations
        quantities = self.ticket_data.quantities  # List of 16 integers

        # Filter out zero quantities
        valid_holds = [q for q in quantities if q > 0]

        for perm_index in range(perms):
            for index, qty in enumerate(valid_holds):
                for i in range(qty):
                    # Naming convention logic
                    if len(valid_holds) == 1:
                        img_name = f'hold{str(i + 1).zfill(2)}{self.suffix}'
                    else:
                        img_name = f'hold{str(index + 1).zfill(2)}-{str(i + 1).zfill(2)}{self.suffix}'

                    padded_imgs = ig.add_additional_image_slots_list(self.addl_imgs_tracker, [img_name])
                    numbs = [''] * self.num_slots

                    tick = uTick('', padded_imgs, numbs, perm_index + 1, 1, self.is_first)
                    self.is_first = False
                    self.batches[perm_index].append(tick)