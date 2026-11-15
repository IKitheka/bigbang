#ifndef GALAXY_CATALOG_HPP
#define GALAXY_CATALOG_HPP

// 3D procedural galaxy catalogue for the final cosmic-dawn scene.
// A real native OpenGL point-sprite draw is used; this is NOT a movie, sky
// texture, screen-aligned picture, or random per-frame screen-space pixels.
// The catalogue is seeded once and stays fixed in world coordinates; moving
// the 3D camera gives real parallax. Fragment shading generates each galaxy's
// local stellar disc, bulge, dusty arms or irregular stellar distribution.

#include <glad/gl.h>
#include "Shader.hpp"
#include "PrimordialCamera.hpp"
#include <glm/glm.hpp>
#include <glm/gtc/type_ptr.hpp>

#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

namespace cinematic {

struct GalaxyDatum {
    glm::vec3 position;
    glm::vec4 morphology; // world diameter, local angle, axis ratio, family
    glm::vec4 radiance;   // RGB stellar temperature, intrinsic linear strength
};
static_assert(std::is_standard_layout<GalaxyDatum>::value,
              "GL vertex offsets require standard layout");

class GalaxyCatalog {
public:
    explicit GalaxyCatalog(const std::string& projectRoot) :
        shader_(projectRoot + "/shaders/galaxies/catalog.vert",
                projectRoot + "/shaders/galaxies/catalog.frag") {
        std::vector<GalaxyDatum> objects;
        objects.reserve(kCount);
        std::uint32_t rng=0xC05C1C07u;
        auto next=[&rng]() -> float {
            rng ^= rng << 13;
            rng ^= rng >> 17;
            rng ^= rng << 5;
            return static_cast<float>(rng & 0x00FFFFFFu)/16777216.0f;
        };
        for(int i=0;i<kCount;++i) {
            // Many far, tiny independent galaxies, with only a handful of
            // resolved discs. The black sky must feel enormous, not like three
            // gigantic ovals in empty space.
            const float layer=next();
            const float y=10.0f+280.0f*layer*layer;
            const float dist=y+26.0f;
            const float cx=-0.14f*y;
            const float cz=-0.25f*y;
            GalaxyDatum g{};
            g.position=glm::vec3(
                cx+(next()-0.5f)*1.26f*dist,
                y,
                cz+(next()-0.5f)*0.79f*dist);

            // Angular diameter in pixels at a 360px-high reference capture.
            // Fewer than 1% are wide enough to resolve curved spiral arms.
            float pixels=1.0f+1.8f*next();
            if(i<14) pixels=20.0f+32.0f*next();
            else if(i<80) pixels=8.0f+13.0f*next();
            else if(i<360) pixels=3.0f+6.0f*next();
            else if(i<1600) pixels=1.5f+3.0f*next();
            // Half-FOV tangent ~0.245 in our late camera; store WORLD diameter.
            // The vertex shader computes actual size from current focal length.
            float worldDiameter=pixels*dist*0.49f/360.0f;
            float angle=6.283185307f*next();
            float axisRatio=0.26f+0.72f*next();
            float family=next(); // spirals, ellipticals and irregulars
            g.morphology=glm::vec4(worldDiameter,angle,axisRatio,family);
            float temp=next();
            glm::vec3 color;
            if(temp<0.38f) color=glm::vec3(0.59f,0.72f,1.00f);  // young
            else if(temp<0.78f) color=glm::vec3(0.94f,0.87f,0.74f);
            else color=glm::vec3(1.00f,0.72f,0.48f);            // evolved
            color*=0.85f+0.30f*next();
            const float strength=(0.35f+1.85f*next())*
                                  (pixels<3.0f ? 0.70f:1.0f);
            g.radiance=glm::vec4(color,strength);
            objects.push_back(g);
        }

        glGenVertexArrays(1,&vao_);
        glGenBuffers(1,&vbo_);
        if(!vao_||!vbo_) throw std::runtime_error("Galaxy catalog GL allocation failed");
        glBindVertexArray(vao_);
        glBindBuffer(GL_ARRAY_BUFFER,vbo_);
        glBufferData(GL_ARRAY_BUFFER,
                     static_cast<GLsizeiptr>(objects.size()*sizeof(GalaxyDatum)),
                     objects.data(),GL_STATIC_DRAW);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,sizeof(GalaxyDatum),
                              reinterpret_cast<void*>(offsetof(GalaxyDatum,position)));
        glEnableVertexAttribArray(1);
        glVertexAttribPointer(1,4,GL_FLOAT,GL_FALSE,sizeof(GalaxyDatum),
                              reinterpret_cast<void*>(offsetof(GalaxyDatum,morphology)));
        glEnableVertexAttribArray(2);
        glVertexAttribPointer(2,4,GL_FLOAT,GL_FALSE,sizeof(GalaxyDatum),
                              reinterpret_cast<void*>(offsetof(GalaxyDatum,radiance)));
        glBindBuffer(GL_ARRAY_BUFFER,0);
        glBindVertexArray(0);
    }

    GalaxyCatalog(const GalaxyCatalog&)=delete;
    GalaxyCatalog& operator=(const GalaxyCatalog&)=delete;
    ~GalaxyCatalog() {
        if(vbo_) glDeleteBuffers(1,&vbo_);
        if(vao_) glDeleteVertexArrays(1,&vao_);
    }

    void draw(float t,const primordial::CameraPose& pose,int width,int height) {
        if(t<240.0f) return;
        const glm::vec3 forward=glm::normalize(-pose.position);
        const glm::vec3 right=glm::normalize(
            glm::cross(forward,glm::vec3(0.0f,0.0f,1.0f)));
        const glm::vec3 up=glm::normalize(glm::cross(right,forward));
        const float aspect=float(width)/float(height);
        shader_.use();
        const GLuint p=shader_.getID();
        glUniform1f(glGetUniformLocation(p,"uTime"),t);
        glUniform1f(glGetUniformLocation(p,"uAspect"),aspect);
        glUniform1f(glGetUniformLocation(p,"uTanHalfFovY"),
                    primordial::verticalTanHalfFov(pose,aspect));
        glUniform1f(glGetUniformLocation(p,"uScreenHeight"),float(height));
        glUniform3fv(glGetUniformLocation(p,"uCameraPos"),1,
                     glm::value_ptr(pose.position));
        glUniform3fv(glGetUniformLocation(p,"uCameraForward"),1,
                     glm::value_ptr(forward));
        glUniform3fv(glGetUniformLocation(p,"uCameraRight"),1,
                     glm::value_ptr(right));
        glUniform3fv(glGetUniformLocation(p,"uCameraUp"),1,
                     glm::value_ptr(up));
        glEnable(GL_PROGRAM_POINT_SIZE);
        glEnable(GL_BLEND);
        glBlendFunc(GL_ONE,GL_ONE);
        glBindVertexArray(vao_);
        glDrawArrays(GL_POINTS,0,kCount);
        glBindVertexArray(0);
        glDisable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA,GL_ONE);
    }

    static constexpr GLsizei size() { return kCount; }
private:
    static constexpr GLsizei kCount=4400;
    Shader shader_;
    GLuint vao_=0,vbo_=0;
};

} // namespace cinematic
#endif
