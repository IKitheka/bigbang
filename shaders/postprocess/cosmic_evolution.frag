#version 330 core
// Native C++ scene-linear transport for the six later epochs.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime;
uniform vec3 uCameraPos, uCameraForward, uCameraRight, uCameraUp;
uniform float uAspect, uTanHalfFovY;
float hash31(vec3 p) {
    p = fract(p * 0.1031);
    p += dot(p, p.yzx + 33.33);
    return fract((p.x + p.y) * p.z);
}

float valueNoise(vec3 p) {
    vec3 i = floor(p);
    vec3 f = fract(p);
    f = f*f*(3.0-2.0*f);
    float n000 = hash31(i);
    float n100 = hash31(i+vec3(1,0,0));
    float n010 = hash31(i+vec3(0,1,0));
    float n110 = hash31(i+vec3(1,1,0));
    float n001 = hash31(i+vec3(0,0,1));
    float n101 = hash31(i+vec3(1,0,1));
    float n011 = hash31(i+vec3(0,1,1));
    float n111 = hash31(i+vec3(1,1,1));
    float a = mix(mix(n000,n100,f.x),mix(n010,n110,f.x),f.y);
    float b = mix(mix(n001,n101,f.x),mix(n011,n111,f.x),f.y);
    return mix(a,b,f.z);
}

float fbm(vec3 p) {
    return 0.60*valueNoise(p)+0.28*valueNoise(p*2.02+17.4)
        +0.12*valueNoise(p*4.05-8.9);
}


#include "cosmic_early.glsl"
#include "cosmic_late.glsl"
void main() {
    vec2 xy=TexCoords*2.0-vec2(1.0);
    vec3 ray=normalize(uCameraForward+xy.x*uAspect*uTanHalfFovY*uCameraRight+
                       xy.y*uTanHalfFovY*uCameraUp);
    float handoff=smoothstep(164.0,176.0,uTime);
    vec3 early=vec3(0), late=vec3(0);
    if (handoff<1.0) early=earlyEpochRadiance(uCameraPos,ray,uTime);
    if (handoff>0.0) late=lateEpochRadiance(uCameraPos,ray,uTime);
    vec3 radiance=mix(early,late,handoff);
    FragColor=vec4(radiance,smoothstep(45.0,56.0,uTime));
}
