#!/usr/bin/env python3
"""Animal Crossing-style "animalese" babble: one quick pitched blip per letter, no real words.

Each character has a voice (base pitch, speed, brightness). Letters map to a stable pitch offset and a
vowel-ish formant so the same line always sounds the same; spaces and punctuation shape the rhythm,
"?" lifts the last syllables and "!" makes them punchier.

    python babble.py out.wav hammi "Good morning, Bobo!"
"""
import argparse
import hashlib
import wave

import numpy as np

SR = 44100

# base_hz: pitch; speed: seconds per letter; bright: how many harmonics; wobble: pitch variation
VOICES = {
    "hammi":  {"base_hz": 330, "speed": 0.060, "bright": 6, "wobble": 0.12},
    "bobo":   {"base_hz": 520, "speed": 0.050, "bright": 4, "wobble": 0.18},
    "dany":   {"base_hz": 410, "speed": 0.068, "bright": 8, "wobble": 0.08},
    "dwight": {"base_hz": 230, "speed": 0.064, "bright": 7, "wobble": 0.10},
    "hoot":   {"base_hz": 190, "speed": 0.075, "bright": 9, "wobble": 0.06},
    "pip":    {"base_hz": 700, "speed": 0.040, "bright": 3, "wobble": 0.25},
    "juniper": {"base_hz": 450, "speed": 0.058, "bright": 5, "wobble": 0.12},
    "vivi":   {"base_hz": 600, "speed": 0.042, "bright": 4, "wobble": 0.22},
    "toozi":  {"base_hz": 260, "speed": 0.055, "bright": 7, "wobble": 0.15},
    "jul":    {"base_hz": 380, "speed": 0.066, "bright": 8, "wobble": 0.09},
    "molly":  {"base_hz": 640, "speed": 0.038, "bright": 3, "wobble": 0.30},
    "damian": {"base_hz": 210, "speed": 0.070, "bright": 8, "wobble": 0.10},
}
DEFAULT_VOICE = {"base_hz": 400, "speed": 0.06, "bright": 5, "wobble": 0.12}

# rough vowel formants (Hz): gives letters a sung-vowel color instead of a pure beep
FORMANTS = {"a": (800, 1200), "e": (500, 1900), "i": (320, 2300), "o": (500, 900), "u": (350, 800)}
VOWEL_OF = {c: v for v, cs in {"a": "ahjkq", "e": "bcdegptvz", "i": "ilmnrsxy", "o": "fow", "u": "u"}.items()
            for c in cs}


def _letter_seed(ch):
    return int(hashlib.md5(ch.encode()).hexdigest()[:8], 16)


def syllable(ch, voice, pitch_mult=1.0, loud=1.0):
    dur = voice["speed"]
    n = int(SR * dur)
    t = np.arange(n) / SR
    offset = ((_letter_seed(ch) % 1000) / 1000 - 0.5) * 2 * voice["wobble"]
    f0 = voice["base_hz"] * (1 + offset) * pitch_mult
    f0 = f0 * (1 + 0.04 * np.sin(2 * np.pi * 9 * t))  # slight chirp so blips sound voiced, not beeped
    f1, f2 = FORMANTS[VOWEL_OF.get(ch, "a")]
    phase = 2 * np.pi * np.cumsum(f0) / SR
    sig = np.zeros(n)
    for k in range(1, voice["bright"] + 1):
        hk = k * f0
        gain = np.exp(-((hk - f1) / 300) ** 2) + 0.6 * np.exp(-((hk - f2) / 400) ** 2) + 0.15 / k
        sig += gain * np.sin(k * phase)
    env = np.minimum(1, t / 0.006) * np.exp(-t / (dur * 0.55))  # fast attack, plucky decay
    return loud * sig * env / (np.abs(sig).max() + 1e-9)


def render_line(text, speaker):
    voice = VOICES.get(speaker, DEFAULT_VOICE)
    words = text.lower()
    out = []
    letters = [c for c in words if c.isalpha()]
    ending = words.rstrip()[-1:] if words.strip() else ""
    li = 0
    for c in words:
        if c.isalpha():
            near_end = li >= len(letters) - 3
            pitch = 1.18 if ending == "?" and near_end else 1.0
            loud = 1.25 if ending == "!" and near_end else 1.0
            out.append(syllable(c, voice, pitch, loud))
            li += 1
        elif c == " ":
            out.append(np.zeros(int(SR * voice["speed"] * 0.5)))
        elif c in ",;:":
            out.append(np.zeros(int(SR * 0.16)))
        elif c in ".!?":
            out.append(np.zeros(int(SR * 0.28)))
    audio = np.concatenate(out) if out else np.zeros(1)
    return 0.5 * audio / (np.abs(audio).max() + 1e-9)


def write_wav(path, audio):
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("out")
    p.add_argument("speaker")
    p.add_argument("text")
    args = p.parse_args()
    write_wav(args.out, render_line(args.text, args.speaker))


if __name__ == "__main__":
    main()
