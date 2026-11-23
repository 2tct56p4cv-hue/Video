#!/usr/bin/env python3
"""Board game: round city island surrounded by water, with a track of spaces around it."""
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


# --- bridges from shore to the track ---
R_TIN, R_TOUT = 735, 885   # track ring in the water
for deg in (45, 135, 225, 315):
    ang = math.radians(deg)
    a(f'<g transform="translate({CX},{CY}) rotate({deg})">'
      f'<rect x="{R_LAND-20}" y="-34" width="{R_TIN-R_LAND+30}" height="68" fill="#000" opacity="0.15" transform="translate(8,10)"/>'
      f'<rect x="{R_LAND-20}" y="-34" width="{R_TIN-R_LAND+30}" height="68" fill="#B07A4F"/>')
    for x in range(R_LAND - 10, R_TIN, 16):
        a(f'<line x1="{x}" y1="-34" x2="{x}" y2="34" stroke="#8C5E3C" stroke-width="3"/>')
    a(f'<rect x="{R_LAND-20}" y="-38" width="{R_TIN-R_LAND+30}" height="6" fill="#7A5033"/>'
      f'<rect x="{R_LAND-20}" y="32" width="{R_TIN-R_LAND+30}" height="6" fill="#7A5033"/></g>')

# --- track of spaces ---
N = 40
GAP = 0.6  # degrees
special = {
    0:  ("#2A9D8F", "START"),
    5:  ("#E9C46A", "?"),
    10: ("#264653", "MĚSTO"),
    13: ("#E76F51", "−2"),
    15: ("#E9C46A", "?"),
    18: ("#8CC474", "+3"),
    20: ("#264653", "MĚSTO"),
    24: ("#E76F51", "STOP"),
    25: ("#E9C46A", "?"),
    28: ("#8CC474", "+2"),
    30: ("#264653", "MĚSTO"),
    33: ("#E76F51", "−3"),
    35: ("#E9C46A", "?"),
    38: ("#8CC474", "+1"),
}
# space 0 is at the top (-90°); spaces at 45° bridges are "MĚSTO": indices 5*k map to deg -90+9*k
# put MĚSTO exactly on bridges: bridge angles 315(-45),45,135,225 -> idx 5,15,25,35
for k in (5, 15, 25, 35):
    special[k] = ("#264653", "MĚSTO")
for k in (10, 20, 30):
    special[k] = ("#E9C46A", "?")

def arc_pt(r, deg):
    t = math.radians(deg)
    return CX + r * math.cos(t), CY + r * math.sin(t)

# track base (shadow + border)
a(f'<circle cx="{CX+8}" cy="{CY+10}" r="{(R_TIN+R_TOUT)/2}" fill="none" stroke="#000" stroke-opacity="0.15" stroke-width="{R_TOUT-R_TIN+16}"/>')
a(f'<circle cx="{CX}" cy="{CY}" r="{(R_TIN+R_TOUT)/2}" fill="none" stroke="#2C5F7A" stroke-width="{R_TOUT-R_TIN+16}"/>')
for i in range(N):
    d0 = -90 - 4.5 + i * 9 + GAP / 2
    d1 = d0 + 9 - GAP
    o0, o1 = arc_pt(R_TOUT, d0), arc_pt(R_TOUT, d1)
    i0, i1 = arc_pt(R_TIN, d0), arc_pt(R_TIN, d1)
    col, label = special.get(i, ("#FBF7EE" if i % 2 else "#F1E9D8", str(i)))
    if label in ("6", "9"):
        label += "."  # distinguish 6 / 9 when the board is turned
    a(f'<path d="M{o0[0]:.1f},{o0[1]:.1f} A{R_TOUT},{R_TOUT} 0 0 1 {o1[0]:.1f},{o1[1]:.1f} '
      f'L{i1[0]:.1f},{i1[1]:.1f} A{R_TIN},{R_TIN} 0 0 0 {i0[0]:.1f},{i0[1]:.1f} Z" fill="{col}"/>')
    mid = -90 + i * 9
    mx, my = arc_pt((R_TIN + R_TOUT) / 2 + (42 if i == 0 else 0), mid)
    rot = mid + 90
    if 0 < rot % 360 < 180 and 90 < rot % 360 < 270:
        pass
    # keep text upright-ish: flip on the bottom half
    if 90 < (rot % 360) < 270:
        rot += 180
    dark = col in ("#FBF7EE", "#F1E9D8", "#E9C46A", "#8CC474")
    tc = "#2B2D42" if dark else "#FFFFFF"
    size = 44 if len(label) <= 2 else (30 if len(label) <= 4 else 24)
    a(f'<text x="{mx:.1f}" y="{my:.1f}" transform="rotate({rot:.1f} {mx:.1f} {my:.1f})" '
      f'font-family="Arial Rounded MT Bold, Nunito, Arial, sans-serif" font-weight="800" font-size="{size}" '
      f'fill="{tc}" text-anchor="middle" dominant-baseline="central">{label}</text>')

