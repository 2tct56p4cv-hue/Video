#!/usr/bin/env python3
"""(tiles library) Board game matching the wooden board: flat-top hexes, round jagged outline, six pieces.
Everything in the city is built from hexagons: hex towers, honeycomb housing, hex courtyards,
domes, markets, plazas, gardens, stadium; streets run along the hex edges."""
import math, random

random.seed(23)
W = H = 2048
CX = CY = W / 2
SQ3 = math.sqrt(3)
S = (H - 80) / (21 * SQ3)
K = S / 64                    # tiles are drawn in a 64-unit canonical hex
RC = 50                       # content radius inside the street band (canonical units)
LIGHT = math.radians(225)     # light from top-left

out = []
a = out.append

# ---------- helpers ----------
def hx(x, y, r, rot=0):
    return " ".join("%.2f,%.2f" % (x + r*math.cos(math.radians(60*k + rot)), y + r*math.sin(math.radians(60*k + rot))) for k in range(6))

def vtx(x, y, r, k, rot=0):
    t = math.radians(60*k + rot)
    return x + r*math.cos(t), y + r*math.sin(t)

def mix(c1, c2, t):
    c1 = [int(c1[i:i+2], 16) for i in (1, 3, 5)]
    c2 = [int(c2[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))

def shade(col, k, rot=0, amt=0.32):
    """colour of facet k (normal at 60k+30+rot) lit from top-left"""
    n = math.radians(60*k + 30 + rot)
    l = math.cos(n - LIGHT)
    return mix(col, "#ffffff", l*amt) if l > 0 else mix(col, "#1b1b2f", -l*amt)

def poly(pts, fill, extra=""):
    a(f'<polygon points="{" ".join("%.2f,%.2f" % p for p in pts)}" fill="{fill}" {extra}/>')

def hexagon(x, y, r, fill, extra="", rot=0):
    a(f'<polygon points="{hx(x, y, r, rot)}" fill="{fill}" {extra}/>')

def shadow_hex(x, y, r, off=6, rot=0, op=0.2):
    hexagon(x+off, y+off, r, "#000", f'opacity="{op}"', rot)

def tree(x, y, r, col="#4F9D5D"):
    a(f'<circle cx="{x+r*0.3:.2f}" cy="{y+r*0.35:.2f}" r="{r:.2f}" fill="#000" opacity="0.14"/>')
    a(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{col}"/>')
    a(f'<circle cx="{x-r*0.3:.2f}" cy="{y-r*0.3:.2f}" r="{r*0.45:.2f}" fill="{mix(col, "#ffffff", 0.25)}"/>')

def pyramid(x, y, r, col, rot=0, h=7, cap=True):
    shadow_hex(x, y, r, h, rot)
    for k in range(6):
        poly([(x, y), vtx(x, y, r, k, rot), vtx(x, y, r, k+1, rot)], shade(col, k, rot))
    if cap:
        hexagon(x, y, r*0.18, mix(col, "#ffffff", 0.45), "", rot)

def hip_ring(x, y, ro, ri, col, rot=0, h=6):
    """hex ring building with sloped (hip) roof facets"""
    shadow_hex(x, y, ro, h, rot)
    for k in range(6):
        poly([vtx(x, y, ro, k, rot), vtx(x, y, ro, k+1, rot), vtx(x, y, ri, k+1, rot), vtx(x, y, ri, k, rot)], shade(col, k, rot, 0.28))

def flat_roof(x, y, r, col, rot=0, h=5):
    shadow_hex(x, y, r, h, rot)
    hexagon(x, y, r, col, "", rot)
    hexagon(x, y, r*0.72, mix(col, "#ffffff", 0.18), "", rot)

ROOFS = ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#B5838D", "#6D597A", "#C8553D", "#F28482"]
GLASS = ["#3D5A80", "#5C7AA8", "#98C1D9", "#264653"]
WALLS = ["#F7F3EA", "#E6DDCB", "#D8E2EA"]

# ---------- tile types (canonical coords, centre 0,0) ----------
def t_tower():
    c = random.choice(ROOFS + GLASS)
    pyramid(0, 0, 38, c, h=10)
    for k in range(6):
        if random.random() < 0.5:
            px, py = vtx(0, 0, 45, k, 30)
            tree(px, py, 4.5)

def t_honeycomb():
    pal = random.sample(ROOFS + WALLS, 4)
    r = 14
    pos = [(0, 0)] + [vtx(0, 0, r*SQ3 + 2.5, k, 30) for k in range(6)]
    for (x, y) in pos:
        roll = random.random()
        if roll < 0.12:
            flat_roof(x, y, r, "#7FB069", h=3)          # roof garden
            tree(x, y, 4)
        elif roll < 0.24:
            flat_roof(x, y, r, "#34568B", h=4)          # solar
            for d in (-5, 0, 5):
                a(f'<line x1="{x-9:.1f}" y1="{y+d:.1f}" x2="{x+9:.1f}" y2="{y+d:.1f}" stroke="#9DB4D8" stroke-width="0.9"/>')
        elif roll < 0.55:
            pyramid(x, y, r, random.choice(pal), h=4, cap=False)
        else:
            flat_roof(x, y, r, random.choice(pal), h=random.uniform(3, 7))

def t_courtyard():
    c = random.choice(ROOFS)
    hip_ring(0, 0, 42, 20, c, h=7)
    hexagon(0, 0, 19, "#8CC474")
    hexagon(0, 0, 9, "#E8DFC9")
    tree(0, 0, 6)
    for k in range(0, 6, 2):
        px, py = vtx(0, 0, 14, k, 30)
        tree(px, py, 3.2, "#5DAA68")

def t_stepped():
    cs = random.choice([GLASS, ["#264653", "#2A9D8F", "#8AB17D"], ["#6D597A", "#B5838D", "#E5989B"]])
    for r, c, h in [(42, cs[0], 11), (31, cs[1], 9), (20, cs[2], 7)]:
        flat_roof(0, 0, r, c, h=h)
    if random.random() < 0.5:
        a('<circle cx="0" cy="0" r="9" fill="none" stroke="#fff" stroke-width="1.6"/>')
        a('<text x="0" y="0.5" font-family="Arial" font-weight="900" font-size="11" fill="#fff" text-anchor="middle" dominant-baseline="central">H</text>')
    else:
        a('<circle cx="0" cy="0" r="3.5" fill="#E63946"/><circle cx="0" cy="0" r="6.5" fill="none" stroke="#E63946" stroke-width="1" opacity="0.6"/>')

def t_dome():
    shadow_hex(0, 0, 40, 8, op=0.18)
    base = random.choice(["#98C1D9", "#A8DADC", "#BDE0FE"])
    for ring, r in enumerate([40, 28, 15]):
        for k in range(6):
            poly([(0, 0), vtx(0, 0, r, k), vtx(0, 0, r, k+1)], shade(mix(base, "#ffffff", ring*0.15), k, 0, 0.35))
    for k in range(6):
        x1, y1 = vtx(0, 0, 40, k)
        a(f'<line x1="0" y1="0" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#fff" stroke-width="1" opacity="0.7"/>')
    for r in (40, 28, 15):
        a(f'<polygon points="{hx(0, 0, r)}" fill="none" stroke="#fff" stroke-width="1" opacity="0.7"/>')

def t_plaza():
    hexagon(0, 0, RC - 2, "#E8DFC9")
    a('<g clip-path="url(#tileclip)">')
    pr = 6
    for i in range(-6, 7):
        for j in range(-6, 7):
            x = pr*1.5*i; y = pr*SQ3*(j + i/2)
            a(f'<polygon points="{hx(x, y, pr)}" fill="none" stroke="#D2C6AC" stroke-width="0.8"/>')
    a('</g>')
    hexagon(0, 0, 15, "#C9B99A")
    hexagon(0, 0, 12, "#7FD0EE")
    hexagon(0, 0, 4, "#F7F3EA")
    for k in range(6):
        x1, y1 = vtx(0, 0, 8, k, 30)
        a(f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="1.3" fill="#fff"/>')
    for k in range(6):
        px, py = vtx(0, 0, 34, k, 30)
        if k % 2:
            tree(px, py, 6)
        else:
            ang = 60*k + 30 + 90
            a(f'<rect x="{px-6:.1f}" y="{py-1.8:.1f}" width="12" height="3.6" rx="1" fill="#8C5E3C" transform="rotate({ang} {px:.1f} {py:.1f})"/>')
    for _ in range(9):
        t = random.uniform(0, 2*math.pi); rr = random.uniform(18, 30)
        a(f'<circle cx="{rr*math.cos(t):.1f}" cy="{rr*math.sin(t):.1f}" r="1.6" fill="{random.choice(["#E63946", "#3A86FF", "#FFB703", "#2B2D42"])}"/>')

def t_market():
    hexagon(0, 0, RC - 2, "#E8DFC9")
    stripes = random.sample([("#E63946", "#FBF7EE"), ("#2A9D8F", "#FBF7EE"), ("#F4A261", "#FBF7EE"), ("#3A86FF", "#FBF7EE"), ("#FFB703", "#E76F51")], 3)
    pos = [vtx(0, 0, 25, k, 30) for k in range(6)] + [(0, 0)]
    for i, (x, y) in enumerate(pos):
        c1, c2 = stripes[i % 3]
        shadow_hex(x, y, 10, 3)
        for k in range(6):
            poly([(x, y), vtx(x, y, 10, k), vtx(x, y, 10, k+1)], shade(c1 if k % 2 else c2, k, 0, 0.18))
        hexagon(x, y, 2, "#2B2D42")

def t_gardens():
    crops = ["#7FB069", "#A7C957", "#B08968", "#6A994E", "#DDA15E", "#90BE6D"]
    random.shuffle(crops)
    for k in range(6):
        p0, p1 = vtx(0, 0, 44, k), vtx(0, 0, 44, k+1)
        q0, q1 = vtx(0, 0, 7, k), vtx(0, 0, 7, k+1)
        poly([q0, p0, p1, q1], crops[k])
        for t in (0.25, 0.45, 0.65, 0.85):
            a0 = (q0[0]+(p0[0]-q0[0])*t, q0[1]+(p0[1]-q0[1])*t)
            a1 = (q1[0]+(p1[0]-q1[0])*t, q1[1]+(p1[1]-q1[1])*t)
            a(f'<line x1="{a0[0]:.1f}" y1="{a0[1]:.1f}" x2="{a1[0]:.1f}" y2="{a1[1]:.1f}" stroke="#000" stroke-opacity="0.12" stroke-width="1.6"/>')
    for k in range(6):
        x1, y1 = vtx(0, 0, 44, k)
        a(f'<line x1="0" y1="0" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#E8DFC9" stroke-width="2.5"/>')
    pyramid(0, 0, 8, "#8C5E3C", h=3, cap=False)       # tool shed / greenhouse hub

def t_park():
    hexagon(0, 0, RC - 2, "#8CC474")
    ox, oy = random.uniform(-10, 10), random.uniform(-10, 10)
    a(f'<path d="M{-40},{oy:.1f} Q{ox:.1f},{oy-20:.1f} 40,{-oy:.1f}" fill="none" stroke="#E8DFC9" stroke-width="4"/>')
    hexagon(ox + 8, oy + 12, 11, "#7FD0EE", 'stroke="#F2D49B" stroke-width="2.5"', 30)
    for _ in range(9):
        t = random.uniform(0, 2*math.pi); rr = random.uniform(16, 38)
        tree(rr*math.cos(t), rr*math.sin(t), random.uniform(4.5, 7.5), random.choice(["#4F9D5D", "#3E8A55", "#6DAA5A"]))

def t_houses():
    hexagon(0, 0, RC - 2, "#B9D89C")
    for k in (0, 2, 4):
        x, y = vtx(0, 0, 21, k, 30)
        pyramid(x, y, 15, random.choice(ROOFS), h=4, cap=False)
        hexagon(x + 3, y - 3, 2.4, "#6B4F3A", "", 30)  # chimney
    for k in (1, 3, 5):
        x, y = vtx(0, 0, 27, k, 30)
        tree(x, y, 5.5)
    hexagon(0, 0, 6, "#7FD0EE", 'stroke="#fff" stroke-width="1.2"')  # little pool

def t_stadium():
    hip_ring(0, 0, 46, 27, "#9AA5B1", h=8)
    for r in (31, 36, 41):
        a(f'<polygon points="{hx(0, 0, r)}" fill="none" stroke="#E63946" stroke-width="1.6" stroke-dasharray="3 2"/>')
    hexagon(0, 0, 26, "#6BBF59")
    for r in (21, 15, 9):
        a(f'<polygon points="{hx(0, 0, r)}" fill="none" stroke="#5CAE4C" stroke-width="3"/>')
    a('<line x1="-20" y1="0" x2="20" y2="0" stroke="#fff" stroke-width="1.4"/>')
    a('<polygon points="' + hx(0, 0, 6, 30) + '" fill="none" stroke="#fff" stroke-width="1.4"/>')

def t_trio():
    hexagon(0, 0, RC - 2, "#CFC8B8")
    cols = random.sample(ROOFS + GLASS, 3)
    for i, k in enumerate((1, 3, 5)):
        x, y = vtx(0, 0, 21, k, 30)
        pyramid(x, y, 19 - i*2, cols[i], h=9 - i*2)
    hexagon(0, 0, 5, "#7FD0EE", 'stroke="#fff" stroke-width="1"')

TYPES = [(t_trio, 8), (t_honeycomb, 22), (t_tower, 13), (t_courtyard, 13), (t_stepped, 9), (t_houses, 12),
         (t_park, 9), (t_plaza, 5), (t_market, 5), (t_gardens, 5), (t_dome, 4)]
def pick():
    tot = sum(w for _, w in TYPES); x = random.uniform(0, tot)
    for f, w in TYPES:
        x -= w
        if x <= 0:
            return f
    return TYPES[0][0]

# beach & water tiles
def t_beach(near_water):
    hexagon(0, 0, 62, "#F2D49B")
    for _ in range(5):
        t = random.uniform(0, 2*math.pi); rr = random.uniform(5, 45)
        a(f'<ellipse cx="{rr*math.cos(t):.1f}" cy="{rr*math.sin(t):.1f}" rx="5" ry="2.4" fill="#E3BE7C"/>')
    roll = random.random()
    if roll < 0.45:
        for _ in range(random.randint(1, 3)):
            t = random.uniform(0, 2*math.pi); rr = random.uniform(0, 32)
            x, y = rr*math.cos(t), rr*math.sin(t)
            c1, c2 = random.choice([("#E63946", "#FBF7EE"), ("#3A86FF", "#FFB703"), ("#2A9D8F", "#FBF7EE"), ("#F4A261", "#264653")])
            a(f'<rect x="{x+6:.1f}" y="{y-3:.1f}" width="16" height="7" rx="1.5" fill="{random.choice(["#FFB703", "#90E0EF", "#F28482"])}"/>')
            shadow_hex(x, y, 12, 5, op=0.15)
            for k in range(6):
                poly([(x, y), vtx(x, y, 12, k), vtx(x, y, 12, k+1)], shade(c1 if k % 2 else c2, k, 0, 0.15))
    elif roll < 0.8:
        for _ in range(random.randint(2, 3)):
            x, y = random.uniform(-30, 30), random.uniform(-30, 30)
            a(f'<circle cx="{x+5:.1f}" cy="{y+6:.1f}" r="10" fill="#000" opacity="0.12"/>')
            for k in range(6):
                px, py = vtx(x, y, 13, k, 15)
                a(f'<path d="M{x:.1f},{y:.1f} Q{(x+px)/2 + 3:.1f},{(y+py)/2 - 3:.1f} {px:.1f},{py:.1f}" stroke="#3E8A55" stroke-width="5" stroke-linecap="round" fill="none"/>')
            a(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#8C5E3C"/>')
    else:
        tree(random.uniform(-15, 15), random.uniform(-15, 15), 9)
        a(f'<circle cx="20" cy="18" r="4" fill="#FBF7EE"/><circle cx="-22" cy="12" r="3" fill="#F28482"/>')

def t_water(depth):
    cols = ["#7FD0EE", "#5BBCE4", "#3FA7D6", "#3498C9"]
    hexagon(0, 0, 62, cols[depth])
    r = random.random()
    if r < 0.45:
        x, y = random.uniform(-20, 10), random.uniform(-20, 20)
        a(f'<path d="M{x-12},{y} q3,-4 6,0 t6,0 t6,0 t6,0" fill="none" stroke="#BFE8F7" stroke-width="2.2" stroke-linecap="round" opacity="0.9"/>')
    elif r < 0.55 and depth >= 1:
        ang = random.uniform(0, 360)
        a(f'<g transform="rotate({ang:.0f})">'
          f'<path d="M-34,0 h-22 M-34,-5 l-18,-7 M-34,5 l-18,7" stroke="#D6F1FB" stroke-width="2" stroke-linecap="round"/>'
          f'<path d="M-32,0 q0,-9 10,-9 h34 l14,9 l-14,9 h-34 q-10,0 -10,-9z" fill="#FBF7EE"/>'
          f'<path d="M-6,-1 L18,-1 L-6,-24 Z" fill="#E63946"/><path d="M-6,1 L12,1 L-6,16 Z" fill="#FBF7EE" stroke="#ddd" stroke-width="0.8"/>'
          f'<line x1="-6" y1="-24" x2="-6" y2="16" stroke="#6B4F3A" stroke-width="1.8"/></g>')
    elif r < 0.62:
        a('<circle cx="6" cy="8" r="6" fill="#000" opacity="0.1"/><circle cx="0" cy="0" r="6" fill="#E63946"/><circle cx="0" cy="0" r="2.5" fill="#FBF7EE"/>')

