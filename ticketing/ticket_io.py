import copy
import os.path
import random as rn
from itertools import cycle
import xml
import xml.etree.ElementTree as ET

from .bonanza_ticket import BonanzaTicket


def write_tickets_to_file(filename: str, tickets: list[BonanzaTicket], output_folder: str = '') -> None:
    """
    Write the tickets out to a file in the order they were created. This file can help
    in verifying the ups have all the expected tickets.

    :param filename: base name part of the file to be created
    :param tickets: list of tickets
    :param output_folder: destination for output files
    :type output_folder: str
    :return: None
    :rtype: None
    """
    # If there is
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"
    # Create a file in the 'results' directory to hold the tickets' information
    file = open(f"{destination}_tickets.csv", 'w')
    # Write the field names to the first lines.
    file.write(f"{','.join(BonanzaTicket.csv_fields)}\n")
    # Loop through the tickets list, write out their information, then close the file.
    for tick in tickets:
        file.write(f'{tick}\n')
    file.close()


def write_permutations_to_files(filename: str, perms: list[list[BonanzaTicket]],
                                verbose=False, output_folder: str = '') -> None:
    """
    Write all the permutations to separate csv files.

    :param filename:
    :param perms:
    :param verbose:
    :param output_folder:
    :return: None
    """
    if verbose:
        print(f"Writing {len(perms)} permutations to files . . .")
        print('    Perm: ', end='')
    # If the output folder isn't blank, use it to set the output destination.
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"
    # Cycle through the perms
    for p, perm in enumerate(perms):
        if verbose:
            print(f'{p + 1}', end=' ')
        # Create a file to write this permutation to.
        file = open(f"{destination}_perm{str(p + 1).zfill(2)}.csv", 'w')
        # Write the csv field headers.
        file.write(f"{','.join(BonanzaTicket.csv_fields)}\n")
        cc = 1
        # Cycle through this perm's tickets.
        for ticket in perm:
            if verbose:
                print(f"{cc}, {ticket}\n")
                cc += 1
            # Write out this tickets information as csv.
            file.write(f"{ticket}\n")
    if verbose:
        print('\n')


def write_permutations_to_debug(filename: str, perms: list[list[BonanzaTicket]], verbose=False) -> None:
    """
    Write the permutations to the screen.

    :param filename:
    :param perms:
    :param verbose:
    :return: None
    """
    if verbose:
        print(f"Writing {len(perms)} permutations to screen . . .")
        print('    Perm: ', end='')
    for p, perm in enumerate(perms):
        if verbose:
            print(f'{p + 1}', end=' ')

        print(f"{','.join(BonanzaTicket.csv_fields)}\n")
        for ticket in perm:
            print(f"{ticket}\n")
    if verbose:
        print('\n')


def write_game_stacks_to_file(filename: str, game_stacks: list[list[BonanzaTicket]], q_ups: int, q_sheets: int,
                              q_sheet_capacity: int, output_folder: str = '') -> list[list[BonanzaTicket]]:
    """
    Write all tickets to a file according to the number of ups required.

    :param filename: the base name for this game
    :type filename: str
    :param game_stacks: list of lists of tickets representing all the ups for the game
    :type game_stacks: list[list[BonanzaTicket]]
    :param q_sheet_capacity: number of tickets per sheet
    :type q_sheet_capacity: int
    :param q_sheets: number of sheets in the flat
    :type q_sheets: int
    :param q_ups: number of ups in this flat
    :type q_ups: int
    :param output_folder: location for output files
    :type output_folder: str
    :return: list of tickets containing cds, all tickets grouped by sheet
    :rtype: list[list[BonanzaTicket]]
    """
    # Create two lists to contain tickets: cd_tickets will contain only those tickets
    # that have cds attached to them. sheets will have all the tickets for a sheet in
    # the order they will be placed. I don't remember why I wanted this information,
    # but I don't use it right now. I'll probably get rid of it in the future.
    cd_tickets = []
    sheets = []
    # Open csv file for tickets
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"
    file = open(f"{destination}.csv", 'w')
    # Write out csv fields
    # file.write(f"{','.join(game_stacks[0][0].csv_fields)}\n")
    # file.write(f"{game_stacks[0][1].fielders()}\n")
    if not os.path.exists('./results'):
        os.mkdir('./results')
    file.write(f"{','.join(BonanzaTicket.csv_fields)}\n")
    # Start loop at the sheet level
    for sheet in range(q_sheets):
        new_sheet = []
        sheet_position = 1
        # Cycle through game stacks
        for stack in game_stacks:
            # Calculate tickets per up per sheet and pop that
            # number of tickets off the list and into the file.
            for j in range((int(q_sheet_capacity / q_ups))):
                tick = stack.pop(0)
                file.write(f'{tick}\n')

                # Add sheet number and position to the ticket
                tick.reset_sheet_number(sheet + 1)
                # If this ticket falls within the cd parameter, add it the list
                if tick.get_cd_tier() != 0:
                    # tick.reset_position(cd_grid[sheet_position])
                    tick.reset_position_on_sheet(sheet_position)
                    cd_tickets.append(copy.deepcopy(tick))
                # Add the ticket to the current sheet and increment the sheet position
                new_sheet.append(tick)
                sheet_position += 1
        # Add current sheet to the sheets list and increase the page number
        sheets.append(new_sheet)
    file.close()
    return [cd_tickets, sheets]


