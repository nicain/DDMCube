#!/usr/bin/env python

def startServers(ppservers = ('fig.amath.washington.edu:8080', 'lemon.amath.washington.edu:8080'), serverDirectory = '~/DDMCube'):
    import os, subprocess, time, socket

    localMachine = socket.gethostname()
    serverDirectory = os.path.expanduser(serverDirectory)
    p = []
    for currServerAndPort in ppservers:
        currServer, currPort = currServerAndPort.split(':')
        if not(currServer == localMachine):
            command = 'cd ' + serverDirectory + '; ppserver.py -p ' + str(currPort)
            p.append(subprocess.Popen(['ssh ' + currServer + ' \'' + command + ' \''], stdout=subprocess.PIPE, shell=True))
            print '   ' + currServer + ': Initialized'
        else:
            print '   ' + currServer + ': Initialized'            

    print '     Finalizing cluster...'
    time.sleep(5)
    return p



def killAllServers(ppservers = ('fig.amath.washington.edu:8080', 'lemon.amath.washington.edu:8080'), serverDirectory = '~/DDMCube'):
    import os, subprocess, time

    userName = os.getlogin()
    p = []
    for currServerAndPort in ppservers:
        currServer, currPort = currServerAndPort.split(':')
        command = 'cd ' + serverDirectory + '; python ppserverKill.py -u ' + userName + ' -p ' + str(currPort)
        p.append(subprocess.Popen(['ssh ' + currServer + ' \'' + command + ' \''], stdout=subprocess.PIPE, shell=True))
        print '     ' + currServer + ': Shutdown complete'

    time.sleep(5)
    return p
