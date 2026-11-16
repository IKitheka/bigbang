#ifndef CINEMATIC_STORY_HPP
#define CINEMATIC_STORY_HPP

// Narrative contract for the native C++ film. No drawing code is implied.
// The fixed-pipeline GLUT reference provides narrative topics only; render
// implementations belong in the GLFW/OpenGL/GLSL engine.
#include <array>
#include <cstdint>
#include <stdexcept>

namespace cinematic {

enum class Epoch : std::uint8_t {
    AbstractOrigin,
    Inflation,
    QuarkGluonPlasma,
    PrimordialNucleosynthesis,
    OpaquePlasma,
    RecombinationCmb,
    DarkAges,
    CosmicDawnGalaxies,
    SolarSystem,
};

struct Chapter {
    Epoch epoch;
    int beginSecond;   // inclusive
    int endSecond;     // exclusive
    const char* key;   // machine-readable
    const char* narrative;
};

constexpr int kFilmDurationSeconds = 300;

// V12: nine STORY chapters; not to be confused with the nine graphics pipeline stages.
constexpr std::array<Chapter, 9> kChapters{{
    {Epoch::AbstractOrigin, 0, 15, "abstract_origin", "Bright speculative origin and ignition"},
    {Epoch::Inflation, 15, 35, "inflation", "Rapid expansion of primordial fluctuations"},
    {Epoch::QuarkGluonPlasma, 35, 50, "quark_gluon_plasma", "Hot early-universe plasma"},
    {Epoch::PrimordialNucleosynthesis, 50, 65, "nucleosynthesis", "Illustration of light nucleus formation"},
    {Epoch::OpaquePlasma, 65, 73, "opaque_plasma", "Light-scattering ionized matter"},
    {Epoch::RecombinationCmb, 73, 80, "recombination_cmb", "Neutral atoms and transparent universe"},
    {Epoch::DarkAges, 80, 87, "dark_ages", "Brief pre-stellar darkness"},
    {Epoch::CosmicDawnGalaxies, 87, 120, "cosmic_dawn_galaxies", "First stars, galaxies and the molecular-cloud journey"},
    {Epoch::SolarSystem, 120, 300, "solar_system", "Young Sun, accretion, planetesimals, eight planets and Earth"},
}};

constexpr bool isWellFormed() {
    if (kChapters.front().beginSecond != 0 ||
        kChapters.back().endSecond != kFilmDurationSeconds) {
        return false;
    }
    for (std::size_t i = 0; i < kChapters.size(); ++i) {
        if (!(kChapters[i].beginSecond < kChapters[i].endSecond))
            return false;
        if (i && kChapters[i-1].endSecond != kChapters[i].beginSecond)
            return false;
    }
    return true;
}
static_assert(isWellFormed(), "The eight film chapters must be contiguous.");

inline const Chapter& chapterAt(double seconds) {
    // Non-finite values cannot satisfy any valid window. Check deliberately
    // without requiring non-constexpr C library math during constant tests.
    if (!(seconds >= 0.0 && seconds < kFilmDurationSeconds)) {
        throw std::out_of_range("Story time must be in [0, 300) seconds.");
    }
    for (const auto& c : kChapters) {
        if (seconds >= c.beginSecond && seconds < c.endSecond)
            return c;
    }
    throw std::logic_error("Cinematic story has a timeline gap.");
}

}  // namespace cinematic

#endif
