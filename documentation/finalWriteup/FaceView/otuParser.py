import sample
import grouping
import os
import csv

class OtuParser:
	def parseFile(self, filePath, metaPath):
		data = self.loadFile(filePath)
		meta = self.loadMeta(metaPath)
		if data is None or meta is None:
			return None
			
		metaDict, names = self.parseMeta(meta)
		
		samples = []
		for name in names:
			samples.append(sample.Sample(name))
		for line in data:
			if line[0].strip()[0] == '#':
				#It's just a comment
				continue
			else:
				# It's a data line
				orgName = line[-1]
				for i in range(0, len(samples)):
					samples[i].addOrg(orgName, float(line[i + 1]))
					
		groups = {"All Samples" : grouping.Group("All Samples", samples)}
		for s in samples:
			sampleName = s.getName()
			attrs = metaDict[sampleName]
			for attrName, attrVal in attrs.iteritems():
				groupName = attrName + ": " + attrVal
				if groupName not in groups:
					groups[groupName] = grouping.Group(groupName, [s])
				else:
					groups[groupName].addSamples([s])
		return samples, list(groups.values())
			
		
		
	def loadFile(self, filePath):
		fileName = os.path.basename(os.path.normpath(filePath))
		if fileName.endswith('.otu'):
			return list(csv.reader(open(filePath, 'rU'), delimiter='\t'))
		return None
		
	def loadMeta(self, filePath):
		fileName = os.path.basename(os.path.normpath(filePath))
		if fileName.endswith('.csv'):
			return list(csv.reader(open(filePath, 'rU'), delimiter=','))
		return None
		
	#returns a dictionary of dictionaries.
	#The first layer associates a sample name with it's attributes
	#The second layer associates an attribute name with its value
	def parseMeta(self, meta):
		first = True
		attrs = {}
		columns = []
		columnNames = []
		sampleNames = []
		for line in meta:
			columns = line[1:]
			if first:
				first = False
				columnNames = columns
				continue
			entryVars = {}
			for i in range(len(columns)):
				entryVars[columnNames[i]] = columns[i]
			attrs[line[0]] = entryVars
			sampleNames.append(line[0])
		return attrs, sampleNames
			

import fvParser

if not fvParser.pReg.extensionIsSupported('.otu'):
	fvParser.pReg.registerParser(OtuParser, '.otu')
		