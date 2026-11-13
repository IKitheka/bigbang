#version 330 core

in vec3 particleColor;

out vec4 FragColor;

void main() {
    vec2 centered = gl_PointCoord - vec2(0.5);

    float distanceFromCenter = length(centered);

    if (distanceFromCenter > 0.5) {
        discard;
    }

    float glow = exp(-distanceFromCenter * distanceFromCenter * 24.0);

    float core = 1.0 - smoothstep(0.0, 0.16, distanceFromCenter);

    float brightness = glow + core * 0.8;

    FragColor = vec4(
        particleColor * brightness,
        brightness * 0.75
    );
}
