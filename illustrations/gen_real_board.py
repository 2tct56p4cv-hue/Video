#!/usr/bin/env python3
"""Hex-city board laid out exactly like the painted wooden board:
hexagonal board of flat-top hexes (radius 10 -> 331 tiles, 6 triangular pieces),
water/city map read from the photo (board_layout.json). Water with depth gradient,
foam, reefs, boats, sea life; city built entirely from hexagons."""
import json, math, os, random
import hex_tiles as T
from hex_tiles import (a, hx, vtx, mix, poly, hexagon, shadow_hex, tree, pyramid, hip_ring,
                       flat_roof, pick, t_stadium, t_dome, t_market, t_plaza, t_park, RC, SQ3, W, H)

random.seed(5)
HERE = os.path.dirname(os.path.abspath(__file__))
R = 10
S, K = T.S, T.K
CX, CY = W / 2, H / 2
NB = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

layout = json.load(open(os.path.join(HERE, "board_layout.json")))
zone = {tuple(map(int, k.split(","))): v for k, v in layout.items()}   # land / water / dark / island

def center(q, r):
    return CX + S * 1.5 * q, CY + S * SQ3 * (r + q / 2)

def ring(q, r):
    return (abs(q) + abs(r) + abs(q + r)) // 2

def edge_k(dq, dr):
    nx, ny = center(dq, dr)
    ang = math.degrees(math.atan2(ny - CY, nx - CX)) % 360
    k = int(round((ang - 30) / 60)) % 6
    return k, (k + 1) % 6

def edge_pts(q, r, dq, dr, s=S):
    x, y = center(q, r)
    k0, k1 = edge_k(dq, dr)
    return vtx(x, y, s, k0), vtx(x, y, s, k1)

# ----- depth (hex distance from land / islands) -----
cells = list(zone)
depth = {}
frontier = [c for c in cells if zone[c] in ("land", "island")]
for c in frontier:
    depth[c] = 0
while frontier:
    nxt = []
    for (q, r) in frontier:
        for dq, dr in NB:
            n = (q + dq, r + dr)
            if n in zone and n not in depth and zone[n] == "water":
                depth[n] = depth[(q, r)] + 1
                nxt.append(n)
    frontier = nxt