def write_cd_positions_to_csv_file(part: str, filename: str, cd_tickets: list[BonanzaTicket],
                                   cd_tier: int, output_folder: str = '') -> None:
    """
    Take a list of cd tickets and write out the pertinent information to a csv file
    for tickets with only one possible cd placement.

    :param part: The Bonanza part prefix for this game
    :type part: str
    :param filename: The base file name for the csv file
    :type filename: str
    :param cd_tickets: tickets containing cds
    :type cd_tickets: list[BonanzaTicket]
    :param cd_tier: the highest tier for cds
    :type cd_tier: int
    :param output_folder: destination for output files
    :type output_folder: str
    :return: None
    :rtype: None
    """
    # If the cd tier is 0, I don't know why I'm here in the first place.
    if len(cd_tickets) == 0 and cd_tier == 0:
        return
    # Open the file and write out the field names
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"
    file = open(f"{destination}_cds.csv", 'w')
    file.write('part,up,tier,position,type\n')
    # Cycle through the tickets and write out the pertinent information for each cd
    for tick in cd_tickets:
        file.write(
            f"{part}_{str(tick.get_sheet_number()).zfill(3)},{tick.get_up()},{tick.get_cd_tier()},"
            f"{tick.get_position_on_sheet()},{tick.get_cd_type()}\n")
    file.close()


def write_cd_positions_to_csv_file_for_d3(part: str, filename: str, cd_tickets: list[BonanzaTicket],
                                          cd_tier: int, ups: int, output_folder: str = '') -> None:
    """
    Take a list of cd tickets and write out the pertinent information to a csv file
    for tickets with only one possible cd placement.

    :param part: The Bonanza part prefix for this game
    :type part: str
    :param filename: The base file name for the csv file
    :type filename: str
    :param cd_tickets: tickets containing cds
    :type cd_tickets: list[BonanzaTicket]
    :param cd_tier: the highest tier for cds
    :type cd_tier: int
    :param ups: number of ups
    :type ups: int
    :param output_folder: destination for output files
    :type output_folder: str
    :return: None
    :rtype: None
    """
    # If the cd tier is 0, I don't know why I'm here in the first place.
    if len(cd_tickets) == 0 and cd_tier == 0:
        return
    # Open the file and write out the field names
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"
    file = open(f"{destination}_cds_d3.csv", 'w')
    file.write('part,up,tier,position,type,spf\n')
    # Cycle through the tickets and write out the pertinent information for each cd
    for tick in cd_tickets:
        file.write(f"{tick.position_line(part)},{ups}\n")
        # file.write(
        #     f"{part}_{str(tick.get_sheet_number()).zfill(3)},{tick.get_up()},{tick.get_cd_tier()},"
        #     f"{tick.get_position_on_sheet()},{tick.get_cd_type()},{ups}\n")
    file.close()


