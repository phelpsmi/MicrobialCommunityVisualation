#version 330 core
//By Thomas Albertine
//Does transformations and passes through enough information for Phong illumination.
in vec2 vST;
in vec3 vNormalModel;
in vec3 vNormalCamera;

#define LIGHT_LOC_CAMERA vec4(1.0, 1.0, 1.0, 1.0)
#define K_AMBIENT 0.25
#define K_DIFFUSE 0.75
#define K_SPECULAR 0.25
#define K_SPEC_EXP 5

in vec4 vModelPos;
in vec4 vWorldPos;
in vec4 vCameraPos;

out vec4 color;

uniform vec4 skinColor;
uniform vec4 skinSpecularColor;

void main(){
	vec3 normal = normalize(vNormalCamera);
	
	//Ambient component. Easy peasy!
	vec4 ambient = K_AMBIENT * skinColor;
	
	//Diffuse component. Almost as easy!
	vec3 toLight = normalize((LIGHT_LOC_CAMERA - vCameraPos).xyz);
	vec4 diffuse = K_DIFFUSE * dot(toLight, normal) * skinColor;
	
	//Specular component. A little tricky.
	vec3 toViewer = normalize((vec4(0,0,0,1) - vCameraPos).xyz);
	vec3 reflection = normalize(-reflect(toLight, normal));
	vec4 specular = K_SPECULAR * pow(dot(reflection, toViewer), K_SPEC_EXP) * skinSpecularColor;
	
	color = ambient + diffuse + specular;
	
}