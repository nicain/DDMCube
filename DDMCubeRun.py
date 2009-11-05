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
try: import DDMCube, scipy, random, time, os, pickle
except: sys.exit(-1)

################################################################################
########################           Dashboard:           ########################
################################################################################

# Define job settings:
settings={
'xMean':list(scipy.linspace(1,1,1)),
'xStd':list(scipy.linspace(1,1,1)),
'xTau':list(scipy.linspace(.5,1,1)),
'theta':list(scipy.linspace(.05,5,25)),
'dt':list(scipy.linspace(.02,1,1))
}

# Define job parameters:
quickName = 'firstJob'
numberOfJobs = 2000
verbose = 1

# Set up saving directories
tempResultDir = '/simResults'
saveResultDir = '/savedResults'

################################################################################
########################         Main function:         ########################
################################################################################

# Display settings:
if verbose: 
	print '################################'
	print '##### Beginning Simulation #####'
	print '################################'
	print 'Parameter Sweep Settings:'
	totalLength = 1
	for parameter in settings: 
		thisSetting = settings[parameter]
		print '  %5s: %5.2f %5.2f %3d' % (parameter,min(thisSetting),min(thisSetting),len(thisSetting))
		totalLength *= len(thisSetting)
	print 'Number of Parameter Space Points:'
	print '  %3d' % totalLength
	print 'Total number of Simulations:'
	print '  %3d' % (totalLength*numberOfJobs)

# Run the job:
tBegin = time.mktime(time.localtime())
DDMCube.DDMOU(settings, numberOfJobs, tempResultDir, saveResultDir, quickName)
tEnd = time.mktime(time.localtime())

# Display Computation Time:
print 'Total Computation Time: ', tEnd - tBegin#time.strftime("H:%H M:%M S:%S",time.gmtime(tEnd - tBegin))