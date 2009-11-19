#!/usr/bin/env python

import subprocess, os, signal
from optparse import OptionParser

# Set up parser:
parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-u", "--user", dest="userName", help="Owner of processes to be deleted", default="nicain", type="string")
parser.add_option("-p", "--port", dest="port", help="Port address of ppserver job", default="8080", type="int")

# Process file inputs:
(options, args) = parser.parse_args()
userName = options.userName
port = options.port

# Collect PID's to kill:
toKillString = subprocess.Popen(['ps -ef | grep ppserve[r] | grep ' + userName + ' | grep ' + str(port)], stdout=subprocess.PIPE, shell=True).communicate()
killStringList = [line for line in toKillString[0].split('\n')]
PIDList = []
for killString in killStringList:
    if killString.strip() != '':
        pieces = [piece for piece in killString.split()]
        PIDList.append(pieces[1])

# Kill 'em all, let god sort 'em out:
print PIDList
for PID in PIDList:
    os.kill(int(PID), signal.SIGTERM)
