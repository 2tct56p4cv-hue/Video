import numpy as np
import wave, json, os

SC = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(os.path.join(SC, "timeline.json")))
TOTAL = tl["total"] + 1.5

SR = 44100

def note_freq(semitones_from_a4):
    return 440.0 * (2 ** (semitones_from_a4 / 12.0))

# simple corporate-pad chord progression, 4 bars looping, in A minor / C major-ish, subtle & upbeat
# chords as semitone offsets from A4
chords = [
    [-12, -8, -5, 0],   # Am
    [-10, -7, -3, 2],   # C
    [-7, -3, 0, 5],     # F-ish  (using relative simple triads)
    [-5, -1, 2, 7],     # G
]
bar_len = 4.0  # seconds per chord
n_bars = int(np.ceil(TOTAL / bar_len))

t = np.linspace(0, TOTAL, int(TOTAL * SR), endpoint=False)
audio = np.zeros_like(t)

# pad layer: soft sine/triangle blend per chord tone, with slow attack
for bar in range(n_bars):
    start = bar * bar_len
    end = min(start + bar_len, TOTAL)
    if start >= TOTAL:
        break
    chord = chords[bar % len(chords)]
    mask = (t >= start) & (t < end)
    local_t = t[mask] - start
    env = np.clip(local_t / 0.6, 0, 1) * np.clip((end - start - local_t) / 0.6, 0, 1)
    for semis in chord:
        freq = note_freq(semis)
        wave_tone = 0.5 * np.sin(2 * np.pi * freq * t[mask]) + 0.5 * (2*(local_t*freq % 1)-1) * 0.15
        audio[mask] += wave_tone * env * 0.028

# gentle rhythmic pulse (soft pluck) on beats, gives "upbeat" motion without being busy
beat_len = 1.0
n_beats = int(np.ceil(TOTAL / beat_len))
pulse = np.zeros_like(t)
rng = np.random.default_rng(7)
for b in range(n_beats):
    bt = b * beat_len
    if bt >= TOTAL:
        break
    chord = chords[(b // 4) % len(chords)]
    semis = chord[0] + 12  # root, one octave up, plucky
    freq = note_freq(semis)
    dur = 0.35
    mask = (t >= bt) & (t < bt + dur)
    local_t = t[mask] - bt
    env = np.exp(-local_t * 9.0)
    pulse[mask] += np.sin(2 * np.pi * freq * t[mask]) * env * 0.05

audio = audio + pulse

# very soft shimmering high harmonic sparkle every 2 bars for "modern tech" feel
sparkle = np.zeros_like(t)
for bar in range(0, n_bars, 2):
    start = bar * bar_len + 2.0
    if start >= TOTAL:
        break
    chord = chords[bar % len(chords)]
    freq = note_freq(chord[-1] + 12)
    mask = (t >= start) & (t < start + 1.6)
    local_t = t[mask] - start
    env = np.exp(-local_t * 2.2) * np.clip(local_t/0.1,0,1)
    sparkle[mask] += np.sin(2*np.pi*freq*t[mask]) * env * 0.02

audio = audio + sparkle

# gentle limiter / normalize, keep it subtle underneath narration
peak = np.max(np.abs(audio)) + 1e-9
audio = audio / peak * 0.55

# fade in / fade out
fade_n = int(1.5 * SR)
audio[:fade_n] *= np.linspace(0, 1, fade_n)
audio[-fade_n:] *= np.linspace(1, 0, fade_n)

pcm = np.int16(np.clip(audio, -1, 1) * 32767)

out_path = os.path.join(SC, "audio", "music.wav")
with wave.open(out_path, "w") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(SR)
    f.writeframes(pcm.tobytes())

print("wrote", out_path, "duration", TOTAL)
