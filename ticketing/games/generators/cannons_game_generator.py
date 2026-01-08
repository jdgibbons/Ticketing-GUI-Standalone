from typing import List, Tuple, Any
from ticketing.games.generators.base_game_generator import BaseGameGenerator
from ticketing.universal_ticket import UniversalTicket as uTick
import ticketing.image_generator as ig


class CannonsGameGenerator(BaseGameGenerator):
    """
    Generator for 'Cannons' style tickets (Iterative Images).

    Logic:
        - Image names change based on the Permutation (e.g. hold01, hold02).
        - Can generate Sequential images (hold01-01, hold01-02) OR 
          Repeated images (winner01, winner01) depending on the ticket type.
    """

    def __init__(self, game_info, addl_imgs_tracker, ticket_data, num_slots: int):
        super().__init__(game_info, addl_imgs_tracker)
        self.ticket_data = ticket_data
        self.num_slots = num_slots
        self.suffix = getattr(game_info, 'image_suffix', '')
        self.initialize_batches()

    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        perms = self.game_info.permutations

        # Determine Mode based on Ticket Type name
        # Legacy Logic: 
        #   HoldCannons = Sequential (hold01-01, hold01-02)
        #   InstantCannons = Repeated (winner01, winner01)
        cls_name = self.ticket_data.__class__.__name__
        is_instant = 'Instant' in cls_name

        # Determine Base Name
        # Legacy defaults: 'hold' for Holds, 'winner' for Instants
        base_prefix = 'winner' if is_instant else 'hold'

        qty = self.ticket_data.quantity

        for perm_index in range(perms):
            # 1. Determine Prefix for this Permutation (e.g. hold01 or winner01)
            # Legacy uses zfill(2) for the permutation number
            current_perm_str = str(perm_index + 1).zfill(2)

            # 2. Generate Image List
            if is_instant:
                # INSTANT LOGIC: Repeated same image (winner01, winner01, ...)
                # Matches legacy: ig.create_image_list_of_same_image(...)
                full_image_name = f"{base_prefix}{current_perm_str}"
                img_list = ig.create_image_list_of_same_image(qty, full_image_name, self.suffix)
            else:
                # HOLD LOGIC: Sequential images (hold01-01, hold01-02, ...)
                # Matches legacy: ig.create_prefixed_images(..., f'hold{perm}-')
                # Note: create_prefixed_images handles the suffix logic internally usually, 
                # but we construct the prefix specifically here.
                prefix = f"{base_prefix}{current_perm_str}-"
                img_list = ig.create_prefixed_images(1, qty, prefix, True, self.suffix)

            # 3. Create Tickets
            for img_name in img_list:
                # Add Padding
                # Note: legacy passes [tick_img] as a list to add_additional_image_slots
                padded_imgs = ig.add_additional_image_slots_list(self.addl_imgs_tracker, [img_name])

                # Empty Number Slots (to align with Non-Winners)
                numbs = [''] * self.num_slots

                tick = uTick(
                    tkt='',
                    imgs=padded_imgs,
                    numbs=numbs,
                    p=perm_index + 1,
                    u=1,
                    is_first=self.is_first
                )

                self.is_first = False
                self.batches[perm_index].append(tick)

        # Cannons don't typically consume from the Number Pool, so we return it unchanged
        return self.batches, self.nw_pool