def write_cd_positions_to_xml_file(part: str, filename: str, cd_tickets: list[BonanzaTicket],
                                   cd_tier: int, ups: int, output_folder: str = '') -> None:
    """
    Take a list of cd tickets and write out the pertinent information to an xml file
    for tickets with only one possible cd placement.

    :param part: The Bonanza part prefix for this game
    :type part: str
    :param filename: The base file name for the csv file
    :type filename: str
    :param cd_tickets: tickets containing cds
    :type cd_tickets: list[BonanzaTicket]
    :param cd_tier: the highest tier for cds
    :type cd_tier: int
    :param ups: number of ups
    :type ups: int
    :param output_folder: destination for output files
    :type output_folder: str
    :return: None
    :rtype: None
    """
    # Just go turn around and go home if there are no CDs.
    if len(cd_tickets) == 0 or cd_tier == 0:
        return
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"

    # Get the game name by splitting the file name prefix. (File name is in the form
    # of game_name-form_name, e.g., 'EmeraldCity-31772'.)
    game_name = filename.split('-')[1]

    # Create the root document and its attributes.
    xml_doc = ET.Element('Game')
    xml_doc.set('id', game_name)
    xml_doc.set('ups', str(ups))
    xml_doc.set('cds', str(len(cd_tickets)))

    # Create a dictionary to keep track of the number of each type of cd.
    cd_types = {'I': 0, 'P': 0}

    # Cycle through the tickets that contain a cd position.
    for tick in cd_tickets:
        # Create the cd position tag and add the part name and
        # sheet number as attributes.
        cd_tag = ET.SubElement(xml_doc, 'CD_position')
        cd_tag.set('part', part)
        cd_tag.set('sheet', str(tick.get_sheet_number()).zfill(3))

        # Create the variant tag and set its type and tier
        # values as attributes.
        variant = ET.SubElement(cd_tag, 'Variant')
        typo = tick.get_cd_type()
        variant.set('type', typo)
        variant.set('tier', str(tick.get_cd_tier()))

        # Increment the count for this cd type.
        cd_types[typo] += 1

        # Create the placement tag and set its position and up
        # values as attributes.
        placement = ET.SubElement(cd_tag, 'Placement')
        placement.set('position', str(tick.get_position_on_sheet()))
        placement.set('up', str(tick.get_up()))
    # Add the instant and pick counts as attributes of the game tag.
    xml_doc.set('instants', str(cd_types['I']))
    xml_doc.set('picks', str(cd_types['P']))

    # Send the xml document off to clean itself up.
    prettify_xml(xml_doc)

    # Create the tree with the xml document and write it to a file.
    tree = ET.ElementTree(xml_doc)
    tree.write(f"{destination}_cds.xml", encoding="utf-8", xml_declaration=True)


def prettify_xml(element: xml.etree.ElementTree.Element, indent: str = '   ') -> None:
    """
    Format the xml to include uniform indentation for all element levels.
    This doesn't work perfectly in all cases (and I haven't been able to track
    down the problem), but it's a damn sight better than the default output.

    :param element: top level element containing xml tree
    :type element: xml.etree.ElementTree.Element
    :param indent: string containing the indentation (default: three spaces)
    :type indent: str
    :return: None
    :rtype: None
    """
    queue = [(0, element)]  # (level, element)
    while queue:
        level, element = queue.pop(0)
        children = [(level + 1, child) for child in list(element)]
        if children:
            element.text = '\n' + indent * (level + 1)  # for child open
        if queue:
            element.tail = '\n' + indent * queue[0][0]  # for sibling open
        else:
            element.tail = '\n' + indent * (level - 1)  # for parent close
        queue[0:0] = children  # prepend so children come before siblings


def write_cd_multi_spot_positions_to_file(part: str, filename: str, cd_tickets: list[BonanzaTicket],
                                          cd_tier_level: int, spots_per_ticket: int, output_folder: str = '') -> None:
    """
    Take a list of cd tickets and write out the pertinent information to a csv file
    specifically for tickets with more than one possible cd placement.

    :param part: The Bonanza part prefix for this game
    :type part: str
    :param filename: The base file name for the csv file
    :type filename: str
    :param cd_tickets: tickets containing cds
    :type cd_tickets: list[BonanzaTicket]
    :param cd_tier_level: the highest tier for cds
    :type cd_tier_level: int
    :param spots_per_ticket: number of possible cd spots on each ticket
    :type spots_per_ticket: int
    :param output_folder: destination for output files
    :type output_folder: str
    :return: None
    :rtype: None
    """
    # If the cd tier level is 0, I don't know why we're here in the first place
    if cd_tier_level == 0:
        return
    # Open the file and write out the field names
    if output_folder != '' and os.path.exists(output_folder):
        destination = f"{output_folder}/{filename}"
    else:
        # Check if a 'results' directory exists in the project directory and creat it if it doesn't.
        if not os.path.exists('./results'):
            os.mkdir('./results')
        destination = f"./results/{filename}"
    file = open(f"{destination}_cds.csv", 'w')
    file.write('part,up,tier,position,type\n')
    # Cycle through the tickets
    for tick in cd_tickets:
        # Because the 3 window has multiple (3) cd positions per ticket,
        # we must multiply the ticket number (-1) by 3 and add the position
        # on ticket to the total to refer to the correct field name.
        t_position = tick.get_position_on_sheet()
        t_slot = tick.get_position_on_ticket()
        sheet = str(tick.get_sheet_number()).zfill(3)
        position = ((t_position - 1) * spots_per_ticket) + t_slot
        # Write out values to the file
        file.write(f"{part}_{sheet},{tick.get_up()},{tick.get_cd_tier()},{position},{tick.get_cd_type()}\n")


