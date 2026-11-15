#version 330 core
// V9: volumetric camera fly-through from cosmic-dawn galaxies to molecular
// cloud material, leading visually into the APPROVED t=260..300 Solar System.
// Original art-directed, time-compressed storytelling, not a claim that
// galaxies physically turn into one protoplanetary disc in seconds.
// Completely absent for t>=260 and t<=240.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime,uAspect,uTanHalfFovY;
uniform vec3 uCameraPos,uCameraForward,uCameraRight,uCameraUp;

float hash31(vec3 p){
    p=fract(p*0.1031);
    p+=dot(p,p.yzx+33.33);
    return fract((p.x+p.y)*p.z);
}
float noise3(vec3 p){
    vec3 i=floor(p),f=fract(p);
    f=f*f*(3.0-2.0*f);
    float a=mix(hash31(i),hash31(i+vec3(1,0,0)),f.x);
    float b=mix(hash31(i+vec3(0,1,0)),hash31(i+vec3(1,1,0)),f.x);
    float c=mix(hash31(i+vec3(0,0,1)),hash31(i+vec3(1,0,1)),f.x);
    float d=mix(hash31(i+vec3(0,0,1)+vec3(1,1,0)),
                hash31(i+vec3(1,1,1)),f.x);
    // top layer: corners z=1
    c=mix(hash31(i+vec3(0,0,1)),hash31(i+vec3(1,0,1)),f.x);
    d=mix(hash31(i+vec3(0,1,1)),hash31(i+vec3(1,1,1)),f.x);
    return mix(mix(a,b,f.y),mix(c,d,f.y),f.z);
}
float fbm3(vec3 p){
    return 0.58*noise3(p)+0.28*noise3(p*2.06+vec3(7.3,1.4,9.8))
         + 0.14*noise3(p*4.10+vec3(3.2,11.8,2.1));
}
void main(){
    float t=uTime;
    // No fragment contribution outside the pre-solar transition.
    float onset=smoothstep(240.0,250.0,t);
    float retreat=1.0-smoothstep(255.0,260.0,t);
    float amount=onset*retreat;
    if(amount<=0.00001){
        FragColor=vec4(0.0);
        return;
    }
    vec2 uv=TexCoords*2.0-vec2(1.0);
    vec3 ray=normalize(uCameraForward+
        uv.x*uAspect*uTanHalfFovY*uCameraRight+
        uv.y*uTanHalfFovY*uCameraUp);
    float progress=smoothstep(240.0,260.0,t);
    vec3 tintCool=vec3(0.045,0.115,0.27);
    vec3 tintWarm=vec3(0.48,0.25,0.14);
    vec3 radiance=vec3(0.0);
    float transmittance=1.0;

    // Ray march in true world space so the camera travels through a curved
    // dust field, rather than switching to a flat screen overlay.
    // 18 samples are intentionally bounded for llvmpipe renders.
    const int STEPS=18;
    const float LEN=1.26;
    for(int i=0;i<STEPS;++i){
        float depth=2.0+(float(i)+0.5)*LEN;
        vec3 p=uCameraPos+ray*depth;
        // Advection and coherent spatial scale change continuously.
        vec3 q=p*0.205+vec3(0.018*t,-0.011*t,0.013*t);
        float broad=fbm3(q+vec3(2.8,7.1,3.4));
        float fine=fbm3(q*2.44+vec3(9.7,1.2,8.6));
        float folds=exp(-75.0*(broad-0.585)*(broad-0.585));
        float pockets=smoothstep(0.42,0.72,fine);
        float density=folds*(0.30+0.70*pockets);
        float depthWindow=smoothstep(2.0,6.0,depth)*
            (1.0-smoothstep(19.0,25.5,depth));
        float alpha=1.0-exp(-0.060*density*depthWindow*LEN);
        vec3 hue=mix(tintCool,tintWarm,progress*(0.44+0.56*pockets));
        vec3 localGlow=hue*(0.3+0.8*pockets)*density;
        radiance+=transmittance*localGlow*alpha;
        transmittance*=(1.0-alpha);
    }

    // A subtle warm focal cocoon hints at the distant future molecular cloud.
    // It expands gently, and fully disappears BEFORE the protected finale.
    float a=max(dot(ray,uCameraForward),0.0);
    float cocoon=pow(a,42.0)*smoothstep(245.0,255.0,t);
    radiance+=mix(vec3(0.065,0.13,0.21),vec3(0.47,0.24,0.10),
                 progress)*cocoon*0.105;

    // Alpha is nonzero only 240<t<260. Additively glowed source avoids
    // masking the original 4,400-galaxy catalogue or making a grey whiteout.
    FragColor=vec4(max(radiance,vec3(0.0))*2.0,amount*0.92);
}
