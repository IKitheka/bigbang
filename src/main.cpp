#include <glad/gl.h>

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include "Shader.hpp"
#include "HDRFramebuffer.hpp"
#include "BloomEffect.hpp"
#include "RenderOptions.hpp"
#include "PngWriter.hpp"
#include "PrimordialCamera.hpp"

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <glm/gtc/constants.hpp>

#include <iostream>
#include <vector>
#include <random>
#include <cstddef>
#include <cmath>
#include <exception>
#include <string>
#include <cstdint>

constexpr int WINDOW_WIDTH = 1280;
constexpr int WINDOW_HEIGHT = 720;
constexpr int PARTICLE_COUNT = 20000;
constexpr int SHOCKWAVE_COUNT = 2400;

struct Particle {
    glm::vec3 position;
    glm::vec3 velocity;
    glm::vec3 color;
    float size;
};

struct ParticleVertex {
    glm::vec3 position;
    glm::vec3 color;
    float size;
};

void framebufferSizeCallback(GLFWwindow* window, int width, int height) {
    (void)window;
    glViewport(0, 0, width, height);
}

std::vector<Particle> createParticles() {
    std::vector<Particle> particles;
    particles.reserve(PARTICLE_COUNT + SHOCKWAVE_COUNT + 3);

    std::mt19937 generator(42);

    std::uniform_real_distribution<float> randomUnit(0.0f, 1.0f);
    std::uniform_real_distribution<float> randomSpeed(0.12f, 0.32f);
    std::uniform_real_distribution<float> randomSize(0.08f, 0.22f);

    for (int i = 0; i < PARTICLE_COUNT; ++i) {
        float z = randomUnit(generator) * 2.0f - 1.0f;
        float angle = randomUnit(generator) * glm::two_pi<float>();

        float horizontal = sqrt(1.0f - z * z);

        glm::vec3 direction(
            horizontal * cos(angle),
            horizontal * sin(angle),
            z
        );

        glm::vec3 color;

        float choice = randomUnit(generator);

        if (choice < 0.70f) {
            color = glm::vec3(1.0f, 0.20f, 0.025f);
        }
        else if (choice < 0.90f) {
            color = glm::vec3(1.0f, 0.65f, 0.12f);
        }
        else if (choice < 0.97f) {
            color = glm::vec3(1.0f, 0.92f, 0.72f);
        }
        else {
            color = glm::vec3(0.20f, 0.48f, 1.0f);
        }

        Particle particle;

        particle.position = glm::vec3(0.0f);
        particle.velocity = direction * randomSpeed(generator);
        particle.color = color;
        particle.size = randomSize(generator);

        particles.push_back(particle);
    }

    // Create three overlapping layers for the central energy core.
    auto addCoreLayer = [&particles](glm::vec3 color, float size) {
        Particle core;
        core.position = glm::vec3(0.0f);
        core.velocity = glm::vec3(0.0f);
        core.color = color;
        core.size = size;
        particles.push_back(core);
    };

    // Large orange outer glow.
    addCoreLayer(glm::vec3(1.0f, 0.20f, 0.025f), 4.5f);

    // Hot golden middle layer.
    addCoreLayer(glm::vec3(1.0f, 0.65f, 0.20f), 2.6f);

    // Brilliant white-hot centre.
    addCoreLayer(glm::vec3(1.0f, 0.95f, 0.80f), 1.15f);


    // Create an expanding circular shockwave.
    std::uniform_real_distribution<float> ringJitter(-0.025f, 0.025f);
    std::uniform_real_distribution<float> ringSize(0.13f, 0.20f);

    for (int i = 0; i < SHOCKWAVE_COUNT; ++i) {
        float angle = randomUnit(generator) * glm::two_pi<float>();

        glm::vec3 direction(
            cos(angle),
            sin(angle),
            ringJitter(generator)
        );

        direction = glm::normalize(direction);

        Particle wave;
        wave.position = direction * 0.22f;
        wave.velocity = direction * 0.48f;

        float colorChoice = randomUnit(generator);

        if (colorChoice < 0.65f) {
            wave.color = glm::vec3(1.0f, 0.82f, 0.48f);
        } else {
            wave.color = glm::vec3(1.0f, 0.96f, 0.82f);
        }

        wave.size = ringSize(generator);

        particles.push_back(wave);
    }

    return particles;
}

