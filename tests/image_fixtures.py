"""Real, minimal, genuinely-decodable image bytes for tests that need an actual valid image.

Before backend/services/evidence_service.py validated real file content, tests across this suite
used placeholder bytes like `b"\\xff\\xd8\\xff" + b"fake jpeg content" * 10` -- a real JPEG magic-
byte prefix followed by arbitrary text, which is NOT a real, decodable image (confirmed directly:
Pillow correctly refuses to open it, "cannot identify image file"). That was fine when the backend
only checked Content-Type, but a placeholder like that now correctly fails the real content check
-- tests that need to prove a *valid* upload succeeds need genuinely valid image bytes instead.

Generated once via Pillow (already a project dependency -- see backend/services/vision_service.py,
which uses the same library for the same reason) rather than committed as binary files, so there's
nothing to keep in sync by hand.
"""

from __future__ import annotations

import io

from PIL import Image


def _generate(fmt: str) -> bytes:
    img = Image.new("RGB", (4, 4), color=(120, 40, 200))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


VALID_JPEG_BYTES = _generate("JPEG")
VALID_PNG_BYTES = _generate("PNG")

# A real, genuinely valid, fully-decodable image -- just in a format this app doesn't support
# (only JPEG/PNG are, see backend/config.py's ALLOWED_PHOTO_CONTENT_TYPES). Distinct from every
# other "invalid" fixture below: this one IS a real image, PIL opens and decodes it fine -- it
# must still be rejected on format, not on decodability.
VALID_GIF_BYTES = _generate("GIF")

# A real PNG signature followed by an IHDR chunk declaration, but no real chunk data after it --
# looks like a PNG at a glance (and to naive signature-only sniffing), but Pillow correctly
# refuses to decode it. Distinct from plain random/text bytes (which fail at the very first
# signature check) -- this exercises the "looks right, isn't" path specifically.
CORRUPTED_PNG_BYTES = b"\x89PNG\r\n\x1a\n" + bytes.fromhex("0000000d49484452") + b"\x00" * 200

# Genuinely not an image at all -- arbitrary random bytes with no recognizable file signature.
RANDOM_BINARY_BYTES = bytes(range(256)) * 4

# A plain text file, renamed to look like an image via its Content-Type/filename only.
TEXT_FILE_BYTES = b"This is a plain text file, not an image, just renamed to look like one."

# The start of a real Windows PE executable's header (MZ signature) -- stands in for "an
# executable renamed to .jpg", without shipping an actual runnable binary in the test suite.
FAKE_EXECUTABLE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00" + b"\x00" * 100
