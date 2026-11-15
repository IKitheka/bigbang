#version 330 core
// Thin galaxy discs, ragged arms, smooth ellipticals, clumpy irregulars.
// For small angular sizes these become resolved stellar points rather than
// featureless circular volumetric spheres. All emission is scene-linear HDR.
in vec4 vMorphology;
in vec4 vRadiance;
in float vVisible,vPointPixels,vSeed;
out vec4 FragColor;

float hash21(vec2 p) {
    p=fract(p*vec2(123.34,345.45));
    p+=dot(p,p+34.345);
    return fract(p.x*p.y);
}

void main() {
    if(vVisible<=0.00001) discard;
    vec2 p=(gl_PointCoord-vec2(0.5))*2.0;
    float a=vMorphology.y;
    mat2 rot=mat2(cos(a),-sin(a),sin(a),cos(a));
    vec2 q=rot*p;
    float ratio=vMorphology.z;
    float family=vMorphology.w;
    vec2 elliptical=vec2(q.x,q.y/max(0.22,ratio));
    float r=length(elliptical);
    if(r>1.0) discard;

    float core=exp(-38.0*r*r);
    float disc=exp(-4.8*r*r)*(1.0-smoothstep(0.82,1.0,r));
    float theta=atan(elliptical.y,elliptical.x);
    float twoArms=pow(0.5+0.5*cos(2.0*theta-5.5*log(r+0.11)+vSeed*5.0),10.0);
    float arms=twoArms*smoothstep(0.16,0.37,r)*
               (1.0-smoothstep(0.75,0.98,r));
    float holes=0.75+0.25*sin(theta*13.0+14.0*r+vSeed*35.0);
    float dust=1.0-0.50*arms*(0.25+0.75*holes);
    float lineArt=disc*(0.12+0.95*arms)*dust+core*0.78;
    float ellipticalArt=0.66*exp(-7.5*r*r)+core*0.24;

    vec2 cells=floor(elliptical*8.0+vSeed*70.0);
    float jagged=hash21(cells);
    float irregular=exp(-3.8*r*r)*
                    (0.20+0.75*smoothstep(0.42,0.82,jagged));
    irregular+=0.32*exp(-36.0*dot(elliptical-vec2(0.32,-0.18),
                                    elliptical-vec2(0.32,-0.18)));
    float intensity=family<0.64 ? lineArt :
                    (family<0.86 ? ellipticalArt : irregular);

    // Galaxy stars are naturally tiny at wide-field angular scales.
    // The central core remains visible even for unresolved subpixel objects.
    float compact=exp(-15.0*r*r);
    intensity=mix(compact*1.6,intensity,smoothstep(2.0,6.0,vPointPixels));
    float rim=1.0-smoothstep(0.77,1.0,r);
    intensity*=rim;
    vec3 light=vRadiance.rgb*intensity*vRadiance.a*vVisible;
    FragColor=vec4(light,1.0);
}
