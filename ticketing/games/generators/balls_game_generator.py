import copy
import random as rn
import itertools as it
from typing import List, Tuple, Any

from ticketing.games.generators.base_game_generator import BaseGameGenerator
from ticketing.universal_ticket import UniversalTicket as uTick
from ticketing import image_generator as ig
from ticketing import game_info_gui as gi


class BallsGameGenerator(BaseGameGenerator):
    """
    Generator for Bingo Ball Hold Tickets.
    Handles: Balls, Downlines, Shazams, Iterations, and Supplemental Holds.
    """

    def __init__(self, game_info, addl_imgs_tracker, ticket_data, num_slots: int):
        super().__init__(game_info, addl_imgs_tracker)
        self.ticket_data = ticket_data
        self.num_slots = num_slots  # 'spt' / spots per ticket
        self.suffix = getattr(game_info, 'image_suffix', '')
        self.initialize_batches()

    def generate(self) -> Tuple[List[List[Any]], List[str]]:
        """
        Main entry point for generating Ball tickets.
        Returns: (batches, pool_updates)
        """
        # Unpack Data
        bb_amt = self.ticket_data.quantity
        bpt = self.ticket_data.bingos_per_ticket
        spt = self.ticket_data.spots_per_ticket
        fill_pool = self.ticket_data.pool_size

        downs = self.ticket_data.use_downlines
        shazams = self.ticket_data.shazams
        sortie = self.ticket_data.sort_balls
        base = self.ticket_data.base_image
        match_bbs = self.ticket_data.match_bbs
        iterations = self.ticket_data.iterations

        permits = self.game_info.permutations

        # Prepare Supplemental Holds Data
        sup_holds_list = [[color, amt] for color, amt in self.ticket_data.additional_holds]
        sup_holds_total = sum(amt for _, amt in self.ticket_data.additional_holds)

        # 1. GENERATE BINGO BALL TICKETS
        perms = []
        tkt_no = self.start_ticket_number

        # FIX: Changed 'self.is_first_ticket' to 'self.is_first'
        is_first = self.is_first

        if bb_amt > 0:
            perms = self._create_bingo_ball_tickets(
                bb_amt, bpt, spt, downs, permits, is_first, 0, fill_pool,
                self.addl_imgs_tracker, tkt_no, shazams, base, iterations, sortie
            )

            # Update start ticket number for next steps
            # Total tickets generated = (Base Qty * Iterations)
            total_generated = bb_amt * iterations
            if isinstance(tkt_no, int):
                tkt_no += total_generated

            is_first = False

        # 2. GENERATE SUPPLEMENTAL HOLDS
        if sup_holds_total > 0:
            if match_bbs:
                # Assuming Supplemental Holds use the same padding tracker as Balls
                ticks = self._create_bb_match_image_holds(
                    sup_holds_list, self.addl_imgs_tracker, fill_pool, spt, base, is_first
                )
            else:
                ticks = self._create_single_image_holds(
                    sup_holds_list, self.addl_imgs_tracker, is_first
                )

            # Distribute Supplemental Holds across permutations
            if not perms:
                perms = [[] for _ in range(permits)]

            for index, perm_list in enumerate(perms):
                single_copy = copy.deepcopy(ticks)
                for tick in single_copy:
                    tick.reset_permutation(index + 1)
                    perm_list.append(tick)

        self.batches = perms
        return self.batches, []

    # --- INTERNAL HELPER METHODS ---

    def _create_bingo_ball_tickets(self, bb_amt, bpt, spt, downs, permits, first, nums, nw_pool,
                                   addl_bb_imgs, tkt, shazams, basic, iterations, sortie):
        global suffix
        perms = []
        numbs = [''] * nums
        tick_places = list(range(bb_amt))

        if downs:
            bangles = [self._create_downline_image_lists(bb_amt, bpt)]
        else:
            bangles = ig.create_bingo_ball_image_permutations(bb_amt, bpt, permits, 'hold', sortie, self.suffix)

        for index, bingos in enumerate(bangles):
            # --- STEP 1: PREPARE MASTER LAYOUTS ---
            for _ in range(rn.randint(2, 5)):
                rn.shuffle(tick_places)
            places = tick_places[0: shazams]
            places.sort(reverse=True)
            shizzle = copy.deepcopy(shazams)

            if bpt != spt:
                nw_imgs = ig.create_image_pool(1, nw_pool, 'nonwinner', True, self.suffix)
                for _ in range(rn.randint(2, 5)):
                    rn.shuffle(nw_imgs)
                nw_cycle = it.cycle(nw_imgs)
                for bingo in bingos:
                    while len(bingo) < spt:
                        bingo.insert(rn.randint(0, len(bingo) + 1), next(nw_cycle))

            positions = list(range(1, spt + 1))
            for _ in range(rn.randint(2, 5)):
                rn.shuffle(positions)
            pos_cycle = it.cycle(positions)

            for innie, bingo in enumerate(bingos):
                if shazams > 0:
                    if shizzle > 0:
                        if innie == places[shizzle - 1]:
                            bingo.append(f'shazam{str(next(pos_cycle)).zfill(2)}{self.suffix}')
                            shizzle -= 1
                        else:
                            bingo.append('')
                    else:
                        bingo.append('')

            # --- STEP 2: GENERATE ITERATIONS ---
            perm_ticks = []

            for i in range(iterations):
                tick_no = tkt

                if iterations > 1:
                    current_base_name = f"{basic}{str(i + 1).zfill(2)}{self.suffix}"
                else:
                    if basic in ['', 'none', 'blank', '0', '000']:
                        current_base_name = ''
                    else:
                        current_base_name = f"{basic}{self.suffix}"

                for bingo_layout in bingos:
                    pics = [current_base_name] if current_base_name else ['']
                    pics.extend(bingo_layout)

                    if isinstance(addl_bb_imgs, list):
                        for addl in addl_bb_imgs:
                            pics = ig.add_additional_image_slots(addl, pics)
                    else:
                        pics = ig.add_additional_image_slots(addl_bb_imgs, pics)

                    perm_ticks.append(uTick(tick_no, pics, numbs, index + 1, 1, first))

                    if tick_no != '' and isinstance(tick_no, int):
                        tick_no += 1
                    first = False

            perms.append(perm_ticks)
        return perms

    def _create_downline_image_lists(self, amt, bpt):
        bingos = ig.create_bingo_downlines(bpt, 'hold', False, self.suffix)
        if len(bingos) < amt:
            return None
        for _ in range(rn.randint(5, 10)):
            rn.shuffle(bingos)
        return bingos[0: amt]

    def _create_bb_match_image_holds(self, suppers, addl_imgs, nws, spt, base, first):
        ticks = []
        numbs = []
        nw_pics = []
        if base != '':
            base = f'{base}{self.suffix}'

        for sup in suppers:
            prefix = f'{sup[0]}'
            pics = ig.create_prefixed_images(1, sup[1], prefix, True, self.suffix)
            for pic in pics:
                if len(nw_pics) < spt - 1:
                    nw_pics = ig.create_image_pool(1, nws, 'nonwinner', True, self.suffix)
                imgs = [pic]
                while len(imgs) < spt:
                    imgs.insert(rn.randint(0, len(imgs)), nw_pics.pop())
                imgs.insert(0, base)

                if isinstance(addl_imgs, list):
                    for add in addl_imgs:
                        imgs = ig.add_additional_image_slots(add, imgs)
                else:
                    imgs = ig.add_additional_image_slots(addl_imgs, imgs)

                ticks.append(uTick('', imgs, numbs, 1, 1, first))
                first = False
        return ticks

    def _create_single_image_holds(self, suppers, addl_imgs, first):
        ticks = []
        numbs = []
        for sup in suppers:
            prefix = f'{sup[0]}'
            pics = ig.create_prefixed_images(1, sup[1], prefix, True, self.suffix)
            for pic in pics:
                imgs = [pic]
                if isinstance(addl_imgs, list):
                    for add in addl_imgs:
                        imgs = ig.add_additional_image_slots(add, imgs)
                else:
                    imgs = ig.add_additional_image_slots(addl_imgs, imgs)

                ticks.append(uTick('', imgs, numbs, 1, 1, first))
                first = False
        return ticks
