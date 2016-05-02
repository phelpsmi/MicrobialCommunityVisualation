#version 330 core
//By Thomas Albertine
//Does transformations and passes through enough information for Phong illumination.
in vec2 vST;
in vec3 vNormalModel;
in vec3 vNormalCamera;

#define LIGHT_LOC_CAMERA vec4(1.0, 1.0, 1.0, 1.0)
#define K_AMBIENT 0.10
#define K_DIFFUSE 0.7
#define K_SPECULAR 0.2
#define K_SPEC_EXP 5

in vec4 vModelPos;
in vec4 vWorldPos;
in vec4 vCameraPos;

out vec4 color;

uniform vec4 ambientColor;
uniform vec4 diffuseColor;
uniform vec4 specularColor;
uniform float specExp;
uniform float dissolve; //Ignore this one for now

uniform sampler2D textureMap;
uniform sampler2D mask;

#ifdef TOON_SHADER
#define COLOR_LEVELS 4

vec4 posterize(vec4 inColor){
	vec4 retval = vec4(ceil(inColor * COLOR_LEVELS) / COLOR_LEVELS);
	retval.a = inColor.a;
	return retval;
}
#endif

void main(){
	vec3 normal = normalize(vNormalCamera);
	
	//Ambient component. Easy peasy!
	vec4 ambient = K_AMBIENT * ambientColor;
	
	//Diffuse component. Almost as easy!
	vec3 toLight = normalize((LIGHT_LOC_CAMERA - vCameraPos).xyz);
	vec4 diffuse = K_DIFFUSE * dot(toLight, normal) * mix(texture(textureMap, vST), diffuseColor, dissolve);
	
	//Specular component. A little tricky.
	vec3 toViewer = normalize((vec4(0,0,0,1) - vCameraPos).xyz);
	vec3 reflection = normalize(-reflect(toLight, normal));
	vec4 specular = K_SPECULAR * pow(dot(reflection, toViewer), K_SPEC_EXP) * specularColor;
	
	color = ambient + diffuse + specular;
	#ifdef TOON_SHADER
	color = posterize(color);
	if (dot(normal, toViewer) < 0.25){
		color.rgb = vec3(0,0,0);
	}
	#endif
}