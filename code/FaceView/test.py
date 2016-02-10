
import modelGenerator
import modelGeneratorTranslator

import fvParser
import otuParser


if not fvParser.pReg.extensionIsSupported('.otu'):
	print "Whoops! Registry is wrong!"

samples = fvParser.pReg.parse('./QIIMEClassic_test.otu')
badSample = fvParser.pReg.parse('./test.txt')

assert badSample is None
assert len(samples) > 0

featureList = modelGenerator.getFeatureList()
print len(featureList)
critterList = samples[0].getOrgList()
mapping = {}
for i in range(0, len(critterList)):
	mapping[critterList[i]] = featureList[i]

print "Switching to Absolute"
absolute = modelGeneratorTranslator.normalizeSampleAbsolute(samples, samples[0].getOrgList())

score = 0
for i in samples:
	score = max(max(i.values()), score)
count = 0
for i in samples:
	for j in i.values():
		if abs(j - score) < 0.1:
			count += 1
for i in absolute:
	for j in i.values():
		if j == 1:
			count -= 1
assert count == 0
	
print "Switching to Ratio"
ratio = modelGeneratorTranslator.normalizeSampleRatio(samples, samples[0].getOrgList())

for i in ratio:
	score = max(i.values())
	count = sum(1 for j in samples if j == score)
	assert count == sum(1 for j in ratio if j == 1)
		
print "Switching to manual"
manual = modelGeneratorTranslator.normalizeSampleManual(samples, samples[0].getOrgList(), 10)

#modelGenerator.generateModels(ratio, mapping)
