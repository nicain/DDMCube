#  analysisTools.py
#  Created by nicain on 11/4/09.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.

################################################################################
# This function plots a sequence  of 2-D slices:
def plot2DSeq(sliceDict, whatToPlot, saveResultDir = 'savedResults', whichRun = 0, tDel = 2000, tPen = 2000, tND = 300, newFigure = 1, colorArray = [], N = 20, quickName = -1, seqLength = 4,  colorBar = 1):
	from numpy import array, linspace, inf
	from pylab import figure, subplot, colorbar, suptitle
	import copy
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')

	zDimensionTuple = sliceDict['ZVar']
	if isinstance(zDimensionTuple, str):
		zDimension = zDimensionTuple
		settings, numberOfJobs, gitVersion =  getSettings(quickName, saveResultDir, whichRun)
		vals = settings[zDimension]
		zDimensionList = linspace(min(vals), max(vals), seqLength)
	else:
		zDimension = zDimensionTuple[0]
		zDimensionList = zDimensionTuple[0]

	del sliceDict['ZVar']
	if newFigure:
		figure(num=None,figsize=(4*seqLength, 4))
	minZ = inf
	maxZ = -inf
	for i in range(len(zDimensionList)):
		subplot(1,len(zDimensionList),i+1)
		sliceDict[zDimension] = zDimensionList[i]
		titleString = zDimension + '=' + '%-5.3f' % zDimensionList[i]
		if i+1 == len(zDimensionList):
			thisPlot = plot2D(copy.copy(sliceDict), whatToPlot,saveResultDir = saveResultDir, whichRun = whichRun, tDel = tDel, tPen = tPen, tND = tND, N = N, quickName = quickName, titleString = titleString, colorBar = 0, newFigure = 0, plotYLabel = 0)
		elif i==0:
			thisPlot = plot2D(copy.copy(sliceDict), whatToPlot,saveResultDir = saveResultDir, whichRun = whichRun, tDel = tDel, tPen = tPen, tND = tND, N = N, quickName = quickName, titleString = titleString, colorBar = 0, newFigure = 0, plotYLabel = 0)
		else:
			thisPlot = plot2D(copy.copy(sliceDict), whatToPlot,saveResultDir = saveResultDir, whichRun = whichRun, tDel = tDel, tPen = tPen, tND = tND, N = N, quickName = quickName, titleString = titleString, colorBar = 0, newFigure = 0, plotYLabel = 0)	
		if min(thisPlot.levels) < minZ:
			minZ = min(thisPlot.levels)
		if max(thisPlot.levels) > maxZ:
			maxZ = max(thisPlot.levels)
	
	colorArray = linspace(minZ, maxZ, N)
			
	for i in range(len(zDimensionList)):
		subplot(1,len(zDimensionList),i+1)
		sliceDict[zDimension] = zDimensionList[i]
		titleString = zDimension + '=' + '%-5.3f' % zDimensionList[i]
		if i+1 == len(zDimensionList):
			thisPlot = plot2D(copy.copy(sliceDict), whatToPlot,saveResultDir = saveResultDir, colorArray = colorArray, whichRun = whichRun, tDel = tDel, tPen = tPen, tND = tND, N = N, quickName = quickName, titleString = titleString, colorBar = 1, newFigure = 0, plotYLabel = 0)
		elif i==0:
			thisPlot = plot2D(copy.copy(sliceDict), whatToPlot,saveResultDir = saveResultDir, colorArray = colorArray, whichRun = whichRun, tDel = tDel, tPen = tPen, tND = tND, N = N, quickName = quickName, titleString = titleString, colorBar = 0, newFigure = 0, plotYLabel = 1)
		else:
			thisPlot = plot2D(copy.copy(sliceDict), whatToPlot,saveResultDir = saveResultDir, colorArray = colorArray, whichRun = whichRun, tDel = tDel, tPen = tPen, tND = tND, N = N, quickName = quickName, titleString = titleString, colorBar = 0, newFigure = 0, plotYLabel = 0)	
	
	if whatToPlot == 'RR':
		suptitle('Reward Rate')
	elif whatToPlot == 'FC':
		suptitle('Fraction Correct')	
	elif whatToPlot == 'RT':
		suptitle('Reaction Time')
		
	return
	

