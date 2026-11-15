#version 330 core
// A deterministic 3D galaxy catalogue; each GL point shades a galaxy disc,
// elliptic light profile, or irregular cluster in its own angular footprint.
layout(location=0) in vec3 aPosition;
layout(location=1) in vec4 aMorphology;
layout(location=2) in vec4 aRadiance;

uniform vec3 uCameraPos,uCameraForward,uCameraRight,uCameraUp;
uniform float uAspect,uTanHalfFovY,uScreenHeight,uTime;
out vec4 vMorphology;
out vec4 vRadiance;
out float vVisible;
out float vPointPixels;
out float vSeed;

void main() {
    vec3 delta=aPosition-uCameraPos;
    float z=dot(delta,uCameraForward);
    // V8: reveal galaxy cores across the dust-clearing transition instead
    // of waiting for the grey veil to disappear.  Visibility is 1.0
    // by t=273 as before, leaving all later galaxy shots unchanged.
    vVisible=smoothstep(238.0,273.0,uTime);
    if(z<0.5 || vVisible<0.00001) {
        gl_PointSize=1.0;
        gl_Position=vec4(3.0,3.0,1.0,1.0);
        vVisible=0.0;
    } else {
        float x=dot(delta,uCameraRight)/(z*uTanHalfFovY*uAspect);
        float y=dot(delta,uCameraUp)/(z*uTanHalfFovY);
        gl_Position=vec4(x,y,0.0,1.0);
        float pixelDiameter=aMorphology.x*uScreenHeight/
            max(0.001,2.0*z*uTanHalfFovY);
        gl_PointSize=clamp(pixelDiameter,1.0,65.0);
    }
    vMorphology=aMorphology;
    vRadiance=aRadiance;
    vPointPixels=gl_PointSize;
    vSeed=fract(float(gl_VertexID)*0.61803398875);
}
