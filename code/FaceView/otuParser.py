import sample
import os
import csv

class OtuParser:
	def parseFile(self, filePath):
		data = self.loadFile(filePath)
	
		sampleNames = []
		samples = []
		for line in data:
			if line[0].strip()[0] == '#' and len(line) > 2:
				# It's the line that specifies the names of samples
				sampleNames = line[1:-2]
				for name in sampleNames:
					samples.append(sample.Sample(name))
			elif line[0].strip()[0] == '#':
				#It's just a comment
				continue
			else:
				# It's a data line
				orgName = line[-1]
				for i in range(0, len(samples)):
					samples[i].addOrg(orgName, float(line[i + 1]))
		return samples
			
		
		
	def loadFile(self, filePath):
		fileName = os.path.basename(os.path.normpath(filePath))
		if fileName.endswith('.otu'):
			return list(csv.reader(open(filePath, 'r'), delimiter='\t'))
		return None

import fvParser

if not fvParser.pReg.extensionIsSupported('.otu'):
	fvParser.pReg.registerParser(OtuParser, '.otu')
		