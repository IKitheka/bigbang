#ifndef FILM_CLOCK_HPP
#define FILM_CLOCK_HPP

#include <cmath>
#include <cstdint>
#include <stdexcept>

namespace film {

constexpr int kDurationSeconds = 300;

inline bool validFps(int fps) {
    return fps == 30 || fps == 60;
}

// Frame 1 is exactly 0 seconds. A 300-second film has FPS * 300 frames.
inline double secondsForFrame(std::int64_t frame, int fps) {
    if (!validFps(fps) || frame < 1 || frame > std::int64_t(fps) * kDurationSeconds) {
        throw std::out_of_range("Frame must be in 1..fps*300 with fps 30 or 60.");
    }
    return static_cast<double>(frame - 1) / static_cast<double>(fps);
}

inline std::int64_t nearestFrameForSeconds(double seconds, int fps) {
    if (!validFps(fps) || !std::isfinite(seconds) ||
        seconds < 0.0 || seconds >= kDurationSeconds) {
        throw std::out_of_range("Time must be finite and between 0 and 300 seconds (exclusive).");
    }
    const auto frame = std::int64_t{1} + static_cast<std::int64_t>(
        std::llround(seconds * static_cast<double>(fps)));
    const auto last = std::int64_t{fps} * kDurationSeconds;
    return frame > last ? last : frame;
}

} // namespace film

#endif
