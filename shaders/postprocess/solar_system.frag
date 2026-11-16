#version 330 core
// Native GLSL ray-traced Solar System finale, not pre-rendered footage.
// Orbital distance, planet diameters and orbital velocities are deliberately
// compressed/exaggerated for clarity within an extended three-minute formation arc.
// Relative order and broad color/morphology are informed by astronomy.
// No claim to real-world to-scale distances or simultaneous planet alignment.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime,uAspect,uFilmTime;

const float PI=3.141592653589793;
float hash21(vec2 p) {
    p=fract(p*vec2(123.34,345.45));
    p+=dot(p,p+34.345);
    return fract(p.x*p.y);
}
float hash31(vec3 p) {
    p=fract(p*0.1031);
    p+=dot(p,p.yzx+33.33);
    return fract((p.x+p.y)*p.z);
}
float noise3(vec3 p) {
    vec3 i=floor(p),f=fract(p);
    f=f*f*(3.0-2.0*f);
    float a=mix(hash31(i),hash31(i+vec3(1,0,0)),f.x);
    float b=mix(hash31(i+vec3(0,1,0)),hash31(i+vec3(1,1,0)),f.x);
    float c=mix(hash31(i+vec3(0,0,1)),hash31(i+vec3(1,0,1)),f.x);
    float d=mix(hash31(i+vec3(0,1,1)),hash31(i+vec3(1,1,1)),f.x);
    return mix(mix(a,b,f.y),mix(c,d,f.y),f.z);
}
float fbm3(vec3 p) {
    return 0.56*noise3(p)+0.27*noise3(p*2.17+1.3)+
           0.12*noise3(p*4.23-3.1)+0.05*noise3(p*8.27+7.2);
}
float planetOrbitRadius(int i) {
    if(i==0)return 2.65;  // Mercury
    if(i==1)return 4.10;  // Venus
    if(i==2)return 5.80;  // Earth
    if(i==3)return 7.30;  // Mars
    if(i==4)return 10.0;  // Jupiter
    if(i==5)return 13.35; // Saturn
    if(i==6)return 17.0;  // Uranus
    return 20.30;         // Neptune
}
float planetBodyRadius(int i) {
    if(i==0)return 0.24;
    if(i==1)return 0.42;
    if(i==2)return 0.51;
    if(i==3)return 0.33;
    if(i==4)return 1.21;
    if(i==5)return 1.00;
    if(i==6)return 0.72;
    return 0.70;
}
vec3 orbitPosition(int i,float t) {
    float elapsed=t-118.0;
    // Artistically condensed orbital periods; all bodies remain in 3D world
    // space and move continuously around a single central Sun.
    float angularRate=0.004+0.0007*float(7-i);
    float phase=0.43+2.39996*float(i)+elapsed*angularRate;
    float r=planetOrbitRadius(i);
    return vec3(r*cos(phase),r*sin(phase),
                0.16*r*sin(phase*0.41+float(i)*0.75)*0.08);
}
float sphereIntersect(vec3 origin,vec3 dir,vec3 center,float radius) {
    vec3 oc=origin-center;
    float b=dot(oc,dir);
    float c=dot(oc,oc)-radius*radius;
    float det=b*b-c;
    if(det<0.0)return 1.0e20;
    float q=sqrt(det);
    float t=-b-q;
    if(t<0.03)t=-b+q;
    return t>0.03 ? t : 1.0e20;
}
// Recognizable terrestrial landmasses from smoothly distorted, manually
// art-directed analytic continental masses (not an actual NASA Earth map).
// Angular longitude wrapping prevents a fake seam in the texture.
float v4Continent(vec2 ll,vec2 center,vec2 width) {
    float delta=atan(sin(ll.x-center.x),cos(ll.x-center.x));
    vec2 p=vec2(delta/width.x,(ll.y-center.y)/width.y);
    return exp(-dot(p,p));
}
vec3 planetAlbedo(int id,vec3 n,float time) {
    vec3 rot=vec3(cos(time*0.023),sin(time*0.023),0.0);
    vec3 q=vec3(n.x*rot.x-n.y*rot.y,n.x*rot.y+n.y*rot.x,n.z);
    float var=fbm3(q*7.5+float(id)*13.7);
    if(id==0) { // Mercury — cratered charcoal rock
        float rock=noise3(q*26.0+vec3(6.0));
        float craters=1.0-0.45*exp(-pow((rock-0.49)*14.0,2.0))+0.15*exp(-pow((rock-0.63)*20.0,2.0));
        return mix(vec3(0.22,0.23,0.25),vec3(0.47,0.43,0.39),
                   0.38+0.62*var)*(0.78+0.31*craters);
    }
    if(id==1) { // Venus — dense pale sulfuric cloud deck
        float strata=fbm3(q*4.3+vec3(time*0.004,0.0,3.0));
        return mix(vec3(0.73,0.57,0.35),vec3(0.98,0.88,0.67),
                   smoothstep(0.30,0.77,strata));
    }
    if(id==2) { // Earth — recognisable oceans, continents, ice and clouds
        // Smooth, procedural geography: North/South America, Eurasia,
        // Africa, Arabia, Australasia and Antarctica; *not* a map texture.
        vec2 ll=vec2(atan(q.y,q.x),asin(clamp(q.z,-1.0,1.0)));
        float mass=0.0;
        mass=max(mass,v4Continent(ll,vec2(-1.75,0.71),vec2(0.65,0.43)));
        mass=max(mass,v4Continent(ll,vec2(-1.19,-0.28),vec2(0.33,0.63)));
        mass=max(mass,v4Continent(ll,vec2(1.04,0.74),vec2(1.35,0.43)));
        mass=max(mass,v4Continent(ll,vec2(0.36,0.07),vec2(0.46,0.68)));
        mass=max(mass,v4Continent(ll,vec2(2.37,-0.47),vec2(0.40,0.27)));
        mass=max(mass,v4Continent(ll,vec2(0.69,0.44),vec2(0.28,0.19)));
        float corrugation=fbm3(q*10.0+vec3(3.0,5.5,7.7));
        float coastal=smoothstep(0.39,0.53,mass+
                                 0.17*(corrugation-0.5));
        float shallow=smoothstep(0.29,0.40,mass+
                                 0.17*(corrugation-0.5));
        vec3 deepWater=vec3(0.008,0.045,0.165);
        vec3 coastalWater=vec3(0.035,0.21,0.36);
        vec3 ocean=mix(deepWater,coastalWater,
                       0.24+0.75*shallow);
        vec3 vegetation=mix(vec3(0.075,0.20,0.09),
                            vec3(0.19,0.27,0.095),corrugation);
        float arid=smoothstep(0.15,0.55,q.z)*
                   smoothstep(0.33,0.62,fbm3(q*5.1+vec3(14.7)));
        vegetation=mix(vegetation,vec3(0.47,0.35,0.17),arid*0.55);
        vec3 globe=mix(ocean,vegetation,coastal);
        float polar=smoothstep(0.75,0.94,abs(q.z));
        globe=mix(globe,vec3(0.83,0.90,0.96),polar);
        // Low-to-high latitude swirling, partially transparent cloud sheets.
        float clouds=fbm3(q*10.5+vec3(0.0,time*0.014,2.0));
        float cloudEdges=fbm3(q*22.0+vec3(time*0.003,4.0,5.3));
        float cloudMask=smoothstep(0.60,0.75,clouds+
                                   0.19*(cloudEdges-0.5));
        return mix(globe,vec3(0.87,0.94,1.04),cloudMask*0.78);
    }
    if(id==3) { // Mars — rust deserts and volcanic highlands
        return mix(vec3(0.39,0.13,0.075),vec3(0.83,0.37,0.18),
                   smoothstep(0.25,0.77,var))*(0.80+0.20*noise3(q*32.0));
    }
    if(id==4) { // Jupiter — turbulent latitudinal bands
        float turbulence=fbm3(vec3(q.xy*12.0,q.z*28.0)+vec3(time*0.008,0.0,0.0));
        float bands=sin(q.z*47.0+5.5*turbulence+sin(q.z*16.0)*0.6);
        vec3 tanColor=vec3(0.82,0.57,0.34);
        vec3 bright=vec3(0.97,0.86,0.69);
        vec3 a=mix(tanColor,bright,smoothstep(-0.60,0.72,bands));
        float storm=exp(-((n.z-0.21)*6.0)*((n.z-0.21)*6.0))*
                    exp(-pow(atan(q.y,q.x)*2.0,2.0));
        return mix(a,vec3(0.76,0.28,0.17),0.68*storm);
    }
    if(id==5) { // Saturn — creamy bands, rings are separate geometry
        return mix(vec3(0.56,0.44,0.26),vec3(0.95,0.83,0.59),
                   0.5+0.5*sin(n.z*32.0+var*1.7));
    }
    if(id==6) { // Uranus — muted blue-cyan
        return mix(vec3(0.31,0.67,0.73),vec3(0.65,0.89,0.87),
                   0.4+0.4*n.z+0.2*var);
    }
    // Neptune — deep blue cloud bands
    return mix(vec3(0.025,0.12,0.56),vec3(0.18,0.41,0.92),
               0.50+0.12*sin(q.z*21.0+var*5.0)+0.15*var);
}
float starLight(vec3 dir) {
    vec2 sky=vec2(atan(dir.y,dir.x)*170.0,
                  asin(clamp(dir.z,-1.0,1.0))*170.0);
    vec2 grid=floor(sky), f=fract(sky);
    float seed=hash21(grid);
    float star=step(0.975,seed);
    vec2 center=vec2(hash21(grid+9.1),hash21(grid-5.6));
    float d=length(f-center);
    return star*exp(-175.0*d*d)*
           (0.38+1.42*hash21(grid+vec2(2.5,8.1)));
}
#include "protoplanetary.glsl"

