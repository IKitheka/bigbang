// Native 170--300 s transport: recombination, neutral dark ages and cosmic
// dawn / galaxy assembly. Included by cosmic_evolution.frag after the shared
// deterministic hash31 / valueNoise / fbm helpers. Scene-linear HDR output.
//
// This is an art-directed, time-compressed interpretation, not an N-body,
// recombination or radiative-transfer simulation. In particular, the subtle
// neutral background at decoupling is a visualization of perturbations; CMB
// photons are not portrayed as a visible rainbow sky.

vec3 lateGalaxyCenter(int index) {
    if (index == 0) return vec3(0.8, 3.5, 0.1);
    if (index == 1) return vec3(-6.4, 8.5, 3.1);
    return vec3(7.1, 16.0, -1.8);
}

// Cinematic M4 galaxy morphology pass. These finite, inclined, geometrically
// thin gas/star discs replace the earlier uniformly glowing ellipsoids. All
// shading is computed in world-space at the current timestamp, never from a
// billboard, still image or cached sequence. The structures are artistic
// cosmological interpretations, not N-body galaxy simulations.
//
// A ray intersects a compact oriented ellipsoid, then receives 18 stratified
// volume samples. Ellipsoid Z is only three disc scale heights (formerly five)
// and a separate small central bulge is added. Narrow, broken density-wave
// arms, dust absorption and diffuse older stars yield a recognisable galaxy
// silhouette without neon outlines or repeated two-dimensional spiral icons.
vec3 lateGalaxy(vec3 origin, vec3 ray, float t, int index,
                out float obscuration) {
    float fi=float(index);
    vec3 center=lateGalaxyCenter(index);
    vec3 normal=normalize(index==0 ? vec3(0.16,-0.48,0.86) :
                          (index==1 ? vec3(-0.52,-0.35,0.78) :
                                      vec3(0.36,-0.76,0.54)));
    vec3 axisX=normalize(cross(vec3(0.0,0.0,1.0),normal));
    vec3 axisY=cross(normal,axisX);
    vec3 rel=origin-center;
    vec3 o=vec3(dot(rel,axisX),dot(rel,axisY),dot(rel,normal));
    vec3 d=vec3(dot(ray,axisX),dot(ray,axisY),dot(ray,normal));

    float youngCluster=smoothstep(243.0+fi*3.5,261.0+fi*2.6,t);
    float mature=smoothstep(252.0+fi*3.0,296.0,t);
    float radius=mix(1.42,index==0 ? 4.75 : 2.8,mature);
    float thickness=mix(0.40,0.145,mature);
    vec3 bounds=vec3(radius*1.06,radius*1.06,thickness*3.15);
    vec3 so=o/bounds,sd=d/bounds;
    float a=dot(sd,sd);
    float b=dot(so,sd);
    float delta=b*b-a*(dot(so,so)-1.0);
    obscuration=0.0;
    if(delta<=0.0 || youngCluster<=0.0001) return vec3(0.0);

    float root=sqrt(delta);
    float nearT=max(0.0,(-b-root)/a);
    float farT=(-b+root)/a;
    if(farT<=nearT) return vec3(0.0);

    const int GALAXY_STEPS=18;
    float ds=(farT-nearT)/float(GALAXY_STEPS);
    float transmission=1.0;
    vec3 result=vec3(0.0);
    for(int i=0;i<GALAXY_STEPS;++i) {
        vec3 q=o+d*(nearT+(float(i)+0.5)*ds);
        float r=length(q.xy);
        float rn=r/max(radius,0.01);
        if(rn>=1.0) continue;
        float azimuth=atan(q.y,q.x);
        float lowNoise=valueNoise(vec3(q.xy*1.25,fi*7.4)+vec3(1.3,3.7,1.1));
        float armNoise=valueNoise(q*vec3(3.0,3.0,4.0)+vec3(fi*11.7,1.0,3.4));
        float fineNoise=valueNoise(q*vec3(8.7,8.7,12.0)+vec3(2.7,fi*13.7,1.6));
        float warpedAngle=azimuth+0.26*(lowNoise-0.5);
        float armPhase=2.0*warpedAngle-4.5*log(rn+0.16)-
                       0.017*(t-240.0)+fi*2.1;
        float wave=pow(0.5+0.5*cos(armPhase),8.0);
        float broken=wave*smoothstep(0.14,0.36,rn)*
                     (1.0-smoothstep(0.72,0.99,rn));
        float knots=smoothstep(0.44,0.76,armNoise)*
                    smoothstep(0.38,0.70,fineNoise);
        float vertical=exp(-abs(q.z)/thickness);
        float radial=exp(-pow(rn/0.63,1.45))*
                     (1.0-smoothstep(0.86,1.0,rn));
        float disc=vertical*radial;
        float bulge=exp(-3.7*length(q/vec3(radius*0.30,
                                              radius*0.30,
                                              thickness*1.7)));
        // Old stellar disc is wide and faint; the brighter blue-white lanes
        // are localised to the two broken arms and compact knots.
        float oldLum=disc*(0.20+0.10*lowNoise)*
                      mix(0.75,0.42,mature);
        float armsLum=mature*disc*broken*(0.55+1.65*knots);
        float clumpLum=youngCluster*disc*knots*(0.06+0.20*broken);
        vec3 source=vec3(0.76,0.69,0.57)*(oldLum+bulge*0.85)+
                    vec3(0.50,0.68,0.96)*(armsLum+clumpLum);
        source*=(0.80+0.40*fineNoise);
        // Muted, irregular dust absorbs background starlight through the
        // inclined disc. No orange or black hand-drawn spiral decorations.
        float dust=disc*mature*(0.12+1.6*broken)*
                   (0.35+1.1*lowNoise)*(0.60+0.55*armNoise);
        float absorption=1.0-exp(-dust*ds*2.5);
        result+=transmission*source*ds*youngCluster*1.75;
        transmission*=1.0-absorption;
        if(transmission<0.025) break;
    }
    obscuration=1.0-transmission;
    return result;
}

