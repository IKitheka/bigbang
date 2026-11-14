#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D uScene;
uniform sampler2D uBloomBlur;

uniform float uBloomStrength;
uniform float uExposure;

void main() {
    vec3 sceneColor = texture(uScene, TexCoords).rgb;
    vec3 bloomColor = texture(uBloomBlur, TexCoords).rgb;

    vec3 hdrColor = sceneColor + bloomColor * uBloomStrength;

    // Exposure-based HDR tone mapping.
    vec3 mapped = vec3(1.0) - exp(-hdrColor * uExposure);

    // Gamma correction for display.
    mapped = pow(max(mapped, vec3(0.0)), vec3(1.0 / 2.2));

    FragColor = vec4(mapped, 1.0);
}