# sector (wooden piece): seams run from the centre to the six corners
def sector(q, r):
    if (q, r) == (0, 0):
        return 0
    x, y = center(q, r)
    ang = (math.degrees(math.atan2(y - CY, x - CX)) + 90 + 0.01) % 360
    return int(ang // 60)

# ======================= SVG =======================
a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
water_cells = [c for c in cells if zone[c] in ("water",)]
a('<defs>')
a(f'<clipPath id="tileclip"><polygon points="{hx(0, 0, RC-2)}"/></clipPath>')
a('<clipPath id="waterclip">' + "".join(f'<polygon points="{hx(*center(*c), S + 0.6)}"/>' for c in water_cells) + '</clipPath>')
a(f'<filter id="blurL" x="0" y="0" width="{W}" height="{H}" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="{S*0.9:.1f}"/></filter>')
a(f'<filter id="blurM" x="0" y="0" width="{W}" height="{H}" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="{S*0.35:.1f}"/></filter>')
a(f'<filter id="blurS" x="0" y="0" width="{W}" height="{H}" filterUnits="userSpaceOnUse"><feGaussianBlur stdDeviation="{S*0.08:.1f}"/></filter>')
a(f'<linearGradient id="glare" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff" stop-opacity="0.22"/>'
  f'<stop offset="0.45" stop-color="#ffffff" stop-opacity="0"/><stop offset="1" stop-color="#001d3d" stop-opacity="0.12"/></linearGradient>')
a('</defs>')
a(f'<rect width="{W}" height="{H}" fill="#F4EEE2"/>')

# board shadow + wooden edge
for c in cells:
    x, y = center(*c)
    a(f'<polygon points="{hx(x + 10*K, y + 14*K, S + 1)}" fill="#000" opacity="0.10"/>')
for c in cells:
    x, y = center(*c)
    a(f'<polygon points="{hx(x + 3*K, y + 4*K, S + 1)}" fill="#D9A441"/>')

# ---------------- WATER ----------------
DEEP = ["#14558F", "#1C69A8", "#2A80BE", "#409AD0", "#62B6DE", "#8ED0E9", "#BDEBF2"]
a('<g clip-path="url(#waterclip)">')
a(f'<rect width="{W}" height="{H}" fill="{DEEP[0]}"/>')
# depth bands, heavily blurred -> smooth gradient from shallows to deep sea
a('<g filter="url(#blurL)">')
for lvl, col in [(5, DEEP[1]), (4, DEEP[2]), (3, DEEP[3]), (2, DEEP[4]), (1, DEEP[5])]:
    for c in cells:
        if zone[c] in ("land", "island") or depth.get(c, 99) <= lvl - 1:
            a(f'<polygon points="{hx(*center(*c), S*1.05)}" fill="{col}"/>')
a('</g>')
# painterly variation (like watercolour on the wooden board)
a('<g filter="url(#blurL)" opacity="0.55">')
for _ in range(38):
    c = random.choice(water_cells)
    x, y = center(*c)
    col = random.choice(["#0B3C6E", "#1C68A6", "#5FB8DE", "#9ADFF0", "#2B7BB9"])
    a(f'<ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{random.uniform(1.0, 2.6)*S:.0f}" ry="{random.uniform(0.6, 1.4)*S:.0f}" '
      f'transform="rotate({random.uniform(0, 180):.0f} {x:.0f} {y:.0f})" fill="{col}" opacity="{random.uniform(0.25, 0.6):.2f}"/>')
a('</g>')
# shallow sandy glow right at the coast
a('<g filter="url(#blurM)" opacity="0.85">')
for c in cells:
    if zone[c] in ("land", "island"):
        a(f'<polygon points="{hx(*center(*c), S*1.15)}" fill="#C9F2EC"/>')
a('</g>')
# reefs & kelp in shallow-ish water
a('<g filter="url(#blurS)">')
for c in water_cells:
    if depth.get(c) in (1, 2) and random.random() < 0.22:
        x, y = center(*c)
        for _ in range(random.randint(4, 8)):
            ox, oy = random.uniform(-0.55, 0.55)*S, random.uniform(-0.55, 0.55)*S
            a(f'<ellipse cx="{x+ox:.1f}" cy="{y+oy:.1f}" rx="{random.uniform(2.5, 6)*K:.1f}" ry="{random.uniform(2, 4.5)*K:.1f}" '
              f'fill="{random.choice(["#2E8B7A", "#3FA796", "#E07A5F", "#F2A07B", "#2A6F97"])}" opacity="0.65"/>')
a('</g>')
# light caustic network in shallows
for c in water_cells:
    if depth.get(c) == 1 and random.random() < 0.7:
        x, y = center(*c)
        pts = [(x + random.uniform(-0.6, 0.6)*S, y + random.uniform(-0.6, 0.6)*S) for _ in range(4)]
        d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(f"Q{pts[i][0]+random.uniform(-6,6)*K:.1f},{pts[i][1]+random.uniform(-6,6)*K:.1f} {pts[i+1][0]:.1f},{pts[i+1][1]:.1f}" for i in range(3))
        a(f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="{1.1*K:.2f}" opacity="0.35"/>')
# wave strokes: tighter, lighter near shore, long swells offshore
for c in water_cells:
    x, y = center(*c)
    dp = depth.get(c, 5)
    for _ in range(1 if dp <= 2 else 2):
        if random.random() < 0.75:
            w = random.uniform(5, 9) * K * (1 + dp * 0.12)
            ox, oy = random.uniform(-0.5, 0.5)*S, random.uniform(-0.5, 0.5)*S
            col = "#E6F7FB" if dp <= 2 else "#8CCBEA"
            a(f'<path d="M{x+ox-2*w:.1f},{y+oy:.1f} q{w/2:.1f},{-w/1.7:.1f} {w:.1f},0 t{w:.1f},0 t{w:.1f},0" fill="none" '
              f'stroke="{col}" stroke-width="{1.8*K:.2f}" stroke-linecap="round" opacity="{0.8 if dp<=2 else 0.55}"/>')
# sun sparkles
for _ in range(90):
    c = random.choice(water_cells)
    x, y = center(*c)
    x += random.uniform(-0.6, 0.6)*S; y += random.uniform(-0.6, 0.6)*S
    s = random.uniform(1.5, 3.5) * K
    a(f'<path d="M{x-s:.1f},{y:.1f} L{x+s:.1f},{y:.1f} M{x:.1f},{y-s:.1f} L{x:.1f},{y+s:.1f}" stroke="#fff" stroke-width="{0.9*K:.2f}" opacity="0.7"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#glare)"/>')
a('</g>')

# tile edges on the water (the board is still made of hexes)
segs = []
for c in water_cells:
    for dq, dr in NB:
        n = (c[0] + dq, c[1] + dr)
        if zone.get(n) == "water" and c < n:
            p0, p1 = edge_pts(*c, dq, dr)
            segs.append(f"M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f}")
a(f'<path d="{" ".join(segs)}" stroke="#ffffff" stroke-width="{1.1*K:.2f}" opacity="0.22" fill="none"/>')

# foam along the coast
foam = []
for c in cells:
    if zone[c] not in ("land", "island"):
        continue
    for dq, dr in NB:
        n = (c[0] + dq, c[1] + dr)
        if zone.get(n) == "water":
            p0, p1 = edge_pts(*c, dq, dr, S + 1.5*K)
            foam.append(f"M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f}")
fd = " ".join(foam)
a(f'<path d="{fd}" stroke="#ffffff" stroke-width="{12*K:.1f}" opacity="0.45" fill="none" stroke-linecap="round" filter="url(#blurS)"/>')
a(f'<path d="{fd}" stroke="#ffffff" stroke-width="{2.6*K:.1f}" opacity="0.95" fill="none" stroke-linecap="round" stroke-dasharray="{9*K:.1f} {4*K:.1f}"/>')

# ---------------- sea life & boats (canonical 64-unit coordinates) ----------------
def at(c, dx=0, dy=0, rot=0, sc=1.0):
    x, y = center(*c)
    return f'<g transform="translate({x+dx*K:.1f},{y+dy*K:.1f}) rotate({rot:.0f}) scale({K*sc:.3f})">'

def sailboat(c, rot):
    a(at(c, rot=rot))
    a('<path d="M-36,0 h-30 M-36,-6 l-26,-10 M-36,6 l-26,10" stroke="#fff" stroke-width="2.4" stroke-linecap="round" opacity="0.8"/>')
    a('<path d="M-30,5 q0,-11 12,-11 h34 l16,11 l-16,11 h-34 q-12,0 -12,-11z" fill="#000" opacity="0.18" transform="translate(4,5)"/>')
    a('<path d="M-30,0 q0,-11 12,-11 h34 l16,11 l-16,11 h-34 q-12,0 -12,-11z" fill="#FBF7EE"/>')
    a('<path d="M-20,0 q0,-6 7,-6 h24 l9,6 l-9,6 h-24 q-7,0 -7,-6z" fill="#C49A6C"/>')
    col = random.choice(["#E63946", "#FFB703", "#2A9D8F", "#FB8500", "#8338EC"])
    a(f'<path d="M-4,-2 L26,-2 L-4,-32 Z" fill="{col}"/><path d="M-4,2 L18,2 L-4,22 Z" fill="#FBF7EE" stroke="#ccd" stroke-width="0.8"/>')
    a('<line x1="-4" y1="-32" x2="-4" y2="22" stroke="#6B4F3A" stroke-width="2.2"/></g>')

def motorboat(c, rot):
    a(at(c, rot=rot))
    a('<path d="M-22,0 C-50,-4 -80,-14 -110,-22 M-22,0 C-50,4 -80,14 -110,22" stroke="#fff" stroke-width="3" fill="none" opacity="0.7"/>')
    a('<path d="M-22,0 C-55,0 -80,0 -105,0" stroke="#fff" stroke-width="6" opacity="0.35"/>')
    a('<path d="M-22,-9 h30 q16,0 22,9 q-6,9 -22,9 h-30 z" fill="#FBF7EE"/>')
    a(f'<rect x="-14" y="-6" width="16" height="12" rx="3" fill="{random.choice(["#3A86FF", "#E63946", "#264653"])}"/>')
    a('<rect x="2" y="-5" width="7" height="10" rx="2" fill="#BFE8F7"/></g>')

def ship(c, rot):
    a(at(c, rot=rot, sc=1.15))
    a('<path d="M-60,0 C-90,0 -120,-10 -150,-14 M-60,0 C-90,0 -120,10 -150,14" stroke="#fff" stroke-width="3" fill="none" opacity="0.5"/>')
    a('<path d="M-56,-15 h92 l22,15 l-22,15 h-92 z" fill="#000" opacity="0.2" transform="translate(5,6)"/>')
    a('<path d="M-56,-15 h92 l22,15 l-22,15 h-92 z" fill="#B23A48"/><path d="M-52,-11 h86 l16,11 l-16,11 h-86 z" fill="#2B2D42"/>')
    cols = ["#E76F51", "#2A9D8F", "#E9C46A", "#3A86FF", "#F4A261", "#8338EC", "#FBF7EE"]
    for i in range(6):
        for j in (-1, 1):
            a(f'<rect x="{-48 + i*13}" y="{-10 if j < 0 else 0.5}" width="12" height="9.5" rx="1" fill="{random.choice(cols)}"/>')
    a('<rect x="30" y="-9" width="12" height="18" rx="2" fill="#FBF7EE"/><rect x="33" y="-6" width="6" height="12" fill="#BFE8F7"/></g>')

def whale(c, rot):
    a(at(c, rot=rot))
    a('<ellipse cx="0" cy="0" rx="40" ry="17" fill="#000" opacity="0.15" transform="translate(4,5)"/>')
    a('<path d="M-38,0 C-38,-16 10,-20 34,-6 C40,-2 40,2 34,6 C10,20 -38,16 -38,0 Z" fill="#41658A"/>')
    a('<path d="M-38,0 L-56,-12 Q-50,0 -56,12 Z" fill="#41658A"/><path d="M-20,-4 C0,-10 20,-8 32,-3" stroke="#6C8EAD" stroke-width="5" fill="none" stroke-linecap="round"/>')
    a('<circle cx="24" cy="-6" r="2.3" fill="#fff"/><path d="M14,-12 q-4,-14 -12,-18 M14,-12 q2,-14 10,-20 M14,-12 q-1,-16 0,-22" stroke="#E0F4FF" stroke-width="2.5" stroke-linecap="round" fill="none"/></g>')

def dolphins(c, rot):
    a(at(c, rot=rot))
    for i, (dx, dy) in enumerate([(0, 0), (-18, 14), (-30, -10)]):
        a(f'<g transform="translate({dx},{dy})"><path d="M-14,0 C-8,-8 8,-8 16,-1 L22,0 L16,2 C8,7 -8,6 -14,0 Z" fill="#7B9EB8"/>'
          f'<path d="M-2,-5 L2,-12 L5,-5 Z" fill="#7B9EB8"/><path d="M-14,0 L-21,-5 L-19,0 L-21,5 Z" fill="#7B9EB8"/>'
          f'<ellipse cx="-20" cy="0" rx="9" ry="4" fill="none" stroke="#fff" stroke-width="1.5" opacity="0.6"/></g>')
    a('</g>')

def fish_school(c):
    x, y = center(*c)
    rot = random.uniform(0, 360)
    a(f'<g transform="translate({x:.1f},{y:.1f}) rotate({rot:.0f}) scale({K:.3f})">')
    col = random.choice(["#FFB703", "#FB8500", "#F28482", "#90E0EF"])
    for _ in range(9):
        fx, fy = random.uniform(-28, 28), random.uniform(-16, 16)
        a(f'<path d="M{fx-5:.1f},{fy:.1f} q5,-4 10,0 q-5,4 -10,0 z M{fx-5:.1f},{fy:.1f} l-4,-3 v6 z" fill="{col}" opacity="0.85"/>')
    a('</g>')

def buoy(c):
    x, y = center(*c)
    ox, oy = random.uniform(-20, 20)*K, random.uniform(-20, 20)*K
    a(f'<g transform="translate({x+ox:.1f},{y+oy:.1f}) scale({K:.3f})"><circle r="11" fill="none" stroke="#fff" stroke-width="1.5" opacity="0.6"/>'
      f'<circle cx="2" cy="3" r="6" fill="#000" opacity="0.2"/><circle r="6" fill="#E63946"/><path d="M-6,0 h12" stroke="#fff" stroke-width="3"/></g>')

def rocks(c):
    x, y = center(*c)
    for _ in range(random.randint(2, 4)):
        ox, oy = random.uniform(-25, 25)*K, random.uniform(-25, 25)*K
        r = random.uniform(4, 8)*K
        a(f'<ellipse cx="{x+ox:.1f}" cy="{y+oy:.1f}" rx="{r*1.6:.1f}" ry="{r*1.2:.1f}" fill="#fff" opacity="0.5"/>')
        a(f'<polygon points="{hx(x+ox, y+oy, r, random.uniform(0, 60))}" fill="#7D8597"/><polygon points="{hx(x+ox-r*0.2, y+oy-r*0.2, r*0.5, 10)}" fill="#A3AAB7"/>')

free = [c for c in water_cells]
random.shuffle(free)
used = set()
def take(cond):
    for c in free:
        if c not in used and cond(c) and all((c[0]+dq, c[1]+dr) not in used for dq, dr in NB):
            used.add(c)
            return c
    return None

start = min((c for c in water_cells if c[0] == 0), key=lambda c: c[1])
used.add(start)
for _ in range(2):
    c = take(lambda c: depth.get(c, 0) >= 4 and ring(*c) <= R - 2); c and ship(c, random.uniform(0, 360))
for _ in range(1):
    c = take(lambda c: depth.get(c, 0) >= 4 and ring(*c) <= R - 2); c and whale(c, random.uniform(0, 360))
for _ in range(2):
    c = take(lambda c: depth.get(c, 0) >= 3 and ring(*c) <= R - 1); c and dolphins(c, random.uniform(0, 360))
for _ in range(7):
    c = take(lambda c: 2 <= depth.get(c, 0) <= 6 and ring(*c) <= R - 1); c and sailboat(c, random.uniform(0, 360))
for _ in range(4):
    c = take(lambda c: 1 <= depth.get(c, 0) <= 4); c and motorboat(c, random.uniform(0, 360))
for _ in range(7):
    c = take(lambda c: 1 <= depth.get(c, 0) <= 3); c and fish_school(c)
for _ in range(8):
    c = take(lambda c: depth.get(c, 0) >= 2); c and buoy(c)
for _ in range(4):
    c = take(lambda c: depth.get(c, 0) in (1, 2)); c and rocks(c)

# ferry routes from the city to the islands (dashed)
islands = [c for c in cells if zone[c] == "island"]
def nearest_land(c):
    return min((l for l in cells if zone[l] == "land"), key=lambda l: (l[0]-c[0])**2 + (l[1]-c[1])**2 + (l[0]-c[0])*(l[1]-c[1]))
for isl in islands:
    l = nearest_land(isl)
    (x0, y0), (x1, y1) = center(*l), center(*isl)
    mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.15, (y0 + y1) / 2 - (x1 - x0) * 0.15
    a(f'<path d="M{x0:.1f},{y0:.1f} Q{mx:.1f},{my:.1f} {x1:.1f},{y1:.1f}" fill="none" stroke="#FBF7EE" stroke-width="{2.2*K:.1f}" stroke-dasharray="{7*K:.1f} {6*K:.1f}" opacity="0.85"/>')

# ---------------- CITY ----------------
land = [c for c in cells if zone[c] == "land"]
park = {c for c in land if ring(*c) <= 1}
for c in cells:
    if zone[c] in ("land", "dark"):
        a(f'<polygon points="{hx(*center(*c), S + 0.8)}" fill="#565C69"/>')

city = [c for c in land if c not in park]
random.shuffle(city)
forced = {city[0]: t_stadium, city[1]: t_dome, city[2]: t_market, city[3]: t_plaza, city[4]: t_dome, city[5]: t_market}

def canal(c):
    x, y = center(*c)
    a(f'<g transform="translate({x:.2f},{y:.2f}) scale({K:.4f})">')
    hexagon(0, 0, 63, "#9C8F7A")                   # stone embankment
    hexagon(0, 0, 55, "#1F5FA0")
    hexagon(0, 0, 44, "#2A74B8")
    a('<path d="M-30,-8 q6,-5 12,0 t12,0 M4,14 q6,-5 12,0 t12,0" stroke="#9FD3F2" stroke-width="2" fill="none" stroke-linecap="round"/>')
    a('</g>')
for c in cells:
    if zone[c] == "dark":
        canal(c)
# water between neighbouring canal tiles + canal mouth into the sea
dark = [c for c in cells if zone[c] == "dark"]
for c in dark:
    for dq, dr in NB:
        n = (c[0]+dq, c[1]+dr)
        if zone.get(n) in ("dark", "water") or n in park:
            (x0, y0), (x1, y1) = center(*c), center(*n)
            if zone.get(n) == "dark" and n < c:
                continue
            ex, ey = (x0+x1)/2, (y0+y1)/2
            if n in park or zone.get(n) == "water":
                x1, y1 = ex, ey
            a(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#9C8F7A" stroke-width="{0.95*S:.1f}"/>')
            a(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#1F5FA0" stroke-width="{0.8*S:.1f}"/>')
for c in dark:
    x, y = center(*c)
    a(f'<polygon points="{hx(x, y, 44*K)}" fill="#2A74B8"/>')
# bridges across the canal (roads continue over the water)
for i, c in enumerate(dark):
    x, y = center(*c)
    ang = 0
    if i % 2: continue
    a(f'<g transform="translate({x:.1f},{y:.1f}) rotate({ang}) scale({K:.3f})">'
      f'<rect x="-60" y="-9" width="120" height="18" fill="#000" opacity="0.2" transform="translate(3,5)"/>'
      f'<rect x="-60" y="-9" width="120" height="18" fill="#6B7280"/><rect x="-60" y="-11" width="120" height="3" fill="#D6CCC2"/>'
      f'<rect x="-60" y="8" width="120" height="3" fill="#D6CCC2"/><line x1="-60" y1="0" x2="60" y2="0" stroke="#F4EEE2" stroke-width="1.4" stroke-dasharray="5 5"/></g>')
    if i == 1:
        a(at(c, 0, 26, 90, 0.6)); a('<path d="M-22,-9 h30 q16,0 22,9 q-6,9 -22,9 h-30 z" fill="#FBF7EE"/><rect x="-14" y="-6" width="16" height="12" rx="3" fill="#E63946"/></g>')

for c in city:
    x, y = center(*c)
    a(f'<g transform="translate({x:.2f},{y:.2f}) scale({K:.4f})">')
    hexagon(0, 0, RC + 3, "#C9C2B2")
    hexagon(0, 0, RC, "#DCD5C5")
    (forced.get(c) or pick())()
    a('</g>')

# piers on the waterfront
for c in land:
    if c in park:
        continue
    for dq, dr in NB:
        n = (c[0]+dq, c[1]+dr)
        if zone.get(n) == "water" and random.random() < 0.18:
            (x0, y0), (x1, y1) = center(*c), center(*n)
            ang = math.degrees(math.atan2(y1-y0, x1-x0))
            ex, ey = (x0+x1)/2, (y0+y1)/2
            a(f'<g transform="translate({ex:.1f},{ey:.1f}) rotate({ang:.1f}) scale({K:.3f})">'
              f'<rect x="0" y="-5" width="34" height="10" fill="#000" opacity="0.2" transform="translate(3,4)"/>'
              f'<rect x="0" y="-5" width="34" height="10" fill="#B07A4F"/>'
              + "".join(f'<line x1="{i}" y1="-5" x2="{i}" y2="5" stroke="#8C5E3C" stroke-width="1"/>' for i in range(4, 34, 5))
              + (f'<path d="M18,8 h14 q6,0 8,4 q-2,4 -8,4 h-14 z" fill="#FBF7EE"/>' if random.random() < 0.6 else "")
              + '</g>')

# street lines + cars
cars = ["#E63946", "#FFB703", "#3A86FF", "#FBF7EE", "#2B2D42", "#8338EC", "#2A9D8F"]
for c in city:
    for dq, dr in NB:
        n = (c[0]+dq, c[1]+dr)
        if n not in city or c > n:
            continue
        p0, p1 = edge_pts(*c, dq, dr)
        a(f'<line x1="{p0[0]:.1f}" y1="{p0[1]:.1f}" x2="{p1[0]:.1f}" y2="{p1[1]:.1f}" stroke="#F4EEE2" stroke-width="{1.4*K:.2f}" stroke-dasharray="{5*K:.1f} {5*K:.1f}" opacity="0.8"/>')
        if random.random() < 0.3:
            t = random.uniform(0.25, 0.75)
            mx, my = p0[0]+(p1[0]-p0[0])*t, p0[1]+(p1[1]-p0[1])*t
            ang = math.degrees(math.atan2(p1[1]-p0[1], p1[0]-p0[0]))
            side = random.choice([-1, 1]) * 3.2 * K
            a(f'<g transform="translate({mx:.1f},{my:.1f}) rotate({ang:.1f}) translate(0,{side:.1f})">'
              f'<rect x="{-5*K:.1f}" y="{-2.5*K:.1f}" width="{10*K:.1f}" height="{5*K:.1f}" rx="{1.5*K:.1f}" fill="{random.choice(cars)}"/>'
              f'<rect x="{-1*K:.1f}" y="{-2*K:.1f}" width="{3.5*K:.1f}" height="{4*K:.1f}" rx="{0.8*K:.1f}" fill="#BFE8F7" opacity="0.8"/></g>')

# central park (whatever park cells are land) with the lake feeding the canal
for c in park:
    a(f'<polygon points="{hx(*center(*c), S - 1)}" fill="#8CC474"/>')
a(f'<g transform="translate({CX},{CY}) scale({K:.4f})">')
for k in range(6):
    x1, y1 = vtx(0, 0, 110, k, 30)
    nb = (NB[(1 - k) % 6]) if False else None
    a(f'<line x1="0" y1="0" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#E8DFC9" stroke-width="9" stroke-linecap="round"/>')
hexagon(0, 0, 44, "#F2D49B"); hexagon(0, 0, 39, "#7FD0EE"); hexagon(0, 0, 30, "#9ADBF2")
for k in range(6):
    px, py = vtx(0, 0, 22, k, 30)
    a(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="4" ry="3" fill="#6DBA6F"/>')
pyramid(0, 0, 12, "#FBF7EE", h=4)
a('</g>')
for c in park:
    if c == (0, 0):
        continue
    x, y = center(*c)
    for _ in range(5):
        t = random.uniform(0, 2*math.pi); rr = random.uniform(0.2, 0.6)*S
        tree(x + rr*math.cos(t), y + rr*math.sin(t), random.uniform(6, 10)*K, random.choice(["#4F9D5D", "#3E8A55", "#6DAA5A"]))

# islands: lighthouse, palm island, little villa
def island(c, kind):
    x, y = center(*c)
    a(f'<g transform="translate({x:.2f},{y:.2f}) scale({K:.4f})">')
    hexagon(0, 0, 63, "#F2D49B")
    hexagon(0, 0, 50, "#9CCB7F")
    if kind == 0:   # lighthouse
        a('<path d="M0,0 L140,-40 L140,40 Z" fill="#FFF3B0" opacity="0.35"/>')
        for r, col in [(22, "#FBF7EE"), (16, "#E63946"), (10, "#FBF7EE")]:
            flat_roof(0, 0, r, col, h=6)
        hexagon(0, 0, 6, "#FFD166"); hexagon(0, 0, 2.5, "#fff")
        tree(-30, 18, 7); tree(28, 24, 6)
    elif kind == 1:  # palms + hut
        pyramid(10, 8, 14, "#C49A6C", h=4, cap=False)
        for (px, py) in [(-22, -14), (-6, -28), (24, -22)]:
            a(f'<circle cx="{px+5}" cy="{py+6}" r="10" fill="#000" opacity="0.12"/>')
            for k in range(6):
                ex, ey = vtx(px, py, 14, k, 15)
                a(f'<path d="M{px},{py} Q{(px+ex)/2+3:.1f},{(py+ey)/2-3:.1f} {ex:.1f},{ey:.1f}" stroke="#3E8A55" stroke-width="5" stroke-linecap="round" fill="none"/>')
            a(f'<circle cx="{px}" cy="{py}" r="3" fill="#8C5E3C"/>')
    else:            # villa with pool
        hip_ring(-6, -6, 26, 11, "#E76F51", h=6)
        hexagon(-6, -6, 10, "#7FD0EE", 'stroke="#fff" stroke-width="1.5"')
        tree(26, 20, 8); tree(-30, 26, 6)
    a('</g>')
for i, c in enumerate(sorted(islands)):
    island(c, i % 3)

# START harbour
def pawn(x, y, col):
    a(f'<g transform="translate({x:.1f},{y:.1f}) scale({K:.4f})">'
      f'<ellipse cx="5" cy="26" rx="24" ry="8" fill="#000" opacity="0.2"/>'
      f'<path d="M-20,24 Q-20,4 -8,-2 A14,14 0 1 1 8,-2 Q20,4 20,24 Z" fill="{col}" stroke="#2B2D42" stroke-width="4"/>'
      f'<circle cx="-4" cy="-19" r="4" fill="#fff" opacity="0.6"/></g>')
sx, sy = center(*start)
a(f'<polygon points="{hx(sx, sy, S - 1.5)}" fill="#2A9D8F" stroke="#FBF7EE" stroke-width="{2*K:.1f}"/>')
a(f'<text x="{sx:.1f}" y="{sy - 27*K:.1f}" font-family="Nunito, Arial, sans-serif" font-weight="800" font-size="{17*K:.1f}" fill="#fff" text-anchor="middle" dominant-baseline="central">START</text>')
pawn(sx - 19*K, sy + 10*K, "#E63946"); pawn(sx + 19*K, sy + 10*K, "#FFB703")

# seams between the six wooden pieces + outline
seam, rim = [], []
for c in cells:
    for dq, dr in NB:
        n = (c[0]+dq, c[1]+dr)
        p0, p1 = edge_pts(*c, dq, dr)
        seg = f"M{p0[0]:.1f},{p0[1]:.1f} L{p1[0]:.1f},{p1[1]:.1f}"
        if n not in zone:
            rim.append(seg)
        elif sector(*n) != sector(*c) and c < n:
            seam.append(seg)
a(f'<path d="{" ".join(seam)}" fill="none" stroke="#1D2B36" stroke-width="{3.2*K:.1f}" stroke-linecap="round" opacity="0.7"/>')
a(f'<path d="{" ".join(rim)}" fill="none" stroke="#1D3B4D" stroke-width="{5*K:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
a('</svg>')

open(os.path.join(HERE, "hex_board_real.svg"), "w").write("\n".join(T.out))
print("tiles", len(cells), {z: sum(1 for c in cells if zone[c] == z) for z in ("land", "water", "dark", "island")},
      "pieces", [sum(1 for c in cells if sector(*c) == i) for i in range(6)])
