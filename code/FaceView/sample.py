class Sample(dict):
	def __init__(self, name):
		#Use parent constructor
		dict.__init__(self)
		self.name = name
		
	def __str__(self):
		return "<Sample Name: " + self.name + ">"  
		
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
		return list(self.keys())
		
	def getName(self):
		return str(self.name)
		
	def __hash__(self):
		return self.name.__hash__()
	