#version 330 core

in vec3 particleColor;
in float particleSize;

out vec4 FragColor;

void main() {
    vec2 centered = gl_PointCoord * 2.0 - vec2(1.0);
    float radius = length(centered);

    if (radius > 1.0) {
        discard;
    }

    bool isEnergyCore = particleSize > 1.0;

    float softGlow = exp(
        -radius * radius * (isEnergyCore ? 4.0 : 9.0)
    );

    float hotCenter = exp(
        -radius * radius * (isEnergyCore ? 18.0 : 22.0)
    );

    float emission;

    if (isEnergyCore) {
        emission = 5.0 * hotCenter + 1.5 * softGlow;
    } else {
        emission = 1.3 * hotCenter + 0.45 * softGlow;
    }

    float alpha;

    if (isEnergyCore) {
        alpha = 1.0 - smoothstep(0.45, 1.0, radius);
    } else {
        alpha = 1.0 - smoothstep(0.25, 1.0, radius);
    }

    // Values above 1.0 are preserved by the HDR framebuffer.
    vec3 hdrColor = particleColor * emission;

    FragColor = vec4(hdrColor, alpha);
}
