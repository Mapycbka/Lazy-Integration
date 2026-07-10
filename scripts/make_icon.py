"""Конвертирует PNG в .ico для приложения."""
import struct, zlib, sys
from pathlib import Path

def png_to_ico(png_path: str, ico_path: str):
    png_data = Path(png_path).read_bytes()
    if png_data[:8] != b'\x89PNG\r\n\x1a\n':
        # Если не PNG, пробуем как BMP или просто оборачиваем
        # Читаем размер из IHDR
        pass
    
    # ICO контейнер: один PNG
    ico = struct.pack("<HHH", 0, 1, 1)
    ico += struct.pack("<BBBBHHIH", 0, 0, 0, 0, 1, 32, len(png_data), 22)
    ico += png_data
    
    Path(ico_path).write_bytes(ico)
    print(f"ICO created: {ico_path} ({len(ico)} bytes)")

if __name__ == "__main__":
    project = Path(__file__).parent.parent
    src = sys.argv[1] if len(sys.argv) > 1 else str(project / "smiling.png")
    dst = sys.argv[2] if len(sys.argv) > 2 else str(project / "app.ico")
    png_to_ico(src, dst)
