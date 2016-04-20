
from PIL import Image #Module is actually called Pillow, not PIL
import os
import numpy

#objModel.py
#By Thomas Albertine
#Parses obj files, but throws away unnecessary information.
#Implements enough of the obj spec for our purposes.

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
		
class Section:
	def __init__(self):
		self.model = None
		self.mtl = None
		
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
		if texture is None:
			texture = Image.new("RGBA", (1,1), (1,1,1,1))
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
			mask = Image.new("RGBA", (1,1), (1,1,1,1))
		else:
			mask = Image.open(mask)
		mask.convert("RGBA")
		self.maskSize = mask.size
		self.mask = numpy.array(list(mask.getdata()), numpy.uint8)
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
	def getMask(self):
		return self.mask
	def setAmbient(self, ambient=(1.0, 1.0, 1.0, 1.0)):
		self.ambient = numpy.array(ambient)
	def setDiffuse(self, diffuse=(1.0, 1.0, 1.0, 1.0)):
		self.diffuse = numpy.array(diffuse)
	def setSpecular(self, specular=(1.0, 1.0, 1.0, 1.0)):
		self.specular = numpy.array(specular)
	def setExponent(self, exp=1.0):
		self.exponent = exp
	def setDissolve(self, dissolve=1.0):
		self.dissolve = dissolve
	def setDiffuseTexture(self, texture=None):
		if texture is None:
			texture = Image.new("RGBA", (1,1), (1,1,1,1))
		else:
			texture = Image.open(texture)
		texture.convert("RGBA")
		self.texSize = texture.size
		self.diffuseTexture = numpy.array(list(texture.getdata()), numpy.uint8)
		texture.close()
	def setMask(self, mask=None):
		if mask is None:
			mask = Image.new("RGBA", (1,1), (1,1,1,1))
		else:
			mask = Image.open(mask)
		mask.convert("RGBA")
		self.maskSize = mask.size
		self.mask = numpy.array(list(mask.getdata()), numpy.uint8)
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
		retval += "\n\tMask: " + str(self.mask) + "\n>"
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
				curMtl.setMask(os.path.join(os.path.split(mtlPath)[0], line[1]))
				continue
	return mtls

class ObjModel:
	def __init__(self, objPath):
		self.vs = []
		self.ns = []
		self.sts = []
		self.iList = []
		mtl = self.loadModel(objPath)
		print "\n\n" + mtl + "\n" + os.path.join(os.path.dirname(os.path.abspath(objPath)),mtl)  + "\n\n"
		self.loadMaterial(os.path.join(os.path.dirname(os.path.abspath(objPath)),mtl ))
		
	def loadModel(self, filePath):
		mtl = ''
		mtls = {}
		vs = []
		ns = []
		sts = []
		faces = []
		with open(filePath, 'rU') as f:
			for line in f:
				oLine = line
				line = line.split()
				if len(line) == 0:
					#Empty line. Unimportant
					continue
				if line[0].startswith('#'):
					continue
					#It's a comment. Skip it.
				elif line[0] == 'mtllib':
					
					#Use this material. There will only be 1 in the files we're loading.
					s = oLine[oLine.find('mtllib') + len('mtllib'):].strip()
					print "Loading: \n\n" + s + "\n\n"
					mtl = s
				elif line[0] == 'v':
					#A vertex
					pos = numpy.array([float(line[1]), float(line[2]), float(line[3]), 1.0], dtype='f')
					vs.append(pos.tolist())
				elif line[0] == 'vn':
					#A normal
					ns.append([float(line[1]), float(line[2]), float(line[3])])
				elif line[0] == 'vt':
					#A texture coordinate
					sts.append([float(line[1]), float(line[2])])
				elif line[0] == 'f':
					#A face. Assume triangle fan order
					newline = []
					for i in line[1:]:
						newline.append(tuple(map(lambda x: int(x) - 1, i.split('/'))))
					first = newline[0]
					for i in range(1, len(newline) - 1):
						faces.append(tuple([first, newline[i], newline[i+1]]))
				elif line[0] == 'usemtl':
					continue
					#Ignore this for now
				elif line[0] == 'g':
					#Not important for us
					continue
		#Reading file is over.
		self.vs = []
		self.ns = []
		self.sts = []
		self.iList = []
		#Break up faces to play nice with element array buffer
		faceMap = {} #Will associate tuples of obj indices that correspond with a vertex in the final product
		nextPos = 0
		for face in faces:
			for vertex in face:
				if vertex in faceMap:
					#We've already found it. Get the index
					self.iList.append(faceMap[vertex])
				else:
					#It's new. Add a new index, and add the corresponding values to the correct lists
					faceMap[vertex] = nextPos
					self.iList.append(nextPos)
					nextPos += 1
					self.vs.append(vs[vertex[0]])
					self.ns.append(ns[vertex[2]])
					self.sts.append(sts[vertex[1]])
		return mtl					
	
	def vertices(self):
		return self.vs[:]
		
	def normals(self):
		return self.ns[:]
		
	def texCoords(self):
		return self.sts[:]
		
	def indices(self):
		return self.iList[:]
		
	def skinColor(self):
		return self.diffuseColor[:]
		
	def skinSpecColor(self):
		return self.specularColor[:]
	
	#returns a map of material names to materials
	
	
	def toFile(self, filePath):
		v = ""
		vn = ""
		vt = ""
		f = ""
		curInd = 0
		for i in chunks(self.iList, 3):
			vertices = map(lambda x: self.vs[x], i)
			normals = map(lambda x: self.ns[x], i)
			texCoords = map(lambda x: self.sts[x], i)
			for vertex in vertices:
				vStr = 'v'
				for coord in vertex[0:3]:
					vStr += " " + str(coord)
				vStr += '\n'
				v += vStr
			for normal in normals:
				nStr = 'vn'
				for comp in normal:
					nStr += ' ' + str(comp)
				nStr += '\n'
				vn += nStr
			for texCoord in texCoords:
				tStr = 'vt'
				for val in texCoord:
					tStr += ' ' + str(val)
				tStr += '\n'
				vt += tStr
				
			f += 'f ' + '/'.join((str((curInd * 3) + 1) for i in range(3))) + ' ' + '/'.join((str((curInd * 3) + 2) for i in range(3))) + ' ' + '/'.join((str((curInd * 3) + 3) for i in range(3))) + '\n'
			curInd += 1
		with open(filePath, 'w') as file:
			file.write(v + "\n" + vn + '\n' + vt + '\n' + f)
			
			
if __name__ == "__main__":
	#Do some testing/debugging stuff
	path = "../../models/derp"
	test = loadMaterial(path + ".mtl")
	for i in test:
		print i
		print test[i]
		raw_input("continue")
	
	
				
			
			
