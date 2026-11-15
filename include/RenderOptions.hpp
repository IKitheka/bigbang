#ifndef RENDER_OPTIONS_HPP
#define RENDER_OPTIONS_HPP

#include "FilmClock.hpp"

#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <string>

namespace film {

struct RenderOptions {
    int width = 1280;
    int height = 720;
    int fps = 60;
    bool showHelp = false;
    bool rendererInfo = false;
    bool capture = false;
    bool batch = false;
    std::int64_t endFrame = 1;
    std::string rawVideo;
    std::int64_t frame = 1; // nearest nominal frame for a --time seek
    double timeSeconds = 0.0;
    std::string output;
};

inline double strictDouble(const std::string& value, const std::string& key) {
    std::size_t pos = 0;
    double parsed = 0;
    try { parsed = std::stod(value, &pos); }
    catch (const std::exception&) { throw std::invalid_argument("Invalid number for " + key); }
    if (pos != value.size() || !std::isfinite(parsed)) {
        throw std::invalid_argument("Invalid finite number for " + key);
    }
    return parsed;
}

inline std::int64_t strictInt(const std::string& value, const std::string& key) {
    std::size_t pos = 0;
    std::int64_t parsed = 0;
    try { parsed = std::stoll(value, &pos, 10); }
    catch (const std::exception&) { throw std::invalid_argument("Invalid integer for " + key); }
    if (pos != value.size()) throw std::invalid_argument("Invalid integer for " + key);
    return parsed;
}

inline RenderOptions parseOptions(int argc, const char* const argv[]) {
    RenderOptions opts;
    bool hasTime = false;
    bool hasFrame = false;
    bool hasStart = false, hasEnd = false;
    std::int64_t startArgument = 1, endArgument = 1;
    double timeArgument = 0.0;
    std::int64_t frameArgument = 1;
    for (int i = 1; i < argc; ++i) {
        const std::string key(argv[i]);
        if (key == "--help" || key == "-h") {
            opts.showHelp = true;
            return opts;
        }
        if (key == "--renderer-info") {
            opts.rendererInfo = true;
            continue;
        }
        if (i + 1 >= argc) throw std::invalid_argument("Missing value after " + key);
        const std::string value(argv[++i]);
        if (key == "--time") {
            hasTime = true;
            timeArgument = strictDouble(value, key);
        } else if (key == "--frame") {
            hasFrame = true;
            frameArgument = strictInt(value, key);
        } else if (key == "--start-frame") {
            hasStart = true;
            startArgument = strictInt(value, key);
        } else if (key == "--end-frame") {
            hasEnd = true;
            endArgument = strictInt(value, key);
        } else if (key == "--raw-video") {
            opts.rawVideo = value;
        } else if (key == "--fps") {
            const auto n = strictInt(value, key);
            if (n != 30 && n != 60) throw std::invalid_argument("--fps must be 30 or 60");
            opts.fps = static_cast<int>(n);
        } else if (key == "--width") {
            const auto n = strictInt(value, key);
            if (n < 1 || n > 4096) throw std::invalid_argument("--width outside 1..4096");
            opts.width = static_cast<int>(n);
        } else if (key == "--height") {
            const auto n = strictInt(value, key);
            if (n < 1 || n > 4096) throw std::invalid_argument("--height outside 1..4096");
            opts.height = static_cast<int>(n);
        } else if (key == "--output") {
            if (value.empty()) throw std::invalid_argument("--output must be a PNG path");
            opts.output = value;
        } else {
            throw std::invalid_argument("Unknown option: " + key);
        }
    }
    if (opts.rendererInfo) {
        if (hasTime || hasFrame || hasStart || hasEnd || !opts.rawVideo.empty() || !opts.output.empty())
            throw std::invalid_argument("--renderer-info cannot be combined with capture options.");
        opts.capture = true; // Query a hidden context, without drawing a frame.
        return opts;
    }
    if (hasTime && hasFrame) throw std::invalid_argument("Use --time OR --frame, not both.");
    opts.batch = hasStart || hasEnd || !opts.rawVideo.empty();
    if (opts.batch) {
        if (!hasStart || !hasEnd || hasTime || hasFrame || !opts.output.empty() ||
            opts.rawVideo != "-" || endArgument < startArgument) {
            throw std::invalid_argument("Batch requires --start-frame N --end-frame N --raw-video - without single-frame options.");
        }
        if (opts.width > 1920 || opts.height > 1080) {
            throw std::invalid_argument("Batch review is limited to 1920x1080; no 4K production.");
        }
        opts.timeSeconds = secondsForFrame(startArgument, opts.fps);
        (void)secondsForFrame(endArgument, opts.fps);
        opts.frame = startArgument;
        opts.endFrame = endArgument;
        opts.capture = true;
        return opts;
    }
    if (std::int64_t(opts.width) * opts.height > 4096LL * 4096LL) {
        throw std::invalid_argument("Pixel budget exceeded");
    }
    if (!opts.output.empty() && !(hasTime || hasFrame)) {
        throw std::invalid_argument("--output requires --time or --frame");
    }
    if ((hasTime || hasFrame) && opts.output.empty()) {
        throw std::invalid_argument("--time/--frame requires --output for native capture");
    }
    if (!opts.output.empty() &&
        (opts.output.size() < 4 || opts.output.substr(opts.output.size() - 4) != ".png")) {
        throw std::invalid_argument("--output must end in .png");
    }

    opts.capture = !opts.output.empty();
    if (hasFrame) {
        opts.timeSeconds = secondsForFrame(frameArgument, opts.fps);
        opts.frame = frameArgument;
    } else if (hasTime) {
        opts.frame = nearestFrameForSeconds(timeArgument, opts.fps);
        opts.timeSeconds = timeArgument; // evaluate exact seek, not a rounded approximation
    }
    return opts;
}

} // namespace film

#endif
