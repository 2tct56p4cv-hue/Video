#!/usr/bin/env python3
"""Board game matching the wooden board: flat-top hexes, round jagged outline,
six puzzle pieces (sectors). City + central park inside, beach, water around.
Adjust RADIUS (in hex rows from the centre) to match the physical board."""
import math, random

random.seed(11)
RADIUS = 10.3          # board radius in hex widths (flat-to-flat) -> ~380 hexes
CITY_R, BEACH_R = 6.2, 7.4
W = H = 2048
CX = CY = W / 2
SQ3 = math.sqrt(3)
S = (W - 70) / 2 / (RADIUS + 0.6) / SQ3   # circumradius in px
K = S / 64                                 # scale vs. the previous design
GAP = 3

roof_cols = ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#264653", "#F7F3EA", "#D8E2EA", "#B5838D", "#6D597A"]
out = []
a = out.append

def corner(x, y, s, k):
    t = math.radians(60 * k)
    return x + s * math.cos(t), y + s * math.sin(t)

def hex_pts(x, y, s):
    return " ".join("%.1f,%.1f" % corner(x, y, s, k) for k in range(6))

def center(q, r):
    return CX + S * 1.5 * q, CY + S * SQ3 * (r + q / 2)

def tree(x, y, r):
    r *= K
    a(f'<circle cx="{x+r*0.25:.1f}" cy="{y+r*0.3:.1f}" r="{r:.1f}" fill="#000" opacity="0.12"/>')
    a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#4F9D5D"/>')
    a(f'<circle cx="{x-r*0.3:.1f}" cy="{y-r*0.3:.1f}" r="{r*0.45:.1f}" fill="#6DBA6F"/>')

def building(x, y, w, h):
    w *= K; h *= K
    c = random.choice(roof_cols)
    hg = random.uniform(5, 11) * K
    a(f'<rect x="{x-w/2+hg:.1f}" y="{y-h/2+hg:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{3*K:.1f}" fill="#000" opacity="0.18"/>')
    a(f'<rect x="{x-w/2:.1f}" y="{y-h/2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{3*K:.1f}" fill="{c}"/>')
    i = min(w, h) * 0.22
    a(f'<rect x="{x-w/2+i:.1f}" y="{y-h/2+i:.1f}" width="{w-2*i:.1f}" height="{h-2*i:.1f}" rx="{2*K:.1f}" fill="#fff" opacity="0.18"/>')
    if random.random() < 0.4:
        a(f'<circle cx="{x+w*0.22:.1f}" cy="{y-h*0.2:.1f}" r="{min(w,h)*0.09:.1f}" fill="#000" opacity="0.15"/>')

