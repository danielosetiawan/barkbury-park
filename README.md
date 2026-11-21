# Corgi Town 🐕

A faceless YouTube series about Hammi the corgi in Pawsley Hollow, a town of animals with no humans in it.
Made with [WanGP](~/repos/wan2gp).

- `BIBLE.md`: world, cast, style lock, episode formula
- `PROMPTS.md`: paste-ready prompts for the WanGP web UI
- `episodes/*.json`: shot lists (one still prompt + one motion prompt per shot)
- `build.py` + `run.sh`: shot list → headless WanGP queues → stitched video

## Pipeline
```bash
P=~/miniforge3/envs/wan2gp/bin/python

# 1. Stills (Z-Image Turbo, 2 candidates per shot)
$P build.py keyframes ep01
./run.sh queues/ep01_keyframes.json keyframes/ep01/raw
#    -> look through keyframes/ep01/raw, copy the best still per shot to keyframes/ep01/s01.png etc.
#       Re-roll bad ones:  $P build.py keyframes ep01 --only s03 s07

# 2. Animate (FastWan 5B, 3 steps, 4s clips)
$P build.py clips ep01             # 832x480 draft
./run.sh queues/ep01_clips.json clips/ep01

# 3. Stitch + captions + music (drop a royalty-free track in music/)
$P build.py assemble ep01          # -> renders/ep01.mp4
```
Add `--dry-run` to any `run.sh` call to check the queue without generating.

## Measured on this M1 Pro / 16 GB (Oct 2026)
| Step | Time |
|---|---|
| Still, Z-Image Turbo 1280x720, 8 steps | ~15 min |
| Clip, Wan2.2 5B + FastWan@60% 832x480, 4s, 6 steps | ~40–45 min (est.; 2s test took ~17 min) |
| Model load per batch | 1–2 min |

So a 16-shot episode is about 4h of stills plus 10h of clips: two overnight
batches. Close other apps while it runs, because decoding pushes macOS into
heavy swap. For faster or 720p output, rent a cloud GPU and run the same queues.

**Local WanGP patch required.** `~/repos/Wan2GP/shared/mps/device_patch.py` has
three Apple Silicon fixes. Without them every image comes out black and clips
crash:
1. Synchronous CPU→GPU copies. Async copies from mmgp's staging buffers raced on MPS and produced NaNs.
2. Opt-in BF16 on M1/M2 (`WANGP_MPS_BF16=1`, which `run.sh` sets).
3. Chunked attention, so video-sized attention fits in Metal's maximum buffer size.

A `git pull` in Wan2GP may conflict with these changes. Re-apply them if they get lost.

## Why clips are color-matched
Wan2.2 5B image-to-video drifts hotter (saturation and contrast) frame by frame. We tested FastWan
strength, steps, CFG with an anti-saturation negative, no LoRA, and full-precision weights, and all of them
drifted. The VAE round-trips cleanly. So `build.py assemble` runs `colormatch.py` on every clip
(LAB mean/std matched to the first frame, strength 0.75) before editing. Use `--no-colormatch` to compare.

## Before uploading
- When you upload, tick YouTube's **"altered or synthetic content"** box if it
  applies, and put "AI-assisted animation" in the description.
- YouTube demonetizes "mass-produced / repetitive" channels. Recurring
  characters, a story arc per episode, and your own editing, captions, and sound
  design are what make this count as original work. Don't just upload raw clips.
- Use music you have rights to: the YouTube Audio Library, or generate it in
  WanGP (Ace Step / Stable Audio). WanGP's **MMAudio** can add sound effects
  like dishes clinking or birds.
