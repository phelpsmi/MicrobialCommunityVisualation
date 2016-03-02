
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

class ObjModel:
	def __init__(self, objPath):
		self.vs = []
		self.ns = []
		self.sts = []
		self.iList = []
		mtl = self.loadModel(objPath)
		self.loadMaterial(os.path.join(os.path.dirname(os.path.abspath(objPath)),mtl ))
		
	def loadModel(self, filePath):
		mtl = ''
		vs = []
		ns = []
		sts = []
		faces = []
		with open(filePath, 'rU') as f:
			for line in f:
				line = line.split()
				if len(line) == 0:
					#Empty line. Unimportant
					continue
				if line[0].startswith('#'):
					continue
					#It's a comment. Skip it.
				elif line[0] == 'mtllib':
					
					#Use this material. There will only be 1 in the files we're loading.
					mtl = line[1]
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
					#I don't know what this is, so skip it.
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
	
	def loadMaterial(self, mtlPath):
		self.diffuseColor = tuple([0.5, 0.5, 0.5, 1.0])
		self.specularColor = tuple([1.0, 1.0, 1.0, 1.0])
		if not os.path.isfile(mtlPath):
			#No material for the file
			return
		with open(mtlPath, 'rU') as file:
			for line in file:
				line = line.split()
				if len(line) == 0:
					#Empty line. Skip it
					continue
				elif line[0].startswith('#'):
					#It's a comment. Skip it.
					continue
				elif line[0] == 'newmtl':
					#It's not important for out purposes
					continue
				elif line[0] == 'Kd':
					self.diffuseColor = tuple([float(line[1]), float(line[2]), float(line[3]), 1.0])
				elif line[0] == 'Ks':
					self.specularColor = tuple([float(line[1]), float(line[2]), float(line[3]), 1.0])
				elif line[0] == 'd':
					#Not important for us
					continue
	
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
			
			
			
				
			
			