def create_game_stacks(tickets: list[BonanzaTicket], q_ups: int, q_sheets: int,
                       q_sheet_capacity: int, mixer=True, q_subflats=0) -> list[list[BonanzaTicket]]:
    """
    Create the required number of ticket variations for each up. The total number of ups
    divided by the number of permutations gives the necessary number of copies of each perm.
    Call the randomize method to evenly spread each type of ticket across the sheet faces.

    :param tickets: list of tickets for this flat
    :type tickets: list[BonanzaTicket]
    :param q_ups: the number of ups in this flat
    :type q_ups: int
    :param q_sheets: number of sheets in the flat
    :type q_sheets: int
    :param q_sheet_capacity: the number of tickets per sheet
    :type q_sheet_capacity: int
    :param mixer: Should these tickets be randomized?
    :type mixer: bool
    :param q_subflats: number of subflats in this flat (should either be 0 or greater than 1 (never 1))
    :type q_subflats: int
    :return: list of lists of tickets for each up
    :rtype: list[list[Ticket]]
    """
    game_stacks = []
    reset_csv_fields = True
    for up in range(q_ups):
        stack = []
        # Randomize evenly across up columns on sheet. Choose the appropriate method based on the
        # presence of subflats.
        if q_subflats > 1:
            # Update the ticket csv field to include the subflat column
            if reset_csv_fields:
                tickets[0].add_subflat_to_csv_fields()
                reset_csv_fields = False
            if mixer:
                stack = apportion_and_randomize_subflat_stack(copy.deepcopy(tickets), up + 1, q_sheets,
                                                              q_sheet_capacity, q_ups, q_subflats)
            else:
                stack = apportion_subflat_stack(copy.deepcopy(tickets), up + 1, q_sheets,
                                                q_sheet_capacity, q_ups, q_subflats)
        else:
            if mixer:
                stack = apportion_and_randomize_stack(copy.deepcopy(tickets), up + 1, q_sheets, q_sheet_capacity, q_ups)
            else:
                stack = apportion_game_stack(copy.deepcopy(tickets), up + 1, q_sheets, q_sheet_capacity, q_ups)
        game_stacks.append(stack)
    return game_stacks


def create_game_stacks_with_schisms(tickets: list[BonanzaTicket], q_ups: int, q_sheets: int,
                                    q_sheet_capacity: int, mixer=False, q_schisms=0) -> list[list[BonanzaTicket]]:
    """
    Generates game stacks that split the ups vertically to simulate subflats. Winners, holds, picks, and
    nonwinners are divided into each split as evenly as possible. This has to be done in order to assign
    the same serial number across the up.

    :param tickets: List of BonanzaTicket objects to arrange into stacks.
    :type tickets: list[BonanzaTicket]
    :param q_ups: The number of ups in the flat.
    :type q_ups: int
    :param q_sheets: Number of sheets in the flat.
    :type q_sheets: int
    :param q_sheet_capacity: The total ticket capacity per sheet.
    :type q_sheet_capacity: int
    :param mixer: Determines if sub-stacks should be shuffled multiple times for randomness. Defaults to False.
    :type mixer: bool, optional
    :param q_schisms: Number of schisms or subdivisions to divide the stacks and rearrange. Defaults to 0.
    :type q_schisms: int, optional
    :return: A list of game stacks containing tickets split for even distribution.
    :rtype: list[list[BonanzaTicket]]
    """
    # Create lists for the game stacks and vertical splits
    game_stacks = []
    schisms = []
    tps = int(int(q_sheet_capacity / q_ups) / q_schisms)
    # Create a sublist for each split
    for _ in range(q_schisms):
        schisms.append([])

    # Cycle through each up.
    for _ in range(q_ups):
        ticks = copy.deepcopy(tickets)
        stacker = []
        # Populate the first three sheets of each split with nonwinners.
        for _ in range(3):
            # Divide the sheet capacity by the number of ups and divide the result by
            # the number of splits to get the number of tickets for each schism.
            # for _ in range(int(int(q_sheet_capacity / q_ups) / q_schisms)):
            for _ in range(tps):
                for i in range(q_schisms):
                    stacker.append(ticks.pop())
        # Cycle through the rest of the sheets and add tickets to each split
        # sequentially until all the expected spaces have been filled. There
        # list should be exhausted a
        for _ in range(q_sheets - 3):
            # Divide the sheet capacity by the number of ups and divide the result by
            # the number of splits to get the number of tickets for each schism.
            # for _ in range(int(int(q_sheet_capacity / q_ups) / q_schisms)):
            for _ in range(tps):
                # Add tickets from the front of the list, since that's where the winners,
                # picks, and holds will be located. We want to keep all of those as close
                # to page 4 as possible, so they will be added first.
                for i in range(q_schisms):
                    schisms[i].append(ticks.pop(0))
            # Combine the schisms consecutively to match how they'll appear on the sheet.
            for i in range(q_schisms):
                stacker.extend(schisms[i])
                schisms[i].clear()
        # Split the stack into their vertical
        # sub_stacks = split_list(stacker, q_schisms)
        sub_stacks = split_schisms(stacker, q_schisms, tps, q_sheets)
        for _ in range(rn.randint(1, 2)):
            rn.shuffle(sub_stacks)
        if mixer:
            for _ in range(rn.randint(2, 4)):
                for sub_stack in sub_stacks:
                    rn.shuffle(sub_stack)
        stacker.clear()
        stacker = fuse_schisms(sub_stacks, tps, q_sheets)
        # for sub_stack in sub_stacks:
        #     stacker.extend(sub_stack)
        game_stacks.append(stacker)

    return game_stacks


