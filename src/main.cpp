#include <glad/gl.h>

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>

#include "Shader.hpp"

#include <iostream>
#include <exception>

void framebufferSizeCallback(GLFWwindow* window, int width, int height) {
    (void)window;
    glViewport(0, 0, width, height);
}

int main() {
    if (!glfwInit()) {
        std::cerr << "ERROR: Failed to initialize GLFW.\n";
        return -1;
    }

    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    GLFWwindow* window = glfwCreateWindow(
        1280,
        720,
        "Big Bang Simulation | OpenGL",
        nullptr,
        nullptr
    );

    if (!window) {
        std::cerr << "ERROR: Failed to create GLFW window.\n";
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);

    if (!gladLoadGL((GLADloadfunc)glfwGetProcAddress)) {
        std::cerr << "ERROR: Failed to initialize GLAD.\n";
        glfwDestroyWindow(window);
        glfwTerminate();
        return -1;
    }

    glfwSetFramebufferSizeCallback(window, framebufferSizeCallback);

    glViewport(0, 0, 1280, 720);
    glfwSwapInterval(1);

    std::cout << "====================================\n";
    std::cout << "       BIG BANG SIMULATION\n";
    std::cout << "====================================\n";
    std::cout << "OpenGL Version: " << glGetString(GL_VERSION) << '\n';
    std::cout << "GPU Renderer: " << glGetString(GL_RENDERER) << '\n';
    std::cout << "====================================\n";

    int result = 0;

    {
        try {
            Shader shader(
                std::string(PROJECT_ROOT) + "/shaders/basic.vert",
                std::string(PROJECT_ROOT) + "/shaders/basic.frag"
            );

            float vertices[] = {
                -0.6f, -0.5f, 0.0f,
                 0.6f, -0.5f, 0.0f,
                 0.0f,  0.6f, 0.0f
            };

            GLuint VAO = 0;
            GLuint VBO = 0;

            glGenVertexArrays(1, &VAO);
            glGenBuffers(1, &VBO);

            glBindVertexArray(VAO);

            glBindBuffer(GL_ARRAY_BUFFER, VBO);
            glBufferData(
                GL_ARRAY_BUFFER,
                sizeof(vertices),
                vertices,
                GL_STATIC_DRAW
            );

            glVertexAttribPointer(
                0,
                3,
                GL_FLOAT,
                GL_FALSE,
                3 * sizeof(float),
                nullptr
            );

            glEnableVertexAttribArray(0);

            glBindBuffer(GL_ARRAY_BUFFER, 0);
            glBindVertexArray(0);

            std::cout << "Shader program loaded successfully.\n";
            std::cout << "Triangle geometry initialized.\n";
            std::cout << "Rendering window is ready.\n";
            std::cout << "Press ESC to exit.\n";

            while (!glfwWindowShouldClose(window)) {
                if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
                    glfwSetWindowShouldClose(window, true);
                }

                glClearColor(0.005f, 0.005f, 0.02f, 1.0f);
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

                shader.use();

                glBindVertexArray(VAO);
                glDrawArrays(GL_TRIANGLES, 0, 3);
                glBindVertexArray(0);

                glfwSwapBuffers(window);
                glfwPollEvents();
            }

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
