import numpy as np
import wave, json, os

SC = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(os.path.join(SC, "timeline.json")))
TOTAL = tl["total"] + 1.5
SR = 44100
BPM = 112.0
BEAT = 60.0 / BPM
N = int(TOTAL * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)

def f(semi):  # semitones from A4
    return 440.0 * 2 ** (semi / 12.0)

# A minor progression, 2 bars (8 beats) per chord: Am, F, C, G  (root, third, fifth, octave)
chords = [[-12, -9, -5, 0], [-16, -12, -9, -4], [-21, -17, -14, -9], [-14, -10, -7, -2]]
CHORD_BEATS = 8

def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = a * acc + (1 - a) * x[i]; y[i] = acc
    return y

def saw(freq, tt):
    return 2.0 * ((tt * freq) % 1.0) - 1.0

out = np.zeros(N)

# ---- pad: two detuned saws per chord tone, heavy lowpass, slow attack ----
pad = np.zeros(N)
n_chords = int(np.ceil(TOTAL / (CHORD_BEATS * BEAT)))
for c in range(n_chords):
    s = c * CHORD_BEATS * BEAT; e = min(s + CHORD_BEATS * BEAT, TOTAL)
    if s >= TOTAL: break
    m = (t >= s) & (t < e); lt = t[m] - s
    env = np.clip(lt / 1.2, 0, 1) * np.clip((e - s - lt) / 1.2, 0, 1)
    for semi in chords[c % 4][:3]:
        fr = f(semi)
        pad[m] += (saw(fr * 1.003, t[m]) + saw(fr * 0.997, t[m])) * 0.5 * env
pad = lowpass(pad, 700) * 0.10

# ---- arpeggio: 16th-note chord tones one octave up, plucky, lowpassed (the "tech" motor) ----
arp = np.zeros(N)
step = BEAT / 4
n_steps = int(np.ceil(TOTAL / step))
pattern = [0, 1, 2, 3, 2, 1, 0, 2]
for k in range(n_steps):
    s = k * step
    if s >= TOTAL: break
    chord = chords[int(s // (CHORD_BEATS * BEAT)) % 4]
    semi = chord[pattern[k % len(pattern)]] + 12
    fr = f(semi)
    m = (t >= s) & (t < s + step * 0.95); lt = t[m] - s
    env = np.exp(-lt * 14.0) * np.clip(lt / 0.004, 0, 1)
    arp[m] += (np.sign(np.sin(2 * np.pi * fr * t[m])) * 0.6 + np.sin(2 * np.pi * fr * t[m]) * 0.4) * env
arp = lowpass(arp, 2400) * 0.075

# ---- sub bass: chord root two octaves down, per beat, gated ----
bass = np.zeros(N)
n_beats = int(np.ceil(TOTAL / BEAT))
for b in range(n_beats):
    s = b * BEAT
    if s >= TOTAL: break
    chord = chords[int(s // (CHORD_BEATS * BEAT)) % 4]
    fr = f(chord[0] - 12)
    m = (t >= s) & (t < s + BEAT * 0.9); lt = t[m] - s
    env = np.clip(lt / 0.01, 0, 1) * np.exp(-lt * 3.0)
    bass[m] += np.sin(2 * np.pi * fr * t[m]) * env
bass *= 0.16

# ---- drums: soft kick on every beat, closed hat on 8th off-beats ----
drums = np.zeros(N)
for b in range(n_beats):
    s = b * BEAT
    if s >= TOTAL: break
    m = (t >= s) & (t < s + 0.25); lt = t[m] - s
    sweep = 110.0 * np.exp(-lt * 28.0) + 42.0
    phase = 2 * np.pi * np.cumsum(sweep) / SR
    drums[m] += np.sin(phase) * np.exp(-lt * 18.0) * 0.55
    # hat on the off-beat
    hs = s + BEAT / 2
    hm = (t >= hs) & (t < hs + 0.035); hl = t[hm] - hs
    noise = rng.standard_normal(hm.sum())
    noise = np.diff(np.concatenate([[0], noise]))  # crude high-pass
    drums[hm] += noise * np.exp(-hl * 120.0) * 0.06
    # extra 16th hat every other beat for drive
    if b % 2 == 1:
        hs2 = s + BEAT * 0.75
        hm2 = (t >= hs2) & (t < hs2 + 0.025); hl2 = t[hm2] - hs2
        n2 = np.diff(np.concatenate([[0], rng.standard_normal(hm2.sum())]))
        drums[hm2] += n2 * np.exp(-hl2 * 140.0) * 0.035

# ---- occasional high "ping" every 4 bars ----
ping = np.zeros(N)
for c in range(0, n_chords, 2):
    s = c * CHORD_BEATS * BEAT + BEAT * 3.5
    if s >= TOTAL: break
    fr = f(chords[c % 4][2] + 24)
    m = (t >= s) & (t < s + 1.2); lt = t[m] - s
    ping[m] += np.sin(2 * np.pi * fr * t[m]) * np.exp(-lt * 3.0) * 0.05

mix = pad + arp + bass + drums + ping
mix = np.tanh(mix * 1.6)             # gentle saturation / limiter
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.6

# fade in / fade out
fade = int(2.0 * SR)
mix[:fade] *= np.linspace(0, 1, fade)
mix[-fade:] *= np.linspace(1, 0, fade)

pcm = np.int16(np.clip(mix, -1, 1) * 32767)
outp = os.path.join(SC, "audio", "music.wav")
with wave.open(outp, "w") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", outp, "duration", round(TOTAL, 2), "bpm", BPM)
