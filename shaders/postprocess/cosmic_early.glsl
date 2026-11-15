// Native scene-linear radiation/collision metaphor; shared noise is included
// by cosmic_evolution.frag. This is not a nuclear or fluid simulation.
vec3 earlyEpochRadiance(vec3 origin, vec3 ray, float t) {
    float epochTime = clamp(t, 45.0, 180.0);
    float reactions = smoothstep(84.0, 101.0, epochTime) *
        (1.0 - smoothstep(122.0, 140.0, epochTime));
    float opaque = smoothstep(125.0, 160.0, epochTime);
    vec3 drift = vec3(0.006, -0.003, 0.004) * (epochTime - 170.0);
    float transmit = 1.0;
    vec3 radiance = vec3(0.0);
    const int EARLY_STEPS = 38;
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
        // Sparse radiative folds live inside a very faint absorbing medium;
        // extinction grows before recombination without filling every gap.
        float optical = mix(0.13, 0.22, opaque) * density * window;
        float alpha = 1.0 - exp(-optical * EARLY_STEP_LENGTH);
        vec3 low = vec3(0.025, 0.040, 0.065);
        vec3 hot = mix(vec3(0.23, 0.35, 0.50),
                       vec3(0.78, 0.65, 0.47), corrugation);
        vec3 source = low + hot * lace * 2.8;
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
        radiance += transmit * alpha * source;
        transmit *= 1.0 - alpha;
        if (transmit < 0.015) break;
    }
    return radiance;
}
