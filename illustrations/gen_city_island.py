#!/usr/bin/env python3
"""Flat illustration: round city island surrounded by water, with an earthworm."""
import math, random

random.seed(7)
W = H = 2048
CX = CY = W / 2
R_WATER = 960   # outer edge of water
R_SHORE = 640   # sand ring
R_LAND = 610    # city land

out = []
a = out.append
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
a('''<defs>
  <clipPath id="land"><circle cx="1024" cy="1024" r="610"/></clipPath>
  <clipPath id="water"><circle cx="1024" cy="1024" r="960"/></clipPath>
</defs>''')
a(f'<rect width="{W}" height="{H}" fill="#F4EEE2"/>')

# --- water ---
a(f'<circle cx="{CX}" cy="{CY}" r="{R_WATER}" fill="#3FA7D6"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="{R_SHORE+90}" fill="#5BBCE4"/>')  # shallows
a(f'<circle cx="{CX}" cy="{CY}" r="{R_SHORE+35}" fill="#7FD0EE"/>')
# little wave strokes
a('<g clip-path="url(#water)" stroke="#BFE8F7" stroke-width="7" stroke-linecap="round" fill="none" opacity="0.85">')
for i in range(70):
    ang = random.uniform(0, 2 * math.pi)
    r = random.uniform(R_SHORE + 110, R_WATER - 40)
    x, y = CX + r * math.cos(ang), CY + r * math.sin(ang)
    s = random.uniform(14, 22)
    a(f'<path d="M{x-2*s:.0f},{y:.0f} q{s/2:.0f},-{s/1.6:.0f} {s:.0f},0 t{s:.0f},0 t{s:.0f},0"/>')
a('</g>')

# --- sand + land ---
a(f'<circle cx="{CX}" cy="{CY}" r="{R_SHORE}" fill="#F2D49B"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="{R_LAND}" fill="#A8D08D"/>')