void main() {
    float t=clamp(uTime,259.0,299.999);
    float filmT=clamp(uFilmTime,0.0,299.999);
    vec3 earth=orbitPosition(2,filmT);
    vec3 camera,target;
    v121Camera(filmT,earth,orbitPosition(4,filmT),camera,target);
    vec3 forward=normalize(target-camera);
    vec3 right=normalize(cross(forward,vec3(0.0,0.0,1.0)));
    vec3 up=normalize(cross(right,forward));
    vec2 xy=TexCoords*2.0-1.0;
    vec3 ray=normalize(forward+xy.x*uAspect*0.62*right+
                        xy.y*0.62*up);

    float star=starLight(ray);
    vec3 color=vec3(0.0005,0.0008,0.0018)+
               vec3(0.64,0.78,1.0)*star*0.60;
    // Faint original, stationary galactic dust in directional space.
    float nebula=fbm3(ray*9.0+vec3(11.0,3.0,1.7));
    color+=vec3(0.006,0.010,0.020)*
           pow(smoothstep(0.54,0.78,nebula),2.0);
    // The source-linked conceptual change: let a real 3D molecular-cloud
    // visualization precede an orbiting dust disc and protoplanets.
    // Cloud and disc are one attenuating foreground volume, composited below.

    float closest=1.0e20;
    int object=-1;
    vec3 objectCenter=vec3(0.0);
    float sunRadius=mix(0.62,1.42,v121Ease(118.0,145.0,filmT));
    float objectRadius=sunRadius;
    float sunHit=sphereIntersect(camera,ray,vec3(0.0),sunRadius);
    if(sunHit<closest) {
        closest=sunHit;object=8;objectCenter=vec3(0);objectRadius=sunRadius;
    }
    for(int i=0;i<8;++i) {
        vec3 p=orbitPosition(i,filmT);
        float development=v4PlanetReveal(t,i);
        // Growth affects true ray/sphere geometry, not a screen-scale icon.
        // Embryos remain small, warm and dusty before the mature disc clears.
        if(development<0.002) continue;
        float radius=planetBodyRadius(i)*pow(development,0.72);
        float distance=sphereIntersect(camera,ray,p,radius);
        if(distance<closest) {
            closest=distance;object=i;objectCenter=p;objectRadius=radius;
        }
    }

    // V12: explicit, world-space planetesimal / embryo growth during the
    // newly extended formation chapter. These analytic bodies are an
    // illustration of accretion, not an N-body collision simulator.
    float debrisWindow=v121Ease(167.0,190.0,filmT)*(1.0-v121Ease(232.0,257.0,filmT));
    if(debrisWindow>0.0001) {
        for(int i=0;i<24;++i) {
            int parent=i%8;
            float id=float(i),growth=v121Ease(180.0,239.0,filmT);
            float angle=id*2.39996323+filmT*(0.11/(1.0+id*0.08));
            float orbit=mix(1.7,0.22,growth)*(0.7+0.3*hash21(vec2(id,4.2)));
            vec3 center=orbitPosition(parent,filmT)+
                vec3(orbit*cos(angle),orbit*sin(angle),0.12*orbit*sin(angle*0.7+id));
            float radius=(0.035+0.10*hash21(vec2(id+11.7,7.3)))*
                mix(0.15,1.0,growth)*debrisWindow;
            float hit=sphereIntersect(camera,ray,center,radius);
            if(hit<closest) {closest=hit;object=9;objectCenter=center;objectRadius=radius;}
        }
    }

    if(object>=0) {
        vec3 surface=camera+ray*closest;
        vec3 n=normalize(surface-objectCenter);
        if(object==9) {
            // Small accreting bodies: muted rock with warm impact-like glow.
            float lit=max(dot(n,normalize(-surface)),0.0);
            float mottled=fbm3(surface*11.0+vec3(2.7,4.1,6.2));
            color=mix(vec3(0.25,0.18,0.15),vec3(0.77,0.43,0.19),
                      0.35+0.65*mottled)*(0.15+0.85*lit);
        } else if(object==8) {
            float granule=fbm3(n*13.0+vec3(filmT*0.007,2.0,4.0));
            float hot=0.35+1.0*smoothstep(0.25,0.75,granule);
            float limb=0.50+0.50*sqrt(max(dot(n,-ray),0.0));
            float spots=smoothstep(0.66,0.78,noise3(n*6.0+vec3(1.7,4.2,filmT*0.003)));
            float ignition=v121Ease(120.0,145.0,filmT);
            vec3 protostar=vec3(0.52,0.19,0.065)*(0.72+0.45*granule);
            vec3 mature=vec3(1.8,1.35,0.94)*hot*limb*(1.0-0.50*spots);
            color=mix(protostar,mature,ignition);
        } else {
            vec3 sunDir=normalize(-surface);
            float lambert=max(dot(n,sunDir),0.0);
            float day=0.018+0.982*pow(lambert,0.85);
            vec3 base=planetAlbedo(object,n,t);
            float developed=v4PlanetReveal(t,object);
            base=v4YoungPlanetColor(base,developed,n,t);
            color=base*day;
            // Tiny atmosphere scatter/rim on Earth and the ice giants.
            if(object==2 || object>=6) {
                float rim=pow(1.0-max(0.0,dot(n,-ray)),4.5);
                color+=vec3(0.075,0.24,0.60)*rim*(0.05+0.45*lambert);
                if(object==2) {
                    vec3 halfVector=normalize(sunDir-ray);
                    float landNoise=fbm3(n*7.5+vec3(0.0,2.0,4.0));
                    color+=vec3(0.35,0.44,0.50)*pow(max(dot(n,halfVector),0.0),90.0)*lambert*(1.0-landNoise);
                }
            }
        }
    }

    // Saturn's real ray-plane intersection: ring may obscure the planet or
    // sit behind it. Fragments are not a flat always-on circular HUD icon.
    vec3 saturn=orbitPosition(5,filmT);
    vec3 ringNormal=normalize(vec3(0.22,0.25,0.94));
    float denom=dot(ray,ringNormal);
    if(abs(denom)>0.001) {
        float rt=dot(saturn-camera,ringNormal)/denom;
        if(rt>0.02 && rt<closest) {
            vec3 hit=camera+ray*rt-saturn;
            float radius=length(hit);
            float sr=planetBodyRadius(5);
            if(radius>1.27*sr && radius<2.14*sr) {
                float frac=radius/sr;
                float strip=0.44+0.25*sin(frac*61.0)+
                            0.15*sin(frac*145.0);
                float edge=smoothstep(1.27,1.36,frac)*
                           (1.0-smoothstep(1.96,2.14,frac));
                float light=abs(dot(ringNormal,normalize(-saturn)));
                float shadow=sphereIntersect(camera+ray*rt,normalize(-saturn),saturn,sr)<1.0e19?0.18:1.0;
                float gap=1.0-0.88*smoothstep(1.71,1.74,frac)*(1.0-smoothstep(1.79,1.82,frac));
                vec3 tint=mix(vec3(0.36,0.25,0.15),
                              vec3(0.84,0.71,0.46),strip);
                float ringsBorn=v121Ease(239.0,266.0,filmT);
                color=mix(color,tint*(0.12+0.88*light)*shadow,
                          edge*gap*(0.42+0.40*strip)*ringsBorn);
            }
        }
    }

    // Real perspective intersections with a rotating accretion disc in
    // three depth layers. Dust cannot shine through an opaque foreground
    // planet or Sun; it remains tied to the world, not the screen.
    vec4 medium=v121Medium(camera,ray,filmT,closest);
    color=color*(1.0-medium.a)+medium.rgb;

    // Sun's layered corona and warm lens glow, preserving deep negative
    // space. Glow does not pretend to depict actual sound in space.
    vec3 toSun=-camera;
    float angularRadius=sunRadius/max(length(toSun),sunRadius);
    float angularDistance=length(cross(normalize(toSun),ray));
    float halo=0.06*exp(-angularDistance/max(angularRadius*2.5,0.001))+
               0.10*exp(-angularDistance/max(angularRadius*0.85,0.001));
    float glowMask=(object<0 && dot(toSun,ray)>0.0) ? 1.0 : 0.0;
    float sunIgnition=v121Ease(120.0,145.0,filmT);
    color+=vec3(1.0,0.40,0.10)*halo*glowMask*(1.0-medium.a)*(0.18+0.82*sunIgnition);

    // User asked for the solar system at the very end. Crossfade from the
    // dense-galaxy sequence without abruptly replacing a beautiful shot.
    float cover=v121Ease(110.0,118.0,filmT);
    FragColor=vec4(max(color,vec3(0.0)),cover);
}