def create_game_stacks_from_permutations(perms: list[list[BonanzaTicket]], q_ups: int,
                                         q_sheets: int, q_sheet_capacity: int, verbose=False,
                                         q_subflats=0) -> list[list[BonanzaTicket]]:
    """
    Take a list of permutations and create the required number of ups from it.

    :param perms: list of lists containing tickets, each list being a permutation
    :type perms: list[list[BonanzaTicket]]
    :param q_ups: number of ups in this flat
    :type q_ups: int
    :param q_sheets: number of sheets in the flat
    :type q_sheets: int
    :param q_sheet_capacity: number of the tickets per sheet
    :type q_sheet_capacity: int
    :param verbose: whether to print debug/tracking information to the screen
    :type verbose: bool
    :param q_subflats: number of subflats in this flat (should either be 0 or greater than 1 (never 1))
    :type q_subflats: int
    :return: list of lists containing tickets for each up
    :rtype: list[list[Ticket]]
    """
    # Get the number of ups per permutation
    q_permutations = len(perms)
    q_ups_per_perm = int(q_ups / q_permutations)
    if verbose:
        print(f"Creating {q_ups_per_perm} iterations of each of the {q_permutations}"
              f" permutations for a total of {q_ups} ups.")
    game_stacks = []
    # Cycle through the permutations and create the required number of shuffled copies for each
    for idx, perm in enumerate(perms):
        if verbose:
            print(f'    Processing perm {idx + 1}')
            print('        Up: ', end='')
        # Produce single up
        for up in range(q_ups_per_perm):
            # Calculate the up number according to permutation number plus up number for this permutation
            x = (idx * q_ups_per_perm) + up + 1
            if verbose:
                print(f"{x}", end=" ")
            # If there are subflats, use the new subflat-friendly apportion and randomize method.
            if q_subflats > 1:
                stack = apportion_and_randomize_subflat_stack(copy.deepcopy(perm), x, q_sheets, q_sheet_capacity,
                                                              verbose, q_subflats)
            else:
                stack = apportion_and_randomize_stack(copy.deepcopy(perm), x, q_sheets, q_sheet_capacity, q_ups)
            game_stacks.append(stack)
        if verbose:
            print('')
    return game_stacks


