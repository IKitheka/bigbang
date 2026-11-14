#ifndef HDR_FRAMEBUFFER_HPP
#define HDR_FRAMEBUFFER_HPP

#include <glad/gl.h>

class HDRFramebuffer {
public:
    HDRFramebuffer(int width, int height);
    ~HDRFramebuffer();

    HDRFramebuffer(const HDRFramebuffer&) = delete;
    HDRFramebuffer& operator=(const HDRFramebuffer&) = delete;

    void bind() const;
    static void unbind();

    void resize(int width, int height);

    GLuint getColorTexture() const;

private:
    GLuint framebufferID = 0;
    GLuint colorTextureID = 0;
    GLuint depthRenderbufferID = 0;

    int framebufferWidth = 0;
    int framebufferHeight = 0;

    void create(int width, int height);
    void destroy();
};

#endif
