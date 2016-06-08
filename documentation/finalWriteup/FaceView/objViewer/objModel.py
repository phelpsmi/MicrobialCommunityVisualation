

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
	
class Material:
	def __init__(self, name, ambient = numpy.array((1.0, 1.0, 1.0, 1.0)), 
		diffuse = numpy.array((1.0, 1.0, 1.0, 1.0)), 
		specular = numpy.array((1.0, 1.0, 1.0, 1.0)), 
		exponent = 1.0, 
		dissolve=1.0, 
		texture=None, 
		mask=None):
		self.name = name
		self.ambient = ambient
		self.diffuse = diffuse
		self.specular = specular
		self.exponent = exponent
		self.dissolve = dissolve
		print texture
		if texture is None:
			texture = Image.new("RGBA", (2,2), (1,1,1,1))
		else:
			texture = Image.open(texture)
		texture.convert("RGBA")
		self.texSize = texture.size
		#possible sticking point.
		# When closing an image, data from getdata is no longer valid
		# I think we've copied the data and not just a reference by making 
		#	it a numpy array, but I'm not sure
		self.diffuseTexture = numpy.array(list(texture.getdata()), numpy.uint8)
		texture.close()
		if mask is None:
			mask = Image.new("RGBA", (2,2), (1,1,1,1))
		else:
			mask = Image.open(mask)
		mask.convert("RGBA")
		self.maskSize = mask.size
		self.maskTexture = numpy.array(list(mask.getdata()), numpy.uint8)
		mask.close()
	
	def getName(self):
		return string(name)
	def getAmbient(self):
		return self.ambient
	def getDiffuse(self):
		return self.diffuse
	def getSpecular(self):
		return self.specular
	def getExponent(self):
		return self.exponent
	def getDissolve(self):
		return self.dissolve
	def getDiffuseTexture(self):
		return self.diffuseTexture
	def getMaskTexture(self):
		return self.maskTexture
	def setAmbient(self, ambient=(1.0, 1.0, 1.0, 1.0)):
		self.ambient = numpy.array(ambient, dtype='float32')
	def setDiffuse(self, diffuse=(1.0, 1.0, 1.0, 1.0)):
		self.diffuse = numpy.array(diffuse, dtype='float32')
	def setSpecular(self, specular=(1.0, 1.0, 1.0, 1.0)):
		self.specular = numpy.array(specular, dtype='float32')
	def setExponent(self, exp=1.0):
		self.exponent = exp
	def setDissolve(self, dissolve=1.0):
		self.dissolve = dissolve
	def setDiffuseTexture(self, texture=None):
		print "setting diffuse texture to image at " + texture
		print texture is None
		if texture is None:
			texture = Image.new("RGBA", (2,2), (1,1,1,1))
		else:
			texture = Image.open(texture)
		texture.convert("RGBA")
		self.texSize = texture.size
		self.diffuseTexture = numpy.array(list(texture.getdata()), numpy.uint8)
		texture.close()
	def setMaskTexture(self, mask=None):
		if mask is None:
			mask = Image.new("RGBA", (2,2), (1,1,1,1))
		else:
			mask = Image.open(mask)
		mask.convert("RGBA")
		self.maskSize = mask.size
		self.maskTexture = numpy.array(list(mask.getdata()), numpy.uint8)
		mask.close()
		
	def __str__(self):
		retval = "<Material:"
		retval += "\n\tName: " + str(self.name)
		retval += "\n\tAmbient: " + str(self.ambient)
		retval += "\n\tDiffuse: " + str(self.diffuse)
		retval += "\n\tSpecular: " + str(self.specular)
		retval += "\n\tExponent: " + str(self.exponent)
		retval += "\n\tDissolve: " + str(self.dissolve)
		retval += "\n\tDiffuse Texture Size: " + str(self.texSize)
		retval += "\n\tDiffuse Texture: " + str(self.diffuseTexture)
		retval += "\n\tMask Size: " + str(self.maskSize)
		retval += "\n\tMask: " + str(self.maskTexture) + "\n>"
		return retval
		
	def __repr__(self):
		return self.__str__()
		
def removeComment(line):
 i = 0
 for i in range(0, len(line)):
  if '#' in line[i]:
   break
  i += 1
 if i < len(line) and line[i][0] != '#':
  line[i] = line[i][0:line[i].find('#')]
  i += 1
 line = line[:i]
 return line
	
