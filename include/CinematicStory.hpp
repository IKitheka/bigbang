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
};

struct Chapter {
    Epoch epoch;
    int beginSecond;   // inclusive
    int endSecond;     // exclusive
    const char* key;   // machine-readable
    const char* narrative;
};

constexpr int kFilmDurationSeconds = 300;

constexpr std::array<Chapter, 8> kChapters{{
    {Epoch::AbstractOrigin, 0, 20, "abstract_origin",
     "Speculative Planck-era fluctuation visual"},
    {Epoch::Inflation, 20, 50, "inflation",
     "Expanding spatial correlation scales"},
    {Epoch::QuarkGluonPlasma, 50, 90, "quark_gluon_plasma",
     "Dense early-universe radiation-coupled continuum"},
    {Epoch::PrimordialNucleosynthesis, 90, 130, "nucleosynthesis",
     "Primordial nuclear reactions, not toy atom diagrams"},
    {Epoch::OpaquePlasma, 130, 170, "opaque_plasma",
     "Optically thick photon-electron-baryon medium"},
    {Epoch::RecombinationCmb, 170, 200, "recombination_cmb",
     "Optical thinning and illustrative CMB perturbations"},
    {Epoch::DarkAges, 200, 240, "dark_ages",
     "Near-dark neutral gas and developing density structure"},
    {Epoch::CosmicDawnGalaxies, 240, 300, "cosmic_dawn_galaxies",
     "First luminous stars and evolving galaxies"},
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
