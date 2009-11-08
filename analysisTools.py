#  analysisTools.py
#  Created by nicain on 11/4/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.

################################################################################
#def compileMultiResults(fileName, tempResultDir = 'simResults', saveResultDir = 'savedResults'):

################################################################################
# This function plots a 1-D slice:
def plot1D( sliceDict, quickName, whatToPlot,saveResultDir = 'savedResults', whichRun = 0, tDel = 2000, tPen = 2000, tND = 300):
	from pylab import plot
	from numpy import transpose, shape
	crossTimeData, resultData, dims, settings, numberOfJobs, gitVersion =  getDataAndSettings(quickName, saveResultDir, whichRun)
	crossTimeData += tND 
	permuteList = range(len(dims))
	xDimension = sliceDict['XVar']
	del sliceDict['XVar']
	for parameter in dims:
		if not(parameter == xDimension or parameter in sliceDict):
			sliceDict[parameter] = settings[parameter][0]
	sliceDims = dims[:]
	sliceDims.remove(xDimension)
	indexList = [slice(None,None)]
	for parameter in sliceDims:
		parameterSweepList = settings[parameter]
		val = parameterSweepList.index(sliceDict[parameter])
		indexList.append(parameterSweepList.index(sliceDict[parameter]))
	coord = tuple(indexList)

	whereIsXDim = dims.index(xDimension)
	permuteList.remove(whereIsXDim)
	permuteList.insert(0,whereIsXDim)
	crossTimeData = transpose(crossTimeData,permuteList)
	resultData = transpose(resultData,permuteList)
	crossTimeSlice = crossTimeData[coord]
	resultSlice = resultData[coord]
	
	xVals = settings[xDimension]
	
	if whatToPlot == 'RR':
		depVar = resultSlice/(crossTimeSlice + tND + tDel + (1-resultSlice)*tPen)
	elif whatToPlot == 'RT':
		depVar = crossTimeSlice
	elif whatToPlot == 'FC':
		depVar = resultSlice
	else: print ' Unrecognized plot option ' + whatToPlot
	
	plot(xVals,depVar)
	return

################################################################################
# This function lists the job names that are available:
def listNames(saveResultDir = 'savedResults'):
	import operator
	nameDict = quickNameIDDictionary(saveResultDir,includeRepeats = 0)
	nameTimeList = []
	for item in nameDict:
		nameTimeList.append((item, nameDict[item][0][1]))
	nameTimeListSorted = sorted(nameTimeList, key=operator.itemgetter(1),reverse=True)
	print ' Available job names:'
	for name in nameTimeListSorted:
		print '   ' + name[0]
	return

################################################################################
# This function prints out a nicely formatted settings string:
def printSettings(quickName, saveResultDir = 'savedResults', whichRun = 0):
	printString = getSettingsString(quickName, saveResultDir = 'savedResults', whichRun = 0)
	print printString
	return

################################################################################
# This function gets the settings string from a file:
def getSettingsString(quickName, saveResultDir = 'savedResults', whichRun = 0):
	import analysisTools
	
	settings, numberOfJobs, gitVersion = getSettings(quickName, saveResultDir, whichRun)
	params = settings.keys()
	constParams = []
	varParams = []
	for parameter in params:
		if len(settings[parameter])>1: varParams.append(parameter)
		else: constParams.append(parameter)
	constParams.sort
	varParams.sort
	settingsString = ' Job "quickName": ' + quickName + '\n'	
	settingsString += ' Parameter Settings:\n'
	totalLength = 1
	for parameter in constParams:
		thisSetting = settings[parameter]
		settingsString += '   %5s: %5.2f\n' % (parameter, min(thisSetting))
		totalLength *= len(thisSetting)
	for parameter in varParams:
		thisSetting = settings[parameter]
		settingsString += '   %5s: %5.2f %5.2f %3d\n' % (parameter,min(thisSetting),max(thisSetting),len(thisSetting))
		totalLength *= len(thisSetting)
		
	settingsString += ' Number of Parameter Space Points: %-5d\n' % totalLength
	settingsString += ' Number of Simulations per Point:  %-5d\n' % numberOfJobs
	settingsString += ' Total number of Simulations:      %-5d' % (totalLength*numberOfJobs)
	
	return settingsString