a('<g clip-path="url(#land)">')
# road grid
GRID = 150
ROAD = 34
a(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#A8D08D"/>')
roads = []
start = CX - GRID * 5
for k in range(11):
    p = start + k * GRID
    roads.append(p)
    a(f'<rect x="{p-ROAD/2}" y="0" width="{ROAD}" height="{H}" fill="#5E6472"/>')
    a(f'<rect x="0" y="{p-ROAD/2}" width="{W}" height="{ROAD}" fill="#5E6472"/>')
# dashed centre lines
for p in roads:
    a(f'<line x1="{p}" y1="0" x2="{p}" y2="{H}" stroke="#F4EEE2" stroke-width="3" stroke-dasharray="14 14"/>')
    a(f'<line x1="0" y1="{p}" x2="{W}" y2="{p}" stroke="#F4EEE2" stroke-width="3" stroke-dasharray="14 14"/>')
# ring road
a(f'<circle cx="{CX}" cy="{CY}" r="{R_LAND-30}" fill="none" stroke="#5E6472" stroke-width="{ROAD}"/>')

roof_cols = ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#264653", "#F7F3EA", "#D8E2EA", "#B5838D", "#6D597A"]

def tree(x, y, r):
    a(f'<circle cx="{x+r*0.25:.0f}" cy="{y+r*0.3:.0f}" r="{r:.0f}" fill="#000" opacity="0.12"/>')
    a(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="#4F9D5D"/>')
    a(f'<circle cx="{x-r*0.3:.0f}" cy="{y-r*0.3:.0f}" r="{r*0.45:.0f}" fill="#6DBA6F"/>')

for i in range(len(roads) - 1):
    for j in range(len(roads) - 1):
        x0 = roads[i] + ROAD / 2 + 8
        y0 = roads[j] + ROAD / 2 + 8
        bw = GRID - ROAD - 16
        bx, by = x0 + bw / 2, y0 + bw / 2
        if math.hypot(bx - CX, by - CY) > R_LAND - 40:
            continue
        # sidewalk
        a(f'<rect x="{x0-4}" y="{y0-4}" width="{bw+8}" height="{bw+8}" rx="10" fill="#D9D4C7"/>')
        if (i, j) in [(4, 4), (5, 5), (4, 5), (5, 4)]:
            continue  # central park handled later
        kind = random.random()
        if kind < 0.18:  # little park block
            a(f'<rect x="{x0}" y="{y0}" width="{bw}" height="{bw}" rx="8" fill="#8CC474"/>')
            for _ in range(4):
                tree(x0 + random.uniform(18, bw - 18), y0 + random.uniform(18, bw - 18), random.uniform(10, 16))
            continue
        # buildings: split block into 1, 2 or 4 parts
        parts = random.choice([1, 2, 2, 4])
        cells = []
        g = 6
        if parts == 1:
            cells = [(x0, y0, bw, bw)]
        elif parts == 2:
            if random.random() < 0.5:
                h = bw / 2 - g / 2
                cells = [(x0, y0, bw, h), (x0, y0 + h + g, bw, h)]
            else:
                w = bw / 2 - g / 2
                cells = [(x0, y0, w, bw), (x0 + w + g, y0, w, bw)]
        else:
            s = bw / 2 - g / 2
            cells = [(x0, y0, s, s), (x0 + s + g, y0, s, s), (x0, y0 + s + g, s, s), (x0 + s + g, y0 + s + g, s, s)]
        for (x, y, w, h) in cells:
            c = random.choice(roof_cols)
            height = random.uniform(6, 16)
            a(f'<rect x="{x+height:.1f}" y="{y+height:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="#000" opacity="0.18"/>')
            a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{c}"/>')
            # roof detail
            inset = min(w, h) * 0.22
            a(f'<rect x="{x+inset:.1f}" y="{y+inset:.1f}" width="{w-2*inset:.1f}" height="{h-2*inset:.1f}" rx="3" fill="#fff" opacity="0.18"/>')
            if random.random() < 0.4:
                a(f'<circle cx="{x+w*0.72:.1f}" cy="{y+h*0.3:.1f}" r="{min(w,h)*0.09:.1f}" fill="#000" opacity="0.15"/>')

# central park with pond
px0 = roads[4] + ROAD / 2
py0 = roads[4] + ROAD / 2
pw = roads[6] - roads[4] - ROAD
a(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{pw}" rx="14" fill="#8CC474"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="70" fill="#7FD0EE" stroke="#F2D49B" stroke-width="10"/>')
a(f'<path d="M{px0},{CY} H{px0+pw}" stroke="#E8DFC9" stroke-width="12"/>')
a(f'<path d="M{CX},{py0} V{py0+pw}" stroke="#E8DFC9" stroke-width="12"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="70" fill="#7FD0EE" stroke="#F2D49B" stroke-width="10"/>')
for (tx, ty) in [(-85, -85), (85, -85), (-85, 85), (85, 85), (-40, -100), (100, 40), (-100, 40), (40, 100)]:
    tree(CX + tx, CY + ty, 16)
a('</g>')

# trees on the sand/land edge
for k in range(40):
    ang = k / 40 * 2 * math.pi + random.uniform(-0.03, 0.03)
    r = R_LAND - 4
    tree(CX + r * math.cos(ang), CY + r * math.sin(ang), random.uniform(11, 16))

# small boats
def boat(ang, r, rot_extra=0):
    x, y = CX + r * math.cos(ang), CY + r * math.sin(ang)
    rot = math.degrees(ang) + 90 + rot_extra
    a(f'<g transform="translate({x:.0f},{y:.0f}) rotate({rot:.0f})">'
      f'<path d="M-60,0 q0,-18 18,-18 h80 l22,18 l-22,18 h-80 q-18,0 -18,-18z" fill="#F7F3EA"/>'
      f'<rect x="-30" y="-10" width="40" height="20" rx="4" fill="#E76F51"/>'
      f'<path d="M-62,0 h-50" stroke="#BFE8F7" stroke-width="6" stroke-linecap="round"/>'
      f'<path d="M-62,-10 l-40,-12 M-62,10 l-40,12" stroke="#BFE8F7" stroke-width="4" stroke-linecap="round"/></g>')
boat(math.radians(-30), 800)
boat(math.radians(150), 820, 180)

# --- earthworm swimming in the water ring ---
R_WORM = 830
a0, a1 = math.radians(40), math.radians(125)
N = 34
pts = []
for k in range(N + 1):
    t = k / N
    ang = a0 + (a1 - a0) * t
    r = R_WORM + 38 * math.sin(t * math.pi * 3)
    pts.append((CX + r * math.cos(ang), CY + r * math.sin(ang)))
# ripples around worm
for (x, y) in pts[::6]:
    a(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="58" ry="58" fill="none" stroke="#BFE8F7" stroke-width="5" opacity="0.6"/>')
d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
a(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.15" stroke-width="66" stroke-linecap="round" stroke-linejoin="round" transform="translate(10,12)"/>')
a(f'<path d="{d}" fill="none" stroke="#E98A8A" stroke-width="64" stroke-linecap="round" stroke-linejoin="round"/>')
a(f'<path d="{d}" fill="none" stroke="#F2A7A0" stroke-width="30" stroke-linecap="round" stroke-linejoin="round" transform="translate(-6,-6)"/>')
# segment rings
for k in range(2, N - 1, 2):
    x, y = pts[k]
    x2, y2 = pts[k + 1]
    ang = math.degrees(math.atan2(y2 - y, x2 - x))
    a(f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang:.1f})"><line x1="0" y1="-30" x2="0" y2="30" stroke="#C9696E" stroke-width="5" stroke-linecap="round"/></g>')
# clitellum (saddle band)
for k in (9, 10, 11):
    x, y = pts[k]
    a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="34" fill="#D9737A"/>')
# head at the end of the path
hx, hy = pts[-1]
px, py = pts[-3]
hang = math.degrees(math.atan2(hy - py, hx - px))
a(f'<g transform="translate({hx:.1f},{hy:.1f}) rotate({hang:.1f})">'
  f'<ellipse cx="14" cy="0" rx="46" ry="36" fill="#E98A8A"/>'
  f'<ellipse cx="6" cy="-8" rx="26" ry="16" fill="#F2A7A0"/>'
  f'<circle cx="28" cy="-15" r="10" fill="#fff"/><circle cx="31" cy="-15" r="5" fill="#2B2D42"/>'
  f'<circle cx="28" cy="15" r="10" fill="#fff"/><circle cx="31" cy="15" r="5" fill="#2B2D42"/>'
  f'<path d="M44,-8 q10,8 0,16" fill="none" stroke="#9E4A52" stroke-width="4" stroke-linecap="round"/>'
  f'<circle cx="20" cy="-26" r="6" fill="#F6B8B8"/><circle cx="20" cy="26" r="6" fill="#F6B8B8"/></g>')

# outer rim
a(f'<circle cx="{CX}" cy="{CY}" r="{R_WATER}" fill="none" stroke="#2C7DA0" stroke-width="10"/>')
a('</svg>')

open(__file__.replace("gen_city_island.py", "city_island.svg"), "w").write("\n".join(out))
print("ok")
