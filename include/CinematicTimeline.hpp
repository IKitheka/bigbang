#ifndef CINEMATIC_TIMELINE_HPP
#define CINEMATIC_TIMELINE_HPP

// Translate five-minute presentation time to our previous deterministic
// eight-epoch renderer time. This is a visual *storytelling clock*, NOT a
// cosmological time-to-seconds calculation. All existing shaders/cameras
// continue to receive continuous finite values, without editing protected
// early-universe geometry. Final 40s are reserved for the new solar system.
#include <algorithm>

namespace cinematic {
inline float legacySceneTime(float filmTime) {
    const float t=std::clamp(filmTime,0.0f,299.999f);
    // Narrative film [start,end], source visual [start,end].
    // Compress the previously long dark ages to 20 seconds, preserve the
    // beloved origin (0–50) and show galaxies before the solar-system finale.
    if(t<=50.0f) return t;
    if(t<=82.0f) return 50.0f + (t-50.0f)*(40.0f/32.0f);
    if(t<=116.0f) return 90.0f + (t-82.0f)*(40.0f/34.0f);
    if(t<=149.0f) return 130.0f + (t-116.0f)*(40.0f/33.0f);
    if(t<=176.0f) return 170.0f + (t-149.0f)*(30.0f/27.0f);
    if(t<=196.0f) return 200.0f + (t-176.0f)*2.0f;
    if(t<=260.0f) return 240.0f + (t-196.0f)*(59.9f/64.0f);
    return 299.9f;
}
constexpr float kSolarStart=260.0f;
constexpr float kSolarFullReveal=268.0f;
} // namespace cinematic
#endif
