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

	def __init__(self, model, parent=None, aspectRatio=1.0):
		QGLWidget.__init__(self, parent)
		self.data = model
		self.vao = None
		self.verts = None
		self.shaderProg = None
		self.shaderVars={}
		self.vertexComps = -1
		self.indexBuffer = -1
		self.aspect = aspectRatio
		
		#Various positioning data
		self.objScale = 1.5
		self.yRotate = 0
		self.xRotate = 0
		self.yPan = 0
		
		self.MODEL_HEIGHT = 16.594
		
		#Various matrices
		self.perspective = None #To be populated on resize
		self.modelToWorld = None
		self.worldToCamera = None
		self.modelNormalToCamera = None
		self.updateMatrices()
		
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
		if x > 180:
			x = 90
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
		newMatrix = genTranslationMatrix(0, self.MODEL_HEIGHT * -.42, -0.66) * newMatrix
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
		#For a test
		GL.glDisable(GL.GL_CULL_FACE)
		GL.glClear(GL.GL_DEPTH_BUFFER_BIT | GL.GL_COLOR_BUFFER_BIT)
		GL.glUseProgram(self.shaderProg)
		
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertexComps)
		offset = 0
		for i in self.attrs:
			name, type, length, data = i
			size = data.size * data.itemsize
			varIndex = self.shaderVars[name]
			if varIndex > -1:
				GL.glEnableVertexAttribArray(varIndex)
				GL.glVertexAttribPointer(varIndex, length, type, GL.GL_FALSE, 0, c_void_p(offset))
			offset += size
			
		#Matrices
		loc = GL.glGetUniformLocation(self.shaderProg, 'uModelWorld')
		if loc > -1:
			GL.glUniformMatrix4fv(loc, 1, GL.GL_TRUE, self.modelToWorld)
		loc = GL.glGetUniformLocation(self.shaderProg, 'uWorldCamera')
		if loc > -1:
			GL.glUniformMatrix4fv(loc, 1, GL.GL_TRUE, self.worldToCamera)
		loc = GL.glGetUniformLocation(self.shaderProg, 'uCameraProjection')
		if loc > -1:
			GL.glUniformMatrix4fv(loc, 1, GL.GL_TRUE, self.perspective)
		loc = GL.glGetUniformLocation(self.shaderProg, 'uModelNormalCamera')
		if loc > -1:
			GL.glUniformMatrix3fv(loc, 1, GL.GL_TRUE, self.modelNormalToCamera)
			
		#Colors
		loc = GL.glGetUniformLocation(self.shaderProg, 'skinColor')
		if loc > -1:
			data = numpy.array(self.data.skinColor(), dtype='float32')
			GL.glUniform4fv(loc, 1, data)
		loc = GL.glGetUniformLocation(self.shaderProg, 'skinSpecularColor')
		if loc > -1:
			data = numpy.array(self.data.skinSpecColor(), dtype='float32')
			GL.glUniform4fv(loc, 1, data)
		
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)
		GL.glDrawElements(GL.GL_TRIANGLES, #Topology
			numpy.array(self.data.indices(), 'uint32').size, #Count in points
			GL.GL_UNSIGNED_INT, #Type
			None)
		for i in self.attrs:
			name = i[0]
			varIndex = self.shaderVars[name]
			if varIndex > -1:
				GL.glDisableVertexAttribArray(varIndex)
		
	def resizeGL(self, width, height):
		self.perspective = genPerspective(50.0, float(width) / float(height), 0.1, 20.0)
		GL.glViewport(0, 0, width, height)

	def initializeGL(self):
		QGLWidget.initializeGL(self)
		GL.glClearColor(0.0, 0.0, 0.0, 1.0)
		GL.glEnable(GL.GL_DEPTH_TEST)
		
		
		self.attrs = [('uModelPos', GL.GL_FLOAT, 4, numpy.array(self.data.vertices(), dtype='float32')),
			('uST', GL.GL_FLOAT, 2, numpy.array(self.data.texCoords(), dtype='float32')),
			('uModelNormal', GL.GL_FLOAT, 3, numpy.array(self.data.normals(), dtype='float32'))] #name, gl type, vector length, data
			
		self.loadShaders('./vert.glsl', './frag.glsl')
		self.loadData()
		
	def unloadData(self):
		arr = numpy.array([self.vertexComps], dtype='uint32')
		GL.glDeleteBuffers(1, arr)
		self.vertexComps = -1
		GL.glDeleteBuffers(1, numpy.array([self.indexBuffer], dtype='uint32'))
		self.indexBuffer = -1
	
	def reloadData(self):
		self.unloadData()
		self.loadData()
	
	def loadData(self):
		self.vao = GL.glGenVertexArrays(1)
		GL.glBindVertexArray(self.vao)
		
		totalSize = 0
		for i in self.attrs:
			data = i[3]
			totalSize += data.size * data.itemsize
		#Generate data buffer
		self.vertexComps = GL.glGenBuffers(1)
		GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vertexComps)
		
		#Get memory
		GL.glBufferData(GL.GL_ARRAY_BUFFER, totalSize, None, GL.GL_STATIC_DRAW)
		
		#Put vertices in buffer
		offset = 0
		for i in self.attrs:
			data = i[3]
			size = data.size * data.itemsize
			
			GL.glBufferSubData(GL.GL_ARRAY_BUFFER, #target
				offset, #offset into the buffer to put the data
				size, #size of data in bytes
				data) #data
			offset += size
		
		#Generate index buffer
		indices = numpy.array(self.data.indices(), dtype='uint32')
		self.indexBuffer = GL.glGenBuffers(1)
		GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer)
		GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.itemsize * indices.size, indices, GL.GL_STATIC_DRAW)
		
		
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
		
		for i in self.attrs:
			name = i[0]
			self.shaderVars[name] = GL.glGetAttribLocation(self.shaderProg, name)
		for key, value in self.shaderVars.iteritems():
			if value == -1:
				print "Double check " + str(key)+ "."
				print "It was not found, but it may have been optimized out of the shaders."
				
if __name__ == '__main__':
	import objModel
	model = objModel.ObjModel('../../models/PC.354.obj')
	app = QtGui.QApplication(["Thomas' "])
	widget = ObjWidget(model)
	widget.resize(400, 400)
	widget.show()
	timer = QtCore.QTimer()
	def timeout_func():
		widget.relativeRotate(0, 1.25)
	
	timer.timeout.connect(timeout_func)
	timer.start(16)
	app.exec_()
	
	