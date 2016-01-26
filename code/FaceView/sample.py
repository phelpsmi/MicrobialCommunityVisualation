class Sample(dict):
	def __init__(self, name):
		#Use parent constructor
		dict.__init__(self)
		self.name = name
		
	def toParamList(self, orgFeatureMapping):
		retval = ['name:' + self.name]
		for critter, pop in self.iteritems():
			retval.append(orgFeatureMapping[critter] + ":" + str(pop))
		return retval
		
	def addOrg(self, org, pop):
		if self.has_key(org):
			self[org] = pop
		else:
			self[org] = pop
			
	def getOrgList(self):
		return self.keys()
		
	def getName(self):
		return self.name
	