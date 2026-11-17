// V12.1: deterministic, art-directed solar-nebula evolution in WORLD SPACE.
// Analytic accretion illustration; no N-body, SPH or collision solver.
// Included after the shared noise, orbital and ray/sphere functions.
float v121Ease(float a,float b,float t) {
    float x=clamp((t-a)/(b-a),0.0,1.0);
    return x*x*x*(x*(x*6.0-15.0)+10.0);
}
float v4PlanetReveal(float ignoredTime,int index) {
    float delay=float(index)*0.65;
    return v121Ease(148.0+delay,184.5+delay,uFilmTime);
}
vec3 v4YoungPlanetColor(vec3 established,float development,vec3 n,float time) {
    float scars=fbm3(n*14.0+vec3(2.1,4.1,9.0));
    float cooling=v121Ease(153.0,188.0,uFilmTime);
    vec3 rock=mix(vec3(0.17,0.085,0.045),vec3(0.49,0.25,0.11),scars);
    rock+=vec3(0.58,0.13,0.025)*smoothstep(0.57,0.75,scars)*(1.0-cooling);
    return mix(rock,established,cooling);
}

// A single ellipsoidal medium collapses vertically into a finite-thickness
// disc. Ray intervals adapt to its thickness, avoiding screen-space sheets.
// Fixed midpoint samples and advected continuous noise prevent random flicker.
vec4 v121Medium(vec3 ro,vec3 rd,float filmT,float opaqueDepth) {
    // Lecturer revision: the dusty formation arc clears before seven planet portraits.
    float clear=1.0-v121Ease(163.0,188.0,filmT);
    if(clear<0.00001) return vec4(0.0);
    float flatten=v121Ease(119.0,146.0,filmT);
    vec3 extent=vec3(26.0,26.0,mix(15.0,1.8,flatten));
    vec3 o=ro/extent,d=rd/extent;
    float a=dot(d,d),b=dot(o,d),c=dot(o,o)-1.0;
    float det=b*b-a*c;
    if(det<=0.0) return vec4(0.0);
    float nearT=max(0.02,(-b-sqrt(det))/a);
    float farT=min(opaqueDepth,(-b+sqrt(det))/a);
    if(farT<=nearT) return vec4(0.0);
    const int SAMPLES=32;
    float stepT=(farT-nearT)/float(SAMPLES);
    float trans=1.0;
    vec3 light=vec3(0.0);
    float ignition=v121Ease(119.0,138.0,filmT);
    for(int j=0;j<SAMPLES;++j) {
        vec3 p=ro+rd*(nearT+(float(j)+0.5)*stepT);
        float r=length(p.xy),theta=atan(p.y,p.x);
        float angle=theta-(filmT-118.0)*0.16/pow(1.0+r*0.24,1.5);
        vec3 advected=vec3(r*cos(angle),r*sin(angle),p.z);
        advected.z+=0.32*sin(r*0.4+angle*2.0+filmT*0.025);
        advected.xy*=mix(0.88,1.0,v121Ease(110.0,145.0,filmT));
        float broad=fbm3(advected*0.19+vec3(2.8,7.1,3.4));
        float fine=noise3(advected*1.15+vec3(9.7,1.2,8.6));
        float boundary=1.0-smoothstep(0.72,1.0,length(p/extent));
        float folds=exp(-70.0*(broad-0.54)*(broad-0.54));
        float cloud=(0.30*pow(smoothstep(0.34,0.76,broad),2.0)+
            0.70*folds*smoothstep(0.38,0.78,fine))*boundary;
        float lane=0.48+0.52*smoothstep(-0.45,0.6,
                       sin(r*1.3+3.5*broad));
        float spiral=0.76+0.24*sin(2.0*angle-r*0.37+2.0*broad);
        float vertical=exp(-p.z*p.z/(0.32+0.014*r*r));
        float disc=boundary*vertical*lane*spiral*(0.3+0.7*broad);
        disc*=smoothstep(1.35,2.5,r);
        float density=mix(cloud*0.13,disc*0.40,flatten)*(0.80+0.20*fine);
        // Same eight world-space centres become the solid embryos below.
        float seeds=v121Ease(132.0,159.0,filmT)*(1.0-v121Ease(174.0,190.0,filmT));
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

// V12.2 — Planet portraits. Keep a common wide, star-centred camera between
// every close-up. Each approach uses C2 quintic ease and retracts to that same
// wide camera, so changing the planet index cannot create a cut or a jump.
// The same orbitPosition(index, filmT) drives both the visible planet and camera.
void v121Camera(float filmT,vec3 earth,vec3 jupiter,
                out vec3 camera,out vec3 target) {
    vec3 farCloud=vec3(10.0,-56.0,28.0);
    vec3 discView=vec3(10.0,-36.0,17.0);
    vec3 accretionView=vec3(5.0,-22.0,10.0);
    vec3 wide=vec3(18.0,-44.0,23.0);
    camera=farCloud;
    target=vec3(0.0);

    if(filmT<138.0) {
        camera=mix(farCloud,discView,v121Ease(110.0,138.0,filmT));
    } else if(filmT<160.0) {
        camera=mix(discView,accretionView,v121Ease(138.0,160.0,filmT));
    } else if(filmT<185.0) {
        camera=mix(accretionView,wide,v121Ease(160.0,185.0,filmT));
    } else if(filmT<271.0) {
        // Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune.
        // Earth retains its 17-second hero close-up at the end.
        int selected=0;
        float begin=185.0, finish=197.0;
        if(filmT>=197.0) {selected=1;begin=197.0;finish=209.0;}
        if(filmT>=209.0) {selected=3;begin=209.0;finish=221.0;}
        if(filmT>=221.0) {selected=4;begin=221.0;finish=234.0;}
        if(filmT>=234.0) {selected=5;begin=234.0;finish=247.0;}
        if(filmT>=247.0) {selected=6;begin=247.0;finish=259.0;}
        if(filmT>=259.0) {selected=7;begin=259.0;finish=271.0;}
        vec3 planet=orbitPosition(selected,filmT);
        vec3 sunward=normalize(-planet);
        vec3 side=normalize(vec3(-sunward.y,sunward.x,0.0));
        float radius=planetBodyRadius(selected);
        // Saturn's complete rings must fit, not just the planet sphere.
        float viewingDistance=(selected==5) ? radius*4.3+0.85 :
                              radius*1.65+0.38;
        vec3 portraitCamera=planet+sunward*viewingDistance+
                            side*(0.10*viewingDistance)+
                            vec3(0.0,0.0,0.23*viewingDistance);
        float approach=v121Ease(begin,begin+3.5,filmT);
        float depart=1.0-v121Ease(finish-3.0,finish,filmT);
        float focus=approach*depart;
        camera=mix(wide,portraitCamera,focus);
        // A small elevation arc makes the move feel cinematic, not a cut.
        camera.z+=3.0*sin(3.141592653589793*focus);
        target=mix(vec3(0.0),planet*0.995,focus);
    } else if(filmT<283.0) {
        // The uninterrupted full system reveal returns to precisely wide.
        float phase=v121Ease(271.0,283.0,filmT);
        camera=wide+vec3(-3.0,3.0,1.2)*
                      sin(3.141592653589793*phase)*
                      sin(3.141592653589793*phase);
    } else {
        // Preserve the V12.1 illuminated Earth composition and Saturn separation.
        vec3 closeEarth=earth+normalize(-earth)*0.95+vec3(-1.0,-0.5,1.0);
        float focus=v121Ease(283.0,300.0,filmT);
        camera=mix(wide,closeEarth,focus);
        target=mix(vec3(0.0),earth*0.995,focus);
    }
}
