import random as rn
import itertools as it
from ticketing.universal_ticket import UniversalTicket as uTick
import ticketing.ticket_io as tio

winners = set()
rejections = 0
big_rejections = 0
numbers = [[], [], []]


def make_lists():
    a = list(range(1, 26))
    b = list(range(26, 51))
    c = list(range(51, 76))

    for i in range(rn.randint(2, 5)):
        rn.shuffle(a)
        rn.shuffle(b)
        rn.shuffle(c)
    return [a, b, c]


def create_candidate_card():
    global numbers
    if len(numbers[0]) < 3:
        numbers = make_lists()
    face = [[], [], []]
    for _ in range(3):
        face[0].append(numbers[0].pop(0))
        face[1].append(numbers[1].pop(0))
        face[2].append(numbers[2].pop(0))
    return face


def create_winning_combinations(face):
    combs = list(it.product(*face))
    cross = (face[0][1], face[1][0], face[1][1], face[1][2], face[2][1])
    cross_perms = list(it.permutations(cross))
    corner = (face[0][0], face[0][2], face[2][0], face[2][2])
    corner_perms = list(it.permutations(corner))
    xs = (face[0][0], face[0][1], face[0][2])
    ys = (face[1][0], face[1][1], face[1][2])
    zs = (face[2][0], face[2][1], face[2][2])
    x_lines = (xs[0], xs[2], ys[1], zs[0], zs[2])
    x_perms = list(it.permutations(x_lines))
    combs.extend(cross_perms)
    combs.extend(corner_perms)
    combs.extend(x_perms)
    return combs


def are_combinations_valid(paths):
    global rejections, big_rejections
    for path in paths:
        if path in winners:
            rejections += 1
            if len(path) > 3:
                big_rejections += 1
            return [False, path]
    return [True, None]


cards = []

while len(cards) < 128:
    card = create_candidate_card()
    line_combos = create_winning_combinations(card)
    validity = are_combinations_valid(line_combos)
    if validity[0]:
        winners.update(line_combos)
        card.append(line_combos)
        cards.append(card)
        print(f"Number of cards: {len(cards)}")
    else:
        for i in range(len(cards)):
            if validity[1] in cards[i][3]:
                if len(validity[1]) > 3:
                    print("\nX X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X")
                print(f"Invalid combination {validity[1]} found in: {[cards[i][0], cards[i][1], cards[i][2]]}")
                if len(validity[1]) > 3:
                    print("X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X X\n")
                break

tkt = 1
imgs = ['base.ai']
tickets = []
first_pass = True
file_name = 'BarBeano-4902'
for i in cards:
    i.pop()
    numbers = i[0] + i[1] + i[2]
    numbs_str = list(map(str, numbers))
    tickets.append(uTick(tkt, imgs, numbs_str, 1, 1, first_pass))
    first_pass = False
    tkt += 1

tio.write_tickets_to_file(file_name, tickets)
game_stacks = tio.create_game_stacks(tickets, 64, 128, 64)
tio.write_game_stacks_to_file(file_name, game_stacks, 64, 128, 64)
print(f"Rejected {rejections} combinations")
print(f"Rejected {big_rejections} big combinations")