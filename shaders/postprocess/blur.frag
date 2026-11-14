#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D uImage;
uniform bool uHorizontal;

const float weight[5] = float[](
    0.227027,
    0.1945946,
    0.1216216,
    0.054054,
    0.016216
);

void main() {
    vec2 texelSize = 1.0 / vec2(textureSize(uImage, 0));

    vec3 result = texture(uImage, TexCoords).rgb * weight[0];

    for (int i = 1; i < 5; i++) {
        vec2 offset;

        if (uHorizontal) {
            offset = vec2(texelSize.x * float(i), 0.0);
        } else {
            offset = vec2(0.0, texelSize.y * float(i));
        }

        result += texture(uImage, TexCoords + offset).rgb * weight[i];
        result += texture(uImage, TexCoords - offset).rgb * weight[i];
    }

    FragColor = vec4(result, 1.0);
}
