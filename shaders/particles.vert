#version 330 core

layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec3 aColor;
layout (location = 2) in float aSize;

uniform mat4 uView;
uniform mat4 uProjection;

out vec3 particleColor;

void main() {
    vec4 viewPosition = uView * vec4(aPosition, 1.0);

    gl_Position = uProjection * viewPosition;

    gl_PointSize = aSize * (220.0 / max(-viewPosition.z, 1.0));

    particleColor = aColor;
}
