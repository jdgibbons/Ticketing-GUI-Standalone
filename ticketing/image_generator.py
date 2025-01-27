import copy
import random as rn
from itertools import cycle, permutations, combinations
from ticketing.game_info import AddImages
from .number_generator import create_bingo_positions


def create_tiered_image_list(amt_list: list[int], prefix: str, add_subimages: bool) -> list[list[str | int]]:
    """
    Create a list of images that reflect the number needed for each tier. Normally, this would
    entail creating a bunch of images that only reflect the tier level: i.e., all instant winner
    images in tier one would be called 'winner01.ai,' tier two would be 'winner02.ai,' etc. If
    there are subimages, however, each ticket in a tier will have a discrete name: e.g., tier one
    images would be 'winner01-01.ai,' 'winner01-02.ai,' 'winner01-03.ai,' etc. If a mixture of types
    is needed, break up the array and call the method multiple times. If tier one has subimages but
    the remaining tiers don't, call the method like so:\n
     create_tiered_image_list([50], 'winner', True)\n
    then\n
     create_tiered_image_list([0, 5, 10, 20], False)\n
    which would result in tier one containing 50 subimages ('winner01-01.ai' . . . 'winner01-50.ai')
    and tiers two through four containing five 'winner02.ai,' ten 'winner03.ai,' and 20 'winner04.ai'

    :param amt_list: list of ticket totals for each tier
    :param prefix: String to add at the front of each ticket name
    :param add_subimages: Does each ticket in a tier have a discrete image?
    :return: list of ticket names for each tier along with its corresponding tier \
    (so it doesn't need to be extracted by the caller).
    :rtype: list[str]
    """
    # Create a list to hold the images
    image_list = []
    # Cycle through the list of image counts
    for index in range(len(amt_list)):
        # Count used for subimage names
        count = 1
        # Cycle through the image-name creation process
        for _ in range(amt_list[index]):
            # If there are subimages for this group, add the count number to the image name.
            if add_subimages:
                imagine = f"{prefix}{str(index + 1).zfill(2)}_{str(count).zfill(2)}.ai"
            # Otherwise, just use the index position (plus one) to create the image name
            else:
                imagine = f"{prefix}{str(index + 1).zfill(2)}.ai"
            # Add the image name to the list and increment the image count.
            image_list.append([imagine, index + 1])
            count += 1
    # Send the image list to whoever ordered it.
    return image_list


def create_image_pool(first: int, last: int, prefix: str, mix: bool = True) -> list[str]:
    """
    Create a pool of images to be used to randomly generate image spreads on tickets.
    The images will be added then shuffled a few times. This method is called
    whenever there are not enough images in the list to fill a ticket. Return the
    list of images.

    :param first: beginning of the range of image numbers
    :param last: end of the range of image numbers
    :param prefix: String to add at the front of each image name
    :param mix: shuffle the resulting list?
    :return: list containing strings of image names for the pool
    """
    nw_image_pool = []
    # Create a list of images using the index + 1 to refer to the correct one.
    for i in range(first, last + 1):
        nw_image_pool.append(f"{prefix}{str(i).zfill(2)}.ai")
    # Shuffle the list between 4 and 25 times
    if mix:
        for x in range(rn.randint(4, 25)):
            rn.shuffle(nw_image_pool)
    return nw_image_pool


def create_image_pool_permutations(first: int, last: int, prefix: str, spots: int) -> list[list[str]]:
    """
    Create a pool of images to be used to randomly generate image spreads on tickets.
    :param first:
    :param last:
    :param prefix:
    :param spots:
    :return:
    """
    images = []
    for i in range(first, last + 1):
        images.append(f"{prefix}{str(i).zfill(2)}.ai")
    image_pool = permutations(images, spots)
    # x = len(list(image_pool))
    nw_image_pool = []
    for imgs in image_pool:
        nw_image_pool.append(list(imgs))
    for _ in range(rn.randint(3, 6)):
        rn.shuffle(nw_image_pool)
    return nw_image_pool


