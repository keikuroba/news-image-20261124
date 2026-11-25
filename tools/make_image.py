#!/usr/bin/env python3
"""Draw the news-image-20261124 broadsheet: five stories of 24 Nov 2026 + ticker.

Run from the repository root:  python3 tools/make_image.py
Writes entry.png (1024x1024, deterministic: fixed palette, fixed fonts, no time
or randomness anywhere in the picture).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "entry.png")

W, H = 1024, 1024
M = 36                      # side margin
CW = W - 2 * M              # content width
COLW = 466                  # story column width
GAP = 20                    # gap between the two columns

PAPER = (242, 237, 227)
INK = (22, 22, 22)
RED = (196, 30, 30)
TEAL = (0, 112, 112)
GREY = (96, 96, 96)
DARKGREY = (70, 70, 70)
NAVY = (10, 25, 55)
GREEN = (18, 92, 52)
YELLOW = (245, 205, 55)
SKY = (146, 188, 224)
GROUND = (118, 94, 68)

SERIF_DISP = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, fill):
    """Draw a wrapped paragraph; returns the y just below it."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def bezier(p0, p1, p2, n=48):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def rule(draw, y, weight=2, fill=INK):
    draw.rectangle([M, y, W - M, y + weight - 1], fill=fill)


def kicker(draw, x, y, text, fill):
    draw.text((x, y), text, font=font(SANS_B, 17), fill=fill)
    return y + 22


def headline(draw, x, y, text, max_w, size=28, leading=33):
    fnt = font(SERIF, size)
    return para(draw, x, y, text, fnt, max_w, leading, INK)


def body(draw, x, y, text, max_w, size=17, leading=23):
    fnt = font(SANS, size)
    return para(draw, x, y, text, fnt, max_w, leading, INK)


def stamp(img, x, y, text, size, color, angle=-12):
    """A rotated rubber-stamp label pasted onto img at (x, y). The layer is
    sized to the text so nothing spills past the scene it stamps."""
    fnt = font(SANS_B, size)
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    tw = probe.textlength(text, font=fnt)
    lw, lh = int(tw) + 44, size + 36
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rectangle([4, 4, lw - 5, lh - 5], outline=color, width=4)
    ld.text(((lw - tw) / 2, (lh - size) / 2 - 2), text, font=fnt, fill=color)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (x, y), layer)


def masthead(draw):
    title = "THE WORLD IN ONE IMAGE"
    size = 76
    while size > 40:
        fnt = font(SERIF_DISP, size)
        if draw.textlength(title, font=fnt) <= CW:
            break
        size -= 2
    draw.text((M, 20), title, font=fnt, fill=INK)
    draw.rectangle([M, 108, W - M, 110], fill=RED)
    draw.text((M, 118), "TUESDAY 24 NOVEMBER 2026",
              font=font(SANS_B, 20), fill=RED)
    right = "FIVE STORIES  •  ONE DAY"
    rf = font(SANS_B, 20)
    draw.text((W - M - draw.textlength(right, font=rf), 118), right,
              font=rf, fill=DARKGREY)
    draw.rectangle([M, 148, W - M, 150], fill=INK)
    draw.rectangle([M, 154, W - M, 154], fill=INK)


