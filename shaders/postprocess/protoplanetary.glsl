// V12.1: deterministic, art-directed solar-nebula evolution in WORLD SPACE.
// Analytic accretion illustration; no N-body, SPH or collision solver.
// Included after the shared noise, orbital and ray/sphere functions.
float v121Ease(float a,float b,float t) {
    float x=clamp((t-a)/(b-a),0.0,1.0);
    return x*x*x*(x*(x*6.0-15.0)+10.0);
}
float v4PlanetReveal(float ignoredTime,int index) {
    float delay=float(index)*0.65;
    return v121Ease(183.0+delay,252.0+delay,uFilmTime);
}
vec3 v4YoungPlanetColor(vec3 established,float development,vec3 n,float time) {
    float scars=fbm3(n*14.0+vec3(2.1,4.1,9.0));
    float cooling=v121Ease(213.0,259.0,uFilmTime);
    vec3 rock=mix(vec3(0.17,0.085,0.045),vec3(0.49,0.25,0.11),scars);
    rock+=vec3(0.58,0.13,0.025)*smoothstep(0.57,0.75,scars)*(1.0-cooling);
    return mix(rock,established,cooling);
}

// A single ellipsoidal medium collapses vertically into a finite-thickness
// disc. Ray intervals adapt to its thickness, avoiding screen-space sheets.
// Fixed midpoint samples and advected continuous noise prevent random flicker.
vec4 v121Medium(vec3 ro,vec3 rd,float filmT,float opaqueDepth) {
    float clear=1.0-v121Ease(238.0,269.0,filmT);
    if(clear<0.00001) return vec4(0.0);
    float flatten=v121Ease(125.0,178.0,filmT);
    vec3 extent=vec3(26.0,26.0,mix(15.0,1.8,flatten));
    vec3 o=ro/extent,d=rd/extent;
    float a=dot(d,d),b=dot(o,d),c=dot(o,o)-1.0;
    float det=b*b-a*c;
    if(det<=0.0) return vec4(0.0);
    float nearT=max(0.02,(-b-sqrt(det))/a);
    float farT=min(opaqueDepth,(-b+sqrt(det))/a);
    if(farT<=nearT) return vec4(0.0);
    const int SAMPLES=24;
    float stepT=(farT-nearT)/float(SAMPLES);
    float trans=1.0;
    vec3 light=vec3(0.0);
    float ignition=v121Ease(120.0,145.0,filmT);
    for(int j=0;j<SAMPLES;++j) {
        vec3 p=ro+rd*(nearT+(float(j)+0.5)*stepT);
        float r=length(p.xy),theta=atan(p.y,p.x);
        float angle=theta-(filmT-118.0)*0.16/pow(1.0+r*0.24,1.5);
        vec3 advected=vec3(r*cos(angle),r*sin(angle),p.z);
        float broad=fbm3(advected*0.19+vec3(2.8,7.1,3.4));
        float fine=noise3(advected*1.15+vec3(9.7,1.2,8.6));
        float boundary=1.0-smoothstep(0.72,1.0,length(p/extent));
        float cloud=pow(smoothstep(0.25,0.76,broad),1.5)*boundary;
        float lane=0.32+0.68*smoothstep(-0.45,0.6,
                       sin(r*2.0+1.7*broad));
        float spiral=0.76+0.24*sin(2.0*angle-r*0.37+2.0*broad);
        float vertical=exp(-p.z*p.z/(0.32+0.014*r*r));
        float disc=boundary*vertical*lane*spiral*(0.3+0.7*broad);
        disc*=smoothstep(1.35,2.5,r);
        float density=mix(cloud*0.13,disc*0.40,flatten)*(0.80+0.20*fine);
        // Same eight world-space centres become the solid embryos below.
        float seeds=v121Ease(155.0,193.0,filmT)*(1.0-v121Ease(239.0,262.0,filmT));
        if(seeds>0.001) {
            for(int k=0;k<8;++k) {
                float development=v4PlanetReveal(0.0,k);
                vec3 delta=p-orbitPosition(k,filmT);
                float width=mix(1.25,planetBodyRadius(k)*1.12,development);
                density+=seeds*0.21*exp(-dot(delta,delta)/(width*width));
            }
        }
        density*=clear;
        float sunDistance=length(p);
        float illumination=(0.25+0.75*ignition)/(1.0+0.055*sunDistance*sunDistance);
        float selfShadow=exp(-density*min(sunDistance,12.0)*1.8);
        vec3 scattering=vec3(0.055,0.075,0.105)+
            vec3(1.85,1.05,0.43)*illumination*(0.35+0.65*selfShadow);
        float alpha=1.0-exp(-density*stepT);
        light+=trans*scattering*alpha;
        trans*=1.0-alpha;
        if(trans<0.012) break;
    }
    return vec4(light,1.0-trans);
}

// C2 ease between deliberate compositions. Absolute film time drives both
// camera and orbital objects, independent of capture chunks and mapped epochs.
void v121Camera(float filmT,vec3 earth,vec3 jupiter,out vec3 camera,out vec3 target) {
    vec3 a=vec3(10.0,-56.0,28.0),b=vec3(10.0,-36.0,17.0);
    vec3 ta=vec3(0.0),tb=vec3(0.0);
    float lo=118.0,hi=145.0;
    if(filmT>=145.0) {a=b;b=vec3(5.0,-22.0,10.0);lo=145.0;hi=180.0;}
    if(filmT>=180.0) {a=b;b=jupiter+vec3(5.0,-12.0,6.0);tb=jupiter*0.85;lo=180.0;hi=215.0;}
    if(filmT>=215.0) {a=jupiter+vec3(5.0,-12.0,6.0);b=vec3(10.0,-32.0,18.0);ta=jupiter*0.85;tb=vec3(0.0);lo=215.0;hi=245.0;}
    if(filmT>=245.0) {a=b;b=vec3(18.0,-44.0,23.0);ta=vec3(0.0);lo=245.0;hi=265.0;}
    if(filmT>=265.0) {a=vec3(18.0,-44.0,23.0);b=a;ta=vec3(0.0);lo=265.0;hi=283.0;}
    if(filmT>=283.0) {a=vec3(18.0,-44.0,23.0);b=earth+vec3(0.70,-2.8,1.35);ta=vec3(0.0);tb=earth*0.995;lo=283.0;hi=300.0;}
    float e=v121Ease(lo,hi,filmT);
    camera=mix(a,b,e);target=mix(ta,tb,e);
}
