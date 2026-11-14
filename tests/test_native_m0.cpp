#include "FilmClock.hpp"
#include "CinematicStory.hpp"
#include "PrimordialCamera.hpp"
#include "RenderOptions.hpp"
#include "PngWriter.hpp"

#include <cassert>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
film::RenderOptions parse(const std::vector<const char*>& args) {
    return film::parseOptions(static_cast<int>(args.size()), args.data());
}
void invalid(const std::vector<const char*>& args) {
    bool threw = false;
    try {
        (void)parse(args);
    } catch (const std::exception&) {
        threw = true;
    }
    assert(threw && "Expected invalid argument to be rejected");
}
std::uint32_t bigEndian(const std::vector<std::uint8_t>& bytes, std::size_t at) {
    return (std::uint32_t(bytes.at(at)) << 24) |
           (std::uint32_t(bytes.at(at + 1)) << 16) |
           (std::uint32_t(bytes.at(at + 2)) << 8) |
           std::uint32_t(bytes.at(at + 3));
}
}

int main() {
    // The narrative comes from the source video's full story, compressed into
    // the previously agreed eight-scene 300-second cinematic main cut.
    static_assert(cinematic::isWellFormed(), "No gaps/overlaps in story");
    assert(cinematic::kChapters.size() == 8);
    assert(cinematic::kFilmDurationSeconds == film::kDurationSeconds);
    const auto& origin = cinematic::chapterAt(0.0);
    const auto& inflation = cinematic::chapterAt(20.0);
    const auto& qgp = cinematic::chapterAt(50.0);
    const auto& nuclei = cinematic::chapterAt(90.0);
    const auto& opaque = cinematic::chapterAt(130.0);
    const auto& cmb = cinematic::chapterAt(170.0);
    const auto& dark = cinematic::chapterAt(200.0);
    const auto& galaxies = cinematic::chapterAt(240.0);
    assert(origin.epoch == cinematic::Epoch::AbstractOrigin);
    assert(inflation.epoch == cinematic::Epoch::Inflation);
    assert(qgp.epoch == cinematic::Epoch::QuarkGluonPlasma);
    assert(nuclei.epoch == cinematic::Epoch::PrimordialNucleosynthesis);
    assert(opaque.epoch == cinematic::Epoch::OpaquePlasma);
    assert(cmb.epoch == cinematic::Epoch::RecombinationCmb);
    assert(dark.epoch == cinematic::Epoch::DarkAges);
    assert(galaxies.epoch == cinematic::Epoch::CosmicDawnGalaxies);
    assert(cinematic::chapterAt(299.99).epoch ==
           cinematic::Epoch::CosmicDawnGalaxies);
    assert(cinematic::chapterAt(49.999).epoch ==
           cinematic::Epoch::Inflation);
    bool rejectedEnd = false;
    try { (void)cinematic::chapterAt(300.0); }
    catch (const std::out_of_range&) { rejectedEnd = true; }
    assert(rejectedEnd);
    // Blender reference camera anchor values; intermediate curves are
    // smoothly approximated and intentionally not claimed exact Bezier parity.
    const auto cam0 = primordial::cameraAt(0.0f);
    const auto cam20 = primordial::cameraAt(20.0f);
    const auto cam50 = primordial::cameraAt(50.0f);
    assert(glm::length(cam0.position-glm::vec3(0,-18,3)) < 0.00001f);
    assert(cam0.focalLengthMm == 68.0f);
    assert(glm::length(cam20.position-glm::vec3(0,-12,2)) < 0.00001f);
    assert(cam20.focalLengthMm == 52.0f);
    assert(glm::length(cam50.position-glm::vec3(-2,1,3.2f)) < 0.00001f);
    assert(cam50.focalLengthMm == 62.0f);
    assert(primordial::verticalTanHalfFov(cam20, 16.0f/9.0f)>0.1f);
    const auto camMid = primordial::cameraAt(22.0f);
    assert(camMid.position.y > -12.0f && camMid.position.y < -10.2f);
    const auto cam70 = primordial::cameraAt(70.0f);
    const auto cam90 = primordial::cameraAt(90.0f);
    assert(glm::length(cam70.position-glm::vec3(2,-8,2)) < 0.00001f);
    assert(cam70.focalLengthMm == 65.0f);
    assert(glm::length(cam90.position-glm::vec3(0,-7,2.5f)) < 0.00001f);
    assert(cam90.focalLengthMm == 70.0f);
    const auto camAtBoundary = primordial::cameraAt(50.0f);
    const auto camAfterBoundary = primordial::cameraAt(50.01f);
    assert(glm::length(camAtBoundary.position-camAfterBoundary.position) < 0.001f);

    assert(film::secondsForFrame(1, 30) == 0.0);
    assert(film::secondsForFrame(751, 30) == 25.0);
    assert(film::secondsForFrame(1501, 60) == 25.0);
    assert(std::abs(film::secondsForFrame(9000, 30) - 8999.0 / 30.0) < 1e-10);
    assert(std::abs(film::secondsForFrame(18000, 60) - 17999.0 / 60.0) < 1e-10);
    assert(film::nearestFrameForSeconds(25.0, 30) == 751);
    assert(film::nearestFrameForSeconds(299.999, 60) == 18000);

    {
        const auto opts = parse({"bigbang", "--frame", "751", "--fps", "30",
                                 "--width", "480", "--height", "270",
                                 "--output", "output/native/test.png"});
        assert(opts.capture && opts.frame == 751 && opts.timeSeconds == 25.0);
        assert(opts.width == 480 && opts.height == 270 && opts.fps == 30);
    }
    {
        const auto opts = parse({"bigbang", "--time", "25", "--fps", "30",
                                 "--output", "output/native/test.png"});
        assert(opts.capture && opts.frame == 751 && opts.timeSeconds == 25.0);
    }
    {
        const auto opts = parse({"bigbang"});
        assert(!opts.capture && opts.fps == 60 && opts.width == 1280);
    }
    assert(parse({"bigbang", "--help"}).showHelp);

    invalid({"bigbang", "--fps", "24"});
    invalid({"bigbang", "--time", "300", "--output", "test.png"});
    invalid({"bigbang", "--time", "-2", "--output", "test.png"});
    invalid({"bigbang", "--time", "nan", "--output", "test.png"});
    invalid({"bigbang", "--frame", "0", "--output", "test.png"});
    invalid({"bigbang", "--frame", "9001", "--fps", "30", "--output", "test.png"});
    invalid({"bigbang", "--frame", "751", "--time", "25", "--output", "test.png"});
    invalid({"bigbang", "--output", "test.png"});
    invalid({"bigbang", "--time", "25"});
    invalid({"bigbang", "--time", "25", "--output", "test.jpg"});

    const std::filesystem::path output =
        std::filesystem::temp_directory_path() / "bigbang_m0_png_unit.png";
    // Pixel buffer is in OpenGL bottom-left-first order.
    const std::vector<std::uint8_t> pixels = {
        255,0,0, 0,255,0,
        0,0,255, 255,255,255,
    };
    png::writeRgbBottomUp(output.string(), 2, 2, pixels);
    std::ifstream stream(output, std::ios::binary);
    assert(stream.good());
    const std::vector<std::uint8_t> image(
        (std::istreambuf_iterator<char>(stream)), std::istreambuf_iterator<char>());
    assert(image.size() > 55);
    assert(image[0] == 137 && image[1] == 80 && image[2] == 78 && image[3] == 71);
    assert(bigEndian(image, 16) == 2 && bigEndian(image, 20) == 2);
    assert(image[25] == 2); // PNG color type 2 = RGB
    std::filesystem::remove(output);

    std::cout << "PASS: M0 film clock, CLI validation and native PNG header tests\n";
}
