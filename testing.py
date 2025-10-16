file = open("./old_results/BarBeano-4902_tickets.csv", "r")

lines = file.readlines()

rows = []
skip = True

for line in lines:
    if skip:
        skip = False
        continue
    line = (line.strip().split(","))[2:-2]
    rows.append(line)

file.close()

spots = list(map(str, range(1, 76)))
spotters = {}
for spot in spots:
    spotters[spot] = 0

for row in rows:
    for spot in row:
        spotters[spot] += 1

print(len(rows))
