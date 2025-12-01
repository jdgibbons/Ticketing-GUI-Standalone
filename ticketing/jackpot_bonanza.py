from ticketing.universal_ticket import UniversalTicket as uTick
import ticketing.game_info_gui as gi
import ticketing.image_generator as ig
import ticketing.ticket_io as tio

import itertools as it
import random as rn

nw_count = 215
inst_count = 8
hold_count = 15
row_count = 5
column_count = 3
pool_size = 9
numbers = 5

ups = 28
sheets = 119
capacity = 56
filename = 'test-10101'


def create_nonwinners(amt: int, pool: int, rows: int, columns: int,
                      addl_imgs: list[gi.AddImages], digits: int, is_first: bool) -> list[uTick] | None:
    # Create ticket list
    ticks = []
    # Calculate the images needed by multiplying the number of columns by the number of rows
    img_count = rows * columns
    # Create a list of empty strings as a placemarker for the number columns
    numbs = [''] * digits
    # Cycle through until there are the required number of tickets.
    while len(ticks) < amt:
        # Create the pool of nonwinner images and a cyclic iterator for it.
        img_pool = ig.create_image_pool(1, pool, 'nonwinner', True)
        img_cycle = it.cycle(img_pool)
        # Create the list of images by using itertools islice, the shuffle the resulting list.
        imgs = list(it.islice(img_cycle, img_count))
        for _ in range(rn.randint(0, 3)):
            rn.shuffle(imgs)
        # Add the additional image slots (single image list equal to the number of rows.
        for addl_img in addl_imgs:
            imgs = ig.add_additional_image_slots(addl_img, imgs)
        # Create the nonwinning ticket and add it to the list.
        tick = uTick('', imgs, numbs, 1, 1, is_first)
        ticks.append(tick)
        is_first = False

    return ticks


def create_instant_winners(amt: int, pool: int, rows: int, columns: int, addl_imgs: list[gi.AddImages],
                           digits: int, is_first: bool) -> list[uTick] | None:
    # Creat ticket list
    ticks = []
    # Calculate the nonwinner images needed by multiplying the number of rows by
    # the number of columns, then subtracting a full row plus one spot from the total.
    img_count = rows * columns - (columns + 1)
    # Create a list of empty strings as a placemarker for the number columns
    numbs = [''] * digits
    # Create a list to represent the row positions.
    spots = list(range(rows))
    # Cycle through until there are the required number of tickets.
    while len(ticks) < amt:
        # Create the nonwinner image pool and an iterator for it.
        img_pool = ig.create_image_pool(1, pool, 'nonwinner', True)
        img_cycle = it.cycle(img_pool)
        # Create the list of images by using itertools islice, the shuffle the resulting list.
        imgs = list(it.islice(img_cycle, img_count))
        # Create a list to represent the single-image, row-size images.
        bar_imgs = [''] * rows
        # Shuffle the row positions and use the first value for the winning image.
        for _ in range(rn.randint(1, 4)):
            rn.shuffle(spots)
        place = spots[0]
        bar_imgs[place] = 'winner01.ai'
        # Determine on which row the dollar image needs to be placed.
        dollar = 0
        # If it's on the first row, the dollar must go on the second row.
        if place == 0:
            dollar = 1
        # If it's on the last row, the dollar must go on the second to last row.
        elif place == rows - 1:
            dollar = rows - 2
        # If it's anywhere else, the dollar can go above or below it. Flip a coin,
        # then assign it to one of those rows based on the result.
        else:
            adjustment = rn.randint(0, 1)
            if adjustment == 0:
                dollar = place - 1
            else:
                dollar = place + 1
        # Create a list to represent a blank row in the smaller image list.
        empty_row = [''] * columns
        # Create a list to represent the placement of the smaller images.
        tiny_imgs = []
        # Cycle through the rows and add images to the small image list
        # based on the placement of the winning and dollar images.
        for i in range(rows):
            # If this is the winning image row, add an empty row to the list.
            if i == place:
                tiny_imgs.extend(empty_row)
            # If this is the dollar image row, add the dollar image and
            # backfill the row with nonwinner images.
            elif i == dollar:
                tiny_imgs.append('ap01.ai')
                for _ in range(columns - 1):
                    tiny_imgs.append(imgs.pop(0))
            # Otherwise, add the number of images equal to the number of columns.
            else:
                for _ in range(columns):
                    tiny_imgs.append(imgs.pop(0))
        # Add the winner image list to the small image list.
        tiny_imgs.extend(bar_imgs)
        # Create the ticket and add it to the ticket list.
        tick = uTick('', tiny_imgs, numbs, 1, 1, is_first)
        ticks.append(tick)
        is_first = False
    return ticks


def create_holds(amt: int, pool: int, rows: int, columns: int, addl_imgs: list[gi.AddImages],
                 is_first: bool) -> list[uTick] | None:
    # Creat ticket list
    ticks = []
    # Calculate the nonwinner images needed by multiplying the number of columns by
    # the number of rows minus the two needed for numbers and the hold image.
    img_count = columns * (rows - 2)
    # Create a list of empty strings as a placemarker for the number columns
    numbs = [''] * rows
    # Create a list to represent the row positions.
    spots = list(range(rows))
    # Cycle through until there are the required number of tickets.
    for i in range(1, amt + 1):
        # Create the nonwinner image pool and a cyclic iterator for it.
        img_pool = ig.create_image_pool(1, pool, 'nonwinner', True)
        img_cycle = it.cycle(img_pool)
        # Create the list of images by using itertools islice, the shuffle the resulting list.
        imgs = list(it.islice(img_cycle, img_count))
        for _ in range(rn.randint(0, 3)):
            rn.shuffle(imgs)
        # Create a list to represent the single-image, row-size images.
        bar_imgs = [''] * rows
        # Create a list of empty strings as a placemarker for the number columns
        numbs = [''] * rows
        # Shuffle the row positions and use the first value for the hold image row
        # and the second value for the numbers row.
        for _ in range(rn.randint(1, 4)):
            rn.shuffle(spots)
        place = spots[0]
        holder = spots[1]
        # Set the number and hold rows to their respective values.
        numbs[place] = f'{i}<@REDFONT>13'
        bar_imgs[holder] = 'hold01.ai'
        # Create a list to represent a blank row in the smaller image list.
        empty_row = [''] * columns
        # Create a list to represent the placement of the smaller images.
        tiny_imgs = []
        # Cycle through the rows and add images to the small image list
        # based on the placement of the numbers and the hold image.
        for j in range(rows):
            if j in [place, holder]:
                tiny_imgs.extend(empty_row)
            else:
                for _ in range(columns):
                    tiny_imgs.append(imgs.pop(0))
        # Add the hold image list to the small image list.
        tiny_imgs.extend(bar_imgs)
        # Create the hold ticket and add it to the tickets list.
        tick = uTick('', tiny_imgs, numbs, 1, 1, is_first)
        ticks.append(tick)
        is_first = False
    return ticks


tickets = create_nonwinners(nw_count, pool_size, row_count, column_count,
                            [gi.add_images_lookup(5)], numbers, True)

tickets.extend(create_instant_winners(inst_count, pool_size, row_count, column_count,
                                      [gi.add_images_lookup(0)], numbers, False))

tickets.extend(create_holds(hold_count, pool_size, row_count, column_count,
                            [gi.add_images_lookup(0)], False))

tio.write_tickets_to_file(filename, tickets)

game_stacks = tio.create_game_stacks(tickets, ups, sheets, capacity)

tio.write_game_stacks_to_file(filename, game_stacks, ups, sheets, capacity)

print('whatevs')
