#!/usr/bin/env python3
"""Pull every frame's colors back toward the clip's first frame (the clean still).

Wan2.2 5B image-to-video drifts hotter (more saturated, more contrast) as it generates frames.
Reinhard-style transfer in LAB: match each frame's per-channel mean/std to frame 0, blended by --strength
so real lighting changes in the shot still come through.

    python colormatch.py in.mp4 out.mp4 [--strength 0.75]
"""
import argparse
import subprocess

import cv2
import numpy as np


def lab_stats(lab):
    flat = lab.reshape(-1, 3)
    return flat.mean(0), flat.std(0) + 1e-6


def match(src, dst, strength=0.75):
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    ok, first = cap.read()
    if not ok:
        raise SystemExit(f"cannot read {src}")
    h, w = first.shape[:2]
    ref_mean, ref_std = lab_stats(cv2.cvtColor(first, cv2.COLOR_BGR2LAB).astype(np.float32))

    import imageio_ffmpeg
    enc = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", dst], stdin=subprocess.PIPE)
    frame = first
    while ok:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB).astype(np.float32)
        mean, std = lab_stats(lab)
        matched = (lab - mean) / std * ref_std + ref_mean
        out = lab + strength * (matched - lab)
        enc.stdin.write(cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).tobytes())
        ok, frame = cap.read()
    enc.stdin.close()
    enc.wait()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--strength", type=float, default=0.75)
    args = p.parse_args()
    match(args.src, args.dst, args.strength)


if __name__ == "__main__":
    main()
