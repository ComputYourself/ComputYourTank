#!/usr/bin/env python3

import os
import sys
import subprocess
import time

playerState = []
playersPos = []
bulletsPos = []
pipes = []
actions = []

readFiles = []

playerSpeed = 1
bulletSpeed = 1
dimX = 128
dimY = 128

nbPlayer = 2


def child(ident):
    print("\nA new child ",  os.getpid())
   
    sys.stderr.write("plop2")
   
    try:
        os.dup2(pipes[ident][0][0], sys.stdin.fileno())
        os.dup2(pipes[ident][1][1], sys.stdout.fileno())
        subprocess.call("./client.py")
    except ValueError:
        sys.stderr.write("plop1")
        
    time.sleep(2)
    
    # Cleaning pipes
    try:
        os.close(pipes[ident][0][0])
        os.close(pipes[ident][0][1])
        os.close(pipes[ident][1][0])
        os.close(pipes[ident][1][1])
    except ValueError:
        sys.stderr.write("plop2")
        
    

    os._exit(0)
    

def server():
    # Initialisation
    actions = ["NONE"] * nbPlayer
    playerState = ["ALIVE"] * nbPlayer
    for i in range(nbPlayer):
        readFiles.append(os.fdopen(pipes[i][1][0], 'r'))
        playersPos.append([0, 0]) #TODO positioner qqpart
        line = str.encode(str(i) + " " + str(nbPlayer) + " " + str(playerSpeed) + " " + str(bulletSpeed) + " " + str(dimX) + " " + str(dimY) + "\n")
        os.write(pipes[i][0][1], line)
    
    
    while True: # Turn loop
        for i in range(nbPlayer):
            actions[i] = "NONE"
            line = str.encode(str(playerState[i]) + " " + str(playersPos[i][0]) + " " + str(playersPos[i][1]) + "\n")
            os.write(pipes[i][0][1], line)
            
        for i in range(nbPlayer):
            firstLine = readFiles[i].readline()
            char = firstLine[0]
            if firstLine[0] == 'I':
                print("Player "+ str(i) +" Infos")
                for i in range(nbPlayer):
                    line = str.encode("JOUEUR " + str(i) + " " + str(playersPos[i][0]) + " " + str(playersPos[i][1]) + "\n")
                    os.write(pipes[i][0][1], line)
            elif firstLine[0] == 'M':
                print("Move")
            elif firstLine[0] == 'F':
                print("Fire")
            else:
                print("Looser")
                os._exit(0)
    
    

def main():
    
    for ident in range(nbPlayer):
        pinr, pinw = os.pipe()
        poutr, poutw = os.pipe()
        pipes.append([[pinr,pinw], [poutr, poutw]])
        newpid = os.fork()
        if newpid == 0: #I'm the child
            child(ident)
        else: # I'm the server
            pids = (os.getpid(), newpid)
    
    server()


main()