def create_image_lists_from_pool(first: int, last: int, prefix: str, amt: int, pics_per_tick: int) -> list[list[str]]:
    """
    Create a list of lists containing image names gathered from a pool of shuffled and scattered images.

    :param first: number of the first image in the pool
    :param last: number of the last image in the pool
    :param prefix: string to add at the front of each image name
    :param amt: total number of image lists needed by the caller
    :param pics_per_tick: number of images per ticket
    :return: list of lists containing images gathered from the pool
    """
    # Create a list to hold the lists of images
    image_lists = []
    # Create the initial pool of images to be used to create the image lists
    nw_image_pool = create_image_pool(first, last, prefix)
    # Loop until there are enough lists
    for _ in range(amt):
        # Create a list to hold the images
        image_list = []
        # If there aren't enough images to create the list, grab a new
        # list, append the images that aren't already in the list, and
        # keep going until we have a full list.
        if len(nw_image_pool) < pics_per_tick:
            temp_pool = create_image_pool(first, last, prefix)
            for tempo in temp_pool:
                if tempo not in nw_image_pool:
                    nw_image_pool.append(tempo)
        # Cycle through the pool and pop off images from the front
        for _ in range(pics_per_tick):
            # Pop off the first image and append it to the new list
            image = nw_image_pool.pop(0)
            image_list.append(image)
        # Add the image this to the main list
        image_lists.append(image_list)
    # Get the lists back the caller, STAT!
    return image_lists


def create_image_lists_from_pool_perms(first: int, last: int, prefix: str,
                                       amt: int, pics_per_tick: int) -> list[list[str]]:
    """
    Create a list of lists containing image names gathered from a pool of images that have
    been dispersed using itertools permutations function.

    :param first: the first image number in the pool
    :type first: int
    :param last: the last image number in the pool
    :type last: int
    :param prefix: the string to add at the front of each image name
    :type prefix: str
    :param amt: the total number of image lists needed in each permutation
    :param pics_per_tick:
    :return:
    """
    images_lists = []
    nw_image_perms = create_image_pool_permutations(first, last, prefix, pics_per_tick)
    for _ in range(amt):
        if len(nw_image_perms) == 0:
            nw_image_perms = create_image_pool_permutations(first, last, prefix, pics_per_tick)
        images_lists.append(nw_image_perms.pop(0))
    return images_lists


def create_bingo_ball_image_list(amt: int, bpt: int, prefix: str):
    image_lists = []
    bb_pool = []
    taken = set()
    attempts = 0
    while len(image_lists) < amt:
        if sum(len(sublist) for sublist in bb_pool) < bpt:
            bb_pool = create_bingo_ball_hold_images(True, True, prefix)
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(bb_pool)
        bb_pool.sort(key=lambda xyz: len(xyz), reverse=True)
        imgs = []
        for i in range(bpt):
            imgs.append(bb_pool[i].pop(0))
        temp = copy.deepcopy(imgs)
        temp.sort()
        if (tuple(temp)) not in taken:
            taken.add(tuple(temp))
            image_lists.append(copy.deepcopy(imgs))
        else:
            attempts += 1
            for x, val in enumerate(imgs):
                bb_pool[x].append(val)
            if attempts == 10:
                bb_pool = create_bingo_ball_hold_images(True, True, prefix)
    return image_lists


def create_bingo_ball_hold_images(multi: bool = True, mixed: bool = False,
                                  name: str = 'hold') -> list[list[str] | str]:
    """
    Create a list of images that represent bingo balls B-1 through O-75. This
    can take the form of a single list of 75 or five lists of 15. If the 'mixed'
    flag is True, the single list will be shuffled, but the multi-list will shuffle
    all the sublists while keeping the sublists themselves in place.

    :param multi: Is this a multi-list representing each letter as a sublist?
    :type multi: bool
    :param mixed: Does the list need to be shuffled?
    :type mixed: bool
    :param name: Prefix for the image files.
    :type name: str
    :return: list of images representing bingo ball images
    :rtype: list[list[str] | str]
    """
    balls = []
    # Cycle through each letter and create a list of values representing its column.
    for i in range(5):
        imgs = []
        # Add the value for every possible spot in this letter's column.
        for j in range(1, 16):
            # Create the string representing the image name.
            imgs.append(f"{name}{str((i * 15) + j).zfill(2)}.ai")
        # Add the images to the master list. If this is a multi-list, add the list
        # itself as an element. Otherwise, add each image individually to the list.
        if multi:
            balls.append(imgs)
        else:
            balls.extend(imgs)
    # Shuffle the list if necessary.
    if mixed:
        # If this is a multi-list situation, shuffle the sublists while
        # maintaining their positions in the list.
        if multi:
            for ball in balls:
                for _ in range(rn.randint(2, 5)):
                    rn.shuffle(ball)
        # Otherwise, shuffle the entire list.
        else:
            for _ in range(rn.randint(2, 5)):
                rn.shuffle(balls)
    return balls


