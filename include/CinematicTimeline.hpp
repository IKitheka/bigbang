#ifndef CINEMATIC_TIMELINE_HPP
#define CINEMATIC_TIMELINE_HPP

// V12 lecturer review: keep the 300-second film, shorten early epochs and
// dedicate its final three minutes to Solar System formation.
// These clocks are cinematic mappings, NOT physical cosmological timescales.
#include <algorithm>

namespace cinematic {
inline float mapInterval(float t, float a, float b, float u, float v) {
    const float p=std::clamp((t-a)/(b-a),0.0f,1.0f);
    return u+(v-u)*p;
}
inline float legacySceneTime(float filmTime) {
    const float t=std::clamp(filmTime,0.0f,299.999f);
    if(t<=15.0f) return mapInterval(t,0,15,0,20);        // origin
    if(t<=35.0f) return mapInterval(t,15,35,20,50);      // inflation
    if(t<=50.0f) return mapInterval(t,35,50,50,82);      // hot plasma
    if(t<=65.0f) return mapInterval(t,50,65,82,116);     // nuclei
    if(t<=73.0f) return mapInterval(t,65,73,116,149);    // opaque plasma
    if(t<=80.0f) return mapInterval(t,73,80,149,176);    // recombination
    if(t<=87.0f) return mapInterval(t,80,87,176,196);    // dark ages
    if(t<=105.0f) return mapInterval(t,87,105,196,240);  // cosmic dawn
    if(t<=130.0f) return mapInterval(t,105,130,240,260); // galaxy to cloud
    return 260.0f;
}
// Re-time the approved formation shader across 182 film seconds. Nonlinear
// mapping increases time spent on dust, planetesimals and planetary embryos.
inline float solarSceneTime(float filmTime) {
    const float t=std::clamp(filmTime,0.0f,299.999f);
    if(t<=118.0f) return 259.0f;
    if(t<=145.0f) return mapInterval(t,118,145,259,264);
    if(t<=180.0f) return mapInterval(t,145,180,264,268);
    if(t<=215.0f) return mapInterval(t,180,215,268,273);
    if(t<=245.0f) return mapInterval(t,215,245,273,278);
    if(t<=265.0f) return mapInterval(t,245,265,278,285);
    if(t<=283.0f) return mapInterval(t,265,283,285,290);
    if(t<=291.0f) return mapInterval(t,283,291,290,294);
    return mapInterval(t,291,300,294,299.999f);
}
// V12.1: cloud entry overlaps the final galaxy approach; the same cloud
// then collapses into the disc in world space. Film length is unchanged.
constexpr float kSolarStart=110.0f;
constexpr float kSolarFullReveal=128.0f;
} // namespace cinematic
#endif
