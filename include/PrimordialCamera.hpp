#ifndef PRIMORDIAL_CAMERA_HPP
#define PRIMORDIAL_CAMERA_HPP

#include <glm/glm.hpp>
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace primordial {

struct CameraPose {
    glm::vec3 position;
    float focalLengthMm;
    float sensorWidthMm;
};

// Shared key-time and lens data from primordial-universe-animation's
// build_universe.py (reference: visual/issue-2-coherent-opening-inflation).
// Target=(0,0,0), Blender camera TRACK_NEGATIVE_Z with UP_Y; native C++
// reconstructs a stable world-Z-up view. Blender's Bezier FCurves are *not*
// yet reproduced exactly; the approximation is intentional and disclosed.
struct CameraKey {
    float seconds;
    glm::vec3 position;
    float lensMm;
};

inline CameraPose cameraAt(float seconds) {
    if (!std::isfinite(seconds) || seconds < 0.0f || seconds > 90.0f)
        throw std::out_of_range("Primordial camera supports 0..90 seconds.");
    const CameraKey keys[] = {
        {0.0f, {0.0f, -18.0f, 3.0f}, 68.0f},
        {12.0f, {0.0f, -15.0f, 2.0f}, 60.0f},
        {20.0f, {0.0f, -12.0f, 2.0f}, 52.0f},
        {24.0f, {0.2f, -10.2f, 2.2f}, 58.0f},
        {28.0f, {0.9f, -8.0f, 2.5f}, 66.0f},
        {35.0f, {2.2f, -5.2f, 3.1f}, 82.0f},
        {43.0f, {0.7f, -2.2f, 3.0f}, 76.0f},
        {50.0f, {-2.0f, 1.0f, 3.2f}, 62.0f},
        {70.0f, {2.0f, -8.0f, 2.0f}, 65.0f},
        {90.0f, {0.0f, -7.0f, 2.5f}, 70.0f},
    };
    for (std::size_t i = 1; i < sizeof(keys)/sizeof(keys[0]); ++i) {
        if (seconds <= keys[i].seconds) {
            const auto& a = keys[i-1];
            const auto& b = keys[i];
            float u = (seconds-a.seconds) / (b.seconds-a.seconds);
            // Cubic smoothstep approximates the original Blender ease, but
            // it is not a byte-for-byte Blender FCurve evaluation.
            u = u * u * (3.0f - 2.0f*u);
            return {glm::mix(a.position, b.position, u),
                    a.lensMm + (b.lensMm-a.lensMm)*u, 36.0f};
        }
    }
    return {keys[9].position, keys[9].lensMm, 36.0f};
}

inline float verticalTanHalfFov(const CameraPose& camera, float aspect) {
    if (!(aspect>0.0f) || !std::isfinite(aspect))
        throw std::invalid_argument("Positive finite camera aspect required");
    return camera.sensorWidthMm / (2.0f * camera.focalLengthMm * aspect);
}

} // namespace primordial

#endif
