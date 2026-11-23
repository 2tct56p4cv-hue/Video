#!/usr/bin/env python3
"""Board game: round board made of hexagons - city in the middle, beach, water around."""
import math, random

random.seed(11)
W = H = 2048
CX = CY = W / 2
R_BOARD = 960
S = 64                      # hex circumradius (pointy top)
SQ3 = math.sqrt(3)
GAP = 5

roof_cols = ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#264653", "#F7F3EA", "#D8E2EA", "#B5838D", "#6D597A"]
out = []
a = out.append

def hex_pts(x, y, s):
    return " ".join(f"{x + s*math.cos(math.radians(60*k-30)):.1f},{y + s*math.sin(math.radians(60*k-30)):.1f}" for k in range(6))

def tree(x, y, r):
    a(f'<circle cx="{x+r*0.25:.1f}" cy="{y+r*0.3:.1f}" r="{r:.1f}" fill="#000" opacity="0.12"/>')
    a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#4F9D5D"/>')
    a(f'<circle cx="{x-r*0.3:.1f}" cy="{y-r*0.3:.1f}" r="{r*0.45:.1f}" fill="#6DBA6F"/>')

def building(x, y, w, h):
    c = random.choice(roof_cols)
    hgt = random.uniform(5, 12)
    a(f'<rect x="{x-w/2+hgt:.1f}" y="{y-h/2+hgt:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#000" opacity="0.18"/>')
    a(f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{c}"/>')
    i = min(w, h) * 0.22
    a(f'<rect x="{x-w/2+i:.1f}" y="{y-h/2+i:.1f}" width="{w-2*i:.1f}" height="{h-2*i:.1f}" rx="3" fill="#fff" opacity="0.18"/>')
    if random.random() < 0.4:
        a(f'<circle cx="{x+w*0.22:.1f}" cy="{y-h*0.2:.1f}" r="{min(w,h)*0.09:.1f}" fill="#000" opacity="0.15"/>')

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a(f'<defs><clipPath id="board"><circle cx="{CX}" cy="{CY}" r="{R_BOARD}"/></clipPath></defs>')
a(f'<rect width="{W}" height="{H}" fill="#F4EEE2"/>')
a(f'<circle cx="{CX+10}" cy="{CY+14}" r="{R_BOARD}" fill="#000" opacity="0.12"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="{R_BOARD}" fill="#2C7DA0"/>')

# collect hexes
hexes = []
N = 12
for q in range(-N, N + 1):
    for r in range(-N, N + 1):
        x = CX + S * SQ3 * (q + r / 2)
        y = CY + S * 1.5 * r
        d = math.hypot(x - CX, y - CY)
        if d < R_BOARD + S:
            ring = (abs(q) + abs(r) + abs(q + r)) // 2
            hexes.append((x, y, d, ring))

R_CITY, R_BEACH = 520, 640
a('<g clip-path="url(#board)">')
# grey "streets" under the land hexes
a(f'<circle cx="{CX}" cy="{CY}" r="{R_BEACH-20}" fill="#5E6472"/>')
start_hex = None
for (x, y, d, ring) in hexes:
    s = S - GAP / 2
    if ring <= 1:                                   # central park (7 hexes)
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="#8CC474"/>')
    elif d <= R_CITY:
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="#D9D4C7"/>')
        kind = random.random()
        if kind < 0.16:                             # small park hex
            a(f'<polygon points="{hex_pts(x, y, s-8)}" fill="#8CC474"/>')
            for _ in range(4):
                ang = random.uniform(0, 2*math.pi); rr = random.uniform(0, 28)
                tree(x + rr*math.cos(ang), y + rr*math.sin(ang), random.uniform(9, 13))
        elif kind < 0.40:
            building(x, y, 62, 62)
        elif kind < 0.70:
            if random.random() < 0.5:
                building(x - 17, y, 30, 66); building(x + 17, y, 30, 66)
            else:
                building(x, y - 17, 66, 30); building(x, y + 17, 66, 30)
        else:
            for (dx, dy) in [(-16, -16), (16, -16), (-16, 16), (16, 16)]:
                if random.random() < 0.85:
                    building(x + dx, y + dy, 28, 28)
                else:
                    tree(x + dx, y + dy, 11)
    elif d <= R_BEACH:
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="#F2D49B"/>')
        if random.random() < 0.55:
            tree(x + random.uniform(-14, 14), y + random.uniform(-14, 14), random.uniform(12, 16))
        else:
            a(f'<ellipse cx="{x+random.uniform(-15,15):.0f}" cy="{y+random.uniform(-15,15):.0f}" rx="9" ry="6" fill="#E3BE7C"/>')
    else:
        shade = "#7FD0EE" if d < R_BEACH + 80 else ("#5BBCE4" if d < R_BEACH + 190 else "#3FA7D6")
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="{shade}"/>')
        if random.random() < 0.35:
            w = random.uniform(9, 12)
            a(f'<path d="M{x-2*w:.0f},{y:.0f} q{w/2:.0f},-{w/1.6:.0f} {w:.0f},0 t{w:.0f},0 t{w:.0f},0" fill="none" stroke="#BFE8F7" stroke-width="5" stroke-linecap="round" opacity="0.85"/>')
        if abs(x - CX) < 1 and y < CY and d + S <= R_BOARD - 10:
            if start_hex is None or y < start_hex[1]:
                start_hex = (x, y)

# central park details: pond in middle hex, paths
for k in range(6):
    ang = math.radians(60 * k)
    x2, y2 = CX + S*SQ3*1.05*math.cos(ang), CY + S*SQ3*1.05*math.sin(ang)
    a(f'<line x1="{CX}" y1="{CY}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#E8DFC9" stroke-width="12" stroke-linecap="round"/>')
a(f'<polygon points="{hex_pts(CX, CY, 50)}" fill="#7FD0EE" stroke="#F2D49B" stroke-width="9"/>')
for k in range(6):
    ang = math.radians(60 * k + 30)
    for rr, rad in [(S*1.25, 15), (S*1.65, 12)]:
        tree(CX + rr*math.cos(ang) + random.uniform(-6, 6), CY + rr*math.sin(ang) + random.uniform(-6, 6), rad)
a('</g>')

# START hex (harbour) in the water, top
if start_hex:
    x, y = start_hex
    a(f'<polygon points="{hex_pts(x, y, S-GAP/2)}" fill="#2A9D8F"/>')
    a(f'<text x="{x}" y="{y-24}" font-family="Nunito, Arial, sans-serif" font-weight="800" font-size="22" fill="#fff" text-anchor="middle" dominant-baseline="central">START</text>')

def pawn(x, y, col):
    a(f'<g transform="translate({x:.0f},{y:.0f})">'
      f'<ellipse cx="5" cy="26" rx="24" ry="8" fill="#000" opacity="0.2"/>'
      f'<path d="M-20,24 Q-20,4 -8,-2 A14,14 0 1 1 8,-2 Q20,4 20,24 Z" fill="{col}" stroke="#2B2D42" stroke-width="4"/>'
      f'<circle cx="-4" cy="-19" r="4" fill="#fff" opacity="0.6"/></g>')

if start_hex:
    x, y = start_hex
    pawn(x - 20, y + 14, "#E63946"); pawn(x + 20, y + 14, "#FFB703")
# a couple of pawns elsewhere on hexes
def hex_center(q, r):
    return CX + S*SQ3*(q + r/2), CY + S*1.5*r
pawn(*hex_center(4, 2), "#3A86FF")
pawn(*hex_center(-6, 6), "#8338EC")

def die(x, y, rot, pips):
    a(f'<g transform="translate({x},{y}) rotate({rot})">'
      f'<rect x="-62" y="-52" width="124" height="124" rx="24" fill="#000" opacity="0.15"/>'
      f'<rect x="-70" y="-70" width="140" height="140" rx="26" fill="#FFFFFF" stroke="#2B2D42" stroke-width="5"/>')
    for (px, py) in pips:
        a(f'<circle cx="{px}" cy="{py}" r="13" fill="#2B2D42"/>')
    a('</g>')
die(170, 1870, -12, [(-35, -35), (35, -35), (0, 0), (-35, 35), (35, 35)])
die(1880, 170, 14, [(-35, -35), (0, 0), (35, 35)])

a(f'<circle cx="{CX}" cy="{CY}" r="{R_BOARD}" fill="none" stroke="#2C7DA0" stroke-width="14"/>')
a('</svg>')
open(__file__.replace("gen_city_hex.py", "city_hex.svg"), "w").write("\n".join(out))
print("ok", len(hexes))
