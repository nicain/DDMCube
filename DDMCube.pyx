#  DDMCube.pyx
#  Created by nicain on 11/1/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.

# Wrapper for the RNG:
cdef extern from "MersenneTwister.h":
	ctypedef struct c_MTRand "MTRand":
		double randNorm( double mean, double stddev)
		void seed( unsigned long bigSeed[])

# External math functions that are needed:
cdef extern from "math.h":
	float sqrt(float sqrtMe)
	float abs(float absMe)

################################################################################
######################## Main function, the workhorse:  ########################
################################################################################
def DDMOU(settings, int perLoc, tempResultDir, quickName, totalUUID):

	# Import necessary python packages:
	import itertools, pickle, random, uuid, os
	from scipy import zeros
	
	# C initializations
	cdef float xCurr, tCurr, yCurr, xMean, xStd, xTau, dt, theta, crossTimes, results
	cdef double mean = 0, std = 1
	cdef unsigned long mySeed[624]
	cdef c_MTRand myTwister
	cdef int i
	
	# Convert settings dictionary to iterator:
	params = settings.keys()
	params.sort()
	settingsList = []
	totalLength = 1
	for parameter in params: 
		settingsList.append(settings[parameter])
		totalLength *= len(settings[parameter])
	settingsIterator = itertools.product(*settingsList)
	resultsArray = zeros(totalLength, dtype=float)
	crossTimesArray = zeros(totalLength, dtype=float)

	# Initialization of random number generator:
	myUUID = uuid.uuid4()
	random.seed(myUUID.int)
	for i in range(624): mySeed[i] = random.randint(0,2**30)
	myTwister.seed(mySeed)

	# Parameter space loop:
	counter = 0
	for currentSettings in settingsIterator:
		dt, theta, xMean, xStd, xTau =  currentSettings

		crossTimes = 0
		results = 0
		for i in range(perLoc):
			tCurr = 0
			xCurr = myTwister.randNorm(xMean,xStd)
			yCurr = 0
			while abs(yCurr) < theta:
				xCurr = xCurr+dt*(xMean - xCurr)/xTau + xStd*sqrt(2*dt/xTau)*myTwister.randNorm(mean,std)
				yCurr = yCurr + .005*dt*xCurr
				tCurr=tCurr+dt
			crossTimes += tCurr
			if yCurr > theta:
				results += 1
		resultsArray[counter] = results
		crossTimesArray[counter] = crossTimes
		counter += 1

	# Create output files:
	fOut = open(os.getcwd() + tempResultDir + '/' + quickName + '_' + str(totalUUID) + '_' + str(myUUID) + '_temp.dat','w')
	pickle.dump((crossTimesArray, resultsArray),fOut)
	fOut.close()
	return