def lead_art(draw, x, y, w, h):
    """Night map: three red missile arcs falling onto south-east Poland."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=NAVY)
    # land silhouette along the bottom
    land = [(x, y + h), (x, y + h - 42), (x + 80, y + h - 58),
            (x + 170, y + h - 40), (x + 260, y + h - 62),
            (x + 350, y + h - 44), (x + w, y + h - 56),
            (x + w, y + h)]
    draw.polygon(land, fill=(24, 74, 44))
    # three arcs, each ending in a yellow impact dot on the land
    arcs = [((x + 70, y + 6), (x + 150, y + 60), (x + 175, y + h - 52)),
            ((x + 210, y + 2), (x + 285, y + 70), (x + 300, y + h - 46)),
            ((x + 330, y + 8), (x + 395, y + 80), (x + 405, y + h - 58))]
    for p0, p1, p2 in arcs:
        draw.line(bezier(p0, p1, p2), fill=(235, 70, 50), width=4)
        ex, ey = p2
        draw.ellipse([ex - 9, ey - 9, ex + 9, ey + 9],
                     fill=YELLOW, outline=(20, 20, 20), width=2)
    # compass rose, top right
    cx, cy = x + w - 52, y + 48
    draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26],
                 outline=(235, 235, 235), width=2)
    star = [(cx, cy - 24), (cx + 6, cy - 6), (cx + 24, cy),
            (cx + 6, cy + 6), (cx, cy + 24), (cx - 6, cy + 6),
            (cx - 24, cy), (cx - 6, cy - 6)]
    draw.polygon(star, fill=(235, 235, 235))
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(235, 235, 235))
    # labels
    draw.text((x + 14, y + 12), "POLAND  •  20 NOV",
              font=font(SANS_B, 19), fill=(255, 255, 255))
    draw.text((x + 14, y + h - 34), "Kh-101  ×  3",
              font=font(SANS_B, 21), fill=YELLOW)


def lead(draw, y0):
    y = kicker(draw, M, y0, "LEAD — EUROPE ON EDGE", RED)
    y = headline(draw, M, y + 4,
                 "NATO rushes AWACS to Poland after Russian missiles "
                 "fall on its soil", 470, size=36, leading=43)
    body(draw, M, y + 6,
         "Three Russian Kh-101 cruise missiles came down in south-east "
         "Poland on 20 November. The alliance is sending AWACS "
         "surveillance planes to guard the eastern flank.", 470)
    lead_art(draw, 530, y0, 458, 232)
    return y0 + 242


def barrier_art(draw, x, y, w, h):
    """Closed border: striped barrier, fence posts, warning triangle."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    draw.rectangle([x, y, x + w - 1, y + 32], fill=SKY)
    draw.rectangle([x, y + 32, x + w - 1, y + h - 1], fill=GROUND)
    # fence posts + top rail
    for px in range(x + 24, x + w - 8, 44):
        draw.rectangle([px, y + 30, px + 8, y + h - 8], fill=(70, 60, 48))
    draw.line([(x, y + 36), (x + w, y + 36)], fill=(70, 60, 48), width=3)
    # red-white striped barrier bar with two legs
    bx0, by0, bx1 = x + 28, y + 46, x + w - 28
    draw.rectangle([bx0, by0, bx1, by0 + 18], outline=INK, width=2)
    flip = False
    seg = bx0
    while seg < bx1:
        nxt = min(seg + 24, bx1)
        draw.rectangle([seg, by0, nxt, by0 + 18],
                       fill=RED if flip else (255, 255, 255))
        flip = not flip
        seg = nxt
    draw.rectangle([bx0 + 6, by0 + 18, bx0 + 16, y + h - 6], fill=INK)
    draw.rectangle([bx1 - 16, by0 + 18, bx1 - 6, y + h - 6], fill=INK)
    # warning triangle, right side
    tx, ty = x + w - 78, y + 62
    draw.polygon([(tx, ty), (tx + 56, ty), (tx + 28, ty - 42)],
                 fill=YELLOW, outline=INK, width=2)
    draw.text((tx + 22, ty - 36), "!", font=font(SANS_B, 22), fill=INK)
    draw.text((x + 10, y + 8), "BORDER CLOSES 1 DEC",
              font=font(SANS_B, 15), fill=NAVY)


def chart_art(draw, x, y, w, h):
    """Soaring market chart: green line rockets up, AI chip at the corner."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=(238, 246, 238),
                   outline=INK, width=2)
    for gy in range(y + 18, y + h - 4, 18):
        draw.line([(x + 6, gy), (x + w - 6, gy)], fill=(205, 220, 205), width=1)
    pts = [(x + 12, y + h - 20), (x + 80, y + h - 34),
           (x + 140, y + h - 30), (x + 195, y + h - 50),
           (x + 250, y + h - 46), (x + 305, y + h - 76),
           (x + w - 16, y + 12)]
    draw.line(pts, fill=GREEN, width=5)
    draw.ellipse([x + w - 24, y + 4, x + w - 8, y + 20], fill=GREEN)
    # AI chip
    cx0, cy0 = x + 14, y + 10
    draw.rectangle([cx0, cy0, cx0 + 44, cy0 + 44], fill=(24, 24, 24))
    draw.rectangle([cx0 + 10, cy0 + 10, cx0 + 34, cy0 + 34],
                   outline=(120, 220, 130), width=2)
    draw.text((cx0 + 12, cy0 + 15), "AI", font=font(SANS_B, 16),
              fill=(120, 220, 130))
    draw.text((x + 68, y + 8), "NVDA", font=font(SANS_B, 14), fill=INK)
    big = font(SANS_B, 26)
    pct = "+31%"
    draw.text((x + w - 10 - draw.textlength(pct, font=big), y + h - 36),
              pct, font=big, fill=GREEN)
    draw.text((x + 10, y + h - 22), "NASDAQ +6.5%  •  S&P +4.7%",
              font=font(SANS_B, 13), fill=INK)


def hall_art(img, draw, x, y, w, h):
    """Empty summit hall: rows of chairs and a tilted NO DEAL stamp."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    draw.rectangle([x, y, x + w - 1, y + 28], fill=(96, 110, 128))
    draw.rectangle([x, y + 28, x + w - 1, y + h - 1], fill=(226, 216, 196))
    for row, ry in enumerate((y + 42, y + 58)):
        for cx in range(x + 22 + row * 8, x + w - 28, 42):
            draw.rectangle([cx, ry, cx + 28, ry + 11], fill=(120, 96, 66))
            draw.rectangle([cx + 4, ry - 6, cx + 24, ry], fill=(140, 114, 80))
    draw.rectangle([x + w - 70, y + 8, x + w - 26, y + 26], fill=(70, 60, 48))
    stamp(img, x + 268, y + 10, "NO DEAL", 22, RED, angle=-10)
    draw.text((x + 10, y + 7), "ANTALYA, TÜRKIYE",
              font=font(SANS_B, 14), fill=(255, 255, 255))


