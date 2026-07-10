"""Генерация .ico для приложения — простой квадрат с буквой L."""
import struct, zlib, sys
from pathlib import Path

def create_png_icon(output_path: str, size: int = 32):
    """Создаёт .ico с одним PNG-изображением."""
    # Создаём RGBA пиксели: синий фон с белой буквой L
    pixels = bytearray()
    cx, cy = size // 2, size // 2
    r = size * 0.35
    for y in range(size):
        for x in range(size):
            # Закруглённый прямоугольник
            dx = abs(x - cx)
            dy = abs(y - cy)
            hw = size * 0.4
            hh = size * 0.4
            corner_r = size * 0.12
            in_corner = False
            if dx > hw - corner_r and dy > hh - corner_r:
                dist = ((dx - (hw - corner_r)) ** 2 + (dy - (hh - corner_r)) ** 2) ** 0.5
                in_corner = dist > corner_r
            inside = not (dx > hw or dy > hh or in_corner)
            if inside:
                # Белая буква L
                lx, ly = x - (cx - hw * 0.4), y - (cy + hh * 0.3)
                thick = size * 0.1
                if (0 <= ly < hh * 0.7 and abs(lx) < thick) or (0 <= lx < hw * 0.6 and abs(ly) < thick):
                    pixels.extend([255, 255, 255, 255])
                else:
                    pixels.extend([74, 124, 217, 255])  # Beeline-like blue
            else:
                pixels.extend([0, 0, 0, 0])

    # Строим PNG (IHDR + IDAT + IEND)
    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)  # 8bit RGBA
    raw = b""
    for y in range(size):
        raw += b"\x00" + bytes(pixels[y * size * 4:(y + 1) * size * 4])
    idat = zlib.compress(raw)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", idat)
    png += chunk(b"IEND", b"")

    # ICO контейнер: один PNG-изображение
    ico = struct.pack("<HHH", 0, 1, 1)  # reserved=0, type=1(ico), count=1
    ico += struct.pack("<BBBBHHIH", size, size, 0, 0, 1, 32, len(png), 22)
    ico += png

    Path(output_path).write_bytes(ico)
    print(f"Icon created: {output_path} ({len(ico)} bytes)")

if __name__ == "__main__":
    create_png_icon(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent / "app.ico"))
