#version 330 core
// Native GLSL ray-traced Solar System finale, not pre-rendered footage.
// Orbital distance, planet diameters and orbital velocities are deliberately
// compressed/exaggerated for educational clarity within a 40-second shot.
// Relative order and broad color/morphology are informed by astronomy.
// No claim to real-world to-scale distances or simultaneous planet alignment.
in vec2 TexCoords;
out vec4 FragColor;
uniform float uTime,uAspect;

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
    float elapsed=t-260.0;
    // Artistically condensed orbital periods; all bodies remain in 3D world
    // space and move continuously around a single central Sun.
    float angularRate=0.024+0.003*float(7-i);
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
vec3 planetAlbedo(int id,vec3 n,float time) {
    vec3 rot=vec3(cos(time*0.023),sin(time*0.023),0.0);
    vec3 q=vec3(n.x*rot.x-n.y*rot.y,n.x*rot.y+n.y*rot.x,n.z);
    float var=fbm3(q*7.5+float(id)*13.7);
    if(id==0) { // Mercury — cratered charcoal rock
        float craters=noise3(q*26.0+vec3(6.0));
        return mix(vec3(0.22,0.23,0.25),vec3(0.47,0.43,0.39),
                   0.38+0.62*var)*(0.78+0.31*craters);
    }
    if(id==1) { // Venus — dense pale sulfuric cloud deck
        float strata=fbm3(q*4.3+vec3(time*0.004,0.0,3.0));
        return mix(vec3(0.73,0.57,0.35),vec3(0.98,0.88,0.67),
                   smoothstep(0.30,0.77,strata));
    }
    if(id==2) { // Earth — dark ocean, irregular continents, cloud systems
        float land=fbm3(q*3.8+vec3(4.0,11.0,0.6));
        land+=0.14*(fbm3(q*13.3+vec3(2.7))-0.5);
        vec3 ocean=mix(vec3(0.012,0.055,0.23),
                       vec3(0.029,0.26,0.45),
                       smoothstep(0.18,0.79,var));
        vec3 forest=mix(vec3(0.16,0.21,0.065),
                        vec3(0.36,0.31,0.15),var);
        float icy=smoothstep(0.76,0.98,abs(n.z));
        vec3 globe=mix(ocean,forest,smoothstep(0.49,0.56,land));
        globe=mix(globe,vec3(0.84,0.88,0.89),icy);
        float clouds=fbm3(q*12.0+vec3(time*0.009,4.0,12.0));
        float cloudMask=smoothstep(0.59,0.71,clouds);
        return mix(globe,vec3(0.91,0.94,0.98),cloudMask*0.66);
    }
    if(id==3) { // Mars — rust deserts and volcanic highlands
        return mix(vec3(0.39,0.13,0.075),vec3(0.83,0.37,0.18),
                   smoothstep(0.25,0.77,var));
    }
    if(id==4) { // Jupiter — turbulent latitudinal bands
        float bands=sin(n.z*47.0+3.9*var+sin(n.z*16.0)*0.6);
        vec3 tanColor=vec3(0.82,0.57,0.34);
        vec3 bright=vec3(0.97,0.86,0.69);
        vec3 a=mix(tanColor,bright,smoothstep(-0.60,0.72,bands));
        float storm=exp(-pow((n.z-0.21)*6.0,2.0))*
                    exp(-pow(atan(n.y,n.x)*2.0,2.0));
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
               0.55+0.35*sin(n.z*21.0+var*5.0));
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
void main() {
    float t=clamp(uTime,260.0,299.999);
    float progress=clamp((t-260.0)/40.0,0.0,1.0);
    float dolly=smoothstep(0.0,1.0,progress);
    vec3 earth=orbitPosition(2,t);
    vec3 wideCamera=vec3(10.0+8.0*dolly,-56.0+12.0*dolly,28.0-9.0*dolly);
    // Final 7 seconds: purposeful fly-in toward Earth, after an extended
    // wide shot showing all eight orbiting planets around the Sun.
    float fly=smoothstep(0.79,0.99,progress);
    vec3 closeCamera=earth+vec3(2.4,-8.9,4.2);
    vec3 camera=mix(wideCamera,closeCamera,fly);
    vec3 target=mix(vec3(0.0),earth,fly*0.92);
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

    float closest=1.0e20;
    int object=-1;
    vec3 objectCenter=vec3(0.0);
    float objectRadius=1.42;
    float sunHit=sphereIntersect(camera,ray,vec3(0.0),1.42);
    if(sunHit<closest) {
        closest=sunHit;object=8;objectCenter=vec3(0);objectRadius=1.42;
    }
    for(int i=0;i<8;++i) {
        vec3 p=orbitPosition(i,t);
        float radius=planetBodyRadius(i);
        float distance=sphereIntersect(camera,ray,p,radius);
        if(distance<closest) {
            closest=distance;object=i;objectCenter=p;objectRadius=radius;
        }
    }

    if(object>=0) {
        vec3 surface=camera+ray*closest;
        vec3 n=normalize(surface-objectCenter);
        if(object==8) {
            float granule=fbm3(surface*7.5+vec3(t*0.02));
            float hot=0.77+0.33*granule;
            color=vec3(2.7,1.68,0.63)*hot;
            color+=vec3(0.62,0.35,0.18)*max(0.0,n.z)*0.3;
        } else {
            vec3 sunDir=normalize(-surface);
            float lambert=max(dot(n,sunDir),0.0);
            float day=0.05+0.95*pow(lambert,0.77);
            vec3 base=planetAlbedo(object,n,t);
            color=base*day;
            // Tiny atmosphere scatter/rim on Earth and the ice giants.
            if(object==2 || object>=6) {
                float rim=pow(1.0-max(0.0,dot(n,-ray)),4.5);
                color+=vec3(0.10,0.24,0.54)*rim*0.36;
            }
        }
    }

    // Saturn's real ray-plane intersection: ring may obscure the planet or
    // sit behind it. Fragments are not a flat always-on circular HUD icon.
    vec3 saturn=orbitPosition(5,t);
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
                float light=max(dot(ringNormal,normalize(-saturn)),0.07);
                vec3 tint=mix(vec3(0.36,0.25,0.15),
                              vec3(0.84,0.71,0.46),strip);
                color=mix(color,tint*(0.17+0.76*light),edge*0.9);
            }
        }
    }

    // Sun's layered corona and warm lens glow, preserving deep negative
    // space. Glow does not pretend to depict actual sound in space.
    vec3 toSun=-camera;
    float rayDist=length(cross(toSun,ray));
    float halo=exp(-rayDist*0.12)*0.075+
               exp(-rayDist*0.44)*0.17;
    float glowMask=(object==8) ? 0.0 : 1.0;
    color+=vec3(1.0,0.40,0.10)*halo*glowMask;

    // User asked for the solar system at the very end. Crossfade from the
    // dense-galaxy sequence without abruptly replacing a beautiful shot.
    float cover=smoothstep(259.0,268.0,uTime);
    FragColor=vec4(max(color,vec3(0.0)),cover);
}