def apportion_and_randomize_stack(stack: list[BonanzaTicket], up: int, q_sheets: int,
                                  q_sheet_capacity: int, q_ups: int) -> list[BonanzaTicket]:
    """
    Create a randomized stack of tickets that uniformly spreads the ticket
    types across the number of substacks needed (equal to the number of tickets
    per up on a sheet).

    :param q_sheets: number of sheets in the flat
    :type q_sheets: int
    :param q_ups: number of ups in each flat
    :type q_ups: int
    :param q_sheet_capacity: number of tickets per sheet
    :type q_sheet_capacity: int
    :param stack: a list of all the tickets used in one up of a game
    :type stack: list[BonanzaTicket]
    :param up: number associated with this up
    :type up: int
    :return: reordered list of tickets
    :rtype: list[Ticket]
    """
    # print(f"up = {up}")
    # global q_sheet_capacity, q_ups, q_sheets
    # Calculate the number of tickets appearing on each sheet for each up
    tickets_per_sheet = int(q_sheet_capacity / q_ups)
    mixed_stack = []
    index = []
    # Create a list for each stack and one containing the index numbers
    for i in range(tickets_per_sheet):
        mixed_stack.append([])
        index.append(i)
    for i in range(rn.randint(2, 6)):
        rn.shuffle(index)
    # Create an iterator for the randomized indexes, then
    # cycle through the tickets and add one to the list
    # at the current index
    cyclindex: cycle[int] = cycle(index)
    for ticket in stack:
        new_up = up
        ticket.reset_up(new_up)
        mixed_stack[next(cyclindex)].append(ticket)

    # Shuffle the ticket positions in each substack
    for substack in mixed_stack:
        shuffles = rn.randint(2, 6)
        for x in range(shuffles):
            rn.shuffle(substack)

    # Shuffle the substack positions on the sheet
    shuffles = rn.randint(2, 6)
    for i in range(shuffles):
        rn.shuffle(mixed_stack)

    # Combine substacks into a single list and return it
    grand_stack = []
    for i in range(q_sheets):
        for substack in mixed_stack:
            grand_stack.append(substack.pop(0))

    return grand_stack


def apportion_game_stack(stack: list[BonanzaTicket], up: int, q_sheets: int,
                         q_sheet_capacity: int, q_ups: int) -> list[BonanzaTicket]:
    """
    Create a stack of tickets that uniformly spreads the ticket-types across the
    number of substacks needed (equal to the number of tickets per up on a sheet).

    :param stack: list of tickets for this up
    :type stack: list[BonanzaTicket]
    :param up: which up this is
    :type up: int
    :param q_sheets: number of sheets in the flat
    :type q_sheets: int
    :param q_sheet_capacity: number of tickets per sheet
    :type q_sheet_capacity: int
    :param q_ups: number of ups in this game
    :type q_ups: int
    :return: apportioned list of tickets
    :rtype: list[BonanzaTicket]
    """
    tickets_per_sheet = int(q_sheet_capacity / q_ups)
    sub_stacks = []
    # Create the lists to hold the tickets for each spot of the up
    for _ in range(tickets_per_sheet):
        sub_stacks.append([])
    # Create three pages worth of nonwinners to avoid crimping on the winning tickets
    for _ in range(3):
        for ss in sub_stacks:
            ticket = stack.pop()
            ticket.reset_up(up)
            ss.append(ticket)
    # Cycle through the remaining sheets and layout the tickets in order of their appearance
    for _ in range(q_sheets - 3):
        for ss in sub_stacks:
            ticket = stack.pop(0)
            ticket.reset_up(up)
            ss.append(ticket)
    # Create a single stack and cycle through each column of each sheet to
    # properly order the tickets for csv export.
    grand_stack = []
    for _ in range(q_sheets):
        for ss in sub_stacks:
            grand_stack.append(ss.pop(0))

    return grand_stack


