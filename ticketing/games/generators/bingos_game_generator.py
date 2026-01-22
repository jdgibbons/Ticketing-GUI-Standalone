import copy
from typing import List, Tuple, Any
from ticketing.games.generators.base_game_generator import BaseGameGenerator
from ticketing.bingo_ticket import BingoTicket as bTick
import ticketing.verified_bingo as vb
import ticketing.image_generator as ig
import ticketing.game_info_gui as gi


class BingosGameGenerator(BaseGameGenerator):
    """
    Generator for Verified Bingo Hold Tickets.
    Wraps the 'verified_bingo' library logic.
    """

    def __init__(self, game_info, addl_imgs_tracker, ticket_data, csv_rows: int):
        """
        :param csv_rows: The number of rows required in the CSV output (1, 2, or 3).
                         Derived from hold_specs.columns_needed.
        """
        super().__init__(game_info, addl_imgs_tracker)
        self.ticket_data = ticket_data
        self.csv_rows = csv_rows
        self.suffix = getattr(game_info, 'image_suffix', '')
        self.initialize_batches()

    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        """
        Generates the core Bingo Cards (Hold Tickets).
        Returns batches of BingoTicket objects.
        """
        # 1. Setup Parameters
        permits = self.game_info.permutations
        reset_pool = self.game_info.reset_pool

        needs = [
            self.ticket_data.dns_counts,
            self.ticket_data.ds_counts,
            self.ticket_data.sns_counts,
            self.ticket_data.ss_counts,
            self.ticket_data.either_ors
        ]

        is_extended = self.ticket_data.extended_csv == 'E' or self.ticket_data.extended_csv is True

        # 2. Call Verification Library
        # This returns a list of lists (permutations -> tickets)
        if reset_pool or permits == 1:
            versions = vb.create_all_bingo_permutations_with_reset(
                needs, permits, self.csv_rows, is_extended, True
            )
        else:
            versions = vb.create_all_bingo_permutations_without_reset(
                needs, permits, self.csv_rows, is_extended, True
            )

        # Safety Check
        if versions[0] is None:
            # In a real scenario, we might want to raise an error or handle this gracefully.
            # For now, we return empty batches and let the orchestrator handle the failure.
            return [], []

        # 3. Configure Headers (Static Method on BingoTicket)
        # We need data from the first ticket to configure the CSV columns once.
        first_face_data = versions[0][0]
        # first_face_data structure: [verification, [lines...], size, frees, staggered]
        first_row_numbers = first_face_data[1][0]
        calculated_line_length = len(first_row_numbers)

        # Calculate Image Slots (Base 1 + Padding)
        # Note: addl_imgs_tracker is an AddImages enum value (int)
        total_image_slots = abs(self.addl_imgs_tracker) + 1

        bTick.configure_csv_headers(
            schema_depth=self.csv_rows,
            line_length=calculated_line_length,
            image_count=total_image_slots,
            lotto_count=0
        )

        # 4. Process Raw Data into Ticket Objects
        for index, perm_batch in enumerate(versions):
            tkt_num = 1

            for face in perm_batch:
                b_type = 'N'
                base_img = []

                # --- Base Image Logic (Ported from game_imgs_imgs_imgs_bingos) ---
                if self.csv_rows == 3:
                    if len(face[1]) == 1:
                        face[1] += [['', '', '', '', ''], ['', '', '', '', '']]
                        base_img = [f'base01{self.suffix}']
                    elif len(face[1]) == 2:
                        b_type = self._determine_bingo_type(face)
                        face[1].insert(0, ['', '', '', '', ''])
                        base_img = [f'base02{self.suffix}']
                    elif len(face[1]) == 3:
                        base_img = [f'base03{self.suffix}']
                        b_type = 'E'
                elif self.csv_rows == 2:
                    base_img = [f'base02{self.suffix}']
                elif self.csv_rows == 1:
                    base_img = [f'base01{self.suffix}']

                # Apply Padding
                # We use the list-compatible add_additional_image_slots function
                images = ig.add_additional_image_slots_list(self.addl_imgs_tracker, base_img)

                # Create Ticket
                tick = bTick(tkt_num, face[0], face[1], images, self.ticket_data.leading_zeroes, index + 1, 1,
                             self.suffix)

                # Apply Type Settings
                if self.ticket_data.free_type:
                    tick.set_free_type(self.ticket_data.free_type[0].upper())

                tick.set_bingo_type(copy.deepcopy(b_type))

                # Add to Batch
                self.batches[index].append(tick)

                tkt_num += 1

        # Bingo generally doesn't use the shared NW pool, so we return empty pool updates
        return self.batches, []

    def _determine_bingo_type(self, facial):
        """
        Helper: Determines if a 2-row bingo ticket is Staggered ('S') or Non-Staggered ('N').
        """
        for a, b in zip(facial[1][0], facial[1][1]):
            if bool(a.strip()) ^ bool(b.strip()):
                return 'S'
        return 'N'
