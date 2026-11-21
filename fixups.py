#!/usr/bin/env python3
"""Local post-fixes for cloud clips (no GPU, runs on the Mac).

    python fixups.py sky   IN.mp4 STILL.jpg OUT.mp4 --rows 300     # paste the still's sky over the top rows (kills model-made smoke)
    python fixups.py photo IN.mp4 PHOTO.jpg OUT.mp4 --quad x,y x,y x,y x,y [--paw cx,cy,rx,ry]
                                                                  # track a picture frame and keep a static photo in it

Both read and write 48 fps H.264 like the rest of the cloud pipeline.
"""
import argparse
import subprocess

import cv2
import numpy as np

import build


def _writer(path, fps, w, h):
    return subprocess.Popen([build.ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                             "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "16",
                             "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)


def frames(path):
    cap = cv2.VideoCapture(path)
    while True:
        ok, fr = cap.read()
        if not ok:
            return
        yield fr


def sky(args):
    still = cv2.imread(args.still)
    cap = cv2.VideoCapture(args.inp)
    fps, w, h = cap.get(5), int(cap.get(3)), int(cap.get(4))
    still = cv2.resize(still, (w, h))
    # full still above `rows`, soft blend over the next `feather` rows, clip below
    a = np.zeros((h, 1, 1), np.float32)
    a[:args.rows] = 1
    a[args.rows:args.rows + args.feather] = np.linspace(1, 0, args.feather)[:, None, None]
    out = _writer(args.out, fps, w, h)
    for fr in frames(args.inp):
        out.stdin.write((still * a + fr * (1 - a)).astype(np.uint8).tobytes())
    out.stdin.close()
    out.wait()


def photo(args):
    quad = np.float32([[float(v) for v in p.split(",")] for p in args.quad])
    pic = cv2.imread(args.photo)
    cap = cv2.VideoCapture(args.inp)
    fps, w, h = cap.get(5), int(cap.get(3)), int(cap.get(4))
    # track corners found on the frame's wooden border (a ring around the photo), frame to frame
    ring = np.zeros((h, w), np.uint8)
    c = quad.mean(0)
    cv2.fillConvexPoly(ring, (c + (quad - c) * 1.18).astype(np.int32), 255)
    cv2.fillConvexPoly(ring, (c + (quad - c) * 0.92).astype(np.int32), 0)
    it = frames(args.inp)
    first = next(it)
    prev = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    pts = cv2.goodFeaturesToTrack(prev, 200, 0.01, 4, mask=ring)
    pts0 = pts.copy()  # homography is always measured from the first frame, so errors don't accumulate
    H_total = np.eye(3)
    ph, pw = pic.shape[:2]
    src = np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]])
    out = _writer(args.out, fps, w, h)
    paw = [float(v) for v in args.paw.split(",")] if args.paw else None

    # a cream mat around the print, as in a real frame: it covers whatever the model drew up to the wood,
    # so the print's own edge sits inside the mat instead of flickering against the model's version
    mat_px = max(4, int(min(pw, ph) * args.mat))
    matted = cv2.copyMakeBorder(pic, mat_px, mat_px, mat_px, mat_px, cv2.BORDER_CONSTANT, value=(214, 228, 236))
    mh, mw = matted.shape[:2]
    src = np.float32([[0, 0], [mw, 0], [mw, mh], [0, mh]])

    def paste(fr, q, paw_c):
        c = q.mean(0)
        q = c + (q - c) * (1 + args.grow)  # tuck the mat's outer edge just under the wooden frame
        warped = cv2.warpPerspective(matted, cv2.getPerspectiveTransform(src, q), (w, h), flags=cv2.INTER_AREA)
        m = np.zeros((h, w), np.uint8)
        cv2.fillConvexPoly(m, q.astype(np.int32), 255)
        if paw_c is not None:
            cv2.ellipse(m, (int(paw_c[0]), int(paw_c[1])), (int(paw[2]), int(paw[3])), 0, 0, 360, 0, -1)
        m = cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32)[..., None] / 255
        lit = cv2.GaussianBlur(fr, (41, 41), 0).astype(np.float32)
        lit = np.clip(lit / np.percentile(lit[m[..., 0] > 0.5], 90), 0.75, 1.05)
        blend = np.clip(warped.astype(np.float32) * (0.55 + 0.45 * lit), 0, 255)
        return (fr * (1 - m) + blend * m).astype(np.uint8)

    if args.static:  # the frame doesn't move (on a table): same quad every frame, nothing to track
        for fr in [first, *it]:
            out.stdin.write(paste(fr, quad, paw[:2] if paw else None).tobytes())
        out.stdin.close()
        out.wait()
        return

    # pass 1: track corners per frame; pass 2: smooth them over time so the print doesn't shimmer
    quads, paws, frs = [quad], [paw[:2] if paw else None], [first]
    for fr in it:
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, pts, None, winSize=(21, 21), maxLevel=3)
        keep = st[:, 0] == 1
        if keep.sum() >= 8:
            Hs, _ = cv2.findHomography(pts0[keep], nxt[keep], cv2.RANSAC, 2.0)
            if Hs is not None:
                H_total = Hs
            pts, pts0 = nxt[keep].reshape(-1, 1, 2), pts0[keep]
        quads.append(cv2.perspectiveTransform(quad[None], H_total)[0])
        paws.append(cv2.perspectiveTransform(np.float32([[paw[:2]]]), H_total)[0, 0] if paw else None)
        frs.append(fr)
        prev = g
    Q = np.array(quads)
    k = args.smooth
    pad = np.concatenate([np.repeat(Q[:1], k, 0), Q, np.repeat(Q[-1:], k, 0)])
    Qs = np.array([pad[i:i + 2 * k + 1].mean(0) for i in range(len(Q))])
    for fr, q, pc in zip(frs, Qs, paws):
        out.stdin.write(paste(fr, q.astype(np.float32), pc).tobytes())
    out.stdin.close()
    out.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sky")
    s.add_argument("inp"); s.add_argument("still"); s.add_argument("out")
    s.add_argument("--rows", type=int, default=300); s.add_argument("--feather", type=int, default=40)
    p = sub.add_parser("photo")
    p.add_argument("inp"); p.add_argument("photo"); p.add_argument("out")
    p.add_argument("--quad", nargs=4, required=True); p.add_argument("--paw")
    p.add_argument("--static", action="store_true", help="frame doesn't move: no tracking")
    p.add_argument("--smooth", type=int, default=6, help="frames on each side to average the tracked corners over")
    p.add_argument("--mat", type=float, default=0.06, help="mat border, as a fraction of the print's short side")
    p.add_argument("--grow", type=float, default=0.03, help="enlarge the pasted quad to tuck under the wood")
    a = ap.parse_args()
    {"sky": sky, "photo": photo}[a.cmd](a)
