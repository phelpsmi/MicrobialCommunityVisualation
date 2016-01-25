import ModelGenerator
import random
fl = ModelGenerator.getFeatureList()

class SampleDummy(dict):
	def __init__(self, name, fl):
		dict.__init__(self)
		self.name = name
		#For the mockup part
		for i in fl:
			var = random.random()
			self[i] = var
		
		
	def toParamList(self):
		retval = ['name:' + self.name]
		for critter, norm in self.iteritems():
			retval.append(critter + ":" +str(norm))
		return retval
		
samples = [SampleDummy("Steve", fl), 
	SampleDummy("Joe", fl), 
	SampleDummy("Lisa", fl)]



ModelGenerator.generateModels(samples)	
	