################################################################################
# This function gets the name of a file, given an ID:
def getFileString(ID, typeOfFile,  saveResultDir = 'savedResults'):
	resultDict = IDquickNameDictionary(saveResultDir)
	quickName = resultDict[ID]
	fileName = quickName + '_' + ID + '.' + typeOfFile
	return fileName

################################################################################
# This function grabs the data for a given quickName:
def getData(quickName, saveResultDir = 'savedResults', whichRun = 0):
	import analysisTools, pickle
	
	ID = quickNameToID(quickName, saveResultDir, whichRun)
	fileName = getFileString(ID,'dat', saveResultDir)
	fIn = open('./' + saveResultDir + '/' + fileName,'r')
	resultTuple = pickle.load(fIn)
	return resultTuple

################################################################################
# This function grabs the settings for a given quickName:
def getSettings(quickName, saveResultDir = 'savedResults', whichRun = 0):
	import analysisTools, pickle
	ID = quickNameToID(quickName, saveResultDir, whichRun)
	fileName = getFileString(ID,'settings', saveResultDir)
	fIn = open('./' + saveResultDir + '/' + fileName,'r')
	resultTuple = pickle.load(fIn)
	return resultTuple

################################################################################
# This function grabs the results and settings for a given quickName:
def getDataAndSettings(quickName, saveResultDir = 'savedResults', whichRun = 0):
	import analysisTools
	crossTimeData, resultData, dims = getData(quickName, saveResultDir, whichRun)
	settings, numberOfJobs, gitVersion = getSettings(quickName, saveResultDir, whichRun)
	return (crossTimeData, resultData, dims, settings, numberOfJobs, gitVersion)
	
################################################################################
# This function creates a dictionary between file "ID's" and quickNames
def IDquickNameDictionary(saveResultDir = 'savedResults'):
	import pickle, os, operator
	
	resultDict = {}
	for root, dirs, files in os.walk('./' + saveResultDir):
		for name in files:
			quickNameAndID,suffix = name.split('.')
			if suffix == 'settings':
				quickName, ID = quickNameAndID.split('_')
				resultDict[ID] = quickName
	return resultDict

################################################################################
# This function creates a dictionary between "quickNames" and file ID's
def quickNameIDDictionary(saveResultDir = 'savedResults',includeRepeats = 0):
	import pickle, os, operator
	
	resultDict = {}
	for root, dirs, files in os.walk('./' + saveResultDir):
		for name in files:
			quickNameAndID,suffix = name.split('.')
			if suffix == 'settings':
				st = os.stat(os.path.join(root, name))
				quickName, ID = quickNameAndID.split('_')
				IDTime = st[8]
				fIn = open(os.path.join(root, name),'r')
				settingTuple = pickle.load(fIn)

				if not(resultDict.has_key(quickName)):
					resultDict[quickName] = [(ID, IDTime)]
				else:
					tempList = resultDict[quickName]
					tempList.append((ID, IDTime))
					tempListSorted = sorted(tempList, key=operator.itemgetter(1),reverse=True)
					if includeRepeats:
						resultDict[quickName] = tempListSorted
					else:
						resultDict[quickName] = [tempListSorted[0]]
	return resultDict

################################################################################
# This function grabs the ID for a given quickName
def quickNameToID(quickName, saveResultDir = 'savedResults', includeRepeats = 0):
	import operator
	from analysisTools import quickNameIDDictionary

	currentDict = quickNameIDDictionary(saveResultDir, includeRepeats)
	try: listOfIDTimeTuple = currentDict[quickName]
	except KeyError: 
		print '  Job "' + quickName + '" not found.'
		print '  Available jobs:'
		for i in currentDict.keys(): print '    ' + i
		raise
	if not(includeRepeats):
		listOfID = map(operator.itemgetter(0), listOfIDTimeTuple)
		return listOfID[0]
	else:
		return listOfIDTimeTuple
	
