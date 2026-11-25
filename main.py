#!/usr/bin/env python3
"""news-image-20261124 entrypoint.

Reads the broadsheet entry.png sitting beside this file, proves it is a
structurally sound PNG, and copies it byte-for-byte to /output/entry.png.
Pure copy, no network, no clock, no randomness: two runs write identical
bytes.
"""
import os
import struct
import sys
import zlib
from collections import namedtuple

Chunk = namedtuple("Chunk", "kind data")

HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(HERE, "entry.png")
OUTPUT_PATH = "/output/entry.png"

SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_FILE_BYTES = 1024 * 1024
MAX_EDGE = 1024


class PngError(ValueError):
    """Raised when the bundled picture fails a structural check."""


def parse_png(blob):
    """Split blob into chunks, verifying signature, order and CRCs.

    Returns (header, chunks) where header is the IHDR tuple
    (width, height, bit_depth, colour_type).
    """
    if len(blob) < 8 or blob[:8] != SIGNATURE:
        raise PngError("not a PNG file: bad signature")
    chunks = []
    offset = 8
    first = True
    ended = False
    while offset < len(blob):
        if ended:
            raise PngError("trailing bytes after IEND")
        if offset + 8 > len(blob):
            raise PngError("truncated chunk header at offset %d" % offset)
        size, kind = struct.unpack_from(">I4s", blob, offset)
        end = offset + 12 + size
        if end > len(blob):
            raise PngError("chunk %r overruns the file" % kind)
        data = blob[offset + 8:offset + 8 + size]
        want_crc, = struct.unpack_from(">I", blob, offset + 8 + size)
        got_crc = zlib.crc32(kind + data) & 0xFFFFFFFF
        if want_crc != got_crc:
            raise PngError("CRC failure in %r chunk" % kind)
        if first and kind != b"IHDR":
            raise PngError("first chunk is %r, not IHDR" % kind)
        first = False
        if kind == b"IEND":
            if size != 0:
                raise PngError("IEND must be empty")
            ended = True
        chunks.append(Chunk(kind, data))
        offset = end
    if first:
        raise PngError("empty file: no chunks at all")
    if not ended:
        raise PngError("file ends without IEND")
    return read_header(chunks), chunks


def read_header(chunks):
    """Pull the IHDR fields out of the parsed chunk list and bound them."""
    ihdr = chunks[0].data
    if len(ihdr) != 13:
        raise PngError("IHDR must be 13 bytes, got %d" % len(ihdr))
    width, height, depth, colour = struct.unpack(">IIBB", ihdr[:10])
    if width == 0 or height == 0:
        raise PngError("image has a zero side")
    if width > MAX_EDGE or height > MAX_EDGE:
        raise PngError("image is %dx%d, over the 1024 cap" % (width, height))
    if depth not in (1, 2, 4, 8, 16):
        raise PngError("bit depth %d is not a PNG depth" % depth)
    if colour not in (0, 2, 3, 4, 6):
        raise PngError("colour type %d is not a PNG colour type" % colour)
    return width, height, depth, colour


def main():
    with open(INPUT_PATH, "rb") as handle:
        blob = handle.read()
    if len(blob) > MAX_FILE_BYTES:
        raise PngError("entry.png is %d bytes, over the 1 MiB cap"
                       % len(blob))
    (width, height, depth, colour), _chunks = parse_png(blob)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "wb") as handle:
        handle.write(blob)
    print("wrote %s: %d bytes, %dx%d, depth %d, colour %d"
          % (OUTPUT_PATH, len(blob), width, height, depth, colour))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except PngError as err:
        print("invalid PNG: %s" % err, file=sys.stderr)
        sys.exit(1)