// Seeded compact first-light clusters occupy 3D positions around the same
// collapsing overdensities that later acquire galaxy structure. A finite
// angular footprint is analytically integrated along each camera ray.
vec3 lateFirstLight(vec3 origin, vec3 ray, float t) {
    vec3 result = vec3(0.0);
    float dawn = smoothstep(240.0,250.0,t);
    if (dawn <= 0.0001) return result;
    for (int k=0; k<12; ++k) {
        float fk = float(k);
        int group = k/4;
        vec3 random = vec3(hash31(vec3(fk,4.7,1.2)),
                           hash31(vec3(fk,8.1,2.3)),
                           hash31(vec3(fk,0.3,9.8)));
        vec3 center = lateGalaxyCenter(group);
        vec3 offset = (random-0.5)*vec3(4.2,3.7,2.7);
        float collapse = smoothstep(240.0,285.0,t);
        vec3 point = center+offset*mix(1.6,0.62,collapse);
        vec3 delta = point-origin;
        float distanceOnRay = dot(delta,ray);
        if (distanceOnRay <= 0.0) continue;
        vec3 nearest = delta-ray*distanceOnRay;
        float ignition = smoothstep(240.0+fk*1.1,249.0+fk*1.1,t);
        // Roughly pixel-sized compact stellar populations at preview size,
        // with a restrained broader scattering envelope, not giant spheres.
        float width = max(0.020,distanceOnRay*0.00115);
        float distance2 = dot(nearest,nearest);
        float compact = exp(-distance2/(width*width));
        float envelope = exp(-distance2/(width*width*22.0))*0.018;
        float assembly = 1.0-0.72*smoothstep(267.0,296.0,t);
        vec3 tint = mix(vec3(0.77,0.83,0.90),vec3(0.94,0.82,0.66),random.z*0.55);
        result += tint*(compact+envelope)*0.48*ignition*dawn*assembly;
    }
    return result;
}

