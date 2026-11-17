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

// V12.3 — One unbroken, cinematic planet-to-planet camera flight.
// No selecting a new portrait / returning to wide / resting at each planet.
// World-space camera + look-at both use the same C2 quintic Hermite path.
// Velocities are shared across both sides of every knot and never zero at a
// planetary pass; both endpoint accelerations are zero, keeping transitions
// C2 even as analytic orbitPosition continues moving every planet each frame.
// Absolute film seconds are deterministic: seeking/splitting is frame exact.
const int V123_KNOTS=11;
const float v123Times[11]=float[11](
    185.0,195.0,205.0,216.0,227.0,239.0,250.0,261.0,
    274.0,290.0,299.999
);
const int v123Ids[11]=int[11](
    -1,0,1,3,4,5,6,7,-1,2,2
);
vec3 v123Knot(int k,float filmT,bool forCamera) {
    // Wide entrances exist only at the start and at the single whole-system
    // reveal; there is NO wide reset between any individual planets.
    if(k==0 || k==8)
        return forCamera ? vec3(18.0,-44.0,23.0) : vec3(0.0);

    int id=v123Ids[k];
    vec3 planet=orbitPosition(id,filmT);
    if(!forCamera) return planet*0.995;
    vec3 sunward=normalize(-planet);
    vec3 side=normalize(vec3(-sunward.y,sunward.x,0.0));
    float radius=planetBodyRadius(id);
    float distance=(id==5) ? radius*4.3+0.85 :
                             radius*1.65+0.38;
    float lateral=0.10;
    float inward=1.0;
    float elevation=0.23;
    // Mercury's former inward camera nearly touched the Sun. Move the
    // portrait laterally over the lit terminator and above the orbital plane
    // to preserve the planet while avoiding a blinding solar close pass.
    if(id==0) { distance=1.12; lateral=0.90; inward=0.20; elevation=0.50; }
    // Earth is not an inert freeze-frame: glide across the illuminated face
    // and gently get closer through the final frame.
    if(k==9) { distance=2.10; lateral=0.42; }
    if(k==10){ distance=1.35; lateral=0.67; }
    return planet+sunward*(inward*distance)+side*(lateral*distance)+
           vec3(0.0,0.0,elevation*distance);
}
vec3 v123KnotVelocity(int k,float filmT,bool forCamera) {
    if(k==0) return vec3(0.0); // match the preceding formation shot
    if(k==V123_KNOTS-1) {
        return 0.50*(v123Knot(k,filmT,forCamera)-
                     v123Knot(k-1,filmT,forCamera))/
                     (v123Times[k]-v123Times[k-1]);
    }
    vec3 velocity=0.62*(v123Knot(k+1,filmT,forCamera)-
                        v123Knot(k-1,filmT,forCamera))/
                        (v123Times[k+1]-v123Times[k-1]);
    // Equal-distance neighbour centres can cancel a finite difference and
    // make a camera appear parked. Keep a tangible lateral flyby velocity
    // for each planetary waypoint, independent of its orbital velocity.
    if(forCamera && k>0 && k<8 && length(velocity)<0.95) {
        vec3 planet=orbitPosition(v123Ids[k],filmT);
        vec3 sideways=normalize(vec3(-planet.y,planet.x,0.0));
        velocity=normalize(velocity+0.28*sideways)*0.95;
    }
    return velocity;
}
// Quintic Hermite: endpoint position/velocity matched, acceleration zero at
// each shared knot. With moving orbit centres, camera and target retain C2
// continuity because both segments evaluate the same knot functions at filmT.
vec3 v123SmoothFlight(vec3 p0,vec3 p1,vec3 v0,vec3 v1,
                      float duration,float u) {
    vec3 delta=p1-p0;
    vec3 d0=v0*duration,d1=v1*duration;
    float u2=u*u,u3=u2*u,u4=u3*u,u5=u4*u;
    return p0+d0*u+
           (10.0*delta-6.0*d0-4.0*d1)*u3+
           (-15.0*delta+8.0*d0+7.0*d1)*u4+
           (6.0*delta-3.0*d0-3.0*d1)*u5;
}
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
        return;
    }
    if(filmT<160.0) {
        camera=mix(discView,accretionView,v121Ease(138.0,160.0,filmT));
        return;
    }
    if(filmT<185.0) {
        camera=mix(accretionView,wide,v121Ease(160.0,185.0,filmT));
        return;
    }

    int segment=V123_KNOTS-2;
    for(int k=0;k<V123_KNOTS-1;++k) {
        if(filmT<v123Times[k+1]) {
            segment=k;
            break;
        }
    }
    float duration=v123Times[segment+1]-v123Times[segment];
    float u=clamp((filmT-v123Times[segment])/duration,0.0,1.0);
    camera=v123SmoothFlight(
        v123Knot(segment,filmT,true),
        v123Knot(segment+1,filmT,true),
        v123KnotVelocity(segment,filmT,true),
        v123KnotVelocity(segment+1,filmT,true),duration,u);
    target=v123SmoothFlight(
        v123Knot(segment,filmT,false),
        v123Knot(segment+1,filmT,false),
        v123KnotVelocity(segment,filmT,false),
        v123KnotVelocity(segment+1,filmT,false),duration,u);
    // A subtle elevated transfer between planets makes the full trajectory
    // pass safely above the inner solar plane instead of tunnelling through
    // the Sun. sin^4 has zero value, slope and curvature at both endpoints.
    float arc=sin(3.141592653589793*u);
    // A higher arc through the inner-system transfers avoids a near-Sun
    // graze without pausing the shot, and still eases in/out at C2 order.
    float lift=(segment<=2) ? 8.00 : 2.00;
    camera.z+=lift*arc*arc*arc*arc;
}
