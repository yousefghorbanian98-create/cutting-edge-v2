#!/usr/bin/env python3
"""Deterministic placeholder icon set for the Tauri shell (S-010).

Why a hand-rolled rasteriser instead of `tauri icon` / Pillow?
  * zero dependencies → runs in the tooling venv, on both CI OSes and in the sandbox;
  * deterministic pixels (only +, -, *, / and `math.sqrt`, which are IEEE-exact) →
    `tests/unit/test_tauri_skeleton.py` regenerates the set and compares raw pixels,
    so the committed binaries are provably produced by this script;
  * the final brand icon is a separate decision (S-063 — generated + reviewed); this
    set only has to be *coherent with DESIGN.md* (surface #18181b, indigo→violet accent).

Output (apps/desktop/src-tauri/icons/):
  32x32.png 128x128.png 128x128@2x.png icon.png(256)      — tauri.conf.json `bundle.icon`
  icon.ico (16 24 32 48 64 128 256, PNG-compressed entries) — exe resource + NSIS

Usage:  python scripts/make_icons.py [--out DIR] [--check]
  --check  regenerate to memory and exit 1 if any committed file's pixels differ.
"""

from __future__ import annotations

import argparse
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "apps" / "desktop" / "src-tauri" / "icons"

# DESIGN.md tokens (S-099): primary (indigo) → ai-glow (violet) gradient, text-100 glyph.
INDIGO = (0x63, 0x66, 0xF1)
VIOLET = (0x8B, 0x5C, 0xF6)
WHITE = (0xFA, 0xFA, 0xFA)

PNG_SIZES = {"32x32.png": 32, "128x128.png": 128, "128x128@2x.png": 256, "icon.png": 256}
ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
SSAA = 4  # 4×4 supersampling → 16 coverage levels, enough for crisp small sizes

# 8-vertex four-point star (unit coordinates, centre 0,0). Axis points reach 0.36,
# diagonal notches 0.11 * cos45°. Concave polygon → crossing-number test below.
_R, _r = 0.36, 0.11 * 0.70710678
STAR = [(_R, 0.0), (_r, _r), (0.0, _R), (-_r, _r), (-_R, 0.0), (-_r, -_r), (0.0, -_R), (_r, -_r)]


def _in_star(x: float, y: float) -> bool:
    inside = False
    n = len(STAR)
    for i in range(n):
        x1, y1 = STAR[i]
        x2, y2 = STAR[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xi:
                inside = not inside
    return inside


def _in_rounded_square(u: float, v: float, radius: float) -> bool:
    # u, v ∈ [0,1); corner radius as a fraction of the side.
    cx = min(max(u, radius), 1.0 - radius)
    cy = min(max(v, radius), 1.0 - radius)
    dx, dy = u - cx, v - cy
    return (dx * dx + dy * dy) ** 0.5 <= radius if (dx or dy) else True


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[float, float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


def render(size: int) -> bytes:
    """RGBA pixels, row-major, no filter bytes."""
    out = bytearray()
    step = 1.0 / (size * SSAA)
    total = SSAA * SSAA
    for py in range(size):
        for px in range(size):
            bg = star = 0
            for sy in range(SSAA):
                v = (py * SSAA + sy + 0.5) * step
                for sx in range(SSAA):
                    u = (px * SSAA + sx + 0.5) * step
                    if _in_rounded_square(u, v, 0.22):
                        bg += 1
                        if _in_star(u - 0.5, v - 0.5):
                            star += 1
            if bg == 0:
                out += b"\x00\x00\x00\x00"
                continue
            t = (px + py + 1) / (2.0 * size)  # diagonal gradient, top-left → bottom-right
            base = _lerp(INDIGO, VIOLET, t)
            k = star / bg
            r = base[0] + (WHITE[0] - base[0]) * k
            g = base[1] + (WHITE[1] - base[1]) * k
            b = base[2] + (WHITE[2] - base[2]) * k
            a = 255.0 * bg / total
            out += bytes((int(r + 0.5), int(g + 0.5), int(b + 0.5), int(a + 0.5)))
    return bytes(out)


def _chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode_png(size: int, rgba: bytes) -> bytes:
    stride = size * 4
    raw = b"".join(b"\x00" + rgba[y * stride : (y + 1) * stride] for y in range(size))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b"")


def decode_png_rgba(data: bytes) -> tuple[int, int, bytes]:
    """Minimal decoder for PNGs written by `encode_png` (8-bit RGBA, filter 0 only)."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, idat, w, h = 8, b"", 0, 0
    while pos < len(data):
        (ln,) = struct.unpack(">I", data[pos : pos + 4])
        tag = data[pos + 4 : pos + 8]
        body = data[pos + 8 : pos + 8 + ln]
        if tag == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            if (depth, ctype) != (8, 6):
                raise ValueError("expected 8-bit RGBA")
        elif tag == b"IDAT":
            idat += body
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 4 + 1
    rows = [raw[y * stride : (y + 1) * stride] for y in range(h)]
    if any(r[0] != 0 for r in rows):
        raise ValueError("unexpected PNG filter")
    return w, h, b"".join(r[1:] for r in rows)


def encode_ico(pngs: list[tuple[int, bytes]]) -> bytes:
    header = struct.pack("<HHH", 0, 1, len(pngs))
    offset = len(header) + 16 * len(pngs)
    entries, blobs = b"", b""
    for size, blob in pngs:
        dim = 0 if size >= 256 else size
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(blob), offset + len(blobs))
        blobs += blob
    return header + entries + blobs


def build() -> dict[str, bytes]:
    cache: dict[int, bytes] = {}

    def png(size: int) -> bytes:
        if size not in cache:
            cache[size] = encode_png(size, render(size))
        return cache[size]

    files = {name: png(size) for name, size in PNG_SIZES.items()}
    files["icon.ico"] = encode_ico([(s, png(s)) for s in ICO_SIZES])
    return files


def check(out_dir: Path) -> list[str]:
    problems: list[str] = []
    for name, blob in build().items():
        path = out_dir / name
        if not path.exists():
            problems.append(f"{name}: missing")
            continue
        have = path.read_bytes()
        if name.endswith(".ico"):
            if have != blob and _ico_pixels(have) != _ico_pixels(blob):
                problems.append(f"{name}: pixels differ from generator output")
        elif decode_png_rgba(have) != decode_png_rgba(blob):
            problems.append(f"{name}: pixels differ from generator output")
    return problems


def _ico_pixels(data: bytes) -> list[tuple[int, int, bytes]]:
    (_, _, count) = struct.unpack("<HHH", data[:6])
    out = []
    for i in range(count):
        _, _, _, _, _, _, size, off = struct.unpack("<BBBBHHII", data[6 + 16 * i : 22 + 16 * i])
        out.append(decode_png_rgba(data[off : off + size]))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ICON_DIR)
    ap.add_argument("--check", action="store_true", help="verify committed icons match the generator")
    args = ap.parse_args(argv)
    if args.check:
        problems = check(args.out)
        for p in problems:
            print(f"make_icons: {p}", file=sys.stderr)
        print(f"make_icons: {'OK' if not problems else 'DRIFT'} — {len(PNG_SIZES) + 1} files in {args.out}")
        return 1 if problems else 0
    args.out.mkdir(parents=True, exist_ok=True)
    for name, blob in build().items():
        (args.out / name).write_bytes(blob)
        print(f"wrote {args.out / name} ({len(blob)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
