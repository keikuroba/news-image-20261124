#!/usr/bin/env python3
"""Entry point for news-image-20261124.

Copies the pre-drawn broadsheet (entry.png, sitting beside this file)
to /output/entry.png, but only after proving the file is a well-formed
PNG. The copy is byte-for-byte, so two runs always produce identical
output. No network, no clock, no randomness anywhere in this program.
"""
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
DEST = "/output/entry.png"

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1 << 20          # 1 MiB, the competition cap
MAX_SIDE = 1024              # 1024 px on either side


class BadPng(Exception):
    """Raised when the bundled picture fails a structural check."""


def read_chunks(blob):
    """Walk the chunk stream, checking every CRC on the way.

    Yields (kind, payload) pairs. Refuses anything after IEND, a
    missing IEND, or a chunk whose declared length runs past the
    end of the file.
    """
    if blob[:8] != PNG_SIGNATURE:
        raise BadPng("missing PNG signature")
    pos = 8
    seen_ihdr = False
    saw_iend = False
    while pos < len(blob):
        if saw_iend:
            raise BadPng("bytes after IEND")
        if pos + 8 > len(blob):
            raise BadPng("truncated chunk header")
        length, kind = struct.unpack(">I4s", blob[pos:pos + 8])
        if pos + 12 + length > len(blob):
            raise BadPng("chunk overruns file: %r" % kind)
        payload = blob[pos + 8:pos + 8 + length]
        stored_crc, = struct.unpack(">I", blob[pos + 8 + length:pos + 12 + length])
        actual_crc = zlib.crc32(kind + payload) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise BadPng("CRC mismatch in %r chunk" % kind)
        if not seen_ihdr:
            if kind != b"IHDR":
                raise BadPng("first chunk is not IHDR")
            seen_ihdr = True
        if kind == b"IEND":
            if length != 0:
                raise BadPng("IEND carries a payload")
            saw_iend = True
        yield kind, payload
        pos += 12 + length
    if not seen_ihdr:
        raise BadPng("no IHDR chunk")
    if not saw_iend:
        raise BadPng("no IEND chunk")


def check_header(payload):
    """Sanity-check the IHDR fields against the competition limits."""
    if len(payload) != 13:
        raise BadPng("IHDR is not 13 bytes")
    width, height, depth, colour = struct.unpack(">IIBB", payload[:10])
    if width == 0 or height == 0:
        raise BadPng("zero-sized image")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise BadPng("image exceeds 1024x1024")
    if depth not in (1, 2, 4, 8, 16):
        raise BadPng("unsupported bit depth: %d" % depth)
    if colour not in (0, 2, 3, 4, 6):
        raise BadPng("unsupported colour type: %d" % colour)
    return width, height, depth, colour


def expected_raw_size(width, height, depth, colour):
    """Bytes the inflated IDAT stream must hold for this header.

    Each scanline is one filter byte plus the pixel data; the number
    of channels follows the colour type, and samples below 8 bits
    pack several pixels per byte.
    """
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[colour]
    bits_per_row = width * channels * depth
    bytes_per_row = (bits_per_row + 7) // 8
    return height * (1 + bytes_per_row)


def check_pixel_data(blob, width, height, depth, colour):
    """Inflate the IDAT stream and confirm it matches the header.

    A truncated or padded IDAT section inflates to the wrong length,
    which the CRC walk alone cannot catch.
    """
    raw = b""
    for kind, payload in read_chunks(blob):
        if kind == b"IDAT":
            raw += payload
    if not raw:
        raise BadPng("no IDAT chunk")
    try:
        pixels = zlib.decompress(raw)
    except zlib.error as exc:
        raise BadPng("IDAT does not inflate: %s" % exc)
    want = expected_raw_size(width, height, depth, colour)
    if len(pixels) != want:
        raise BadPng("inflated IDAT is %d bytes, header promises %d"
                     % (len(pixels), want))


def main():
    with open(SOURCE, "rb") as handle:
        blob = handle.read()
    if len(blob) > MAX_BYTES:
        raise BadPng("image exceeds 1 MiB")
    width = height = depth = colour = None
    for kind, payload in read_chunks(blob):
        if kind == b"IHDR":
            width, height, depth, colour = check_header(payload)
    check_pixel_data(blob, width, height, depth, colour)
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, "wb") as handle:
        handle.write(blob)
    print("wrote %s (%d bytes, %dx%d)" % (DEST, len(blob), width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
