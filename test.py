#!/usr/bin/env python3

# TODO Checker Popen dans le package subprocess (si on reste en Python)

import os
import sys
import subprocess
import time
import glob
import signal
import math
import random
from bullet import Bullet

PROCESSES = []

PLAYER_STATES = []
PLAYER_POS = []
BULLETS = []
PIPES = []
READPIPES = []
ACTIONS = []


PLAYER_SPEED = 1
BULLET_SPEED = 2
DIM_X = 128
DIM_Y = 128
TANK_RADIUS = 1


def try_move(player_id, string):
    """Process a movement from a player.

    Returns true if request is processed, false if wrongly formed"""
    words = string.split()
    if len(words) != 3:
        return False
    x_direction = float(words[1])
    y_direction = float(words[2])
    direction = [x_direction - PLAYER_POS[player_id][0],
                 y_direction - PLAYER_POS[player_id][1]]
    norm = math.sqrt(direction[0] * direction[0] + direction[1] * direction[1])
    if norm == 0:  # The player tries to move to where he already is, do not make move at all
        return True
    direction[0] /= norm
    direction[1] /= norm
    if norm > PLAYER_SPEED:
        direction *= PLAYER_SPEED
    new_pos = (PLAYER_POS[player_id][0] + direction[0],
               PLAYER_POS[player_id][1] + direction[1])
    # print("playersPos[playerID] : "+str(playersPos[playerID][0])+" "+str(playersPos[playerID][1]))
    # print("direction : "+str(direction[0])+" "+str(direction[1]))
    # print("newPos : "+str(newPos[0])+" "+str(newPos[1]))

    PLAYER_POS[player_id][0] = max(min(new_pos[0], DIM_X), 0)
    PLAYER_POS[player_id][1] = max(min(new_pos[1], DIM_Y), 0)
    return True


def try_fire(player_id, string):
    """Process a shot from a player.

    Returns true if request is processed, false if wrongly formed"""
    words = string.split()
    if len(words) != 3:
        return False
    x_destination = float(words[1])
    y_destination = float(words[2])
    direction = [x_destination - PLAYER_POS[player_id][0],
                 y_destination - PLAYER_POS[player_id][1]]
    norm = math.sqrt(direction[0] * direction[0] + direction[1] * direction[1])
    if norm == 0:
        return False
    position = (PLAYER_POS[player_id][0] + direction[0] / norm,
                PLAYER_POS[player_id][1] + direction[1]/norm)
    destination = (x_destination, y_destination)
    BULLETS.append(Bullet(destination, position +
                          destination * TANK_RADIUS, BULLET_SPEED))
    return True


def move_bullets():
    """Moves each bullet a step further, and checks if they collided on the way"""
    for bullet in BULLETS:
        hit = False
        min_t = 0
        tank_no = 0
        position = bullet.position()
        destination = bullet.step()  # Actually moves the bullet
        vector = (destination[0] - position[0], destination[1] - position[1])
        for i, tank_position in enumerate(PLAYER_POS):

            a_coeff = vector[0] * vector[0] + vector[1] * vector[1]
            temp = (position[0] - tank_position[0], position[1] - tank_position[1])
            b_coeff = 2 * (vector[0] * temp[0] + vector[1] * temp[1])
            c_coeff = position[0] * position[0] + position[1] * position[1]
            c_coeff += tank_position[0] * tank_position[0] + \
                tank_position[1] * tank_position[1]
            c_coeff -= 2 * \
                (position[0] * tank_position[0] +
                 position[1] * tank_position[1])
            c_coeff -= TANK_RADIUS * TANK_RADIUS
            discriminant = b_coeff*b_coeff - 4*a_coeff*c_coeff
            if discriminant >= 0:
                sqrt_disc = math.sqrt(discriminant)
                root1 = (-b_coeff + sqrt_disc) / (2 * a_coeff)
                root2 = (-b_coeff - sqrt_disc) / (2 * a_coeff)

                if 0 <= root1 <= 1:
                    if min_t == 0:
                        min_t = root1
                        hit = True
                        tank_no = i
                    else:
                        if root1 < min_t:
                            min_t = root1
                            tank_no = i
                if 0 <= root2 <= 1:
                    if min_t == 0:
                        min_t = root2
                        hit = True
                        tank_no = i
                    else:
                        if root2 < min_t:
                            min_t = root2
                            tank_no = i

        if hit:
            PLAYER_STATES[tank_no] = "DEAD"
            print("Player " + str(tank_no) + " has been shot")
            BULLETS.remove(bullet)



