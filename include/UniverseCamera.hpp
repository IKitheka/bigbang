#ifndef UNIVERSE_CAMERA_HPP
#define UNIVERSE_CAMERA_HPP
#include "PrimordialCamera.hpp"

namespace cinematic {
// Preserve the approved early camera evaluation exactly. Later slow dollies
// reveal larger domains without changing view direction at chapter boundaries.
inline primordial::CameraPose cameraAt(float t) {
    if (t <= 90.0f) return primordial::cameraAt(t);
    const primordial::CameraKey keys[] = {
        {90, {0,-7,2.5f},70}, {130,{2,-11,3},58},
        {170,{0,-16,4},55}, {200,{.8f,-18,4},52},
        {240,{2,-21,5},46}, {270,{2.8f,-21,6.5f},46},
        {300,{2.6f,-16,6},53}
    };
    t = std::min(t,300.0f);
    for (std::size_t i=1;i<sizeof(keys)/sizeof(keys[0]);++i) {
        if (t<=keys[i].seconds) {
            const auto& a=keys[i-1]; const auto& b=keys[i];
            float u=(t-a.seconds)/(b.seconds-a.seconds);
            u=u*u*(3.0f-2.0f*u);
            return {glm::mix(a.position,b.position,u),
                    a.lensMm+(b.lensMm-a.lensMm)*u,36.0f};
        }
    }
    return {keys[6].position,keys[6].lensMm,36.0f};
}

// A hero-camera target evolves only in cosmic dawn. Earlier chapters keep
// their exact original origin-facing view direction, preserving the user's
// approved 18–22s C++ reference. The star-forming galaxy coordinates are
// intentionally shared with lateGalaxyCenter(0) in cosmic_late.glsl.
inline glm::vec3 targetAt(float t) {
    if (t<=240.0f) return glm::vec3(0.0f);
    float u=std::clamp((t-240.0f)/50.0f,0.0f,1.0f);
    u=u*u*(3.0f-2.0f*u);
    return glm::vec3(0.8f,3.5f,0.1f)*u;
}
}
#endif
