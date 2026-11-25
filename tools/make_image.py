#!/usr/bin/env python3
"""Draw the 24 November 2026 world-news broadsheet (1024x1024 PNG).

Five lead stories plus a ticker, drawn with Pillow only. Layout flows
downwards: each block starts where the previous one ended, so text can
never run into the block below it. Run: python3 tools/make_image.py
writes entry.png beside the repository root.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (178, 34, 34)
NAVY = (18, 52, 86)
TEAL = (14, 90, 86)
GREEN = (18, 110, 52)
GREY = (90, 88, 82)

DJ = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(DJ, "DejaVuSerif.ttf")
SERIF_B = os.path.join(DJ, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(DJ, "DejaVuSans.ttf")
SANS_B = os.path.join(DJ, "DejaVuSans-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(drw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if drw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(drw, xy, text, fnt, max_w, fill=INK, leading=None):
    """Draw a wrapped paragraph; returns y just below the last line."""
    x, y = xy
    lead = leading or int(fnt.size * 1.28)
    for line in wrap(drw, text, fnt, max_w):
        drw.text((x, y), line, font=fnt, fill=fill)
        y += lead
    return y


def rule(drw, x0, y, x1, width=2):
    drw.line([(x0, y), (x1, y)], fill=INK, width=width)


def kicker(drw, x, y, text, color):
    f = font(SANS_B, 15)
    drw.text((x, y), text.upper(), font=f, fill=color)
    return y + 21


def scene_frame(drw, box, fill):
    drw.rectangle(box, fill=fill, outline=INK, width=2)


def draw_nato_scene(drw, box):
    """Night sky over south-east Poland: three missile arcs, NATO star."""
    x0, y0, x1, y1 = box
    scene_frame(drw, box, (16, 32, 58))
    drw.polygon([(x0, y1), (x0, y1 - 44), (x0 + 90, y1 - 58),
                 (x0 + 210, y1 - 38), (x0 + 330, y1 - 56),
                 (x1, y1 - 34), (x1, y1)], fill=(38, 74, 52))
    for sx, sy, ex, ey in [(x0 + 30, y0 + 24, x0 + 150, y1 - 62),
                           (x0 + 120, y0 + 12, x0 + 235, y1 - 48),
                           (x0 + 210, y0 + 28, x0 + 315, y1 - 60)]:
        midx, midy = (sx + ex) // 2, min(sy, ey) - 30
        pts = []
        for t in range(0, 21):
            u = t / 20.0
            px = int((1 - u) ** 2 * sx + 2 * (1 - u) * u * midx + u * u * ex)
            py = int((1 - u) ** 2 * sy + 2 * (1 - u) * u * midy + u * u * ey)
            pts.append((px, py))
        drw.line(pts, fill=(232, 84, 60), width=4)
        drw.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(255, 214, 90))
    for cx, cy in [(x0 + 150, y1 - 62), (x0 + 235, y1 - 48),
                   (x0 + 315, y1 - 60)]:
        drw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9],
                    outline=(255, 214, 90), width=2)
    cx, cy, r = x1 - 42, y0 + 42, 26
    drw.ellipse([cx - r, cy - r, cx + r, cy + r],
                outline=(255, 255, 255), width=2)
    drw.polygon([(cx, cy - r - 8), (cx + 7, cy), (cx, cy + r + 8),
                 (cx - 7, cy)], fill=(255, 255, 255))
    drw.polygon([(cx - r - 8, cy), (cx, cy + 7), (cx + r + 8, cy),
                 (cx, cy - 7)], fill=(255, 255, 255))
    lab = font(SANS_B, 15)
    drw.text((x0 + 10, y0 + 8), "POLAND  •  20 NOV", font=lab,
             fill=(255, 255, 255), stroke_width=3,
             stroke_fill=(16, 32, 58))
    drw.text((x0 + 10, y1 - 26), "Kh-101  ×  3", font=lab,
             fill=(255, 214, 90))


def draw_estonia_scene(drw, box):
    """Closed border: striped barrier, fence, warning triangle."""
    x0, y0, x1, y1 = box
    scene_frame(drw, box, (214, 208, 190))
    drw.rectangle([x0, y0, x1, y0 + 44], fill=(140, 170, 196))
    drw.rectangle([x0, y0 + 44, x1, y1], fill=(120, 110, 88))
    for px in range(x0 + 26, x1 - 10, 44):
        drw.rectangle([px, y0 + 40, px + 8, y1 - 12], fill=(70, 60, 48))
    drw.line([(x0, y0 + 50), (x1, y0 + 50)], fill=(70, 60, 48), width=3)
    bx0, by0 = x0 + 30, y0 + 58
    drw.rectangle([bx0, by0, x1 - 30, by0 + 22], outline=INK, width=2)
    toggle = False
    for sx in range(bx0, x1 - 30, 26):
        drw.rectangle([sx, by0, min(sx + 26, x1 - 30), by0 + 22],
                      fill=RED if toggle else (255, 255, 255))
        toggle = not toggle
    drw.rectangle([x0 + 34, by0 + 22, x0 + 46, y1 - 10], fill=INK)
    drw.rectangle([x1 - 46, by0 + 22, x1 - 34, y1 - 10], fill=INK)
    tx, ty = x1 - 96, y0 + 52
    drw.polygon([(tx, ty), (tx + 62, ty), (tx + 31, ty - 46)],
                fill=(255, 214, 90), outline=INK, width=2)
    drw.text((tx + 25, ty - 38), "!", font=font(SANS_B, 24), fill=INK)
    lab = font(SANS_B, 14)
    drw.text((x0 + 10, y0 + 8), "BORDER CLOSES 1 DEC", font=lab, fill=INK)


def draw_nvidia_scene(drw, box):
    """Soaring chart: green line rockets up, chip at the corner."""
    x0, y0, x1, y1 = box
    scene_frame(drw, box, (238, 246, 238))
    for gy in range(y0 + 20, y1 - 6, 22):
        drw.line([(x0 + 6, gy), (x1 - 6, gy)], fill=(205, 220, 205), width=1)
    pts = [(x0 + 12, y1 - 22), (x0 + 80, y1 - 38), (x0 + 140, y1 - 34),
           (x0 + 195, y1 - 56), (x0 + 250, y1 - 52), (x0 + 305, y1 - 96),
           (x1 - 16, y0 + 14)]
    drw.line(pts, fill=GREEN, width=5)
    drw.ellipse([x1 - 24, y0 + 6, x1 - 8, y0 + 22], fill=GREEN)
    cx0, cy0 = x0 + 16, y0 + 12
    drw.rectangle([cx0, cy0, cx0 + 48, cy0 + 48], fill=(24, 24, 24))
    drw.rectangle([cx0 + 11, cy0 + 11, cx0 + 37, cy0 + 37],
                  outline=GREEN, width=2)
    drw.text((cx0 + 14, cy0 + 18), "AI", font=font(SANS_B, 17),
             fill=(120, 220, 130))
    lab = font(SANS_B, 14)
    drw.text((x0 + 76, y0 + 8), "NVDA", font=lab, fill=INK)
    big = font(SANS_B, 28)
    pct = "+31%"
    drw.text((x1 - 10 - drw.textlength(pct, font=big), y1 - 40), pct,
             font=big, fill=GREEN)
    drw.text((x0 + 10, y1 - 24), "NASDAQ +6.5%  •  S&P +4.7%",
             font=lab, fill=INK)


def draw_cop_scene(img, drw, box):
    """Empty summit hall: rows of chairs and a tilted NO DEAL stamp."""
    x0, y0, x1, y1 = box
    scene_frame(drw, box, (226, 216, 196))
    drw.rectangle([x0, y0, x1, y0 + 34], fill=(96, 110, 128))
    for row, ry in enumerate((y0 + 48, y0 + 66)):
        for cx in range(x0 + 24 + row * 8, x1 - 30, 44):
            drw.rectangle([cx, ry, cx + 30, ry + 12], fill=(120, 96, 66))
            drw.rectangle([cx + 4, ry - 7, cx + 26, ry], fill=(140, 114, 80))
    drw.rectangle([x0 + 396, y0 + 12, x0 + 440, y0 + 34], fill=(70, 60, 48))
    stamp = Image.new("RGBA", (150, 48), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([2, 2, 147, 45], outline=RED, width=4)
    sd.text((11, 9), "NO DEAL", font=font(SANS_B, 28), fill=RED)
    stamp = stamp.rotate(-9, expand=True, resample=Image.BICUBIC)
    img.paste(stamp, (x0 + 236, y0 + 30), stamp)
    lab = font(SANS_B, 14)
    drw.text((x0 + 10, y0 + 8), "ANTALYA, TÜRKIYE", font=lab, fill=INK)


def draw_hormuz_scene(drw, box):
    """The strait: tanker silhouette, mines, a count of the dead."""
    x0, y0, x1, y1 = box
    scene_frame(drw, box, (24, 68, 92))
    for yy in range(y0 + 48, y1, 20):
        drw.line([(x0, yy), (x1, yy)], fill=(52, 110, 150), width=2)
    hx0, hy0 = x0 + 34, y0 + 62
    drw.rectangle([hx0, hy0, hx0 + 190, hy0 + 26], fill=(30, 30, 34))
    drw.rectangle([hx0 + 150, hy0 - 22, hx0 + 184, hy0], fill=(30, 30, 34))
    drw.rectangle([hx0 + 8, hy0 - 10, hx0 + 60, hy0], fill=(120, 40, 36))
    drw.line([(hx0 + 168, hy0 - 38), (hx0 + 168, hy0 - 22)],
             fill=(200, 200, 200), width=3)
    for mx, my in [(x0 + 268, y0 + 74), (x0 + 300, y0 + 52),
                   (x0 + 238, y0 + 40)]:
        drw.ellipse([mx - 9, my - 9, mx + 9, my + 9], fill=(20, 20, 20),
                    outline=(255, 214, 90), width=2)
        for dx, dy in [(0, -13), (0, 13), (-13, 0), (13, 0)]:
            drw.line([(mx, my), (mx + dx, my + dy)], fill=(20, 20, 20),
                     width=2)
    drw.ellipse([hx0 + 20, hy0 - 30, hx0 + 52, hy0 - 6], fill=(90, 90, 90))
    lab = font(SANS_B, 14)
    drw.text((x0 + 10, y0 + 8), "STRAIT OF HORMUZ", font=lab,
             fill=(255, 255, 255))
    big = font(SANS_B, 28)
    dead = "25 DEAD"
    drw.text((x1 - 10 - drw.textlength(dead, font=big), y1 - 40), dead,
             font=big, fill=(255, 214, 90))


def story_block(drw, img, x, y, width, kick, color, head, body,
                scene_fn, scene_h, head_size=24):
    """One column: kicker, headline, body, scene. Returns bottom y."""
    y = kicker(drw, x, y, kick, color)
    y = para(drw, (x, y), head, font(SERIF_B, head_size), width,
             leading=int(head_size * 1.12))
    y = para(drw, (x, y + 8), body, font(SERIF, 16), width, leading=20)
    top = y + 10
    if scene_fn is draw_cop_scene:
        draw_cop_scene(img, drw, (x, top, x + width, top + scene_h))
    else:
        scene_fn(drw, (x, top, x + width, top + scene_h))
    return top + scene_h


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 36

    # ---- masthead ----
    rule(d, mx, 26, W - mx, 3)
    d.text((mx, 34), "THE WORLD IN ONE IMAGE",
           font=font(SERIF_B, 58), fill=INK)
    date_f = font(SANS_B, 20)
    d.text((mx, 104), "TUESDAY 24 NOVEMBER 2026", font=date_f, fill=RED)
    d.text((W - mx - 320, 104), "FIVE STORIES  •  ONE DAY", font=date_f,
           fill=GREY)
    rule(d, mx, 132, W - mx, 2)
    rule(d, mx, 137, W - mx, 5)

    # ---- lead: NATO / Poland (scene fixed height, text flows) ----
    lead_top = 150
    y = kicker(d, mx, lead_top, "Lead — Europe on edge", RED)
    y = para(d, (mx, y),
             "NATO rushes AWACS to Poland after Russian missiles fall on its soil",
             font(SERIF_B, 33), W - 2 * mx - 400, leading=37)
    y = para(d, (mx, y + 10),
             "Three Russian Kh-101 cruise missiles came down in south-east "
             "Poland on 20 November. The alliance is sending AWACS "
             "surveillance planes to guard the eastern flank.",
             font(SERIF, 19), W - 2 * mx - 400, leading=24)
    draw_nato_scene(d, (W - mx - 372, lead_top, W - mx, lead_top + 200))
    lead_bottom = max(y, lead_top + 200)
    rule(d, mx, lead_bottom + 10, W - mx, 2)

    # ---- middle row: Estonia | Nvidia ----
    col_w = (W - 2 * mx - 28) // 2
    x2 = mx + col_w + 28
    mid_top = lead_bottom + 24
    left_end = story_block(
        d, img, mx, mid_top, col_w, "Baltics", RED,
        "Russia warns Estonia of “open war”",
        "Moscow summons Tallinn's envoy after Estonia says it will shut "
        "its Russian border from 1 December, blaming a Russian arson "
        "plot against a defence firm.",
        draw_estonia_scene, 100)
    right_end = story_block(
        d, img, x2, mid_top, col_w, "Markets", GREEN,
        "Huang is back — Nvidia soars 31%",
        "Eleven days after he quit, Jensen Huang is reinstated as chief "
        "executive. Shares jump a third, the Nasdaq 6.5% and the S&P "
        "500 4.7% — the best day since April 2025.",
        draw_nvidia_scene, 100)
    row_end = max(left_end, right_end)
    rule(d, mx, row_end + 10, W - mx, 2)

    # ---- bottom row: COP31 | Hormuz ----
    y = row_end + 24
    left_end = story_block(
        d, img, mx, y, col_w, "Climate", TEAL,
        "COP31 collapses: no deal in Antalya",
        "The climate summit ends without agreement and the draft drops "
        "any fossil-fuel phase-out — a split world walks away "
        "empty-handed.",
        draw_cop_scene, 90)
    right_end = story_block(
        d, img, x2, y, col_w, "The Gulf", NAVY,
        "25 seafarers killed at Hormuz, UN says",
        "The United Nations counts 25 dead and 134 attacks on shipping "
        "since February, and warns the strangled strait must not "
        "become “the new normal”.",
        draw_hormuz_scene, 90)
    row_end = max(left_end, right_end)

    # ---- ticker ----
    ty = row_end + 14
    d.rectangle([mx, ty, W - mx, ty + 58], fill=INK)
    d.text((mx + 12, ty + 6), "ALSO TODAY", font=font(SANS_B, 15),
           fill=(255, 214, 90))
    small = font(SANS, 14)
    d.text((mx + 12, ty + 24),
           "INDONESIA FACTORY FIRE: 24 DEAD  •  TRUMP HALTS IOWA "
           "EXPLOSIVES BLAST  •  ALCARAZ WINS FIRST ATP FINALS TITLE",
           font=small, fill=(255, 255, 255))
    d.text((mx + 12, ty + 42),
           "INDIA PLEDGES $1.6BN TO NEPAL  •  GAZA STRIKES KILL UN "
           "WORKER  •  VERSTAPPEN WINS IN LAS VEGAS",
           font=small, fill=(255, 255, 255))

    # ---- footer ----
    foot = font(SANS, 12)
    d.text((mx, ty + 66),
           "Drawn from the day's reporting — Tuesday 24 November 2026",
           font=foot, fill=GREY)
    d.text((W - mx - 210, ty + 66), "make.fun  •  news-image-20261124",
           font=foot, fill=GREY)

    out = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "entry.png"))
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    build()