def strait_art(draw, x, y, w, h):
    """The strait: tanker silhouette, mines, a count of the dead."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=(24, 68, 92),
                   outline=INK, width=2)
    for yy in range(y + 40, y + h, 16):
        draw.line([(x, yy), (x + w, yy)], fill=(52, 110, 150), width=2)
    # tanker hull + funnel + smoke
    hx0, hy0 = x + 30, y + 52
    draw.rectangle([hx0, hy0, hx0 + 180, hy0 + 22], fill=(30, 30, 34))
    draw.rectangle([hx0 + 140, hy0 - 20, hx0 + 172, hy0], fill=(30, 30, 34))
    draw.rectangle([hx0 + 6, hy0 - 9, hx0 + 56, hy0], fill=(120, 40, 36))
    draw.line([(hx0 + 156, hy0 - 34), (hx0 + 156, hy0 - 20)],
              fill=(200, 200, 200), width=3)
    draw.ellipse([hx0 + 16, hy0 - 28, hx0 + 46, hy0 - 4], fill=(90, 90, 90))
    # mines
    for mx, my in [(x + 258, y + 62), (x + 292, y + 42),
                   (x + 230, y + 32)]:
        draw.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=(20, 20, 20),
                     outline=YELLOW, width=2)
        for dx, dy in [(0, -12), (0, 12), (-12, 0), (12, 0)]:
            draw.line([(mx, my), (mx + dx, my + dy)], fill=(20, 20, 20),
                      width=2)
    draw.text((x + 10, y + 7), "STRAIT OF HORMUZ",
              font=font(SANS_B, 14), fill=(255, 255, 255))
    big = font(SANS_B, 26)
    dead = "25 DEAD"
    draw.text((x + w - 10 - draw.textlength(dead, font=big), y + h - 34),
              dead, font=big, fill=YELLOW)


def story(img, draw, x, y, kick, color, head, text, art, art_h=80):
    """One column: kicker, headline, body, scene. Returns bottom y."""
    y = kicker(draw, x, y, kick, color)
    y = headline(draw, x, y + 4, head, COLW)
    y = body(draw, x, y + 6, text, COLW)
    top = y + 8
    if art is hall_art:
        art(img, draw, x, top, COLW, art_h)
    else:
        art(draw, x, top, COLW, art_h)
    return top + art_h


def ticker(draw, y):
    draw.rectangle([M, y, W - M, y + 62], fill=INK)
    draw.text((M + 12, y + 6), "ALSO TODAY", font=font(SANS_B, 15),
              fill=YELLOW)
    small = font(SANS, 14)
    draw.text((M + 12, y + 26),
              "INDONESIA FACTORY FIRE: 24 DEAD  •  TRUMP HALTS IOWA "
              "EXPLOSIVES BLAST  •  ALCARAZ WINS FIRST ATP FINALS TITLE",
              font=small, fill=(255, 255, 255))
    draw.text((M + 12, y + 44),
              "INDIA PLEDGES $1.6BN TO NEPAL  •  GAZA STRIKES KILL UN "
              "WORKER  •  VERSTAPPEN WINS IN LAS VEGAS",
              font=small, fill=(255, 255, 255))
    return y + 62


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    masthead(draw)

    # ---- lead: NATO / Poland ----
    bottom = lead(draw, 168)
    rule(draw, bottom + 12)

    # ---- middle row: Estonia | Nvidia ----
    x2 = M + COLW + GAP
    y = bottom + 26
    left = story(img, draw, M, y, "BALTICS", RED,
                 "Russia warns Estonia of “open war”",
                 "Moscow summons Tallinn's envoy as Estonia moves to shut "
                 "its Russian border from 1 December.",
                 barrier_art)
    right = story(img, draw, x2, y, "MARKETS", GREEN,
                  "Huang is back — Nvidia soars 31%",
                  "Eleven days after he quit, Jensen Huang is reinstated "
                  "as chief executive. Shares jump a third.",
                  chart_art)
    row_end = max(left, right)
    rule(draw, row_end + 12)

    # ---- bottom row: COP31 | Hormuz ----
    y = row_end + 26
    left = story(img, draw, M, y, "CLIMATE", TEAL,
                 "COP31 collapses: no deal in Antalya",
                 "The summit ends without agreement; the draft drops any "
                 "fossil-fuel phase-out.",
                 hall_art)
    right = story(img, draw, x2, y, "THE GULF", NAVY,
                  "25 seafarers killed at Hormuz, UN says",
                  "The United Nations counts 25 dead and 134 attacks on "
                  "shipping since February.",
                  strait_art)
    row_end = max(left, right)

    # ---- ticker + footer ----
    ty = ticker(draw, row_end + 14)
    foot = font(SANS, 13)
    draw.text((M, ty + 8),
              "Drawn from the day's reporting — Tuesday 24 November 2026",
              font=foot, fill=GREY)
    tail = "make.fun  •  news-image-20261124"
    draw.text((W - M - draw.textlength(tail, font=foot), ty + 8),
              tail, font=foot, fill=GREY)

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    build()