def create_bingo_downlines(spots: int, prefix: str = 'hold', mixers: bool = False) -> list[list[str]]:
    """
    Creates image names for bingo downlines of given number of spots.

    :param spots: number of spots in the downline
    :type spots: int
    :param prefix string for image name prefix
    :type prefix: str
    :param mixers: shuffle the downlines?
    :type mixers: bool
    :return: list of bingo downlines
    :rtype: list[list[str]]
    """
    # Create the bingo positions and DO NOT have them shuffled! They'll be mixed
    # further down if necessary.
    bingos = create_bingo_positions(False, False, True, True, False)
    downers = []
    for index in range(len(bingos[0])):
        bingo = []
        for bins in bingos:
            bingo.append(bins[index])
        combos = combinations(bingo, spots)
        for combo in combos:
            teepee = []
            for spot in combo:
                teepee.append(f"{prefix}{str(spot).zfill(2)}.ai")
            downers.append(copy.deepcopy(teepee))
    if mixers:
        for _ in range(rn.randint(4, 11)):
            rn.shuffle(downers)
    return downers


def create_prefixed_images(first: int, last: int, prefix: str, uniq: bool = False) -> list[str]:
    """
    Create a list of images that uses the prefix and numbers in the range
    from first to last to create the file names. The 'uniq' flag indicates whether the
    images will all have the same name or not: true means they will be sequentially
    named, false means they will all be named 'xxx01.ai'.

    :param first: the number of the first image in the pool
    :type first: int
    :param last: the number of the last image in the pool
    :type last: int
    :param prefix: the string to add at the front of each image name
    :type prefix: str
    :param uniq: Is the name of each file unique?
    :type uniq: bool
    :return: list of strings comprising image names for the pool
    :rtype: list[str]
    """
    images = []
    for img in range(first, last + 1):
        if uniq:
            images.append(f"{prefix}{str(img).zfill(2)}.ai")
        else:
            images.append(f"{prefix}01.ai")
    return images


def add_additional_image_slots(addl_imgs: AddImages, line: list[str]) -> list[str]:
    if addl_imgs != AddImages.NoneAdded:
        if addl_imgs == AddImages.PreBase:
            line.insert(0, 'base.ai')
        elif addl_imgs == AddImages.PostBase:
            line.append('base.ai')
        elif addl_imgs.value < 0:
            for _ in range(abs(addl_imgs.value)):
                line.insert(0, '')
        elif addl_imgs.value > 0:
            for _ in range(abs(addl_imgs.value)):
                line.append('')
    return line


def create_winning_tictactoe_paths():
    # The list elements are comprised of:
    #       ((winning path), 'winner letter for image type', position for dollar amount, cd cutout row)
    #       So, for the first element:
    #           winning path = (0, 1, 2),   ##### Positions of the tic-tac-toe
    #           winning letter = 'a',       ##### This refers to the letter in the cross-out images needed to align
    #                                       ##### the red lines to create a tic-tac-toe
    #           dollar amount position = 3, ##### the spot in the winning line to place the winner image
    #           cd cutout row = 2)          ##### which of the three rows to place the cd number on

    winning_paths = [((0, 1, 2), 'a', 3, 2), ((3, 4, 5), 'a', 6, 3), ((6, 7, 8), 'a', 3, 2),
                     ((0, 4, 8), 'd', 3, 2), ((6, 4, 2), 'c', 7, 3), ((0, 3, 6), 'b', 1, 1),
                     ((6, 3, 0), 'b', 7, 3), ((1, 4, 7), 'b', 0, 1), ((7, 4, 1), 'b', 6, 3)]
    # Shuffle the winning
    for i in range(rn.randint(10, 25)):
        rn.shuffle(winning_paths)
    return winning_paths


