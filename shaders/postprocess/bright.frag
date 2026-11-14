#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D uScene;

void main() {
    vec3 color = texture(uScene, TexCoords).rgb;

    float brightness = max(
        color.r,
        max(color.g, color.b)
    );

    float strength = smoothstep(0.8, 1.8, brightness);

    FragColor = vec4(color * strength, 1.0);
}