def apportion_and_randomize_subflat_stack(stack: list[BonanzaTicket], up: int, q_sheets: int, q_sheet_capacity: int,
                                          q_ups: int, q_subflats: int) -> list[BonanzaTicket] | None:
    """
    Create a randomized stack of tickets that uniformly spreads the ticket types
    across the number of substacks needed (equal to the number of tickets per up
    on a sheet) AS WELL AS evenly distributing them among the subflats.

    :param stack: a list of all the tickets used in one up of a game
    :type stack: list[BonanzaTicket]
    :param up: number associated with this up
    :type up: int
    :param q_sheets: number of sheets in the flat
    :type q_sheets: int
    :param q_sheet_capacity: number of tickets per sheet
    :type q_sheet_capacity: int
    :param q_ups: number of ups in each flat
    :type q_ups: int
    :param q_subflats: number of subflats in this flat
    :type q_subflats: int
    :return: reordered list of tickets
    :rtype: list[Ticket]
    """
    # Calculate the number of tickets on each sheet for this up as
    # well as how many tickets are in each subflat.
    ticks_per_sheet = int(q_sheet_capacity / q_ups)
    sheets_per_subflat = int(q_sheets / q_subflats)

    # Create a list containing subflats, each comprised of a list of columns in this
    # up, which will all contain a list of tickets for their associated subflat.
    # Create the subflat list
    subflat_stacks = []
    for _ in range(q_subflats):
        # Create the column list for this flat
        column_stack = []
        # Add a list to each column to hold the tickets
        for _ in range(ticks_per_sheet):
            column_stack.append([])
        # Add each column to the subflat
        subflat_stacks.append(column_stack)

    # Create a list of integers for each subflat that represents the
    # positions of the tickets on a given sheet for this up and use it to
    # randomize the placement of tickets. This will reduce the chance
    # of winners clumping together in one area of the flat.
    stack_orders = []
    for _ in range(q_subflats):
        stack_orders.append(list(range(0, ticks_per_sheet)))
    for i in range(len(stack_orders)):
        rn.shuffle(stack_orders[i])

    # Cycle through the sheets for each subflat and add a ticket to every
    # column for this up in order of the shuffled positions.
    for t in range(sheets_per_subflat):
        # Shuffle the column order for each subflat
        for x in range(len(stack_orders)):
            rn.shuffle(stack_orders[x])
        # Iterate through the number of tickets needed a single sheet
        for c in range(ticks_per_sheet):
            # Add one ticket to a column in each subflat
            for i in range(q_subflats):
                # Pop a ticket off the ticket list, reset the up and subflat
                # values, and add it to the next column.
                tick = stack.pop(0)
                tick.reset_up(up)
                tick.reset_subflat(i + 1)
                subflat_stacks[i][stack_orders[i][c]].append(tick)

    # There's a whole lotta shufflin' goin' on.
    # Cycle through the subflats
    for s in range(q_subflats):
        # Cycle through the columns
        for c in range(ticks_per_sheet):
            # Shuffle the tickets in each column
            for _ in range(rn.randint(2, 5)):
                rn.shuffle(subflat_stacks[s][c])
        # Shuffle the columns in each subflat
        for _ in range(rn.randint(2, 5)):
            rn.shuffle(subflat_stacks[s])
    # Shuffle the subflat positions
    for _ in range(rn.randint(2, 5)):
        rn.shuffle(subflat_stacks)

    # Create a single list with tickets in the order they'll be
    # sent to the csv file.
    final_stack = []
    # Cycle through each subflat
    for subby in range(q_subflats):
        # Cycle through each sheet in the subflat
        for _ in range(sheets_per_subflat):
            # Cycle through the columns for each sheet
            for uptick in range(ticks_per_sheet):
                # Pop a ticket off at the next flat position and reset
                # its subflat, then add it to the final stack.
                tick = subflat_stacks[subby][uptick].pop(0)
                tick.reset_subflat(subby + 1)
                final_stack.append(tick)

    return final_stack


