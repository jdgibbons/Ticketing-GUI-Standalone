from ticketing import ticket_io as tio
from ticketing import game_info as gi
from ticketing import image_generator as ig
from ticketing import number_generator as ng

from ticketing.universal_ticket import UniversalTicket


def create_instant_winners(amt: list[int], cd_tier, subs, tkt, addl_imgs, nummies, first=True):
    imgs = ig.create_tiered_image_list(amt, 'instant', subs)
    nums = [''] * nummies
    ticks = []
    cull_ticket = first
    for img in imgs:
        pics = [''] * addl_imgs

        pics.insert(0, img[0])
        if cull_ticket:
            ticks.append(UniversalTicket(tkt, pics, nums, 1, 1, True))
            cull_ticket = False
        else:
            ticks.append(UniversalTicket(tkt, pics, nums))
        tkt += 1
    return ticks


def create_hold_tickets(amt, spots, tkt):
    ticks = []
    lines = ng.create_unique_bingo_lines(amt, spots, False, False, False)
    imgs = ['base01.ai', '', '', '']
    for line in lines:
        ticks.append(UniversalTicket(tkt, imgs, line))
        tkt += 1
    return ticks


def create_tictactoe_holds(amt: int, q_nw_image_pool: int, ticket_number: int):
    holders = tf.create_tictactoe_one_row_image(amt, q_nw_image_pool, 'hold', True)
    ticks = []
    for imgs in holders:
        ticket = GeneralTicket(ticket_number, imgs[0], imgs[1])
        ticket.reset_position_on_ticket(imgs[2])
        ticks.append(ticket)
        ticket_number += 1
    return ticks


def create_nonwinner_tickets(amt: int, q_nw_image_pool: int, pics_per_ticket: int):
    numbs = [''] * 4
    nw_image_lines = ig.create_image_lists_from_pool(1, q_nw_image_pool, 'nonwinner', amt, pics_per_ticket)
    ticks = []
    for nw in nw_image_lines:
        nw.insert(0, '')
        ticks.append(UniversalTicket('', nw, numbs))

    return ticks


def create_single_nonwinner_tickets(first: int, q_nw_image_pool: int, amt: int, pics_per_ticket: int,
                                    pre: list[str], post: list[str], nummies: int = 0):
    numbs = [''] * nummies
    nw_image_lines = ig.create_image_lists_from_pool(first, first + q_nw_image_pool,
                                                     'nonwinner', amt, pics_per_ticket)
    ticks = []
    for nw in nw_image_lines:
        line = pre
        line += nw
        line += post
        ticks.append(UniversalTicket('', line, numbs))
    return ticks


def create_pick_winners(amt_list):
    global tickets, ticket_number, pick_cd_tier_level
    if len(amt_list) == 1:
        for i in range(amt_list[0]):
            imagine = f"pick{str(i + 1).zfill(2)}.ai"
            ticket_number += 1
            ticket = GenericOneImageTicket(ticket_number, imagine)
            ticket.reset_cd_type('P')
            ticket.reset_instant_cd_tier('1')
            tickets.append(ticket)
    else:
        for index in range(len(amt_list)):
            imagine = f"pick{str(index + 1).zfill(2)}.ai"
            for item in range(amt_list[index]):
                ticket_number += 1
                ticket = GenericOneImageTicket(ticket_number, imagine)
                ticket.reset_instant_cd_tier(index + 1)
                ticket.reset_cd_type('P')
                tickets.append(ticket)


def set_game_parameters():
    sheet_params = [4, 1, 60, [240, 80]]
    nw_params = [1142, 9, 9]
    inst_params = [[4, 15, 24], 2, False]
    pick_params = [0]
    hold_params = 15
    nombres = ['300-004', 'TheGeneral-T0008']
    return [sheet_params, nw_params, inst_params, pick_params, hold_params, nombres]


def input_game_parameters():
    params: list[list[int] | int] = [gi.get_up_sheet_ticket_perms(False, False),
                                     gi.get_nonwinner_image_info(),
                                     gi.get_instant_winner_info(),
                                     gi.get_pick_tickets_info(),
                                     gi.get_single_integer('Holds', 15),
                                     gi.get_part_and_file_names()]
    return params


if __name__ == '__main__':
    sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, name_specs = input_game_parameters()
    # sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs, names = set_game_parameters()

    gi.check_game_parameters(sheet_specs, nw_specs, inst_specs, pick_specs, hold_specs)
    tick = 1
    inst_specs.append(nw_specs[1])
    inst_specs.append(tick)
    tickets = create_instant_winners(*inst_specs)
    tickets += create_holds(hold_specs, nw_specs[1], len(tickets))
    tickets += create_nonwinner_tickets(*nw_specs)
    tio.write_tickets_to_file(name_specs[1], tickets)
    game_stacks = tio.create_game_stacks(sheet_specs[0], tickets, sheet_specs[2], sheet_specs[3][1])
    cd_tickets, sheets = tio.write_game_stacks_to_file(name_specs[1], game_stacks, sheet_specs[2],
                                                       sheet_specs[3][1], sheet_specs[0])
    tio.write_cd_multi_spot_positions_to_file(name_specs[0], name_specs[1], cd_tickets, inst_specs[1], 3)
    print('whatevers')
