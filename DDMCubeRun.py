#  DDMCubeRun.py
#  Created by nicain on 11/1/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#  Run from command line: 
#			python DDMCubeRun.py build_ext --inplace

# Compile DDMCube.pyx package
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension("DDMCube", ['DDMCube.pyx'],language="c++")])

# Import remaining python packages:
import sys
try: import DDMCube
except: sys.exit(-1)
import scipy, random, time, os, pickle, uuid, analysisTools
from subprocess import Popen, PIPE

################################################################################
########################           Dashboard:           ########################
################################################################################

# Define job settings:
settings={									# Example values:
'A':list(scipy.linspace(0,0,1)),			# 0
'B':list(scipy.linspace(0,0,1)),			# 0
'beta':list(scipy.linspace(0,.2,1)),		# 0
'chop':list(scipy.linspace(0,25,1)),			# 0
'dt':list(scipy.linspace(.5,.1,1)),		# .02
'K':list(scipy.linspace(.05,.05,1)),		# .05
'tMax':list(scipy.linspace(700,1000,1)),	# 10000, or 400->600 in FD paradigm
'theta':list(scipy.linspace(5,15,20)),		# 10
'xMean':list(scipy.linspace(3,6,1)),		# 3 = 5%C
'xStd':list(scipy.linspace(12.8,15,1)),		# 12.8
'xTau':list(scipy.linspace(20,25,1)),		# 20
'yBegin':list(scipy.linspace(0,40,4)),		# 40
'yTau':list(scipy.linspace(10,10,1))		# 0
}

# Define job parameters:
quickName = 'Test1'
FD=1
numberOfJobs = 5000
verbose = 1
runType = 'localCluster' # Options: 'singleCore', 'dualCore', 'localCluster'

# Set up saving directories
tempResultDir = '/simResults'
saveResultDir = '/savedResults'

################################################################################
########################         Main function:         ########################
################################################################################

# Write a "settings" file:
myUUID = uuid.uuid4()
output = Popen(['git tag | tail -n 1'],stdout=PIPE, shell=True).communicate()
gitVersion = output[0][:-1]
totalLength = 1
for parameter in settings: 
	thisSetting = settings[parameter]
	totalLength *= len(thisSetting)
fOutSet = open(os.getcwd() + saveResultDir + '/' + quickName + '_' + str(myUUID) + '.settings','w')	
pickle.dump((settings, FD, numberOfJobs, gitVersion),fOutSet)
fOutSet.close()

# Display settings:
analysisTools.printSettings(quickName, saveResultDir)

# Run the job:
if runType == 'localCluster' or runType == 'dualCore':
	import pp, math, ppUWTools
	from time import sleep
	
	# Define a helper routine to pass through with pp package:
	def DDMOU_help(settings, FD, perLoc, tempResultDir, quickName, totalUUID, procNum):
		try:
		 	DDMCube.DDMOU(settings, FD, perLoc, tempResultDir, quickName, totalUUID)
			return '   Sub-simulation ' + str(procNum + 1) + ' Complete'
		except: sys.exit(-1)

	if runType == 'dualCore':
		ppservers=()
		job_server = pp.Server(ppservers=ppservers)
		numOfProc = job_server.get_ncpus()		
	else:
		ppservers=("fig.amath.washington.edu:8080","lemon.amath.washington.edu:8080", "grape.amath.washington.edu:8080", "watermelon.amath.washington.edu:8080")
		ppservers=("fig.amath.washington.edu:8080","lemon.amath.washington.edu:8080", "grape.amath.washington.edu:8080", "watermelon.amath.washington.edu:8080", "pineapple.amath.washington.edu:8080", "peach.amath.washington.edu:8080")
		ppUWTools.startServers(ppservers = ppservers)
		job_server = pp.Server(ppservers = ppservers)		
		sleep(10)
		nodeDict = job_server.get_active_nodes()
		print '     ', nodeDict
		numOfProc = 0
		for node in iter(nodeDict):
			numOfProc += nodeDict[node]

	print ' Starting job with ', str(numOfProc), ' processors:'
	tBegin = time.mktime(time.localtime())
	jobs = [(i+1,job_server.submit(DDMOU_help, (settings, FD, math.floor(numberOfJobs/numOfProc), tempResultDir, quickName, myUUID, i,), (), ("DDMCube",))) for i in range(numOfProc-1)]
	jobs.append((numOfProc, job_server.submit(DDMOU_help, (settings, FD, numberOfJobs - math.floor(numberOfJobs/numOfProc)*(numOfProc-1), tempResultDir, quickName, myUUID, numOfProc - 1,), (), ("DDMCube",))))
	for indexNum, job in jobs:
		result = job()
		print result
	tEnd = time.mktime(time.localtime())
	if runType == 'localCluster': ppUWTools.killAllServers(ppservers = ppservers)
elif runType == 'singleCore':
	tBegin = time.mktime(time.localtime())
	DDMCube.DDMOU(settings, FD, numberOfJobs, tempResultDir, quickName, myUUID)
	tEnd = time.mktime(time.localtime())
else:
	print 'Unrecognized runType option.  Exiting...'
	sys.exit(-1)

# Collect results:
resultsArray = scipy.zeros(totalLength, dtype=float)
crossTimesArray = scipy.zeros(totalLength, dtype=float)
for root, dirs, files in os.walk('./' + tempResultDir):
	for name in files:
		currQuickName, currTotalID, ID, junk = name.split('_')
		if currQuickName == quickName and currTotalID == str(myUUID):
			fIn = open(os.path.join(root, name),'r')
			currArray = pickle.load(fIn)
			crossTimesArray += currArray[0]
			resultsArray += currArray[1]
		os.remove(os.path.join(root, name))
crossTimesArray = crossTimesArray/numberOfJobs
resultsArray = resultsArray/numberOfJobs
			
# Reshape results and save to output:			
params = settings.keys()
params.sort()
newDims = [len(settings[parameter]) for parameter in params]
crossTimesArray = scipy.reshape(crossTimesArray,newDims)
resultsArray = scipy.reshape(resultsArray,newDims)
fOut = open(os.getcwd() + saveResultDir + '/' + quickName + '_' + str(myUUID) + '.dat','w')
pickle.dump((crossTimesArray, resultsArray, params),fOut)

# Display Computation Time:
print 'Total Computation Time: ', time.strftime("H:%H M:%M S:%S",time.gmtime(tEnd - tBegin))
if numberOfJobs < 1000:
	for NN in [2000,5000]: print ' Time to complete ' + str(NN) +  ' sims: ', time.strftime("H:%H M:%M S:%S",time.gmtime(NN*totalLength*(tEnd - tBegin)/(totalLength*numberOfJobs)))
job_server.print_stats()
