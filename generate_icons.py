"""Generate simple PNG icons for the PWA."""
import struct
import zlib

def create_png(width, height, color_rgb=(20, 80, 144), text_color=(255, 255, 255)):
    """Create a simple PNG with an 'e' letter on e-Trak blue background."""

    def make_pixel_data(w, h):
        rows = []
        cx, cy = w // 2, h // 2
        r = min(w, h) // 2 - 2

        for y in range(h):
            row = b'\x00'  # filter byte
            for x in range(w):
                # Circle background
                dx, dy = x - cx, y - cy
                dist = (dx*dx + dy*dy) ** 0.5

                if dist <= r:
                    # Inside circle - draw "e" for e-Trak
                    nx, ny = (x - cx) / r, (y - cy) / r

                    # Lowercase "e" shape
                    # Main body: oval from -0.5 to 0.5 vertically, -0.45 to 0.45 horizontally
                    in_body = (nx / 0.45)**2 + (ny / 0.5)**2 <= 1
                    in_hole_top = (nx / 0.25)**2 + ((ny + 0.08) / 0.22)**2 <= 1
                    in_hole_bottom = (nx / 0.25)**2 + ((ny - 0.18) / 0.22)**2 <= 1

                    # Horizontal bar of e (middle)
                    in_bar = -0.45 < nx < 0.45 and -0.12 < ny < 0.04

                    # Opening at bottom-right
                    in_opening = ny > 0.15 and nx > 0.15 and (nx / 0.45)**2 + (ny / 0.5)**2 > 0.6

                    is_letter = (in_body and not in_hole_top and not in_hole_bottom and not in_opening) or in_bar

                    if is_letter:
                        row += bytes(text_color)
                    else:
                        row += bytes(color_rgb)
                else:
                    # Outside circle - dark e-Trak background
                    row += bytes((10, 30, 54))
            rows.append(row)
        return b''.join(rows)

    def make_png(w, h, pixel_data):
        # PNG signature
        sig = b'\x89PNG\r\n\x1a\n'

        # IHDR chunk
        ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
        ihdr = make_chunk(b'IHDR', ihdr_data)

        # IDAT chunk
        compressed = zlib.compress(pixel_data)
        idat = make_chunk(b'IDAT', compressed)

        # IEND chunk
        iend = make_chunk(b'IEND', b'')

        return sig + ihdr + idat + iend

    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)

    pixel_data = make_pixel_data(width, height)
    return make_png(width, height, pixel_data)


if __name__ == '__main__':
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for size in [192, 512]:
        data = create_png(size, size)
        path = os.path.join(script_dir, f'icon-{size}.png')
        with open(path, 'wb') as f:
            f.write(data)
        print(f'Created {path} ({len(data)} bytes)')

    print('Done!')
