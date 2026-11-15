#!/usr/bin/env python3
"""Repair V10's first-run film manifest without rerendering any native frames.

V10 source run 43735984392 successfully produced and uploaded every original
OpenGL segment. The assembly-only job rejected part 08 because the first
version of SIZES accidentally copied 600 instead of 720 frames for it.
Correct that validation metadata IN MEMORY, keeping original 12 video files,
native C++ source commit and SHA evidence untouched.
"""
import assemble_v10_review as review

review.SIZES[7] = 720   # segment 08: native frames 5881..6600 (24 seconds)
review.BOUNDARIES[7] = 220  # the true transition at 220 seconds

assert sum(review.SIZES) == 9000
assert len(review.SIZES) == 12

if __name__ == "__main__":
    review.main()