def create_tictactoe_instants(amts: list[int], q_nw_image_pool: int, default_winner: int):
    """
    Create a list of images for winning tic-tac-toe lines. This is for a 3x3, nine-space game.\n
    The winning lines are generated and shuffled in another method and passed back with additional
    information:\n

    -    [winning line (e.g., (0, 1, 2), representing the spots where the winning images (tier, base, base),
    -    cross out image letter (images with the cross-out 'bar' pointing in the correct direction (/, \\, -)),
    -    dollar amount position (which spot the dollar amount image needs to go on based on the winning line),
    -    cd cutout row (row in which the dollar amount resides)]:\n

    to create a balanced spread of winning lines. The

    :param amts: list of integers representing the number of tickets in each tier
    :param q_nw_image_pool: number of images in the nonwinner image pool
    :param default_winner: integer representing the default image used in winners
    :return: [images, cd_tier, position on ticket]
    """
    # Get a list of paths representing winning lines, the image variety for that line,
    # the spot on which to place the winning dollar amount, and the row for the cd cutout.
    # Create a cycle of the list to allow even distribution of winning lines.
    winning_paths = create_winning_tictactoe_paths()
    paths_cycle = cycle(winning_paths)
    # 'images_plus' is a list of lists containing the images in the grid,
    # the tier level, and the cd slot position.
    images_plus = []
    # This is filled within the loop, where it is refilled when the number of
    # images falls below the number required to populate the nonwinning spaces.
    nw_image_pool = []
    # Cycle through the amts list. The index + 1 is equal to the current cd
    # tier level. The value is the number of tickets needed for this tier.
    for index, amt in enumerate(amts):
        # Cycle through once for each ticket.
        for i in range(amt):
            # Replenish the nonwinner image pool if there are fewer than the number
            # of nonwinner spaces required to fill out the grid.
            if len(nw_image_pool) < 5:
                nw_image_pool = create_image_pool(1, q_nw_image_pool, 'nonwinner')
            # Create the list so the indexes can be used to fill the spots.
            spots = [''] * 9
            # Get the next winning path . . . plus
            current_path = next(paths_cycle)
            # The list elements are comprised of:
            #       ((winning path), 'winner letter for image type', position for dollar amount, cd cutout row)

            # First spot is filled with tier-specific winner image (letter = image 'spin' (/, \\, or --)
            spots[current_path[0][0]] = f"winner{str(index + 1).zfill(2)}{current_path[1]}.ai"

            # Next two spots are filled with the generic winner image (letter represents image 'spin')
            spots[current_path[0][1]] = f"winner{str(default_winner).zfill(2)}{current_path[1]}.ai"
            spots[current_path[0][2]] = f"winner{str(default_winner).zfill(2)}{current_path[1]}.ai"

            # This spot is filled with the dollar amount image
            spots[current_path[2]] = f"ap{str(index + 1).zfill(2)}.ai"

            # Cycle through the spots. If an empty spot is encountered, fill
            # it with the next nonwinner image.
            for indy, spot in enumerate(spots):
                if spot == '':
                    spots[indy] = nw_image_pool.pop(0)
            # Add the images, the cd tier, and the position cd slot position
            images_plus.append([spots, index + 1, current_path[3]])
    # return list[[images, cd tier, cd slot position]]
    return images_plus


def create_tictactoe_one_row_image(amt, q_nw_image_pool, prefix, use_img_index=False):
    """

    :param amt:
    :param q_nw_image_pool:
    :param prefix:
    :param use_img_index:
    :return:
    """
    nw_image_pool = []
    images = []
    pick_rows = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    rowers = [0, 1, 2]
    winning_row = 0
    for q_pick in range(amt):
        imgs = [''] * 9
        picks = [''] * 3
        if use_img_index:
            picks[winning_row] = f'{prefix}{str(q_pick + 1).zfill(2)}.ai'
        else:
            picks[winning_row] = f'{prefix}01.ai'
        for i in rowers:
            if i != winning_row:
                for rowdy in pick_rows[i]:
                    if len(nw_image_pool) == 0:
                        nw_image_pool = create_image_pool(1, q_nw_image_pool, 'nonwinner')
                    imgs[rowdy] = nw_image_pool.pop(0)
        images.append([imgs, picks, winning_row + 1])
        winning_row += 1
        if winning_row == 3:
            winning_row = 0
    return images
