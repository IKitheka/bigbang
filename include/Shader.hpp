#ifndef SHADER_HPP
#define SHADER_HPP

#include <string>
#include <glad/gl.h>

class Shader {
public:
    Shader(const std::string& vertexPath,
           const std::string& fragmentPath);

    ~Shader();

    Shader(const Shader&) = delete;
    Shader& operator=(const Shader&) = delete;

    Shader(Shader&& other) noexcept;
    Shader& operator=(Shader&& other) noexcept;

    void use() const;

    GLuint getID() const;

private:
    GLuint programID = 0;

    std::string readFile(const std::string& path);
    GLuint compileShader(GLenum type, const std::string& source);
};

#endif