int main(int argc, char** argv) {
    film::RenderOptions options;
    try {
        options = film::parseOptions(argc, argv);
    } catch (const std::exception& error) {
        std::cerr << "Invalid render options: " << error.what() << '\n';
        std::cerr << "Run --help for supported options.\n";
        return 2;
    }
    if (options.showHelp) {
        std::cout
            << "BigBang native C++ OpenGL preview (M0 particle prototype)\n"
            << "Interactive: ./bigbang [--width W --height H]\n"
            << "Native frame: ./bigbang --time 25 --fps 30 "
               "--width 480 --height 270 --output output/native/25.png\n"
            << "Or: ./bigbang --frame 751 --fps 30 --output output/native/frame751.png\n"
            << "--frame is 1-indexed, time=(frame-1)/fps, film duration 300 s.\n"
            << "Capture is native glReadPixels from the C++ OpenGL pipeline.\n"
            << "The current M0 image is not yet a Blender-quality scene.\n";
        return 0;
    }
    if (!glfwInit()) {
        std::cerr << "ERROR: GLFW initialization failed.\n";
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    if (options.capture) {
        // A hidden OpenGL window provides a one-frame offscreen capture
        // without showing or playing any Blender-rendered media.
        glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
        glfwWindowHint(GLFW_RESIZABLE, GLFW_FALSE);
    }

    GLFWwindow* window = glfwCreateWindow(
        options.width,
        options.height,
        "Big Bang Simulation | Particle Expansion",
        nullptr,
        nullptr
    );

    if (!window) {
        std::cerr << "ERROR: Window creation failed.\n";
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    if (!gladLoadGL((GLADloadfunc)glfwGetProcAddress)) {
        std::cerr << "ERROR: GLAD initialization failed.\n";
        glfwDestroyWindow(window);
        glfwTerminate();
        return -1;
    }

    glfwSetFramebufferSizeCallback(window, framebufferSizeCallback);
    glfwSwapInterval(options.capture ? 0 : 1);

    glEnable(GL_PROGRAM_POINT_SIZE);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE);
    glDisable(GL_DEPTH_TEST);

    std::cout << "\n====================================\n";
    std::cout << "       BIG BANG SIMULATION\n";
    std::cout << "====================================\n";
    std::cout << "OpenGL: " << glGetString(GL_VERSION) << '\n';
    std::cout << "GPU: " << glGetString(GL_RENDERER) << '\n';
    std::cout << "Particles: " << PARTICLE_COUNT << '\n';
    std::cout << "====================================\n";

    int result = 0;

    {
        try {
            Shader shader(
                std::string(PROJECT_ROOT) + "/shaders/particles.vert",
                std::string(PROJECT_ROOT) + "/shaders/particles.frag"
            );

            Shader compositeShader(
                std::string(PROJECT_ROOT) +
                    "/shaders/postprocess/screen.vert",
                std::string(PROJECT_ROOT) +
                    "/shaders/postprocess/composite.frag"
            );

            // M1: independent native fragment-raymarch of the 0–50 s
            // primordial field. No Blender renderer/assets are invoked.
            Shader primordialShader(
                std::string(PROJECT_ROOT) +
                    "/shaders/postprocess/screen.vert",
                std::string(PROJECT_ROOT) +
                    "/shaders/postprocess/primordial_volume.frag"
            );

            int initialWidth = 0;
            int initialHeight = 0;
            glfwGetFramebufferSize(
                window, &initialWidth, &initialHeight
            );

            HDRFramebuffer hdr(
                initialWidth > 0 ? initialWidth : 1,
                initialHeight > 0 ? initialHeight : 1
            );

            BloomEffect bloom(
                std::string(PROJECT_ROOT) + "/shaders/postprocess",
                initialWidth > 0 ? initialWidth : 1,
                initialHeight > 0 ? initialHeight : 1
            );

            std::vector<Particle> particles = createParticles();

            std::vector<ParticleVertex> vertices(particles.size());

            GLuint VAO = 0;
            GLuint VBO = 0;

            glGenVertexArrays(1, &VAO);
            glGenBuffers(1, &VBO);

            glBindVertexArray(VAO);
            glBindBuffer(GL_ARRAY_BUFFER, VBO);

            glBufferData(
                GL_ARRAY_BUFFER,
                vertices.size() * sizeof(ParticleVertex),
                nullptr,
                GL_DYNAMIC_DRAW
            );

            glVertexAttribPointer(
                0, 3, GL_FLOAT, GL_FALSE,
                sizeof(ParticleVertex),
                (void*)offsetof(ParticleVertex, position)
            );
            glEnableVertexAttribArray(0);

            glVertexAttribPointer(
                1, 3, GL_FLOAT, GL_FALSE,
                sizeof(ParticleVertex),
                (void*)offsetof(ParticleVertex, color)
            );
            glEnableVertexAttribArray(1);

            glVertexAttribPointer(
                2, 1, GL_FLOAT, GL_FALSE,
                sizeof(ParticleVertex),
                (void*)offsetof(ParticleVertex, size)
            );
            glEnableVertexAttribArray(2);

            glBindBuffer(GL_ARRAY_BUFFER, 0);
            glBindVertexArray(0);


            // Fullscreen quad: position (x,y) and texture (u,v).
            const float quadVertices[] = {
                -1.0f, -1.0f, 0.0f, 0.0f,
                 1.0f, -1.0f, 1.0f, 0.0f,
                -1.0f,  1.0f, 0.0f, 1.0f,
                 1.0f,  1.0f, 1.0f, 1.0f
            };

            GLuint quadVAO = 0;
            GLuint quadVBO = 0;

            glGenVertexArrays(1, &quadVAO);
            glGenBuffers(1, &quadVBO);

            glBindVertexArray(quadVAO);
            glBindBuffer(GL_ARRAY_BUFFER, quadVBO);

            glBufferData(
                GL_ARRAY_BUFFER,
                sizeof(quadVertices),
                quadVertices,
                GL_STATIC_DRAW
            );

            glEnableVertexAttribArray(0);
            glVertexAttribPointer(
                0, 2, GL_FLOAT, GL_FALSE,
                4 * sizeof(float), (void*)0
            );

            glEnableVertexAttribArray(1);
            glVertexAttribPointer(
                1, 2, GL_FLOAT, GL_FALSE,
                4 * sizeof(float),
                (void*)(2 * sizeof(float))
            );

            glBindBuffer(GL_ARRAY_BUFFER, 0);
            glBindVertexArray(0);

            GLint viewLocation = glGetUniformLocation(
                shader.getID(), "uView"
            );

            GLint projectionLocation = glGetUniformLocation(
                shader.getID(), "uProjection"
            );

            glm::mat4 view = glm::lookAt(
                glm::vec3(0.0f, 0.0f, 12.0f),
                glm::vec3(0.0f, 0.0f, 0.0f),
                glm::vec3(0.0f, 1.0f, 0.0f)
            );

            const double startTime = glfwGetTime();
            if (options.capture) {
                std::cout << "Capture requested: t=" << options.timeSeconds
                          << " s, nominal frame " << options.frame << "/"
                          << (options.fps * film::kDurationSeconds)
                          << " @ " << options.fps << " fps\n";
            }

            std::cout << "Particle system initialized.\n";
            std::cout << "M1.3 native primordial/QGP preview volume active at t=0..90s.\n";
            std::cout << "Press ESC to exit.\n\n";

            while (!glfwWindowShouldClose(window)) {
                if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
                    glfwSetWindowShouldClose(window, true);
                }

                // Time is a pure input to evaluation. Interactive mode uses
                // wall time; capture mode uses the explicit frame/time seek.
                const float elapsed = static_cast<float>(
                    options.capture ? options.timeSeconds : glfwGetTime() - startTime
                );

                for (size_t i = 0; i < particles.size(); ++i) {
                    const Particle& particle = particles[i];

                    vertices[i].position =
                        particle.position + particle.velocity * elapsed;

                    vertices[i].color = particle.color;
                    vertices[i].size = particle.size;
                }

                glBindBuffer(GL_ARRAY_BUFFER, VBO);

                glBufferSubData(
                    GL_ARRAY_BUFFER,
                    0,
                    vertices.size() * sizeof(ParticleVertex),
                    vertices.data()
                );

                int width = 0;
                int height = 0;
                glfwGetFramebufferSize(window, &width, &height);

                if (height == 0) {
                    glfwPollEvents();
                    continue;
                }

                hdr.resize(width, height);
                bloom.resize(width, height);
                hdr.bind();

                glViewport(0, 0, width, height);

                glm::mat4 projection = glm::perspective(
                    glm::radians(45.0f),
                    static_cast<float>(width) / static_cast<float>(height),
                    0.1f,
                    100.0f
                );

                glClearColor(0.002f, 0.001f, 0.008f, 1.0f);
                glClear(GL_COLOR_BUFFER_BIT);

                if (elapsed <= 90.0f) {
                    // Fullscreen world-space volume raymarch: camera pose and
                    // focal lengths sampled from Blender's reference keys.
                    // The cinematic shader is an independent C++/GLSL
                    // implementation, not a converted Cycles node graph.
                    glDisable(GL_BLEND);
                    const auto pose = primordial::cameraAt(elapsed);
                    const glm::vec3 forward =
                        glm::normalize(-pose.position);
                    const glm::vec3 right = glm::normalize(glm::cross(
                        forward, glm::vec3(0.0f,0.0f,1.0f)));
                    const glm::vec3 up = glm::normalize(glm::cross(
                        right, forward));
                    primordialShader.use();
                    const GLuint program = primordialShader.getID();
                    const float aspect = float(width)/float(height);
                    glUniform1f(glGetUniformLocation(program,"uTime"),elapsed);
                    glUniform3fv(glGetUniformLocation(program,"uCameraPos"),
                                 1,glm::value_ptr(pose.position));
                    glUniform3fv(glGetUniformLocation(program,"uCameraForward"),
                                 1,glm::value_ptr(forward));
                    glUniform3fv(glGetUniformLocation(program,"uCameraRight"),
                                 1,glm::value_ptr(right));
                    glUniform3fv(glGetUniformLocation(program,"uCameraUp"),
                                 1,glm::value_ptr(up));
                    glUniform1f(glGetUniformLocation(program,"uAspect"),aspect);
                    glUniform1f(
                        glGetUniformLocation(program,"uTanHalfFovY"),
                        primordial::verticalTanHalfFov(pose,aspect));
                    glBindVertexArray(quadVAO);
                    glDrawArrays(GL_TRIANGLE_STRIP,0,4);
                    glBindVertexArray(0);
                } else {
                    // Scenes after 90 seconds still use the M0 particle prototype.
                    // These are placeholders pending M2/M3 native ports.
                    shader.use();
                    glUniformMatrix4fv(
                        viewLocation,1,GL_FALSE,glm::value_ptr(view));
                    glUniformMatrix4fv(
                        projectionLocation,1,GL_FALSE,
                        glm::value_ptr(projection));
                    glBindVertexArray(VAO);
                    glDrawArrays(GL_POINTS,0,
                        static_cast<GLsizei>(vertices.size()));
                    glBindVertexArray(0);
                }

                // Stop rendering to the HDR framebuffer.
                HDRFramebuffer::unbind();

                GLuint bloomTexture = bloom.render(
                    hdr.getColorTexture(),
                    quadVAO
                );

                glViewport(0, 0, width, height);

                // Present the HDR texture on screen.
                glDisable(GL_BLEND);

                glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
                glClear(GL_COLOR_BUFFER_BIT);

                compositeShader.use();

                glActiveTexture(GL_TEXTURE0);
                glBindTexture(
                    GL_TEXTURE_2D,
                    hdr.getColorTexture()
                );

                // Blurred HDR highlights.
                glActiveTexture(GL_TEXTURE1);
                glBindTexture(
                    GL_TEXTURE_2D,
                    bloomTexture
                );

                glUniform1i(
                    glGetUniformLocation(
                        compositeShader.getID(), "uScene"
                    ), 0
                );

                glUniform1i(
                    glGetUniformLocation(
                        compositeShader.getID(), "uBloomBlur"
                    ), 1
                );

                glUniform1f(
                    glGetUniformLocation(
                        compositeShader.getID(), "uBloomStrength"
                    ), 1.2f
                );

                glUniform1f(
                    glGetUniformLocation(
                        compositeShader.getID(), "uExposure"
                    ), 1.0f
                );

                glBindVertexArray(quadVAO);
                glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
                glBindVertexArray(0);

                glActiveTexture(GL_TEXTURE1);
                glBindTexture(GL_TEXTURE_2D, 0);

                glActiveTexture(GL_TEXTURE0);
                glBindTexture(GL_TEXTURE_2D, 0);

                glEnable(GL_BLEND);

                if (options.capture) {
                    // Read the actual C++/GLSL-composited default back buffer.
                    // glReadPixels is bottom-up; PngWriter flips it to PNG rows.
                    std::vector<std::uint8_t> pixels(
                        static_cast<std::size_t>(width) *
                        static_cast<std::size_t>(height) * 3u
                    );
                    glFinish();
                    glPixelStorei(GL_PACK_ALIGNMENT, 1);
                    glReadBuffer(GL_BACK);
                    glReadPixels(0, 0, width, height, GL_RGB,
                                 GL_UNSIGNED_BYTE, pixels.data());
                    if (glGetError() != GL_NO_ERROR) {
                        throw std::runtime_error("OpenGL readback failed");
                    }
                    png::writeRgbBottomUp(options.output, width, height, pixels);
                    std::cout << "Native C++ PNG: " << options.output
                              << " (" << width << "x" << height << ")\n";
                    break;
                }
                glfwSwapBuffers(window);
                glfwPollEvents();
            }

            glDeleteBuffers(1, &quadVBO);
            glDeleteVertexArrays(1, &quadVAO);

            glDeleteBuffers(1, &VBO);
            glDeleteVertexArrays(1, &VAO);
        }
        catch (const std::exception& error) {
            std::cerr << "ERROR: " << error.what() << '\n';
            result = -1;
        }
    }

    glfwDestroyWindow(window);
    glfwTerminate();

    return result;
}
