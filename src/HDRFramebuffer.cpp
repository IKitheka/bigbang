#include "HDRFramebuffer.hpp"

#include <stdexcept>

HDRFramebuffer::HDRFramebuffer(int width, int height) {
    create(width, height);
}

HDRFramebuffer::~HDRFramebuffer() {
    destroy();
}

void HDRFramebuffer::create(int width, int height) {
    if (width <= 0 || height <= 0) {
        throw std::runtime_error("Invalid framebuffer dimensions.");
    }

    // Create the framebuffer.
    glGenFramebuffers(1, &framebufferID);
    glBindFramebuffer(GL_FRAMEBUFFER, framebufferID);

    // Create a floating-point HDR colour texture.
    glGenTextures(1, &colorTextureID);
    glBindTexture(GL_TEXTURE_2D, colorTextureID);

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA16F,
        width,
        height,
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
        colorTextureID,
        0
    );

    glBindTexture(GL_TEXTURE_2D, 0);

    // Create a depth and stencil renderbuffer.
    glGenRenderbuffers(1, &depthRenderbufferID);
    glBindRenderbuffer(GL_RENDERBUFFER, depthRenderbufferID);

    glRenderbufferStorage(
        GL_RENDERBUFFER,
        GL_DEPTH24_STENCIL8,
        width,
        height
    );

    glFramebufferRenderbuffer(
        GL_FRAMEBUFFER,
        GL_DEPTH_STENCIL_ATTACHMENT,
        GL_RENDERBUFFER,
        depthRenderbufferID
    );

    glBindRenderbuffer(GL_RENDERBUFFER, 0);

    // Tell OpenGL where fragment colours will be written.
    GLenum attachments[] = {GL_COLOR_ATTACHMENT0};
    glDrawBuffers(1, attachments);

    // Validate the framebuffer.
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER)
        != GL_FRAMEBUFFER_COMPLETE) {

        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        destroy();

        throw std::runtime_error(
            "HDR framebuffer is incomplete."
        );
    }

    framebufferWidth = width;
    framebufferHeight = height;

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void HDRFramebuffer::destroy() {
    if (depthRenderbufferID != 0) {
        glDeleteRenderbuffers(1, &depthRenderbufferID);
        depthRenderbufferID = 0;
    }

    if (colorTextureID != 0) {
        glDeleteTextures(1, &colorTextureID);
        colorTextureID = 0;
    }

    if (framebufferID != 0) {
        glDeleteFramebuffers(1, &framebufferID);
        framebufferID = 0;
    }

    framebufferWidth = 0;
    framebufferHeight = 0;
}

void HDRFramebuffer::bind() const {
    glBindFramebuffer(GL_FRAMEBUFFER, framebufferID);
}

void HDRFramebuffer::unbind() {
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
}

void HDRFramebuffer::resize(int width, int height) {
    if (width <= 0 || height <= 0) {
        return;
    }

    if (width == framebufferWidth &&
        height == framebufferHeight) {
        return;
    }

    destroy();
    create(width, height);
}

GLuint HDRFramebuffer::getColorTexture() const {
    return colorTextureID;
}
