#!/usr/bin/env python3




INIT = input()

INIT = INIT.split()

ID = int(INIT[0])
NB_TANKS = int(INIT[1])
STATE_TANKS = []
for i in range (0,NB_TANKS):
    STATE_TANKS.append("ALIVE")

target = 0
target_pos = (0, 0)


while True:
    print("Info")
    for i in range (0, NB_TANKS):
        line = input()
        line = line.split()
        STATE_TANKS[i] = line[2]
        if i != ID and STATE_TANKS[i] == "ALIVE" and target <= i:
            target = i
            target_pos = (float(line[3]), float(line[4]))
    input()
    print("Fire " + str(target_pos[0]) + " " + str(target_pos[1]))
input()
print("Plop")
