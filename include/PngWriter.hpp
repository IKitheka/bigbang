#ifndef PNG_WRITER_HPP
#define PNG_WRITER_HPP

#include <cstdint>
#include <string>
#include <vector>

// Write a valid RGB8 PNG from OpenGL-style bottom-up RGB pixel bytes.
// No Python, Blender, image converter or additional image dependencies.
namespace png {
void writeRgbBottomUp(const std::string& path, int width, int height,
                      const std::vector<std::uint8_t>& rgb);
}

#endif
