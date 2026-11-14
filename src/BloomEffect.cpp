#include "BloomEffect.hpp"

#include <algorithm>
#include <stdexcept>
#include <string>

BloomEffect::BloomEffect(
    const std::string& shaderDirectory,
    int width,
    int height
)
    : brightShader(
          shaderDirectory + "/screen.vert",
          shaderDirectory + "/bright.frag"
      ),
      blurShader(
          shaderDirectory + "/screen.vert",
          shaderDirectory + "/blur.frag"
      )
{
    resize(width, height);
}

BloomEffect::~BloomEffect() {
    destroy();
}

void BloomEffect::destroy() {
    glDeleteTextures(3, textures);
    glDeleteFramebuffers(3, framebuffers);

    for (int i = 0; i < 3; ++i) {
        textures[i] = 0;
        framebuffers[i] = 0;
    }

    sourceWidth = 0;
    sourceHeight = 0;
    bloomWidth = 0;
    bloomHeight = 0;
}

void BloomEffect::resize(int width, int height) {
    if (width <= 0 || height <= 0) {
        return;
    }

    if (width == sourceWidth && height == sourceHeight) {
        return;
    }

    destroy();

    // Half-resolution bloom reduces GPU workload.
    bloomWidth = std::max(1, width / 2);
    bloomHeight = std::max(1, height / 2);

    glGenFramebuffers(3, framebuffers);
    glGenTextures(3, textures);

    try {
        for (int i = 0; i < 3; ++i) {
            glBindFramebuffer(
                GL_FRAMEBUFFER, framebuffers[i]
            );

            glBindTexture(
                GL_TEXTURE_2D, textures[i]
            );

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA16F,
                bloomWidth,
                bloomHeight,
                0,
                GL_RGBA,
                GL_FLOAT,
                nullptr
            );

            glTexParameteri(
                GL_TEXTURE_2D,
                GL_TEXTURE_MIN_FILTER,
                GL_LINEAR
            );

            glTexParameteri(
                GL_TEXTURE_2D,
                GL_TEXTURE_MAG_FILTER,
                GL_LINEAR
            );

            glTexParameteri(
                GL_TEXTURE_2D,
                GL_TEXTURE_WRAP_S,
                GL_CLAMP_TO_EDGE
            );

            glTexParameteri(
                GL_TEXTURE_2D,
                GL_TEXTURE_WRAP_T,
                GL_CLAMP_TO_EDGE
            );

            glFramebufferTexture2D(
                GL_FRAMEBUFFER,
                GL_COLOR_ATTACHMENT0,
                GL_TEXTURE_2D,
                textures[i],
                0
            );

            if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
                != GL_FRAMEBUFFER_COMPLETE) {
                throw std::runtime_error(
                    "Bloom framebuffer " +
                    std::to_string(i) +
                    " is incomplete."
                );
            }
        }
    }
    catch (...) {
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        glBindTexture(GL_TEXTURE_2D, 0);
        destroy();
        throw;
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glBindTexture(GL_TEXTURE_2D, 0);

    sourceWidth = width;
    sourceHeight = height;
}

GLuint BloomEffect::render(
    GLuint sceneTexture,
    GLuint quadVAO
) {
    if (bloomWidth <= 0 || bloomHeight <= 0) {
        throw std::runtime_error(
            "Bloom framebuffer has not been initialized."
        );
    }

    const GLboolean blendingWasEnabled =
        glIsEnabled(GL_BLEND);

    const GLboolean depthWasEnabled =
        glIsEnabled(GL_DEPTH_TEST);

    glDisable(GL_BLEND);
    glDisable(GL_DEPTH_TEST);

    glViewport(0, 0, bloomWidth, bloomHeight);
    glBindVertexArray(quadVAO);
    glActiveTexture(GL_TEXTURE0);

    // Pass 1: Extract highlights from HDR scene.
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffers[0]);

    brightShader.use();

    glUniform1i(
        glGetUniformLocation(
            brightShader.getID(), "uScene"
        ),
        0
    );

    glBindTexture(GL_TEXTURE_2D, sceneTexture);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

    // Pass 2: Alternating horizontal/vertical blur.
    blurShader.use();

    glUniform1i(
        glGetUniformLocation(
            blurShader.getID(), "uImage"
        ),
        0
    );

    const GLint horizontalLocation =
        glGetUniformLocation(
            blurShader.getID(), "uHorizontal"
        );

    GLuint finalTexture = textures[0];

    constexpr int BLUR_PASSES = 10;

    for (int pass = 0; pass < BLUR_PASSES; ++pass) {
        const int targetIndex = 1 + (pass % 2);

        const int inputIndex =
            (pass == 0) ? 0 : 1 + ((pass - 1) % 2);

        glBindFramebuffer(
            GL_FRAMEBUFFER,
            framebuffers[targetIndex]
        );

        glBindTexture(
            GL_TEXTURE_2D,
            textures[inputIndex]
        );

        glUniform1i(
            horizontalLocation,
            (pass % 2 == 0) ? 1 : 0
        );

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);

        finalTexture = textures[targetIndex];
    }

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glBindTexture(GL_TEXTURE_2D, 0);
    glBindVertexArray(0);

    if (blendingWasEnabled) {
        glEnable(GL_BLEND);
    }

    if (depthWasEnabled) {
        glEnable(GL_DEPTH_TEST);
    }

    return finalTexture;
}
