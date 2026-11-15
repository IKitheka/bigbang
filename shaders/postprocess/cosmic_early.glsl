// Native scene-linear radiation/collision metaphor; shared noise is included
// by cosmic_evolution.frag. This is not a nuclear or fluid simulation.
vec3 earlyEpochRadiance(vec3 origin, vec3 ray, float t) {
    float epochTime = clamp(t, 45.0, 180.0);
    float reactions = smoothstep(84.0, 101.0, epochTime) *
        (1.0 - smoothstep(122.0, 140.0, epochTime));
    float opaque = smoothstep(125.0, 160.0, epochTime);
    // A *continuous* visual progression. The owner-approved 0–50s and
    // 240–300s clips are outside this shader's new grade. 90–130s emphasizes
    // localized hot reaction interfaces; 130–175s develops a high-key
    // radiation-coupled veil that recombination can gradually disperse.
    // These are art-directed metaphors, not nuclear reaction dynamics.
    float nuclearWeight=smoothstep(90.0,105.0,epochTime)*
                        (1.0-smoothstep(121.0,135.0,epochTime));
    float mistWeight=smoothstep(126.0,150.0,epochTime)*
                     (1.0-smoothstep(168.0,182.0,epochTime));
    // Separate QGP visual language from the grey radiation-fold metaphor.
    // This is stylized correlated fluid energy, not individually coloured
    // quarks, an orange fireball, or a physically solved hydrodynamics field.
    // Its weights are zero outside the 52–100s window.
    float qgp = smoothstep(52.0, 67.0, epochTime) *
                (1.0 - smoothstep(87.0, 101.0, epochTime));
    vec3 drift = vec3(0.006, -0.003, 0.004) * (epochTime - 170.0);
    float transmit = 1.0;
    vec3 radiance = vec3(0.0);
    const int EARLY_STEPS = 42;
    const float EARLY_STEP_LENGTH = 0.62;
    for (int i = 0; i < EARLY_STEPS; ++i) {
        float depth = 0.8 + (float(i) + 0.5) * EARLY_STEP_LENGTH;
        float window = smoothstep(1.8, 5.0, depth) *
            (1.0 - smoothstep(19.0, 24.0, depth));
        vec3 p = origin + ray * depth + drift;
        float coarse = fbm(p * 0.28 + vec3(2.7, 0.8, 4.1));
        float fine = fbm(p * 0.95 + vec3(1.1, 3.4, 0.7));
        // Two independent thin scalar interfaces must coincide before light
        // is emitted. Integrating a broad luminous cloud washes out all depth.
        // These locally curved radiation folds are not a mature stellar web.
        float sheet = exp(-2400.0 * (coarse - 0.53) * (coarse - 0.53));
        float crossing = exp(-150.0 * (fine - 0.56) * (fine - 0.56));
        float corrugation = smoothstep(0.30, 0.65, fine);
        float lace = sheet * crossing;
        float veil = exp(-180.0 * (coarse - 0.53) * (coarse - 0.53));
        float density = 0.001 + 0.13 * veil + 1.1 * lace;

        // Spatially anchored, slow advection. A warped 3D scalar field
        // produces correlated hot sheets and translucent cavities rather
        // than a collection of independent neon dots.
        vec3 flow = p + 0.43 * vec3(
            sin(p.y * 0.62 + epochTime * 0.034 + sin(p.z*0.34)),
            cos(p.z * 0.49 - epochTime * 0.029 + sin(p.x*0.27)),
            sin(p.x * 0.54 + epochTime * 0.026 + cos(p.y*0.31)));
        float plasmaCoarse = fbm(flow*0.34 + vec3(3.1,8.2,-2.4));
        float plasmaFine = valueNoise(flow*1.78 + vec3(2.5,4.8,epochTime*0.087));
        float ribbon = exp(-420.0*pow(plasmaCoarse-0.595,2.0));
        float vortex = smoothstep(0.46,0.74,plasmaFine);
        float cavities = smoothstep(0.54,0.73,plasmaCoarse);
        float hotEdge = ribbon*(0.38+1.5*vortex);
        float plasmaDensity = 0.002 + 0.025*cavities + 0.56*hotEdge;
        // QGP has a broad hot medium, but emissive optical thickness must
        // retain depth and visible pockets of negative space.
        density = mix(density,plasmaDensity,qgp);
        float optical = mix(0.13, 0.22, opaque) * density * window;
        optical *= mix(1.0,0.67,qgp);
        float alpha = 1.0 - exp(-optical * EARLY_STEP_LENGTH);
        vec3 low = vec3(0.025, 0.040, 0.065);
        vec3 hot = mix(vec3(0.23, 0.35, 0.50),
                       vec3(0.78, 0.65, 0.47), corrugation);
        vec3 source = low + hot * lace * 2.8;
        // Desaturated deep cyan-blue shadows against pale amber/ivory,
        // with turbulence following the same 3D mass distribution.
        // A few concentrated high-energy streaks provide actual local
        // structure instead of globally brightening the entire screen.
        vec3 plasmaCool = vec3(0.018,0.062,0.15);
        vec3 plasmaWarm = vec3(0.71,0.30,0.12);
        vec3 plasmaHot = vec3(1.02,0.80,0.52);
        vec3 plasmaTint = mix(plasmaCool,plasmaWarm,
                              smoothstep(0.35,0.78,plasmaCoarse));
        vec3 plasmaSource = plasmaTint*(0.015+0.22*cavities);
        plasmaSource += plasmaHot*(1.18*hotEdge + 0.09*vortex*hotEdge);
        source = mix(source,plasmaSource,qgp);
        if (reactions > 0.001) {
            // Two counter-advecting fluctuations briefly exchange energy
            // where high local amplitudes coincide. These are irregular warm
            // interface flashes, not literal particles or nuclear trajectories.
            float microA = valueNoise(p * 1.35 +
                vec3(0.0, 0.0, epochTime * 0.16));
            float microB = valueNoise(p * 1.35 +
                vec3(3.7, 1.1, -epochTime * 0.19));
            float coincidence = exp(-150.0 * (microA - microB) * (microA - microB));
            float exchange = lace * coincidence * smoothstep(0.52, 0.73, min(microA, microB));
            source *= mix(1.0, 0.82 + 0.36 * microA, reactions);
            source += reactions * vec3(2.6, 1.75, 0.95) * exchange;
        }
        // Primordial nucleosynthesis is NOT an atom diagram. Warm,
        // intermittent concentrations brighten thin collision interfaces
        // already embedded in the continuous plasma. Movement follows the
        // native 3D advected scalar field without screen-space flicker.
        float knot=smoothstep(0.49,0.72,plasmaFine)*
                   smoothstep(0.45,0.68,fine)*
                   exp(-190.0*pow(coarse-0.55,2.0));
        float seam=exp(-240.0*pow(fine-0.59,2.0))*
                   (0.25+0.75*plasmaCoarse);
        float ignition=nuclearWeight*(knot*2.2+seam*0.54);
        source+=ignition*vec3(2.10,1.16,0.46);
        // Reused 3D density correlations produce a broad, spatially varied
        // scattering medium, instead of the previous near-identical grey
        // filaments through every scientific era. Emission is treated as
        // a finite luminous veil over ~20 world units.
        float cloudVariance=0.24+0.62*smoothstep(0.25,0.74,coarse)+
                            0.14*fine;
        float mistAlpha=1.0-exp(-mistWeight*window*
                           (0.055+0.17*cloudVariance)*EARLY_STEP_LENGTH);
        vec3 mistColor=mix(vec3(0.57,0.65,0.76),
                           vec3(1.04,0.98,0.91),
                           smoothstep(0.39,0.72,coarse));
        radiance+=transmit*(alpha*source+mistAlpha*mistColor);
        transmit*=(1.0-alpha)*(1.0-mistAlpha);
        if (transmit < 0.015) break;
    }
    return radiance;
}
