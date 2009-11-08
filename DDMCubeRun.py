#  DDMCubeRun.py
#  Created by nicain on 11/1/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#  Run from command line: python DDMCubeRun.py build_ext --inplace

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
'xMean':list(scipy.linspace(3,.55,1)),		# 3
'xStd':list(scipy.linspace(12.8,1,1)),		# 12.8
'xTau':list(scipy.linspace(20,1,1)),		# 20
'theta':list(scipy.linspace(.5,20,10)),		# 10
'dt':list(scipy.linspace(.02,1,1)),			# .02
'chop':list(scipy.linspace(0,10,2))			# 0
}

# Define job parameters:
quickName = 'firstChop'
numberOfJobs = 5000
verbose = 1
multiProc = 1

# Set up saving directories
tempResultDir = '/simResults'
saveResultDir = '/savedResults'

################################################################################
########################         Main function:         ########################
################################################################################

# Write a "settings" file:
myUUID = uuid.uuid4()
output = Popen(['git','tag'],stdout=PIPE).communicate()
gitVersion = output[0][:-1]
totalLength = 1
for parameter in settings: 
	thisSetting = settings[parameter]
	totalLength *= len(thisSetting)
fOutSet = open(os.getcwd() + saveResultDir + '/' + quickName + '_' + str(myUUID) + '.settings','w')	
pickle.dump((settings, numberOfJobs, gitVersion),fOutSet)
fOutSet.close()

# Display settings:
analysisTools.printSettings(quickName, saveResultDir)

# Run the job:
if multiProc == 1:
	def DDMOU_help(settings, perLoc, tempResultDir, quickName, totalUUID, procNum):
		try:
		 	DDMCube.DDMOU(settings, perLoc, tempResultDir, quickName, totalUUID)
			return '   Sub-simulation ' + str(procNum) + ' Complete'
		except: sys.exit(-1)
		
	import pp, math
	job_server = pp.Server(ppservers=())
	print ' Starting pp with', job_server.get_ncpus(), 'workers'
	tBegin = time.mktime(time.localtime())
	job1 = job_server.submit(DDMOU_help, (settings, math.floor(numberOfJobs/2), tempResultDir, quickName, myUUID, 1,), (), ("DDMCube",))
	job2 = job_server.submit(DDMOU_help, (settings, numberOfJobs - math.floor(numberOfJobs/2), tempResultDir, quickName, myUUID, 2,), (), ("DDMCube",))
	print job1()
	print job2()
	tEnd = time.mktime(time.localtime())
else:
	tBegin = time.mktime(time.localtime())
	DDMCube.DDMOU(settings, numberOfJobs, tempResultDir, quickName, myUUID)
	tEnd = time.mktime(time.localtime())

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
print 'Total Computation Time: ', tEnd - tBegin#time.strftime("H:%H M:%M S:%S",time.gmtime(tEnd - tBegin))