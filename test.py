#!/usr/bin/env python3

# TODO Checker Popen dans le package subprocess (si on reste en Python)

import os
import sys
import subprocess
import time
import glob
import signal

processes = []

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

#nbPlayer = 3


def child(ident, program):
    print("A new child", os.getpid(), "player", ident, "exec program", program)
   
    # sys.stderr.write("plop2")
   
    try:
        os.dup2(pipes[ident][0][0], sys.stdin.fileno())
        os.dup2(pipes[ident][1][1], sys.stdout.fileno())

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
        
    

    os._exit(0)
    

def server(nbPlayer):
    # Initialisation
    actions = ["NONE"] * nbPlayer
    playerState = ["ALIVE"] * nbPlayer
    for i in range(nbPlayer):
        readFiles.append(os.fdopen(pipes[i][1][0], 'r'))
        playersPos.append([0, 0]) #TODO positioner qqpart
        line = str.encode(str(i) + " " + str(nbPlayer) + " " + str(playerSpeed) + " " + str(bulletSpeed) + " " + str(dimX) + " " + str(dimY) + "\n")
        os.write(pipes[i][0][1], line)
    
    
    gameEnded = False
    
    while not gameEnded: # Turn loop
        #input() # a des fins de test
        print("\n===========================")
        for i in range(nbPlayer):
            actions[i] = "NONE"
            line = str.encode(str(playerState[i]) + " " + str(playersPos[i][0]) + " " + str(playersPos[i][1]) + "\n")
            print("Player "+str(i)+" "+str(playerState[i]) + " " + str(playersPos[i][0]) + " " + str(playersPos[i][1]))
            os.write(pipes[i][0][1], line)

        # TODO le mouvement des balles ici

            
        for i in range(nbPlayer):
            if playerState[i] == "ALIVE":
                firstLine = readFiles[i].readline()
                char = firstLine[0]
                if firstLine[0] == 'I':
                    print("Player "+ str(i) +" Infos")
                    for i in range(nbPlayer):
                        line = str.encode("JOUEUR " + str(i) + " " + str(playersPos[i][0]) + " " + str(playersPos[i][1]) + "\n")
                        os.write(pipes[i][0][1], line)
                elif firstLine[0] == 'M':
                    print("Player "+ str(i) +" Move")
                elif firstLine[0] == 'F':
                    print("Player "+ str(i) +" Fire")
                else:
                    print("Player "+ str(i) +" lost by inaction")
                    playerState[i] = "DEAD"

        # Checks if at least two players are alive
        onePlayerAlive = False
        gameEnded = True
        for i in range(nbPlayer):
            if playerState[i] == "ALIVE":
                if not onePlayerAlive :
                    onePlayerAlive = True
                else :
                    gameEnded = False
                    break
        
        if gameEnded:
            print("\nGAME OVER")
            draw = True
            for i in range(nbPlayer):
                if playerState[i] == "ALIVE":
                    draw = False
                    print("Player "+str(i)+" won")
            if draw:
                print("Draw")

            # print(processes)
            # for p in processes:
            #     print("process "+str(p))
            #     p.terminate()

            # Cleaning pipes
            for ident in range(nbPlayer):
                try:
                    os.kill(processes[ident], signal.SIGSTOP) 
                    os.close(pipes[ident][0][0])
                    os.close(pipes[ident][0][1])
                    os.close(pipes[ident][1][0])
                    os.close(pipes[ident][1][1])
                except ValueError:
                    sys.stderr.write("plop2")
            os._exit(0)
            


    
    

def main():
    
    # TODO pour chancun des enfant, lui faire ouvrir une IA differente des autres dans le dossier ./clients
    clients = glob.glob('./clients/*')
    nbPlayer = len(clients)

    print("nbPlayer = "+str(nbPlayer))
    print("Parent", os.getpid())
    for ident in range(nbPlayer):
        pinr, pinw = os.pipe()
        poutr, poutw = os.pipe()
        pipes.append([[pinr,pinw], [poutr, poutw]])
        newpid = os.fork()
        if newpid == 0: #I'm the child
            child(ident, clients[ident])
        else: # I'm the server
            pids = (os.getpid(), newpid)
            processes.append(newpid)
    
    server(nbPlayer)


main()
