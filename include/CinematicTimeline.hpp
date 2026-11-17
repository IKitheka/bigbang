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
// V12.2: keep the 300-second film, compress diffuse gas and dust,
// then reserve seven consecutive planet portraits plus the Earth finale.
// This maps absolute film seconds to the approved source shader clock;
// physical cosmological time is intentionally not represented here.
inline float solarSceneTime(float filmTime) {
    const float t=std::clamp(filmTime,0.0f,299.999f);
    if(t<=110.0f) return 259.0f;
    if(t<=138.0f) return mapInterval(t,110,138,259,264);
    if(t<=160.0f) return mapInterval(t,138,160,264,272);
    if(t<=185.0f) return mapInterval(t,160,185,272,283);
    if(t<=271.0f) return mapInterval(t,185,271,283,292);
    if(t<=283.0f) return mapInterval(t,271,283,292,295);
    return mapInterval(t,283,300,295,299.999f);
}
struct PlanetFlyby {
    const char* name;
    int shaderPlanetIndex;
    float startSecond;
    float endSecond;
};
constexpr PlanetFlyby kPlanetFlybys[8] = {
    {"Mercury",0,185.0f,197.0f}, {"Venus",1,197.0f,209.0f},
    {"Mars",3,209.0f,221.0f}, {"Jupiter",4,221.0f,234.0f},
    {"Saturn",5,234.0f,247.0f}, {"Uranus",6,247.0f,259.0f},
    {"Neptune",7,259.0f,271.0f}, {"Earth",2,283.0f,300.0f}
};

// V12.1: cloud entry overlaps the final galaxy approach; the same cloud
// then collapses into the disc in world space. Film length is unchanged.
constexpr float kSolarStart=110.0f;
constexpr float kSolarFullReveal=118.0f;
} // namespace cinematic
#endif
