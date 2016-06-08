#Normalizes values with respect to the largest population
#	in the file.
# It only considers a subset of the organisms for the scale, 
# since we want to ignore the organisms not being compared
def normalizeSampleAbsolute(samples, critterSubset):
	scale = 0
	for sampleInst in samples:
		for org in critterSubset:
			scale = max(scale, sampleInst[org])
	if scale == 0:
		scale = 1
	retval = []
	for sampleInst in samples:
		newSample = sample.Sample(sampleInst.getName())
		retval.append(newSample)
		for critter in critterSubset:
			newSample.addOrg(critter, sampleInst[critter] / scale)
	return retval
	
# Normalizes values with respect to the largest population 
# in the sample.
# It only considers a subset of the organisms for the scale, because 
# we want to ignore the organisms not being compared.
def normalizeSampleRatio(samples, critterSubset):
	retval = []
	for sampleInst in samples:
		scale = 0
		for critter in critterSubset:
			scale = max(scale, sampleInst[critter])
		newSample = sample.Sample(sampleInst.getName())
		retval.append(newSample)
		if scale == 0:
			scale = 1
		for critter in critterSubset:
			newSample.addOrg(critter, sampleInst[critter] / scale)
	return retval
		
#Normalizes values with respect to a value passed in
#Good for comparing to other data sets that haven't been loaded
#Use at your own risk
def normalizeSampleManual(samples, critterSubset, scale):
	retval = []
	if sample <= 0:
		return None
	for sampleInst in samples:
		newSample = sample.Sample(sampleInst.getName())
		retval.append(newSample)
		for critter in critterSubset:
			newSample.addOrg(critter, sampleInst[critter] / scale)
	return retval
		
	


			