vec3 lateEpochRadiance(vec3 origin, vec3 ray, float t) {
    float decoupling = smoothstep(170.0,200.0,t);
    float darkAges = smoothstep(195.0,212.0,t);
    float collapse = smoothstep(208.0,270.0,t);
    float dawn = smoothstep(240.0,280.0,t);
    float transmit = 1.0;
    vec3 radiance = vec3(0.0);
    // Fixed time-independent quadrature avoids a sampling change at dawn.
    // 24 gas samples; galaxy work is bounded to intersected finite volumes.
    const int GAS_STEPS = 24;
    const float stepLength = 0.95;
    for (int i=0; i<GAS_STEPS; ++i) {
        float distanceAlongRay = 0.8+(float(i)+0.5)*stepLength;
        vec3 p = origin+ray*distanceAlongRay;
        // A slow, coherent collapse changes the morphology without reseeding
        // the volume each frame. Shared coarse coordinates match the preceding
        // opaque-plasma continuum; extinction, rather than a material cut,
        // reveals its depth during recombination.
        vec3 drift = vec3(0.0008,-0.0005,0.0003)*(t-170.0);
        float coarse = fbm(p*0.28+vec3(2.7,0.8,4.1)+drift);
        float fine = fbm(p*0.95+vec3(1.1,3.4,0.7)+drift*1.4);
        // The same two correlated scalar interfaces as the opaque plasma
        // survive recombination. Thin overlap regions retain depth while broad
        // opacity recedes, rather than fading an undifferentiated grey screen.
        float sheet = exp(-2400.0*(coarse-0.53)*(coarse-0.53));
        float crossing = exp(-150.0*(fine-0.56)*(fine-0.56));
        float lace = sheet*crossing;
        float veil = exp(-180.0*(coarse-0.53)*(coarse-0.53));
        float corrugation = smoothstep(0.30,0.65,fine);
        float concentrated = pow(smoothstep(0.40,0.73,coarse),2.5);
        float density = 0.001+mix(0.13,0.015,decoupling)*veil+1.1*lace;
        density *= mix(1.0,0.55+1.6*concentrated,collapse);
        float depthWindow = smoothstep(1.8,5.0,distanceAlongRay)*
                            (1.0-smoothstep(19.0,24.0,distanceAlongRay));
        float opticalDepth = mix(0.22,0.025,decoupling)*density*depthWindow;
        float alpha = 1.0-exp(-opticalDepth*stepLength);
        vec3 earlyHot = mix(vec3(0.23,0.35,0.50),
                            vec3(0.78,0.65,0.47),corrugation);
        vec3 neutral = mix(vec3(0.27,0.29,0.30),
                           vec3(0.61,0.56,0.47),corrugation);
        vec3 hot = mix(earlyHot,neutral,decoupling);
        vec3 source = vec3(0.025,0.040,0.065)+hot*lace*2.8;
        source *= mix(1.0,0.075,decoupling);
        source *= mix(1.0,0.32,darkAges);
        // The neutral dark-age density is a very faint presentation layer:
        // it is not visible pre-stellar emission, stars or a luminous web.
        // Keep a readable evolving trace while retaining large black gaps.
        float traceWeight = smoothstep(192.0,210.0,t)*
                            (1.0-smoothstep(242.0,266.0,t));
        vec3 darkTrace = vec3(0.0031,0.0029,0.0025)*
                         pow(max(lace,0.0),0.85)*traceWeight*depthWindow;
        radiance += transmit*darkTrace*stepLength;
        source += vec3(0.016,0.014,0.011)*concentrated*dawn;
        radiance += transmit*alpha*source;
        transmit *= 1.0-alpha;
    }
    // Low-amplitude scalar perturbations on a neutral background: deliberately
    // no false-color/rainbow CMB map, spherical shell, grid or visible sky dome.
    float backgroundNoise = valueNoise(ray*4.7+vec3(3.4,7.1,1.8));
    float cmbVisibility = smoothstep(175.0,192.0,t)*(1.0-smoothstep(192.0,207.0,t));
    radiance += transmit*vec3(0.0008,0.00072,0.00061)*
                (0.92+0.16*backgroundNoise)*cmbVisibility;
    if (t > 240.0) {
        vec3 galaxies = vec3(0.0);
        float totalDust = 0.0;
        for (int galaxy=0; galaxy<3; ++galaxy) {
            float dust;
            galaxies += lateGalaxy(origin,ray,t,galaxy,dust);
            totalDust += dust;
        }
        radiance += transmit*(galaxies+lateFirstLight(origin,ray,t))*
                    exp(-0.16*totalDust);
    }
    return max(radiance,vec3(0.0));
}
