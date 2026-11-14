#ifndef BLOOM_EFFECT_HPP
#define BLOOM_EFFECT_HPP

#include "Shader.hpp"

#include <glad/gl.h>
#include <string>

class BloomEffect {
public:
    BloomEffect(const std::string& shaderDirectory,
                int width, int height);
    ~BloomEffect();

    BloomEffect(const BloomEffect&) = delete;
    BloomEffect& operator=(const BloomEffect&) = delete;

    void resize(int width, int height);

    GLuint render(GLuint sceneTexture, GLuint quadVAO);

private:
    Shader brightShader;
    Shader blurShader;

    // 0 = bright extraction, 1 and 2 = alternating blur buffers.
    GLuint framebuffers[3] = {0, 0, 0};
    GLuint textures[3] = {0, 0, 0};

    int sourceWidth = 0;
    int sourceHeight = 0;
    int bloomWidth = 0;
    int bloomHeight = 0;

    void destroy();
};

#endif
