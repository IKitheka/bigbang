#include "Shader.hpp"

#include <fstream>
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <filesystem>

std::string Shader::readFile(const std::string& path) {
    std::ifstream file(path);

    if (!file.is_open()) {
        throw std::runtime_error("Could not open shader file: " + path);
    }

    std::stringstream buffer;
    buffer << file.rdbuf();

    const std::string source = buffer.str();
    // Existing shaders without includes keep exactly their original bytes.
    if (source.find("#include \"") == std::string::npos) return source;
    std::istringstream lines(source);
    std::string line, expanded;
    while (std::getline(lines,line)) {
        if (line.rfind("#include \"",0) == 0) {
            const auto end=line.find('"',10);
            if (end==std::string::npos) throw std::runtime_error("Malformed GLSL include");
            const auto child=line.substr(10,end-10);
            if (child.find("..")!=std::string::npos || child.find('/')!=std::string::npos)
                throw std::runtime_error("GLSL include must be a sibling filename");
            expanded += readFile((std::filesystem::path(path).parent_path()/child).string());
            expanded += '\n';
        } else expanded += line+'\n';
    }
    return expanded;
}

GLuint Shader::compileShader(GLenum type, const std::string& source) {
    GLuint shader = glCreateShader(type);

    const char* sourceCode = source.c_str();
    glShaderSource(shader, 1, &sourceCode, nullptr);
    glCompileShader(shader);

    GLint success = GL_FALSE;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);

    if (!success) {
        GLint logLength = 0;
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &logLength);

        std::string log(static_cast<size_t>(logLength), '\0');
        glGetShaderInfoLog(shader, logLength, nullptr, log.data());

        glDeleteShader(shader);

        throw std::runtime_error(
            "Shader compilation failed:\n" + log
        );
    }

    return shader;
}

Shader::Shader(
    const std::string& vertexPath,
    const std::string& fragmentPath
) {
    std::string vertexSource = readFile(vertexPath);
    std::string fragmentSource = readFile(fragmentPath);

    GLuint vertexShader = compileShader(GL_VERTEX_SHADER, vertexSource);
    GLuint fragmentShader = 0;

    try {
        fragmentShader = compileShader(GL_FRAGMENT_SHADER, fragmentSource);

        programID = glCreateProgram();

        glAttachShader(programID, vertexShader);
        glAttachShader(programID, fragmentShader);
        glLinkProgram(programID);

        GLint success = GL_FALSE;
        glGetProgramiv(programID, GL_LINK_STATUS, &success);

        if (!success) {
            GLint logLength = 0;
            glGetProgramiv(programID, GL_INFO_LOG_LENGTH, &logLength);

            std::string log(static_cast<size_t>(logLength), '\0');
            glGetProgramInfoLog(programID, logLength, nullptr, log.data());

            throw std::runtime_error(
                "Shader linking failed:\n" + log
            );
        }
    }
    catch (...) {
        if (programID != 0) {
            glDeleteProgram(programID);
            programID = 0;
        }

        glDeleteShader(vertexShader);

        if (fragmentShader != 0) {
            glDeleteShader(fragmentShader);
        }

        throw;
    }

    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
}

Shader::~Shader() {
    if (programID != 0) {
        glDeleteProgram(programID);
    }
}

Shader::Shader(Shader&& other) noexcept
    : programID(std::exchange(other.programID, 0)) {
}

Shader& Shader::operator=(Shader&& other) noexcept {
    if (this != &other) {
        if (programID != 0) {
            glDeleteProgram(programID);
        }

        programID = std::exchange(other.programID, 0);
    }

    return *this;
}

void Shader::use() const {
    glUseProgram(programID);
}

GLuint Shader::getID() const {
    return programID;
}