# direction arrow next to START
ax0, ay0 = arc_pt(R_TOUT + 40, -84)
ax1, ay1 = arc_pt(R_TOUT + 40, -68)
a(f'<path d="M{ax0:.0f},{ay0:.0f} A{R_TOUT+40},{R_TOUT+40} 0 0 1 {ax1:.0f},{ay1:.0f}" fill="none" stroke="#FBF7EE" stroke-width="10" stroke-linecap="round"/>')
hx, hy = arc_pt(R_TOUT + 40, -66)
a(f'<g transform="translate({hx:.0f},{hy:.0f}) rotate({-66+90})"><path d="M-6,-22 L24,0 L-6,22 Z" fill="#FBF7EE"/></g>')

# --- pawns ---
def pawn(idx, col, off, dang=0):
    x, y = arc_pt((R_TIN + R_TOUT) / 2 + off, -90 + idx * 9 + dang)
    a(f'<g transform="translate({x:.0f},{y:.0f})">'
      f'<ellipse cx="6" cy="30" rx="28" ry="10" fill="#000" opacity="0.2"/>'
      f'<path d="M-24,28 Q-24,4 -10,-2 A16,16 0 1 1 10,-2 Q24,4 24,28 Z" fill="{col}" stroke="#2B2D42" stroke-width="4"/>'
      f'<circle cx="-5" cy="-22" r="5" fill="#fff" opacity="0.6"/></g>')
pawn(0, "#E63946", -22, -2.3)
pawn(0, "#FFB703", -22, 2.3)
pawn(7, "#3A86FF", 0)
pawn(22, "#8338EC", 0)

# --- die in the corner ---
def die(x, y, rot, pips):
    a(f'<g transform="translate({x},{y}) rotate({rot})">'
      f'<rect x="-62" y="-52" width="124" height="124" rx="24" fill="#000" opacity="0.15"/>'
      f'<rect x="-70" y="-70" width="140" height="140" rx="26" fill="#FFFFFF" stroke="#2B2D42" stroke-width="5"/>')
    for (px, py) in pips:
        a(f'<circle cx="{px}" cy="{py}" r="13" fill="#2B2D42"/>')
    a('</g>')
die(170, 1870, -12, [(-35, -35), (35, -35), (0, 0), (-35, 35), (35, 35)])
die(1880, 170, 14, [(-35, -35), (0, 0), (35, 35)])

# --- legend ---
leg = [("#8CC474", "+N  posuň se dopředu"), ("#E76F51", "−N / STOP  zpět / stůj"),
       ("#E9C46A", "?  vytáhni kartu"), ("#264653", "MĚSTO  přejdi most do města")]
for k, (c, t) in enumerate(leg):
    x, y = 1560, 1795 + k * 58
    a(f'<rect x="{x}" y="{y}" width="40" height="40" rx="8" fill="{c}"/>'
      f'<text x="{x+56}" y="{y+21}" font-family="Nunito, Arial, sans-serif" font-weight="700" font-size="26" fill="#2B2D42" dominant-baseline="central">{t}</text>')

# outer rim
a(f'<circle cx="{CX}" cy="{CY}" r="{R_WATER}" fill="none" stroke="#2C7DA0" stroke-width="10"/>')
a('</svg>')

open(__file__.replace("gen_city_board.py", "city_board.svg"), "w").write("\n".join(out))
print("ok")
