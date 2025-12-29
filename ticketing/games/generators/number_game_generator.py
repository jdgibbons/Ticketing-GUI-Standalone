from typing import List, Tuple, Any
from ticketing.games.generators.base_game_generator import BaseGameGenerator
import ticketing.game_info_gui as gi
import ticketing.image_generator as ig
import ticketing.number_generator as ng
from ticketing.ticket_creation import uTick


class NumberGameGenerator(BaseGameGenerator):
    """
    Generator for tickets populated by numbers (e.g. Non-Winners).
    """

    def __init__(self, game_info, addl_imgs_tracker, ticket_data, num_slots: int):
        """
        Args:
            ticket_data: NonWinnerNumbersTicket object
            num_slots: Total number slots required (for padding)
        """
        super().__init__(game_info, addl_imgs_tracker)
        self.ticket_data = ticket_data
        self.num_slots = num_slots
        self.addl_nums = num_slots - ticket_data.spots
        self.suffix = getattr(game_info, 'image_suffix', '')

        self.initialize_batches()

    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        """
        Generates Non-Winner Number tickets.
        """
        self._prepare_pool()

        # Determine permutations count
        perms = getattr(self.game_info, 'permutations', 1)

        # If we are just creating one batch and copying it (standard for NWs),
        # or generating unique perms. Logic depends on specific game rules,
        # but typically NW numbers are generated once per game or unique per perm.
        # This implementation generates unique numbers for every ticket across all perms.

        for perm_index in range(perms):
            self._create_ticket_batch(perm_index)

        return self.batches, self.nw_pool

    def _prepare_pool(self):
        """Initializes the number generation pool."""
        # Convert exclusion string to list
        exclusions = self.ticket_data.exclusions.split(',') if self.ticket_data.exclusions else []
        if '00' not in exclusions:
            exclusions.append('00')
        # Remove duplicates and empty strings
        self.exclusions = sorted(list(set(x for x in exclusions if x)))

    def _create_ticket_batch(self, perm_index):
        qty = self.ticket_data.quantity
        spots = self.ticket_data.spots

        # Prepare Base Image
        base_name = f"{self.ticket_data.base_image}{self.suffix}" if self.ticket_data.base_image else ""
        # Apply Image Padding (NonWinners usually need padding to match Holds)
        # Note: You might need to pass specific padding rules here in the future
        imgs = ig.add_additional_image_slots_list(self.addl_imgs_tracker, [base_name])

        for _ in range(qty):
            # Refill pool if low
            if len(self.nw_pool) < spots:
                self.nw_pool = ng.create_number_pools_from_suffix_list(
                    self.ticket_data.first_num,
                    self.ticket_data.last_num,
                    self.exclusions,
                    True
                )

            # Draw Numbers
            numbs = []
            for _ in range(spots):
                numbs.append(self.nw_pool.pop(0))

            # Add Padding Slots
            numbs.extend([''] * self.addl_nums)

            # Create Ticket
            ticket = uTick('', imgs, numbs, perm_index + 1, 1, self.is_first)
            self.is_first = False
            self.batches[perm_index].append(ticket)