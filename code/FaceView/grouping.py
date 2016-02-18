
#grouping.py
#By Thomas Albertine

#Backend for users to add and modify groups of samples
#Needs to be able to do the following
#  - Add samples to a group (as multiple selected samples)
#  - Remove samples from a group (as multiple selected samples)
#  - Keep track of all the groups
#  - Easily reset when new groups are created

# Represents each individual group
class Group:
	
	def __init__(self, name, samples=[]):
		self.samples = set(samples)
		self.name = name
		
	def __eq__(self, other):
		if not callable(getattr(other, "__hash__", None)):
			return False
		if self.__hash__() != other.__hash__():
			return False
		return True
		
	def __ne__(self, other):
		not self.__eq__(other)
		
	def __hash__(self):
		return self.name.__hash__()
		
	#Add samples and remove samples use collections so that the UI
	#can add or remove all elements at once.
	def addSamples(self, samples=[]):
		self.samples |= set(samples)
	
	def remSamples(self, samples=[]):
		self.samples -= set(samples=[])

	def getSamples(self):
		return list(self.samples)
		
	def getName(self):
		return self.name
		
		

