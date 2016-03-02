#version 330 core
//By Thomas Albertine
//Just Phong illumination
in vec4 uModelPos;
in vec2 uST;
in vec3 uModelNormal;

out vec2 vST;
out vec3 vNormalModel;
out vec3 vNormalCamera;

out vec4 vModelPos;
out vec4 vWorldPos;
out vec4 vCameraPos;

uniform mat4 uModelWorld;
uniform mat4 uWorldCamera;
uniform mat4 uCameraProjection;
uniform mat3 uModelNormalCamera;

void main(){
	vModelPos = uModelPos;
	vWorldPos = uModelWorld * uModelPos;
	vCameraPos = uWorldCamera * uModelWorld * uModelPos;
	gl_Position = uCameraProjection * uWorldCamera * uModelWorld * uModelPos;
	vST = uST;
	vNormalCamera = uModelNormalCamera * uModelNormal;
	vNormalModel = uModelNormal;
}