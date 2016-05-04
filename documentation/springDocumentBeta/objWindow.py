

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