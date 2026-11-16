#version 330 core
// V9: volumetric camera fly-through from cosmic-dawn galaxies to molecular
// cloud material, leading visually into the APPROVED t=260..300 Solar System.
// Original art-directed, time-compressed storytelling, not a claim that
// galaxies physically turn into one protoplanetary disc in seconds.
// Completely absent for t>=260 and t<=240.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime,uAspect,uTanHalfFovY,uFilmTime;
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
    float d=mix(hash31(i+vec3(0,1,1)),hash31(i+vec3(1,1,1)),f.x);
    return mix(mix(a,b,f.y),mix(c,d,f.y),f.z);
}
float fbm3(vec3 p){
    return 0.56*noise3(p)+0.27*noise3(p*2.17+1.3)+
           0.12*noise3(p*4.23-3.1)+0.05*noise3(p*8.27+7.2);
}
// V12.1: approach the SAME world-space cloud used by the solar shader.
// Move the ray camera into its final composition before the overlap ends.
void main(){
    float x=clamp((uFilmTime-105.0)/13.0,0.0,1.0);
    float e=x*x*x*(x*(x*6.0-15.0)+10.0);
    vec3 ro=mix(uCameraPos,vec3(10.0,-56.0,28.0),e);
    vec3 f=normalize(mix(uCameraForward,normalize(-vec3(10.0,-56.0,28.0)),e));
    vec3 right=normalize(cross(f,vec3(0,0,1))),up=normalize(cross(right,f));
    vec2 xy=TexCoords*2.0-1.0;
    vec3 ray=normalize(f+xy.x*uAspect*mix(uTanHalfFovY,0.62,e)*right+
                         xy.y*mix(uTanHalfFovY,0.62,e)*up);
    vec3 extent=vec3(26,26,15),o=ro/extent,d=ray/extent;
    float a=dot(d,d),b=dot(o,d),c=dot(o,o)-1.0,det=b*b-a*c;
    if(det<=0.0){FragColor=vec4(0);return;}
    float nearT=max(0.02,(-b-sqrt(det))/a),farT=(-b+sqrt(det))/a;
    float stepT=max(0.0,farT-nearT)/24.0,trans=1.0;
    vec3 radiance=vec3(0);
    for(int j=0;j<24;++j){
        vec3 p=ro+ray*(nearT+(float(j)+0.5)*stepT);
        float r=length(p.xy),angle=atan(p.y,p.x)-(uFilmTime-118.0)*0.16/pow(1.0+r*0.24,1.5);
        vec3 advected=vec3(r*cos(angle),r*sin(angle),p.z);
        float broad=fbm3(advected*0.19+vec3(2.8,7.1,3.4));
        float fine=noise3(advected*1.15+vec3(9.7,1.2,8.6));
        float density=pow(smoothstep(0.25,0.76,broad),1.5)*
            (1.0-smoothstep(0.72,1.0,length(p/extent)))*0.13*(0.80+0.20*fine);
        float illumination=0.25/(1.0+0.055*dot(p,p));
        vec3 scatter=vec3(0.055,0.075,0.105)+vec3(1.85,1.05,0.43)*illumination*
            (0.35+0.65*exp(-density*min(length(p),12.0)*1.8));
        float alpha=1.0-exp(-density*stepT);
        radiance+=trans*scatter*alpha;trans*=1.0-alpha;
    }
    FragColor=vec4(radiance,smoothstep(105.0,112.0,uFilmTime)*0.75);
}
