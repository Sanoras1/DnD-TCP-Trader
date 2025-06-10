#!/usr/bin/env python3
"""decode_login.py – quick‑and‑dirty Dark‑and‑Darker LoginRequest hex decoder

Usage examples
--------------
1. Paste the raw hex blob into a file (one long line, or whitespace/newlines – both accepted):

   $ python decode_login.py --hex login_hex.txt

2. If you already have the binary payload:

   $ python decode_login.py --bin login.bin

The script will:
 • turn hex → binary if needed
 • try to call `protoc --decode_raw` (if the `protoc` CLI is on PATH)
 • fall back to a minimal Python wire‑format walker that prints
   field‑numbers, wire‑types, and raw values.

Works on Python ≥3.8.  Requires `protobuf` pip package *only* for the
fallback decoder (most systems already have it via `scapy`).
"""

from __future__ import annotations
import argparse, shutil, subprocess, sys, textwrap, binascii, re, io
from pathlib import Path
from typing import Iterable, Tuple

########################## helpers ###########################################

def load_hex_file(path: Path) -> bytes:
    """Read hex from *path* (whitespace/newlines allowed) → bytes."""
    text = Path(path).read_text(encoding="ascii")
    # strip 0x, \x00, spaces, newlines
    cleaned = re.sub(r"(?:0x|\\x|[^0-9a-fA-F])", "", text)
    if len(cleaned) % 2:
        raise ValueError("Hex string has odd length; is it valid?")
    return binascii.unhexlify(cleaned)


def protoc_decode(buf: bytes) -> str | None:
    """Return protoc --decode_raw output or None if protoc missing/error."""
    if shutil.which("protoc") is None:
        return None
    try:
        out = subprocess.check_output(
            ["protoc", "--decode_raw"], input=buf, stderr=subprocess.DEVNULL
        )
        return out.decode("utf-8", "replace")
    except subprocess.CalledProcessError:
        return None

#################### minimal fallback decoder ################################

# Based on google.protobuf internals; prints field‑number and raw value.
# Handles varint, 64‑bit, len‑delimited.  Skips 32‑bit (not seen so far).

from google.protobuf.internal import decoder, wire_format

VarintDecoder = decoder._DecodeVarint
Varint32Decoder = decoder._DecodeVarint32

WIRE_VARIANT = wire_format.WIRETYPE_VARINT
WIRE_LEN     = wire_format.WIRETYPE_LENGTH_DELIMITED
WIRE_64BIT   = wire_format.WIRETYPE_FIXED64
WIRE_32BIT   = wire_format.WIRETYPE_FIXED32


def fallback_decode(buf: bytes) -> str:
    """Walk the protobuf wire format and print each field crudely."""
    out_lines: list[str] = []
    pos = 0
    l = len(buf)
    indent = ""
    while pos < l:
        key, pos = VarintDecoder(buf, pos)
        field_num = key >> 3
        wire_type = key & 0x07
        if wire_type == WIRE_VARIANT:
            val, pos = VarintDecoder(buf, pos)
            out_lines.append(f"{field_num}: {val}")
        elif wire_type == WIRE_LEN:
            length, pos = Varint32Decoder(buf, pos)
            data = buf[pos : pos + length]
            pos += length
            # show ASCII if printable, else hex
            if all(32 <= b < 127 for b in data):
                preview = data.decode(errors="replace")
            else:
                preview = data[:32].hex() + ("…" if len(data) > 32 else "")
            out_lines.append(f"{field_num}: (len {length}) {preview}")
        elif wire_type == WIRE_64BIT:
            val = int.from_bytes(buf[pos : pos + 8], "little")
            pos += 8
            out_lines.append(f"{field_num}: 0x{val:016x} (64‑bit)")
        elif wire_type == WIRE_32BIT:
            val = int.from_bytes(buf[pos : pos + 4], "little")
            pos += 4
            out_lines.append(f"{field_num}: 0x{val:08x} (32‑bit)")
        else:
            out_lines.append(f"{field_num}: <wire‑type {wire_type} not handled>")
            break  # bail out
    return "\n".join(out_lines)

########################## main ##############################################


def main():
    ap = argparse.ArgumentParser(description="Decode Dark‑and‑Darker LoginRequest hex/raw bytes")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--hex", metavar="FILE", type=Path, help="file containing hex string")
    grp.add_argument("--bin", metavar="FILE", type=Path, help="file containing raw binary")
    args = ap.parse_args()

    if args.hex:
        raw = load_hex_file(args.hex)
    else:
        raw = Path(args.bin).read_bytes()

    # Attempt protoc first
    decoded = protoc_decode(raw)
    if decoded is not None:
        print(decoded)
        return

    # Fallback pure‑python decode
    print("(protoc not available) – fallback decode:\n")
    print(fallback_decode(raw))

if __name__ == "__main__":
    main()
