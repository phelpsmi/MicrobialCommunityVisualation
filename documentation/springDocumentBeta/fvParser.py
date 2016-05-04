
#The parser registry
class parserRegistry:
	def __init__(self):
		self.mapping = {}

	def registerParser(self, parser, extension):
		self.mapping[extension] = parser

	def getParserForExtension(self, extension):
		if self.extensionIsSupported(extension):
			return self.mapping[extension]
		else:
			return None
	
	def extensionIsSupported(self, extension):
		return self.mapping.has_key(extension)
		
	def parse(self, filePath, metaPath):
		fileExt = os.path.splitext(os.path.normpath(filePath))[1]
		parser = self.getParserForExtension(fileExt)
		if parser is not None:
			return parser().parseFile(filePath, metaPath)
		else:
			return None