################################################################################
# This function plots a 2-D slice:
def plot2D( sliceDict, whatToPlot,saveResultDir = 'savedResults', whichRun = 0, tDel = 2000, tPen = 2000, tND = 300, newFigure = 1, colorArray = [], N = 20, quickName = -1, colorBar = 1, plotYLabel = 1, titleString = -1):
	from numpy import transpose, shape, squeeze, array
	import pylab as pl
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')

	# Get data:
	crossTimeData, resultData, dims, settings, numberOfJobs, gitVersion =  getDataAndSettings(quickName, saveResultDir, whichRun)
	crossTimeData += tND 
	
	# Record variable to plot, and then strip input dictionary of that variable:
	xDimension = sliceDict['XVar']
	yDimension = sliceDict['YVar']
	del sliceDict['XVar']
	del sliceDict['YVar']
	
	# Reorder dimension list and cube to put plotting variable first:
	permuteList = range(len(dims))
	whereIsXDim = dims.index(xDimension)
	whereIsYDim = dims.index(yDimension)
	dims[0], dims[whereIsXDim] = dims[whereIsXDim], dims[0]
	dims[1], dims[whereIsYDim] = dims[whereIsYDim], dims[1]
	permuteList[0], permuteList[whereIsXDim] = permuteList[whereIsXDim], permuteList[0]
	permuteList[1], permuteList[whereIsYDim] = permuteList[whereIsYDim], permuteList[1]
	crossTimeData = transpose(crossTimeData,permuteList)
	resultData = transpose(resultData,permuteList)
	
	# Collapse all non-constant dimensions:
	crossDims = dims[:]
	resultDims = dims[:]
	for collapseDim in iter(sliceDict):
		crossTimeData, crossDims = reduce1D(crossTimeData, crossDims, collapseDim, settings[collapseDim], sliceDict[collapseDim])
		resultData, resultDims = reduce1D(resultData, resultDims, collapseDim, settings[collapseDim], sliceDict[collapseDim])
	crossTimeSlice = squeeze(crossTimeData)
	resultSlice = squeeze(resultData) 
	
	# Create x-axis values, and plot:
	xVals = settings[xDimension]
	yVals = settings[yDimension]
	if whatToPlot == 'RR':
		depVar = resultSlice/(crossTimeSlice + tND + tDel + (1-resultSlice)*tPen)
		heightLabel = 'Reward Rate'
	elif whatToPlot == 'RT':
		depVar = crossTimeSlice
		heightLabel = 'Reaction Time'
	elif whatToPlot == 'FC':
		depVar = resultSlice
		heightLabel = 'Fraction Correct'
	else: print ' Unrecognized plot option ' + whatToPlot
	
	if newFigure:
		pl.figure()
	if colorArray == []:
		myPlot = pl.contourf(xVals,yVals,depVar,N)
	else:
		myPlot = pl.contourf(xVals,yVals,depVar,N,levels = colorArray)
	pl.xlabel(xDimension)
	if plotYLabel:
		pl.ylabel(yDimension)
	if titleString == -1:
		pl.title(heightLabel)
	else:
		pl.title(titleString)
	if colorBar:
		pl.colorbar()
	return myPlot

################################################################################
# This function plots a 1-D slice:
def plot1D( sliceDict, whatToPlot,saveResultDir = 'savedResults', whichRun = 0, tDel = 2000, tPen = 2000, tND = 300, newFigure = 1, quickName = -1):
	from numpy import transpose, shape, squeeze
	import pylab as pl
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')

	# Get data:
	crossTimeData, resultData, dims, settings, numberOfJobs, gitVersion =  getDataAndSettings(quickName, saveResultDir, whichRun)
	crossTimeData += tND 
	
	# Record variable to plot, and then strip input dictionary of that variable:
	xDimension = sliceDict['XVar']
	del sliceDict['XVar']
	
	# Reorder dimension list and cube to put plotting variable first:
	permuteList = range(len(dims))
	whereIsXDim = dims.index(xDimension)
	dims[0], dims[whereIsXDim] = dims[whereIsXDim], dims[0]
	permuteList[0], permuteList[whereIsXDim] = permuteList[whereIsXDim], permuteList[0]
	crossTimeData = transpose(crossTimeData,permuteList)
	resultData = transpose(resultData,permuteList)
	
	# Collapse all non-constant dimensions:
	crossDims = dims[:]
	resultDims = dims[:]
	for collapseDim in iter(sliceDict):
		crossTimeData, crossDims = reduce1D(crossTimeData, crossDims, collapseDim, settings[collapseDim], sliceDict[collapseDim])
		resultData, resultDims = reduce1D(resultData, resultDims, collapseDim, settings[collapseDim], sliceDict[collapseDim])
	crossTimeSlice = squeeze(crossTimeData)
	resultSlice = squeeze(resultData) 
	
	# Create x-axis values, and plot:
	xVals = settings[xDimension]
	if whatToPlot == 'RR':
		depVar = resultSlice/(crossTimeSlice + tND + tDel + (1-resultSlice)*tPen)
		yAxisLabel = 'Reward Rate'
	elif whatToPlot == 'RT':
		depVar = crossTimeSlice
		yAxisLabel = 'Reaction Time'
	elif whatToPlot == 'FC':
		depVar = resultSlice
		yAxisLabel = 'Fraction Correct'
	else: print ' Unrecognized plot option ' + whatToPlot
	
	if newFigure:
		pl.figure()
	myPlot = pl.plot(xVals,depVar)
	pl.xlabel(xDimension)
	pl.ylabel(yAxisLabel)
	return myPlot
	