def loadMaterial(mtlPath):
	if not os.path.isfile(mtlPath):
		#No material for the file
		return {}
	mtls = {}
	curMtl = None
	with open(mtlPath, 'rU') as file:
		for line in file:
			line = line.split()
			line = removeComment(line)
			
			if len(line) == 0:
				#Empty line. Skip it
				continue
			elif line[0] == 'newmtl':
				#Create a new material
				curMtl = Material(line[1])
				mtls[line[1]] = curMtl
				continue
			elif line[0] == 'Ka':
				#convert all components into floats
				row = map(lambda x: float(x), line[1:])
				for i in range(len(row), 4):
					row.append(0.0)
				row[-1] = 1.0
				curMtl.setAmbient(row)
				continue
			elif line[0] == 'Kd':
				#convert all components into floats
				row = map(lambda x: float(x), line[1:])
				for i in range(len(row), 4):
					row.append(0.0)
				row[-1] = 1.0
				curMtl.setDiffuse(row)
				continue
			elif line[0] == 'Ks':
				#convert all components into floats
				row = map(lambda x: float(x), line[1:])
				for i in range(len(row), 4):
					row.append(0.0)
				row[-1] = 1.0
				curMtl.setSpecular(row)
				continue
			elif line[0] == 'd':
				#dissolve, in this case 1 means no texture, and 0 means only texture
				curMtl.setDissolve(float(line[1]))
				continue
			elif line[0] == 'Ns':
				#Specular exponent
				curMtl.setExponent(float(line[1]))
				continue
			elif line[0] == 'map_Kd':
				#Diffuse texture
				curMtl.setDiffuseTexture(os.path.join(os.path.split(mtlPath)[0], line[1]))
				continue
			elif line[0] == 'map_D':
				#Dissolve texture, aka mask
				curMtl.setMaskTexture(os.path.join(os.path.split(mtlPath)[0], line[1]))
				continue
	return mtls

class Section:
	def __init__(self, name, mat=None, 
		verts=[], 
		norms=[],
		texCoords=[],
		inds=[]):
		self.vertices = numpy.array(verts, dtype='float32')
		self.normals = numpy.array(norms, dtype='float32')
		self.texPos = numpy.array(texCoords, dtype='float32')
		self.indices = numpy.array(inds, dtype='uint32')
		self.mtl = mat
		self.name = name
		
	def __str__(self):
		retval = "<Section" + \
			"\n\tName: " + str(self.name) + \
			"\n\tMaterial: " + str(self.mtl) + \
			"\n\tIndices: " + str(self.indices) + \
			"\n\tVertices: " + str(self.vertices) + \
			"\n\tNormals: " + str(self.normals) + \
			"\n\tTexture Coordinates: " + str(self.texPos) + \
			">"
		return retval
		
	def __repr__(self):
		return self.__str__()


def loadModel(filePath):
	vertices = {}
	nextVertex = 1
	normals = {}
	nextNormal = 1
	texCoords = {}
	nextTex = 1
	mtls = {"":None}
	curMaterial = ""
	curFaces = []
	parts = {"":None}
	curPart = ""
	with open(filePath, 'rU') as file:
		for line in file:
			lineStr = line
			line = line.split()
			line = removeComment(line)
			if len(line) < 1:
				#Blank line
				continue
			if line[0] == "mtllib":
				#add materials to known materials dict
				strPath = lineStr.strip()[6:].strip()
				mtlPath = os.path.join(os.path.split(filePath)[0], strPath)
				mtls.update(loadMaterial(mtlPath))
				continue
			elif line[0] == "v":
				#add vertex
				vertices[nextVertex] = (float(line[1]), float(line[2]), float(line[3]), 1.0)
				nextVertex += 1
				continue
			elif line[0] == "vn":
				#add normal
				normals[nextNormal] = (float(line[1]), float(line[2]), float(line[3]))
				nextNormal += 1
				continue
			elif line[0] == "vt":
				#add texture coordinate
				texCoords[nextTex] = (float(line[1]), 1 - float(line[2]))
				nextTex += 1
				continue
			elif line[0] == "usemtl":
				#set following faces parts to use the current material
				curMaterial = line[1]
				continue
			elif line[0] == "g":
				#Create a new section
				curPart = line[1]
				curFaces = []
				parts[curPart] = (curFaces, mtls[curMaterial])
			elif line[0] == "f":
				vertexStart = tuple(map(lambda x: int(x), line[1].split("/")))
				for i in range(2, len(line) - 1):
					vertex2 = tuple(map(lambda x: int(x), line[i].split("/")))
					vertex3 = tuple(map(lambda x: int(x), line[i + 1].split("/")))
					curFaces.append((vertexStart, vertex2, vertex3))
	#Reading file is over.
	retval = []
	for i in parts:
		if i == "":
			continue
		faces = parts[i][0]
		wholeVerts = {}
		nextVertIndex = 0
		vs = []
		vts = []
		vns = []
		
		indices = []
		for face in faces:
			for vert in face:
				#pick apart a vertex
				vertexInd = vert[0]
				texCoordInd = vert[1]
				normInd = vert[2]
				#Have we seen the vertex before? If not, add it
				if vert not in wholeVerts:
					wholeVerts[vert] = nextVertIndex
					nextVertIndex += 1
					vs += list(vertices[vertexInd])
					vts += list(texCoords[texCoordInd])
					vns += list(normals[normInd])
				#Whatever position it is, reference it by that
				indices.append(wholeVerts[vert])
		#Create a section object with this name, material, vertices, normals, texture coordinates, and indices, and stick it on the list of sections to return
		retval.append(Section(i, parts[i][1], vs, vns, vts, indices))
	return retval
			
