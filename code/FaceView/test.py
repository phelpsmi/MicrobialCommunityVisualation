
import modelGenerator
import modelGeneratorTranslator

import fvParser
import otuParser


if not fvParser.pReg.extensionIsSupported('.otu'):
	print "Whoops! Registry is wrong!"

samples, groups = fvParser.pReg.parse('./trivial.otu', './trivial.csv')
badSample = fvParser.pReg.parse('./test.txt', './test.txt')

assert badSample is None
assert len(samples) > 0
assert len(groups) > 0

print "Groups:"
for i in groups:
	print i.name
	
print
print "Samples by group"
for i in groups:
	print i.getName()
	for sample in i.getSamples():
		print "\t", sample

print
print "Samples:"
for i in samples:
	print i.getName()
	for org in i.getOrgList():
		print "\t", org, i[org]