# --- hexes of the board ---
cells = {}
N = int(RADIUS) + 3
for q in range(-2 * N, 2 * N + 1):
    for r in range(-2 * N, 2 * N + 1):
        x, y = center(q, r)
        d = math.hypot(x - CX, y - CY) / (S * SQ3)   # distance in hex widths
        if d <= RADIUS:
            ang = (math.degrees(math.atan2(y - CY, x - CX)) + 0.01) % 360
            cells[(q, r)] = dict(x=x, y=y, d=d, sector=int(ang // 60) if d > 0 else 0,
                                 ring=(abs(q) + abs(r) + abs(q + r)) // 2)

NB = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
# neighbour direction -> edge (corner indices) for flat-top hexes
def edge_for(dq, dr):
    nx, ny = center(dq, dr)
    ang = math.degrees(math.atan2(ny - CY, nx - CX)) % 360   # 30, 90, ...
    k = int(round((ang - 30) / 60)) % 6
    return k, (k + 1) % 6

a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a(f'<rect width="{W}" height="{H}" fill="#F4EEE2"/>')

# board shadow + base (gap colour)
for c in cells.values():
    a(f'<polygon points="{hex_pts(c["x"]+8*K, c["y"]+11*K, S+1)}" fill="#000" opacity="0.10"/>')
for c in cells.values():
    base = "#5E6472" if c["d"] <= BEACH_R - 0.6 else "#2C7DA0"
    a(f'<polygon points="{hex_pts(c["x"], c["y"], S+1)}" fill="{base}"/>')

start = None
for (q, r), c in cells.items():
    x, y, d, ring = c["x"], c["y"], c["d"], c["ring"]
    s = S - GAP / 2
    if ring <= 1:
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="#8CC474"/>')
    elif d <= CITY_R:
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="#D9D4C7"/>')
        kind = random.random()
        if kind < 0.16:
            a(f'<polygon points="{hex_pts(x, y, s-7*K)}" fill="#8CC474"/>')
            for _ in range(4):
                t = random.uniform(0, 2*math.pi); rr = random.uniform(0, 26*K)
                tree(x + rr*math.cos(t), y + rr*math.sin(t), random.uniform(9, 13))
        elif kind < 0.40:
            building(x, y, 62, 62)
        elif kind < 0.70:
            if random.random() < 0.5:
                building(x - 17*K, y, 30, 66); building(x + 17*K, y, 30, 66)
            else:
                building(x, y - 17*K, 66, 30); building(x, y + 17*K, 66, 30)
        else:
            for (dx, dy) in [(-16, -16), (16, -16), (-16, 16), (16, 16)]:
                if random.random() < 0.85:
                    building(x + dx*K, y + dy*K, 28, 28)
                else:
                    tree(x + dx*K, y + dy*K, 11)
    elif d <= BEACH_R:
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="#F2D49B"/>')
        if random.random() < 0.55:
            tree(x + random.uniform(-14, 14)*K, y + random.uniform(-14, 14)*K, random.uniform(12, 16))
        else:
            a(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{9*K:.1f}" ry="{6*K:.1f}" fill="#E3BE7C"/>')
    else:
        shade = "#7FD0EE" if d < BEACH_R + 1.0 else ("#5BBCE4" if d < BEACH_R + 2.0 else "#3FA7D6")
        a(f'<polygon points="{hex_pts(x, y, s)}" fill="{shade}"/>')
        if random.random() < 0.35:
            w = random.uniform(9, 12) * K
            a(f'<path d="M{x-2*w:.0f},{y:.0f} q{w/2:.1f},-{w/1.6:.1f} {w:.1f},0 t{w:.1f},0 t{w:.1f},0" fill="none" stroke="#BFE8F7" stroke-width="{4.5*K:.1f}" stroke-linecap="round" opacity="0.85"/>')
        if q == 0 and r < 0 and (start is None or r < start[1]):
            start = (q, r)

# central park details
for k in range(6):
    t = math.radians(60 * k + 30)
    a(f'<line x1="{CX}" y1="{CY}" x2="{CX+S*SQ3*1.05*math.cos(t):.1f}" y2="{CY+S*SQ3*1.05*math.sin(t):.1f}" stroke="#E8DFC9" stroke-width="{12*K:.1f}" stroke-linecap="round"/>')
a(f'<polygon points="{hex_pts(CX, CY, 50*K)}" fill="#7FD0EE" stroke="#F2D49B" stroke-width="{9*K:.1f}"/>')
for k in range(6):
    t = math.radians(60 * k)
    for rr, rad in [(S*1.25, 15), (S*1.65, 12)]:
        tree(CX + rr*math.cos(t), CY + rr*math.sin(t), rad)

# START
def pawn(x, y, col):
    a(f'<g transform="translate({x:.0f},{y:.0f}) scale({K:.3f})">'
      f'<ellipse cx="5" cy="26" rx="24" ry="8" fill="#000" opacity="0.2"/>'
      f'<path d="M-20,24 Q-20,4 -8,-2 A14,14 0 1 1 8,-2 Q20,4 20,24 Z" fill="{col}" stroke="#2B2D42" stroke-width="4"/>'
      f'<circle cx="-4" cy="-19" r="4" fill="#fff" opacity="0.6"/></g>')
if start:
    x, y = center(*start)
    a(f'<polygon points="{hex_pts(x, y, S-GAP/2)}" fill="#2A9D8F"/>')
    a(f'<text x="{x:.0f}" y="{y-24*K:.0f}" font-family="Nunito, Arial, sans-serif" font-weight="800" font-size="{20*K:.0f}" fill="#fff" text-anchor="middle" dominant-baseline="central">START</text>')
    pawn(x - 19*K, y + 12*K, "#E63946"); pawn(x + 19*K, y + 12*K, "#FFB703")
pawn(*center(5, -1), "#3A86FF")
pawn(*center(-7, 9), "#8338EC")

# seams between the 6 wooden pieces + outer outline
seam, rim = [], []
for (q, r), c in cells.items():
    for dq, dr in NB:
        k0, k1 = edge_for(dq, dr)
        p0 = corner(c["x"], c["y"], S, k0); p1 = corner(c["x"], c["y"], S, k1)
        nb = cells.get((q + dq, r + dr))
        seg = f'M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f}'
        if nb is None:
            rim.append(seg)
        elif nb["sector"] != c["sector"] and (q, r) < (q + dq, r + dr):
            seam.append(seg)
a(f'<path d="{" ".join(seam)}" fill="none" stroke="#1D2B36" stroke-width="{5*K:.1f}" stroke-linecap="round"/>')
a(f'<path d="{" ".join(rim)}" fill="none" stroke="#1D3B4D" stroke-width="{6*K:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')

a('</svg>')
open(__file__.replace("gen_city_hexboard.py", "city_hexboard.svg"), "w").write("\n".join(out))
print("hexes:", len(cells), "per piece:", [sum(1 for c in cells.values() if c["sector"] == i) for i in range(6)])
