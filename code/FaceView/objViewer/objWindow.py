import OpenGL.GL as GL
import OpenGL.GLU as GLU
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtOpenGL import *
import numpy
import os.path
import math

from ctypes import c_void_p

#By Thomas Albertine
#It should allow you to view obj files in a little window in your app.

def genTranslationMatrix(x, y, z):
	return numpy.matrix([
		[1, 0, 0, x],
		[0, 1, 0, y],
		[0, 0, 1, z],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genScaleMatrix(x, y, z):
	return numpy.matrix([
		[x, 0, 0, 0],
		[0, y, 0, 0],
		[0, 0, z, 0],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genRotationMatrixX(angle):
	angle = math.radians(angle)
	return numpy.matrix([
		[1, 0, 0, 0],
		[0, math.cos(angle), math.sin(angle), 0],
		[0, -math.sin(angle), math.cos(angle), 0],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genRotationMatrixY(angle):
	angle = math.radians(angle)
	return numpy.matrix([
		[math.cos(angle), 0, -math.sin(angle), 0],
		[0, 1, 0, 0],
		[math.sin(angle), 0, math.cos(angle), 0],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genRotationMatrixZ(angle):
	angle = math.radians(angle)
	return numpy.matrix([
		[math.cos(angle), math.sin(angle), 0, 0],
		[-math.sin(angle), math.cos(angle), 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genRotMatFromQuat(x, y, z, angle):
	angle = math.radians(angle)
	xx = x * x
	xy = x * y
	xz = x * z 
	xw = x * w
	yy = y * y
	yz = y * z 
	yw = y * w 
	zz = z * z 
	zw = z * w 
	return numpy.matrix([
		[1 - 2 * (yy + zz), 2 * (xy - zw), 2 * (xz + yw), 0],
		[2 * (xy + zw), 1 - 2 * (xx + zz), 2 * (yz - xw), 0],
		[2 * (xz - yw), 2 * (yz + xw), 1 - 2 * (xx + yy), 0],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genIdentity():
	return numpy.matrix([
		[1, 0, 0, 0],
		[0, 1, 0, 0],
		[0, 0, 1, 0],
		[0, 0, 0, 1]
		], dtype='float32')
		
def genPerspective(vFov, aspect, near, far):
	fov = math.radians(vFov)
	tanHalf = math.tan(fov / 2)
	
	#return numpy.identity(4)
	return numpy.matrix([
		[1 / (aspect * tanHalf), 0, 0, 0],
		[0, 1 / tanHalf, 0, 0],
		[0, 0, -(far + near) / (far - near), -(2*far*near) / (far - near)],
		[0, 0, -1, 0]
		], dtype='float32')
	
class ObjWidget(QGLWidget):
	# Any default values should be stored in the class

	def __init__(self, models, highlighted = False, parent=None, aspectRatio=1.0):
		QGLWidget.__init__(self, parent)
		
		self.sections = models
		
		self.vaos = []
		self.shaderProg = None
		self.attribIds = []
		self.iBuffers = []
		self.dTexIds = []
		self.maskIds = []
		self.aspect = aspectRatio
		
		#Various positioning data
		self.objScale = 1.5
		self.yRotate = 0
		self.xRotate = 0
		self.yPan = 0
		
		self.MODEL_HEIGHT = 16.594
		#self.MODEL_HEIGHT = 0.5
		
		#Various matrices
		self.perspective = None #To be populated on resize
		self.modelToWorld = None
		self.worldToCamera = None
		self.modelNormalToCamera = None
		self.updateMatrices()

		self.highlighted = highlighted
	
	def getData(self):
		return self.sections

	def highlight(self):
		print "hello"

	def pan(self, y):
		'Allows the user to pan vertically around the model'
		self.yPan = max(min(y, self.MODEL_HEIGHT * 0.8), -self.MODEL_HEIGHT * 0.92)
		self.updateMatrices()
		self.update()
	
	def relativePan(self, y):
		self.pan(self.yPan + y)
		
	def rotate(self, x, z):
		if z > 360 or z < 0:
			z = z % 360
		if x > 70:
			x = 70
		if x < -90:
			x = -90
		self.xRotate = x
		self.yRotate = z
		self.updateMatrices()
		self.update()
		
	def relativeRotate(self, x, z):
		self.rotate(self.xRotate + x, self.yRotate + z)
		
	def scale(self, zoom):
		self.objScale = man(min(zoom, 3), 0.1)
		self.updateMatrices()
		self.update()
	
	def relativeScale(self, zoom):
		self.scale(self.objScale + zoom)
		
	def updateMatrices(self):
		"Updates every matrix except projection, which will be updated on resize"
		newMatrix = genIdentity()
		#Center on the face
		newMatrix = genTranslationMatrix(0, self.MODEL_HEIGHT * -0.42, -0.66) * newMatrix
		newMatrix = genScaleMatrix(self.objScale, self.objScale, self.objScale) * newMatrix
		newMatrix = genRotationMatrixY(self.yRotate) * newMatrix
		newMatrix = genRotationMatrixX(self.xRotate) * newMatrix
		newMatrix = genTranslationMatrix(0, self.yPan, 0) * newMatrix
		self.modelToWorld = newMatrix
		
		newMatrix = genIdentity()
		newMatrix = genTranslationMatrix(0, 0, -5) * newMatrix
		self.worldToCamera = newMatrix
		
		self.modelNormalToCamera = numpy.linalg.inv((self.worldToCamera * self.modelToWorld)[0:3,0:3]).T
		
	
	def __del__(self):
		if callable(hasattr(super(type(self), self), "__del__")):
			super(type(self), self).__del__(parent)
		#Don't call unloadData because it's about to unload anyway.
		
	def paintGL(self):
		#Set background color to denote selected or not selected
		if self.highlighted:
			GL.glClearColor(0.0, 0.5, 0.0, 1.0)
		else:
			GL.glClearColor(0.5, 0.5, 0.5, 1.0)
		GL.glDisable(GL.GL_CULL_FACE)
		GL.glClear(GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)
		
		GL.glUseProgram(self.shaderProg)
		
		#Bind matrices, since they'll be the same for every object
		loc = GL.glGetUniformLocation(self.shaderProg, 'uModelWorld')
		if loc > -1:
			GL.glUniformMatrix4fv(loc, 1, GL.GL_TRUE, numpy.array(self.modelToWorld))
		loc = GL.glGetUniformLocation(self.shaderProg, 'uWorldCamera')
		if loc > -1:
			GL.glUniformMatrix4fv(loc, 1, GL.GL_TRUE, numpy.array(self.worldToCamera))
		loc = GL.glGetUniformLocation(self.shaderProg, 'uCameraProjection')
		if loc > -1:
			GL.glUniformMatrix4fv(loc, 1, GL.GL_TRUE, numpy.array(self.perspective))
		loc = GL.glGetUniformLocation(self.shaderProg, 'uModelNormalCamera')
		if loc > -1:
			GL.glUniformMatrix3fv(loc, 1, GL.GL_TRUE, numpy.array(self.modelNormalToCamera))
		
		#For each object in the scene
		for i in range(len(self.vaos)):
			#Bind Vertex attributes
			GL.glBindVertexArray(self.vaos[i])
			GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.attribIds[i])
			offset = 0
			loc = GL.glGetAttribLocation(self.shaderProg, "uModelPos")
			if loc > -1:
				GL.glEnableVertexAttribArray(loc)
				GL.glVertexAttribPointer(loc, #which variable
					4, #How many components?
					GL.GL_FLOAT, #What type?
					GL.GL_FALSE, #Normalize?
					0, #Stride, that is, distance between consecutive entries
					c_void_p(offset)) #Offset into the buffer
			offset += self.sections[i].vertices.size * self.sections[i].vertices.itemsize
			loc = GL.glGetAttribLocation(self.shaderProg, "uModelNormal")
			if loc > -1:
				GL.glEnableVertexAttribArray(loc)
				GL.glVertexAttribPointer(loc, #which variable
					3, #How many components?
					GL.GL_FLOAT, #What type?
					GL.GL_FALSE, #Normalize?
					0, #Stride, that is, distance between consecutive entries
					c_void_p(offset)) #Offset into the buffer
			offset += self.sections[i].normals.size * self.sections[i].normals.itemsize
			loc = GL.glGetAttribLocation(self.shaderProg, "uST")
			if loc > -1:
				GL.glEnableVertexAttribArray(loc)
				GL.glVertexAttribPointer(loc, #which variable
					2, #How many components?
					GL.GL_FLOAT, #What type?
					GL.GL_FALSE, #Normalize?
					0, #Stride, that is, distance between consecutive entries
					c_void_p(offset)) #Offset into the buffer
			offset += self.sections[i].texPos.size * self.sections[i].texPos.itemsize
			
			#Bind material properties
			loc = GL.glGetUniformLocation(self.shaderProg, 'ambientColor')
			if loc > -1:
				GL.glUniform4fv(loc, 1, self.sections[i].mtl.ambient)
			loc = GL.glGetUniformLocation(self.shaderProg, 'diffuseColor')
			if loc > -1:
				GL.glUniform4fv(loc, 1, self.sections[i].mtl.diffuse)
			loc = GL.glGetUniformLocation(self.shaderProg, 'specularColor')
			if loc > -1:
				GL.glUniform4fv(loc, 1, self.sections[i].mtl.specular)
			loc = GL.glGetUniformLocation(self.shaderProg, 'specExp')
			if loc > -1:
				GL.glUniform1fv(loc, 1, self.sections[i].mtl.exponent)
			loc = GL.glGetUniformLocation(self.shaderProg, 'dissolve')
			if loc > -1:
				GL.glUniform1fv(loc, 1, self.sections[i].mtl.dissolve)
				
			#Bind Textures
			
			loc = GL.glGetUniformLocation(self.shaderProg, 'textureMap')
			if loc > -1:
				GL.glUniform1i(loc, 0)
			GL.glActiveTexture(GL.GL_TEXTURE0)
			GL.glBindTexture(GL.GL_TEXTURE_2D, self.dTexIds[i])
			
			loc = GL.glGetUniformLocation(self.shaderProg, 'mask')
			if loc > -1:
				GL.glUniform1i(loc, 1)
			GL.glActiveTexture(GL.GL_TEXTURE1)
			GL.glBindTexture(GL.GL_TEXTURE_2D, self.maskIds[i])
				
			GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.iBuffers[i])
			GL.glDrawElements(GL.GL_TRIANGLES, #Topology
				self.sections[i].indices.size, #how many vertices
				GL.GL_UNSIGNED_INT, #Type
				None)
			
		
	def resizeGL(self, width, height):
		self.perspective = genPerspective(50.0, float(width) / float(height), 0.1, 20.0)
		GL.glViewport(0, 0, width, height)

	def initializeGL(self):
		QGLWidget.initializeGL(self)
		GL.glEnable(GL.GL_DEPTH_TEST)
		
		self.loadShaders('../FaceView/objViewer/vert.glsl', '../FaceView/objViewer/frag.glsl')
		self.loadData()
		
	def unloadData(self):
		for i in range(0,len(self.vaos)):
			GL.glBindVertexArray(self.vaos[i])
			arr = numpy.array([self.attribIds[i]], dtype='uint32')
			GL.glDeleteBuffers(len(arr), arr)
			arr = numpy.array([self.iBuffers[i]], dtype='uint32')
			GL.glDeleteBuffers(len(arr), arr)
		arr = numpy.array([self.vaos], dtype='unit32')
		GL.glDeleteVertexArrays(len(arr), arr)
		self.vaos = []
		self.attribIds = []
		self.iBuffers = []
			
	
	def reloadData(self):
		self.unloadData()
		self.loadData()
	
	def loadData(self):
		for i in self.sections:
			vao = GL.glGenVertexArrays(1)
			self.vaos.append(vao)
			GL.glBindVertexArray(vao)
			
			#Calculate how big the buffer needs to be
			totalSize = 0
			totalSize += i.vertices.size * i.vertices.itemsize
			totalSize += i.normals.size * i.normals.itemsize
			totalSize += i.texPos.size * i.texPos.itemsize
			
			#generate the vertex attribute buffer (VBO)
			attribsId = GL.glGenBuffers(1)
			self.attribIds.append(attribsId)
			GL.glBindBuffer(GL.GL_ARRAY_BUFFER, attribsId)
			
			#Allocate the requisite space
			GL.glBufferData(GL.GL_ARRAY_BUFFER, totalSize, None, GL.GL_STATIC_DRAW)
			
			#Put data in buffer
			offset = 0
			size = i.vertices.size * i.vertices.itemsize
			GL.glBufferSubData(GL.GL_ARRAY_BUFFER, #Type
				offset, #Offset into the buffer to put our data
				size,   #How much data (in bytes) are we putting in?
				i.vertices) #The data itself
			offset += size
			size = i.normals.size * i.normals.itemsize
			GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
				offset,
				size,
				i.normals)
			offset += size
			size = i.texPos.size * i.texPos.itemsize
			GL.glBufferSubData(GL.GL_ARRAY_BUFFER,
				offset,
				size,
				i.texPos)
			offset += size
			
			#Index buffer creation
			indexBuffer = GL.glGenBuffers(1)
			self.iBuffers.append(indexBuffer)
			#Populate index buffer
			GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, indexBuffer)
			GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, i.indices.size * i.indices.itemsize, i.indices, GL.GL_STATIC_DRAW)
			
			#load textures
			tex = GL.glGenTextures(1)
			self.dTexIds.append(tex)
			GL.glBindTexture(GL.GL_TEXTURE_2D, tex)
			GL.glTexImage2D(GL.GL_TEXTURE_2D,
				0, 
				GL.GL_RGBA,
				i.mtl.texSize[0],
				i.mtl.texSize[1],
				0,
				GL.GL_RGBA,
				GL.GL_UNSIGNED_BYTE,
				i.mtl.diffuseTexture)
			GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
			GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
			tex = GL.glGenTextures(1)
			self.maskIds.append(tex)
			GL.glBindTexture(GL.GL_TEXTURE_2D, tex)
			GL.glTexImage2D(GL.GL_TEXTURE_2D,
				0, 
				GL.GL_RGBA,
				i.mtl.maskSize[0],
				i.mtl.maskSize[1],
				0,
				GL.GL_RGBA,
				GL.GL_UNSIGNED_BYTE,
				i.mtl.maskTexture)
			GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
			GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
			
	def loadShaders(self, vertexPath, fragmentPath):
		if self.shaderProg is not None:
			GL.glDeleteProgram(self.shaderProg)
			
		vert = GL.glCreateShader(GL.GL_VERTEX_SHADER)
		frag = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
		
		#Read shader text
		vertexText = ""
		fragmentText = ""
		with open(vertexPath, 'rU') as f:
			vertexText = f.read()
		with open(fragmentPath, 'rU') as f:
			fragmentText = f.read()
			
		#Compile vertex shader
		GL.glShaderSource(vert, vertexText)
		GL.glCompileShader(vert)
		if GL.glGetShaderiv(vert, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
			raise RuntimeError("\n\nVertex Shader: " + GL.glGetShaderInfoLog(vert))
		
		#Compile fragment shader
		GL.glShaderSource(frag, fragmentText)
		GL.glCompileShader(frag)
		if GL.glGetShaderiv(frag, GL.GL_COMPILE_STATUS) != GL.GL_TRUE:
			raise RuntimeError("\n\nFragment Shader: "  + GL.glGetShaderInfoLog(frag))
			
		#Link
		prog = GL.glCreateProgram()
		GL.glAttachShader(prog, vert)
		GL.glAttachShader(prog, frag)
		GL.glLinkProgram(prog)
		if GL.glGetProgramiv(prog, GL.GL_LINK_STATUS) != GL.GL_TRUE:
			raise RuntimeError(GL.glGetProgramInfoLog(prog))
		GL.glDetachShader(prog, vert)
		GL.glDetachShader(prog, frag)
		GL.glDeleteShader(vert)
		GL.glDeleteShader(frag)
		self.shaderProg = prog
				
	def setHighlighted(self, hl):
		self.highlighted = hl
		self.updateGL()
				
if __name__ == '__main__':
	import objModel
	import os
	model = objModel.loadModel("../models/Sample 1.obj")
	print model
	#model = objModel.loadModel("objViewer/test.obj")
	app = QtGui.QApplication(["Thomas' widget"])
	widget = ObjWidget(model)
	widget.resize(300, 300)
	widget.highlight()
	widget.show()
	timer = QtCore.QTimer()
	def timeout_func():
		widget.relativeRotate(0, 0)
	
	timer.timeout.connect(timeout_func)
	timer.start(16)
	app.exec_()
	
	
