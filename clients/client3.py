#!/usr/bin/env python3




INIT = input()

INIT = INIT.split()

ID = int(INIT[0])
NB_TANKS = int(INIT[1])


STATE_TANKS = []
for i in range(0, NB_TANKS):
    STATE_TANKS.append("ALIVE")

TARGET = 0
TARGET_POS = (0, 0)


while True:
    input() # get own stat line
    target_acquired = False
    print("Info")
    for i in range(0, NB_TANKS):
        line = input()

        if i != ID and not target_acquired:
            line = line.split()
            STATE_TANKS[i] = line[2]
            if STATE_TANKS[i] == "ALIVE":
                TARGET = i
                TARGET_POS = (float(line[3]), float(line[4]))
                target_acquired = True
    input() #get own stat line
    if TARGET != ID:
        print("Fire " + str(TARGET_POS[0]) + " " + str(TARGET_POS[1]) + " targeting player "+str(TARGET))
    else:
        print("Move 128 128")
input()
print("Plop")
