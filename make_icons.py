#!/usr/bin/env python3
"""生成 PWA 图标：渐变背景 + 白色柱状图 + AI 光点"""
import zlib, struct, math, os

OUT = os.path.join(os.path.dirname(__file__), 'icons')
os.makedirs(OUT, exist_ok=True)

def rounded_rect(px, py, x, y, w, h, r):
    """判断像素(px,py)是否在圆角矩形内"""
    if x + r <= px <= x + w - r and y <= py <= y + h: return True
    if x <= px < x + r and y + r <= py < y + h: return True
    if x + w - r < px <= x + w and y + r <= py < y + h: return True
    if y + h - r < py <= y + h and x + r <= px <= x + w - r: return True
    for cx, cy in [(x+r, y+r), (x+w-r, y+r), (x+r, y+h-r), (x+w-r, y+h-r)]:
        if (px-cx)**2 + (py-cy)**2 <= r*r: return True
    return False

def draw(size, name, maskable=False):
    # 背景垂直渐变 #6366F1 -> #4F46E5
    c1 = (0x63, 0x66, 0xF1); c2 = (0x4F, 0x46, 0xE5)
    scale = 1.0 if not maskable else 0.72  # maskable 需留出安全区
    img = []
    cx = size / 2
    for y in range(size):
        row = bytearray()
        t = y / size
        bg = tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))
        for x in range(size):
            r, g, b = bg
            # 白色柱状图（三根柱子）
            bw = size * 0.11 * scale      # 柱宽
            gap = size * 0.075 * scale    # 间距
            total = bw*3 + gap*2
            x0 = cx - total/2
            base = cx + total*0.42        # 底部基线
            heights = [size*0.30*scale, size*0.52*scale, size*0.42*scale]
            for i in range(3):
                bx = x0 + i*(bw+gap)
                by = base - heights[i]
                if rounded_rect(x+0.5, y+0.5, bx, by, bw, heights[i], bw*0.3):
                    r, g, b = 255, 255, 255
                    break
            # 右上角 AI 光点（小实心圆 + 环）
            sx, sy = cx + total/2 + size*0.02, base - size*0.52*scale
            d = math.hypot(x+0.5-sx, y+0.5-sy)
            sr = size*0.045*scale
            if d <= sr: r, g, b = 255, 255, 255
            elif sr*1.9 <= d <= sr*2.5: r, g, b = 255, 255, 255
            row += bytes((r, g, b, 255))
        img.append(bytes(row))

    raw = b''.join(b'\x00' + r for r in img)
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9))
    png += chunk(b'IEND', b'')
    path = os.path.join(OUT, name)
    with open(path, 'wb') as f: f.write(png)
    print(f'{name}: {size}x{size} {len(png)}B')

draw(192, 'icon-192.png')
draw(512, 'icon-512.png')
draw(512, 'icon-512-maskable.png', maskable=True)
draw(180, 'apple-touch-icon.png')