def apportion_subflat_stack(stack: list[BonanzaTicket], up: int, q_sheets: int, q_sheet_capacity: int,
                            q_ups: int, q_subflats: int) -> list[BonanzaTicket] | None:
    """
    Create a stack of tickets that uniformly spreads the ticket types across the
    number of substacks needed (equal to the number of tickets per up on a sheet)
    AS WELL AS evenly distributing them among the subflats.

    :param stack: a list of all the tickets used in one up of a game
    :type stack: list[BonanzaTicket]
    :param up: the number associated with this up
    :type up: int
    :param q_sheets: the number of sheets in the flat
    :type q_sheets: int
    :param q_sheet_capacity: the number of tickets per sheet`
    :type q_sheet_capacity: int
    :param q_ups: the total number of ups in this flat
    :type q_ups: int
    :param q_subflats: the number of subflats in this flat
    :type q_subflats: int
    :return: a reordered list of tickets
    :rtype: list[BonanzaTicket] | None
    """
    # Calculate the number of tickets on each sheet for this up as
    # well as how many tickets are in each subflat.
    ticks_per_sheet = int(q_sheet_capacity / q_ups)
    sheets_per_subflat = int(q_sheets / q_subflats)

    # Create a list containing subflats, each comprised of a list of columns in this
    # up, which will all contain a list of tickets for their associated subflat.
    # Create the subflat list
    subflat_stacks = []
    for _ in range(q_subflats):
        # Create the column list for this subflat
        column_stack = []
        # Add a list for each column to hold the tickets
        for _ in range(ticks_per_sheet):
            column_stack.append([])
        # Add the columns list to the subflat
        subflat_stacks.append(column_stack)

    # Cycle through the first three pages of subflats and add nonwinners to each spot,
    # which are located at the end of the list of tickets. So, pop the tickets from
    # the very end of the list.
    for _ in range(3):
        # Cycle through each subflat list
        for s in range(q_subflats):
            # Cycle through the stacks for each space on the sheet for this up.
            for c in subflat_stacks[s]:
                ticket = stack.pop(-1)
                ticket.reset_up(up)
                ticket.reset_subflat(s + 1)
                c.append(ticket)

    # Cycle through the remaining sheets by subflat and add tickets from the
    # front of the list to each one until the well is dry.
    # Cycle through sheets (total sheets minus the three already created for each subflat)
    for _ in range(sheets_per_subflat - 3):
        # Cycle through the tickets per sheet first, so the important (winners/picks)
        # tickets are spread evenly (-ish) across the subflats.
        for c in range(ticks_per_sheet):
            # Cycle through each subflat and add a ticket to its list.
            for s in range(q_subflats):
                ticket = stack.pop(0)
                ticket.reset_up(up)
                ticket.reset_subflat(s + 1)
                subflat_stacks[s][c].append(ticket)

    # Create a single list with tickets in the order they'll be
    # sent to the csv file.
    final_stack = []
    # Cycle through each subflat in the outer loop to assure all the
    # tickets for that subflat are contiguous in the csv file.
    for subby in range(q_subflats):
        # Next, cycle through each sheet in the subflat, so its
        # tickets are together in the csv.
        for _ in range(sheets_per_subflat):
            # Cycle through the columns for each sheet, and add their tickets
            # consecutively to ensure they're clumped together in the csv.
            for uptick in range(ticks_per_sheet):
                # Pop a ticket off at the next flat position, reset its
                # subflat, then add it to the final stack.
                tick = subflat_stacks[subby][uptick].pop(0)
                tick.reset_subflat(subby + 1)
                final_stack.append(tick)
    # Return the reordered ticket list.
    return final_stack


def split_list(lst: list, schisms: int) -> list[list]:
    """
    Splits a given list into `n` parts as evenly as possible. The resulting sub-lists
    may vary in size by at most one element. The function ensures that the extra
    elements are distributed among the first few sub-lists.

    :param lst: The input list to be split into sub-lists
    :type lst: list
    :param schisms: The number of sub-lists to split the input list into
    :type schisms: int
    :return: A list containing `n` sub-lists, with elements distributed as evenly
        as possible
    :rtype: list[list]
    """
    quote, rem = divmod(len(lst), schisms)
    return [lst[i * quote + min(i, rem):(i + 1) * quote + min(i + 1, rem)] for i in range(schisms)]


def split_schisms(lst: list[BonanzaTicket], q_schisms: int, tps: int, pps: int) -> list[list[BonanzaTicket]]:
    """
    Split a list of tickets vertically into `n` parts. This makes it possible to
    shuffle the location of each split so the casing of winners will vary from
    game to game when the pseudo-subflat layout is employed.

    :param lst: The input list to be split into sub-lists
    :type lst: list
    :param q_schisms: The number of sub-lists to split the input list into
    :type q_schisms: int
    :param tps: tickets per schism per sheet
    :type tps: int
    :param pps: total number of sheets
    :type pps: int
    :return: list of lists of tickets
    :rtype list[list]
    """
    # Create the list to hold the splits
    schisms = []
    for _ in range(q_schisms):
        schisms.append([])
    # Cycle through the tickets sheet by sheet
    for _ in range(pps):
        # Cycle through each split
        for i in range(q_schisms):
            # Add the tickets for this split from this sheet.
            for _ in range(tps):
                schisms[i].append(lst.pop(0))
    return schisms


def fuse_schisms(lst: list[list[BonanzaTicket]], tps: int, ppf: int) -> list[BonanzaTicket]:
    """
    Take a list of lists comprised of tickets representing the vertical splits and place them
    in a single list in the order they will be written to the csv file.

    :param lst: List of lists of tickets
    :type lst: list[list[BonanzaTicket]]
    :param tps: tickets per sheet
    :type tps: int
    :param ppf: pages per flat
    :type ppf: int
    :return: list of tickets
    :rtype list[BonanzaTicket]
    """
    # Create the single-dimension list to be used to contain the tickets.
    fusion = []
    # Cycle through the number of pages.
    for _ in range(ppf):
        # Cycle through the splits.
        for schism in lst:
            # Cycle through each ticket for this split on this sheet
            # and add them to the fused list.
            for _ in range(tps):
                fusion.append(schism.pop(0))
    return fusion