def child(ident, program):
    """Open pipes to cummunicate with server then fetches and exec the IA program to be a player"""
    print("A new child", os.getpid(), "player", ident, "exec program", program)

    # sys.stderr.write("plop2")

    try:
        os.dup2(PIPES[ident][0][0], sys.stdin.fileno())
        os.dup2(PIPES[ident][1][1], sys.stdout.fileno())

        # subprocess.call(program)
        subprocess.Popen(program)
        # processes.append(subprocess.Popen(program))

    except ValueError:
        sys.stderr.write("plop1")

    time.sleep(2)

    # # Cleaning pipes
    # try:
    #     os.close(pipes[ident][0][0])
    #     os.close(pipes[ident][0][1])
    #     os.close(pipes[ident][1][0])
    #     os.close(pipes[ident][1][1])
    # except ValueError:
    #     sys.stderr.write("plop2")

    os._exit(0)  # pylint: disable=W0212


def end_check(nb_player):
    """Checks if at least two players are alive, else the game should end"""
    is_one_player_alive = False
    for i in range(nb_player):
        if PLAYER_STATES[i] == "ALIVE":
            if not is_one_player_alive:
                is_one_player_alive = True
            else:
                return False

    print("\nGAME OVER")
    draw = True
    for i in range(nb_player):
        if PLAYER_STATES[i] == "ALIVE":
            draw = False
            print("Player "+str(i)+" won")
    if draw:
        print("Draw")

    # print(processes)
    # for p in processes:
    #     print("process "+str(p))
    #     p.terminate()

    # Cleaning pipes
    for ident in range(nb_player):
        try:
            os.kill(PROCESSES[ident], signal.SIGSTOP)
            os.close(PIPES[ident][0][0])
            os.close(PIPES[ident][0][1])
            os.close(PIPES[ident][1][0])
            os.close(PIPES[ident][1][1])
        except ValueError:
            sys.stderr.write("plop2")
    os._exit(0)
    return True


def server(nb_player):
    """Body of the server"""
    # Initialisation
    random.seed()
    for i in range(nb_player):
        ACTIONS.append("NONE")
        PLAYER_STATES.append("ALIVE")
        READPIPES.append(os.fdopen(PIPES[i][1][0], 'r'))

        PLAYER_POS.append([random.uniform(0, DIM_X), random.uniform(0, DIM_Y)])
        line = str.encode(str(i) + " " + str(nb_player) + " " + str(PLAYER_SPEED) +
                          " " + str(BULLET_SPEED) + " " + str(DIM_X) + " " + str(DIM_Y) + "\n")
        os.write(PIPES[i][0][1], line)

    game_ended = False

    # Turn loop
    while not game_ended:
        # input() # a des fins de test
        print("\n===========================")
        for i in range(nb_player):
            ACTIONS[i] = "NONE"
            line = str.encode(str(PLAYER_STATES[i]) +
                              " " + str(PLAYER_POS[i][0]) + " " + str(PLAYER_POS[i][1]) + "\n")
            print("Player "+str(i)+" "+str(PLAYER_STATES[i]) + " " + str(
                PLAYER_POS[i][0]) + " " + str(PLAYER_POS[i][1]))
            os.write(PIPES[i][0][1], line)

        move_bullets()

        for i in range(nb_player):
            if PLAYER_STATES[i] == "ALIVE":
                first_line = READPIPES[i].readline()
                if first_line[0] == 'I':
                    print("Player " + str(i) + " Infos")
                    for j in range(nb_player):
                        line = str.encode(
                            "JOUEUR " + str(j) + " " + str(PLAYER_POS[j][0]) + " " + str(PLAYER_POS[j][1]) + "\n")
                        os.write(PIPES[j][0][1], line)
                elif first_line[0] == 'M':  # If player moves
                    if try_move(i, first_line):
                        words = first_line.split()
                        print("Player " + str(i) +
                              " moves toward "+words[1]+" "+words[2])
                    else:
                        print("Player " + str(i) + " went into a wall and died")
                        PLAYER_STATES[i] = "DEAD"
                elif first_line[0] == 'F':  # If player fires
                    if try_fire(i, first_line):
                        words = first_line.split()
                        print("Player " + str(i) +
                              " fires toward "+words[1]+" "+words[2])
                    else:
                        print("Player " + str(i) + " misfired and exploded")
                        PLAYER_STATES[i] = "DEAD"
                else:  # If player does nothing
                    print("Player " + str(i) + " lost by inaction")
                    PLAYER_STATES[i] = "DEAD"

        # Checks if at least two players are alive
        game_ended = end_check(nb_player)


def main():
    """Main fonction"""
    # For each child process, open an IA code from ./clients folder
    clients = glob.glob('./clients/*')
    nb_player = len(clients)

    print("nbPlayer = "+str(nb_player))
    print("Parent", os.getpid())
    for ident in range(nb_player):
        pinr, pinw = os.pipe()
        poutr, poutw = os.pipe()
        PIPES.append([[pinr, pinw], [poutr, poutw]])
        newpid = os.fork()
        if newpid == 0:  # I'm the child
            child(ident, clients[ident])
        else:  # I'm the server
            #pids = (os.getpid(), newpid)
            PROCESSES.append(newpid)

    server(nb_player)


main()