################################################################################
# This function reduces the dimension of a cube by 1, along a given slice:
def reduce1D(cube, dims, varToReduce, vals, sliceVal):

	for i in range(len(vals)-1):
		if vals[i] <= sliceVal and sliceVal < vals[i+1]:
			lInd=i
			rInd=i+1
			break
	indexListL = [slice(None,None)]*len(dims)
	indexListR = indexListL[:]
	indToSet = dims.index(varToReduce)
	if vals[-1] != sliceVal:
		indexListL[indToSet] = lInd
		indexListR[indToSet] = rInd
		cubeL = cube[tuple(indexListL)]
		cubeR = cube[tuple(indexListR)]
		cubeReduce = (cubeL*float(vals[rInd] - sliceVal) + cubeR*float(sliceVal - vals[lInd]))/float(vals[rInd] - vals[lInd])
	else:
		indexListR[indToSet] = -1
		cubeReduce = cube[tuple(indexListR)]
	dims.remove(varToReduce)
	return (cubeReduce, dims)

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
def printSettings(quickName = -1, saveResultDir = 'savedResults', whichRun = 0):
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')

	printString = getSettingsString(quickName, saveResultDir = 'savedResults', whichRun = 0)
	print printString
	return

################################################################################
# This function gets the settings string from a file:
def getSettingsString(quickName = -1, saveResultDir = 'savedResults', whichRun = 0):
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')

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
		settingsString += '   %6s: %5.2f\n' % (parameter, min(thisSetting))
		totalLength *= len(thisSetting)
	for parameter in varParams:
		thisSetting = settings[parameter]
		settingsString += '   %6s: %5.2f %5.2f %3d\n' % (parameter,min(thisSetting),max(thisSetting),len(thisSetting))
		totalLength *= len(thisSetting)

	settingsString += ' Drif-Diffusion Software version:  %-5s\n' % gitVersion		
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
def getData(quickName = -1, saveResultDir = 'savedResults', whichRun = 0):
	import pickle
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')
	
	ID = quickNameToID(quickName, saveResultDir, whichRun)
	fileName = getFileString(ID,'dat', saveResultDir)
	fIn = open('./' + saveResultDir + '/' + fileName,'r')
	resultTuple = pickle.load(fIn)
	return resultTuple

################################################################################
# This function grabs the settings for a given quickName:
def getSettings(quickName = -1, saveResultDir = 'savedResults', whichRun = 0):
	import pickle
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')
		
	ID = quickNameToID(quickName, saveResultDir, whichRun)
	fileName = getFileString(ID,'settings', saveResultDir)
	fIn = open('./' + saveResultDir + '/' + fileName,'r')
	resultTuple = pickle.load(fIn)
	return resultTuple

################################################################################
# This function grabs the results and settings for a given quickName:
def getDataAndSettings(quickName = -1, saveResultDir = 'savedResults', whichRun = 0):
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')
	
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
# This function grabs the ID for a given quickName:
def quickNameToID(quickName = -1, saveResultDir = 'savedResults', includeRepeats = 0):
	import operator
	if quickName == -1:
		quickName = getLastQuickName(saveResultDir = 'savedResults')

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
		
################################################################################
# This function gets the most recent quickname:
def getLastQuickName(saveResultDir = 'savedResults'):
	import operator
	
	d = quickNameIDDictionary()
	d2 = IDquickNameDictionary() 
	myIndex = [d[key][0] for key in iter(d)]
	myIndexSorted = sorted(myIndex, key=operator.itemgetter(1),reverse=True)
	IDName = myIndexSorted[0][0]
	lastQuickName = d2[IDName]
	return lastQuickName
		
