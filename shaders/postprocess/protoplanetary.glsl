// NASA / Bob Stanford-inspired scientific visual *interpretation* of the
// Solar Nebular Hypothesis. World-space, temporally coherent gas/dust shading,
// NOT a physical SPH, N-body or collisional accretion simulation.
// Included by solar_system.frag after noise3(), fbm3() and hash21().

float safeGaussian(float x,float width) {
    float q=x/max(width,0.001);
    return exp(-q*q);
}

float v4SolarFormationProgress(float t) {
    return smoothstep(274.0,291.5,t);
}

// The early dusty molecular cloud resolves into a flattened circumsun disk.
// Evaluated in world-space, so the cloud and arms do not track the screen.
vec3 v4NebularEnvelope(vec3 origin,vec3 dir,float t) {
    float arrival=smoothstep(259.0,263.0,t);
    float departure=1.0-smoothstep(274.0,285.0,t);
    float active=arrival*departure;
    if(active<0.0001) return vec3(0.0);
    float nearPoint=max(0.0,dot(-origin,dir));
    vec3 p=origin+dir*nearPoint;
    float dist=length(p);
    float shape=exp(-dist*dist/(20.0*20.0));
    if(shape<0.002) return vec3(0.0);

    vec3 drift=vec3(t*0.018,-t*0.011,t*0.006);
    float low=fbm3(p*0.105+vec3(4.7,2.1,1.4)+drift);
    float fine=fbm3(p*0.29+vec3(-1.3,6.4,2.2)+drift*0.66);
    float opening=smoothstep(0.28,0.71,low);
    // Localized blue-grey cavities and warm sunward cloud surfaces.
    float sunFacing=exp(-length(p.xy)*0.09);
    vec3 cold=vec3(0.070,0.11,0.19);
    vec3 warm=vec3(0.42,0.21,0.125);
    vec3 emission=mix(cold,warm,clamp(0.34+0.70*sunFacing+0.16*fine,0.0,1.0));
    return emission*shape*active*(0.25+1.2*opening)*
           (0.78+0.45*fine);
}

// A 3D perspective ray intersects distinct gas/dust sheets parallel to the
// orbital plane. Annular pressure structures, differential rotation, dark
// lanes and bright clumps are locally bound to the same orbiting world field.
// Three sample planes create a thicker medium with finite foreground depth.
vec3 v4ProtoplanetaryDisk(vec3 origin,vec3 dir,float time,float opaqueDepth) {
    float condensation=smoothstep(262.0,267.0,time);
    float clearing=1.0-smoothstep(282.0,295.0,time);
    float present=condensation*clearing;
    if(present<0.0001 || abs(dir.z)<0.035) return vec3(0.0);

    vec3 sum=vec3(0.0);
    for(int layer=0;layer<3;++layer) {
        float altitude=(float(layer)-1.0)*0.48;
        float travel=(altitude-origin.z)/dir.z;
        if(travel<=0.02 || travel>=opaqueDepth) continue;
        vec3 p=origin+dir*travel;
        float r=length(p.xy);
        if(r<1.4 || r>25.0) continue;

        float theta=atan(p.y,p.x);
        // Differential angular advection, continuous over the entire shot.
        float rotated=theta-time*(0.055/sqrt(1.2+r*0.21));
        float turbulence=fbm3(vec3(p.xy*0.24,altitude*0.9)+
                              vec3(3.7,-1.8,6.1));
        float granular=noise3(vec3(p.xy*0.83,time*0.005+float(layer)*13.1));
        float spiral=sin(3.0*rotated-0.45*r+
                          1.45*(turbulence-0.5));
        float arm=smoothstep(-0.32,0.74,spiral);
        float radial=exp(-((r-11.5)/10.2)*((r-11.5)/10.2));
        radial*=smoothstep(1.35,3.4,r)*
                (1.0-smoothstep(22.0,25.0,r));
        // Vary annular density with perturbed narrow gaps.
        float rings=0.57+0.43*sin(r*1.45+2.9*turbulence+
                                 rotated*0.75);
        float dust=radial*(0.15+0.73*arm)*
                   (0.56+0.44*rings)*
                   (0.53+0.47*granular);

        // Bright, sparse condensations inside arms hint at planetesimals.
        // Never claim these are simulated gravitational collisions.
        vec2 cell=floor(p.xy*0.82);
        vec2 f=fract(p.xy*0.82);
        vec2 seed=vec2(hash21(cell+13.4),hash21(cell-8.7));
        float grain=safeGaussian(length(f-seed),0.13)*
                    step(0.935,hash21(cell+vec2(7.1,2.4)));
        float growth=smoothstep(268.0,281.0,time);
        float sparkle=grain*radial*growth*(0.5+0.5*arm);
        vec3 cool=vec3(0.22,0.34,0.49);
        vec3 gold=vec3(0.89,0.56,0.25);
        vec3 tint=mix(cool,gold,
                      clamp(0.30+0.51*arm+0.15*turbulence,0.0,1.0));
        float depthWeight=(layer==1)?0.53:0.32;
        sum+=present*depthWeight*
             (tint*dust*0.67+vec3(1.22,0.94,0.63)*sparkle*0.70);
    }
    return sum;
}

// Young circumstellar clouds condense into rocky protoplanets. World
// positions are the same as in the final established orbital system; only
// radii and colors evolve, so no objects suddenly appear at new positions.
float v4PlanetReveal(float time,int planetIndex) {
    float delay=0.70*float(planetIndex);
    return smoothstep(271.5+delay,286.0+delay*0.55,time);
}

vec3 v4YoungPlanetColor(vec3 established,float development,
                        vec3 surfaceNormal,float time) {
    float scars=fbm3(surfaceNormal*14.0+
                     vec3(time*0.012,4.1,9.0));
    vec3 molten=mix(vec3(0.31,0.085,0.036),
                    vec3(1.25,0.44,0.09),
                    smoothstep(0.37,0.80,scars));
    return mix(molten,established,smoothstep(0.28,0.95,development));
}
