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

// Integrate a finite, tilted stellar / dust distribution in its own 3D
// coordinate system. Eight samples concentrate work inside the galaxy instead
// of undersampling thin discs with the much longer neutral-gas ray march.
// The inclination, depth, bulge, broad uneven arms and dust attenuation are
// evaluated in world space; this is not a screen-aligned galaxy sprite.
vec3 lateGalaxy(vec3 origin, vec3 ray, float t, int index,
                out float obscuration) {
    float fi = float(index);
    vec3 center = lateGalaxyCenter(index);
    // Inclined thin rotating gas disks, deliberately not near-spherical
    // volumes. The viewing angles vary so one disk reads edge-on while
    // another reveals the ragged arm structure.
    vec3 normal = normalize(index == 0 ? vec3(0.14, 0.60, 0.78) :
                            (index == 1 ? vec3(-0.35, 0.82, 0.45) :
                                          vec3(0.61, 0.69, 0.41)));
    vec3 axisX = normalize(cross(vec3(0.0,0.0,1.0), normal));
    vec3 axisY = cross(normal, axisX);
    vec3 rel = origin-center;
    vec3 o = vec3(dot(rel,axisX),dot(rel,axisY),dot(rel,normal));
    vec3 d = vec3(dot(ray,axisX),dot(ray,axisY),dot(ray,normal));
    float development = smoothstep(252.0+fi*3.0, 298.0, t);
    float firstCluster = smoothstep(243.0+fi*4.0, 261.0+fi*3.0, t);
    float radius = mix(1.65, index == 0 ? 4.5 : 2.65, development);
    float height = mix(0.42,0.11,development);
    // Closest approach to the ellipsoid bounds a compact integration range.
    vec3 scale = vec3(radius*1.12,radius*1.12,height*3.7);
    vec3 so = o/scale, sd = d/scale;
    float a = dot(sd,sd);
    float b = dot(so,sd);
    float discriminant = b*b-a*(dot(so,so)-1.0);
    obscuration = 0.0;
    if (discriminant <= 0.0 || firstCluster < 0.0001) return vec3(0.0);
    float root = sqrt(discriminant);
    float entry = max(0.0,(-b-root)/a);
    float leave = (-b+root)/a;
    if (leave <= entry) return vec3(0.0);
    float stepSize = (leave-entry)/12.0;
    float transmittance = 1.0;
    vec3 result = vec3(0.0);
    for (int j=0; j<12; ++j) {
        vec3 q = o+d*(entry+(float(j)+0.5)*stepSize);
        float r = length(q.xy);
        float rn = r/radius;
        float theta = atan(q.y,q.x);
        float turn = 2.0*theta - 3.4*log(rn+0.12) -
                     0.030*(t-240.0) + fi*2.3;
        float irregularity = valueNoise(q*vec3(1.7,1.7,3.0)+fi*9.3);
        float mottling = valueNoise(q*vec3(5.8,5.8,7.0)+vec3(fi*17.0,4.2,1.8));
        float boundary = smoothstep(0.0,0.23,1.0-dot(q/scale,q/scale));
        // Initially amorphous clusters acquire a rotationally supported disc
        // gradually. The arms remain a broad density enhancement with broken
        // star-forming regions, rather than repeated bright spiral outlines.
        float arm = pow(0.5+0.5*cos(turn+1.20*(irregularity-0.5)),8.0);
        arm *= smoothstep(0.12,0.35,rn)*(1.0-smoothstep(0.68,1.0,rn));
        float vertical = exp(-abs(q.z)/height);
        float radial = exp(-2.8*rn)*(1.0-smoothstep(0.76,1.12,rn));
        float disc = vertical*radial;
        float bulgeRadius = length(q*vec3(1.0,1.0,2.80));
        float bulge = exp(-bulgeRadius/(0.18*radius));
        float clumps = smoothstep(0.42,0.76,irregularity)*
                       smoothstep(0.24,0.74,mottling);
        float stars = disc*mix(0.52,0.17,development);
        stars += development*disc*(2.8*arm*(0.18+1.5*clumps)+0.08*clumps);
        float young = development*disc*arm*clumps;
        float dust = disc*(0.35+3.7*arm)*(0.18+1.4*irregularity)*development;
        float alpha = 1.0-exp(-dust*stepSize*2.3);
        vec3 oldStars = mix(vec3(0.79,0.72,0.60),
                           vec3(0.69,0.75,0.80),development*0.32);
        vec3 emission = oldStars*(stars*0.55+bulge*0.24) +
                        vec3(0.62,0.71,0.80)*young*1.0;
        emission *= boundary;
        // Sub-resolution stellar granularity is deterministic in 3D; its
        // contrast stays low to avoid swimming, glitter and neon star lanes.
        emission *= 0.62+0.76*mottling;
        result += transmittance*emission*stepSize*firstCluster;
        transmittance *= 1.0-alpha;
    }
    // Add stars on the *same local 3D disk plane*, as unresolved irregular
    // point populations. Unlike a star-textured sphere or billboard these
    // positions remain anchored to the galaxy under camera motion.
    // Finite plane intersections avoid drawing points through the camera.
    if (development > 0.025 && abs(d.z)>0.028) {
        float planeT=-o.z/d.z;
        if (planeT>0.0) {
            vec3 crossPt=o+d*planeT;
            float rn=length(crossPt.xy)/radius;
            if (rn<1.0) {
                vec2 gridPos=crossPt.xy*7.0;
                vec2 centralCell=floor(gridPos);
                float localArm=pow(0.5+0.5*cos(2.0*atan(crossPt.y,crossPt.x)-
                                     3.4*log(rn+0.12)-0.030*(t-240.0)+fi*2.3),6.0);
                float radialWeight=exp(-1.50*rn*rn)*
                                  (1.0-smoothstep(0.83,1.0,rn));
                vec3 pinpoint=vec3(0);
                for (int gx=-1; gx<=1; ++gx)
                for (int gy=-1; gy<=1; ++gy) {
                    vec2 cell=centralCell+vec2(float(gx),float(gy));
                    vec3 seed=vec3(cell,fi*17.3+11.4);
                    vec2 jitter=vec2(hash31(seed),hash31(seed+vec3(6.3,1.4,7.7)));
                    vec2 offset=cell+jitter-gridPos;
                    float d2=dot(offset,offset);
                    float starVisible=step(0.55,hash31(seed+vec3(2.3,4.1,0.5)));
                    float light=exp(-25.0*d2)*starVisible;
                    float young=step(0.72,hash31(seed+vec3(3.9,8.2,1.2)));
                    vec3 color=mix(vec3(0.83,0.73,0.60),vec3(0.62,0.76,0.93),
                                   young);
                    pinpoint+=color*light*(0.25+0.9*localArm*young);
                }
                // Stars emerge *within* a dusty flattened disk; this isn't
                // an unrelated all-sky white dot field.
                float dustLane=valueNoise(crossPt*vec3(0.63,0.63,0.09)+fi*10.0);
                float starObscuration=mix(0.77,0.39,
                                          smoothstep(0.49,0.77,dustLane));
                result+=pinpoint*(0.41*development*radialWeight*
                                   starObscuration*firstCluster);
            }
        }
    }
    obscuration = 1.0-transmittance;
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
