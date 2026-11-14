#include "PngWriter.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <vector>

namespace {
using Byte = std::uint8_t;

void appendBe32(std::vector<Byte>& output, std::uint32_t v) {
    output.push_back(static_cast<Byte>((v >> 24) & 255));
    output.push_back(static_cast<Byte>((v >> 16) & 255));
    output.push_back(static_cast<Byte>((v >> 8) & 255));
    output.push_back(static_cast<Byte>(v & 255));
}

std::uint32_t crc32(const std::vector<Byte>& bytes, std::size_t from) {
    std::uint32_t crc = 0xffffffffu;
    for (std::size_t i = from; i < bytes.size(); ++i) {
        crc ^= bytes[i];
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ ((crc & 1u) ? 0xedb88320u : 0u);
        }
    }
    return crc ^ 0xffffffffu;
}

std::uint32_t adler32(const std::vector<Byte>& data) {
    std::uint32_t a = 1, b = 0;
    for (const Byte value : data) {
        a = (a + value) % 65521u;
        b = (b + a) % 65521u;
    }
    return (b << 16) | a;
}

void chunk(std::vector<Byte>& result, const char type[5],
           const std::vector<Byte>& payload) {
    appendBe32(result, static_cast<std::uint32_t>(payload.size()));
    const std::size_t crcStart = result.size();
    for (int i = 0; i < 4; ++i) result.push_back(static_cast<Byte>(type[i]));
    result.insert(result.end(), payload.begin(), payload.end());
    appendBe32(result, crc32(result, crcStart));
}
}

namespace png {
void writeRgbBottomUp(const std::string& path, int width, int height,
                      const std::vector<std::uint8_t>& rgb) {
    if (width < 1 || height < 1 || width > 4096 || height > 4096) {
        throw std::invalid_argument("Invalid PNG dimensions");
    }
    const std::size_t stride = static_cast<std::size_t>(width) * 3;
    if (rgb.size() != stride * static_cast<std::size_t>(height)) {
        throw std::invalid_argument("RGB pixel buffer size is incorrect");
    }

    // PNG scanlines are top-down, while OpenGL glReadPixels returns bottom-up.
    // Filter type 0 means exact pixels; DEFLATE stored blocks keep dependencies low.
    std::vector<Byte> raw;
    raw.reserve((stride + 1) * static_cast<std::size_t>(height));
    for (int y = height - 1; y >= 0; --y) {
        raw.push_back(0);
        const std::size_t offset = static_cast<std::size_t>(y) * stride;
        raw.insert(raw.end(), rgb.begin() + offset, rgb.begin() + offset + stride);
    }

    std::vector<Byte> compressed;
    compressed.reserve(raw.size() + raw.size() / 65535 * 5 + 32);
    compressed.push_back(0x78); // zlib CMF: deflate, 32 KB window
    compressed.push_back(0x01); // zlib FLG: no compression

    for (std::size_t offset = 0; offset < raw.size();) {
        const std::size_t count = std::min<std::size_t>(65535, raw.size() - offset);
        const bool last = offset + count == raw.size();
        compressed.push_back(last ? 0x01 : 0x00); // stored DEFLATE block
        const auto len = static_cast<std::uint16_t>(count);
        const auto nlen = static_cast<std::uint16_t>(~len);
        compressed.push_back(static_cast<Byte>(len & 255));
        compressed.push_back(static_cast<Byte>((len >> 8) & 255));
        compressed.push_back(static_cast<Byte>(nlen & 255));
        compressed.push_back(static_cast<Byte>((nlen >> 8) & 255));
        compressed.insert(compressed.end(), raw.begin() + offset, raw.begin() + offset + count);
        offset += count;
    }
    appendBe32(compressed, adler32(raw));

    const std::filesystem::path target(path);
    if (!target.parent_path().empty()) {
        std::filesystem::create_directories(target.parent_path());
    }
    std::vector<Byte> image = {137, 80, 78, 71, 13, 10, 26, 10};
    std::vector<Byte> header;
    appendBe32(header, static_cast<std::uint32_t>(width));
    appendBe32(header, static_cast<std::uint32_t>(height));
    header.insert(header.end(), {8, 2, 0, 0, 0}); // 8-bit RGB, no interlace
    chunk(image, "IHDR", header);
    chunk(image, "IDAT", compressed);
    chunk(image, "IEND", {});
    std::ofstream output(target, std::ios::binary);
    if (!output) throw std::runtime_error("Cannot open PNG output: " + path);
    output.write(reinterpret_cast<const char*>(image.data()),
                 static_cast<std::streamsize>(image.size()));
    if (!output) throw std::runtime_error("Cannot write PNG output: " + path);
}
} // namespace png
