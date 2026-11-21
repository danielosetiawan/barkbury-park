#!/usr/bin/env python3
"""Turn an episode file into WanGP headless queues, then assemble the final video.

    python build.py keyframes ep01          # -> queues/ep01_keyframes.json  (Z-Image stills)
    python build.py clips ep01 [--final]    # -> queues/ep01_clips.json      (FastWan 5B image-to-video)
    python build.py animatic ep01           # -> renders/ep01_animatic.mp4   (stills rough cut)
    python build.py assemble ep01           # -> renders/ep01.mp4            (concat + captions + music)

Run the queues with ./run.sh (it calls `wgp.py --process`).
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
WAN2GP = os.path.expanduser(os.environ.get("WAN2GP_DIR", "~/repos/wan2gp"))

# Keep these identical across every shot -- this is what holds the look together.
STYLE = ("stylized 3D animated film, cozy storybook town, soft warm lighting, gentle depth of field, "
         "rounded shapes, rich textures, pastel and warm autumn color palette, cinematic composition")
NEGATIVE = ("humans, people, person, human hands, human face, text, watermark, logo, blurry, distorted anatomy, "
            "extra limbs, extra legs, six legs, extra arms, four legs, on all fours, quadruped, "
            "deformed paws, flicker, low quality")
NEGATIVE_ALLOW_TEXT = NEGATIVE.replace("text, ", "")


def negative_for(shot):
    neg = NEGATIVE_ALLOW_TEXT if shot.get("allow_text") else NEGATIVE
    return f"{neg}, {shot['negative_extra']}" if shot.get("negative_extra") else neg


CAST = {
    "hammi": "Hammi, an anthropomorphic Pembroke Welsh corgi with a red-headed tri-color coat (deep mahogany copper-red head and ears with pale cream insides, a white blaze up the middle of the face widening into a white muzzle and white lower cheeks, white chest, just a small patch of black fur on the hips below the sweater (mostly copper-red, not a black rump), copper-red legs, white paws), a sturdy chunky corgi build, soulful dark eyes and big upright ears, a docked rump with no tail, "
             "always standing upright on two short hind legs like a cartoon character, with exactly two arms and two legs, "
               "wearing a mustard-yellow knit sweater and a small forest-green scarf",
    "bobo": "Bobo, a small fluffy white bichon poo dog with a curly cloud-like coat, round black button eyes "
            "and nose, wearing a sky-blue bandana, standing upright on two short hind legs like a cartoon character, "
            "with exactly two arms and two legs",
    "dany": "Dany, a plump ginger tabby cat in a flour-dusted pink apron, standing upright on two hind legs like a cartoon character, with exactly two arms and two legs",
    "dwight": "Dwight, a sleek brown river otter in a navy bus-driver cap and vest, left-handed",
    "hoot": "Professor Hoot, a stern great horned owl with half-moon spectacles and a tweed waistcoat",
    "toozi": "Toozi, a tall chestnut horse with a flowing blonde mane, wearing a faded band t-shirt, colorful festival "
             "wristbands on one foreleg and big headphones on the head, standing upright on two hind legs like a cartoon character, with exactly two arms and two legs",
    "vivi": "Vivi, a small warm chocolate-brown smooth-coated dachshund (solid warm brown all over), with a smooth bare furry neck, with a long body and floppy ears, "
            "always holding a cup of boba milk tea with a wide straw, standing upright on two hind legs like a cartoon character, with exactly two arms and two legs",
    "jul": "Jul, a slender white goat with elegant curled horns, dressed super hip in a cropped lavender puffer jacket, "
            "a bucket hat, round tinted sunglasses and chunky white sneakers, standing upright on two hind legs like a cartoon character, with exactly two arms and two legs",
    "damian": "Damian, a barn owl with a heart-shaped white face and sleepy eyes, wearing teal hospital scrubs "
              "with a stethoscope around the neck",
    "pip": "Pip, a tiny golden hamster in an oversized red hoodie",
    "juniper": "Juniper, a slender red fox in a green gardening apron, standing upright on two hind legs like a cartoon character, with exactly two arms and two legs",
    "molly": "Molly, a small round fluffy yellow duck with a bright orange bill and orange webbed feet, a tiny pink polka-dot bow on the head "
             "and big sparkly eyes, standing upright on two feet like a cartoon character, with exactly two wings and two feet",
    "movers": "two cheerful beaver movers in orange overalls",
    "pigeons": "three pigeons wearing little flat caps",
}

KEYFRAME_MODEL = "z_image"            # Z-Image Turbo, 8 steps
CLIP_MODEL = "ti2v_2_2"               # Wan2.2 TI2V 5B, with the FastWan LoRA turned down (see clip task)
FASTWAN_LORA = "Wan2_2_5B_FastWanFullAttn_lora_rank_128_bf16.safetensors"
# Cloud (Modal H100): Wan2.2 14B i2v Enhanced Lightning, native 720p, 5 s at 16 fps, RIFE x3 -> 48 fps.
# Clean colors, so cloud clips skip colormatch/denoise at assembly (assemble --cloud).
CLOUD_CLIP = {
    "model_type": "i2v_2_2_Enhanced_Lightning_v2",
    "resolution": "1280x720",
    "video_length": 81,
    "num_inference_steps": 4,
    "guidance_scale": 1,
    "guidance2_scale": 1,
    "temporal_upsampling": "rife*3",
}
FPS = 24                              # Wan2.2 5B native frame rate
RES = {"draft": "832x480", "final": "1280x704"}
# Wan2.2 5B i2v drifts hotter frame by frame; colormatch.py pulls each clip back to its first frame,
# then a light denoise softens the remaining texture.
COLORMATCH_STRENGTH = 0.75
GRADE = "hqdn3d=2:2:3:3"


def load_episode(ep):
    matches = glob.glob(os.path.join(ROOT, "episodes", f"{ep}*.json"))
    if not matches:
        sys.exit(f"No episode file matching episodes/{ep}*.json")
    with open(matches[0]) as f:
        return json.load(f)


def cast_text(shot):
    return "; ".join(CAST[c] for c in shot.get("cast", []) if c in CAST)


def talking_cue(shot):
    """Shots with dialogue: ask for moving mouths so the babble looks spoken."""
    speakers = []
    for line in shot.get("dialogue", []):
        if line["speaker"] not in speakers:
            speakers.append(line["speaker"])
    if not speakers:
        return ""
    names = [CAST.get(sp, sp).split(",")[0] for sp in speakers]
    who = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]
    verb = "talks" if len(names) == 1 else "chat"
    return f" {who} {verb} animatedly, mouth{'s' if len(names) > 1 else ''} moving as if speaking."


def frames_for(seconds):
    # Wan needs 4n+1 frames
    return int(round(seconds * FPS / 4)) * 4 + 1


def write_queue(name, tasks):
    os.makedirs(os.path.join(ROOT, "queues"), exist_ok=True)
    path = os.path.join(ROOT, "queues", name)
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)
    print(f"Wrote {len(tasks)} tasks -> {os.path.relpath(path, ROOT)}")
    return path


def cmd_keyframes(args):
    ep = load_episode(args.ep)
    tasks = []
    for shot in ep["shots"]:
        if args.only and shot["id"] not in args.only:
            continue
        prompt = f"{cast_text(shot)}. {shot['keyframe']}. {STYLE}"
        tasks.append({
            "model_type": KEYFRAME_MODEL,
            "prompt": prompt,
            "negative_prompt": negative_for(shot),
            "resolution": "1280x720",
            "num_inference_steps": 8,
            "guidance_scale": 0,
            "seed": -1,
            "batch_size": args.variants,
            "output_filename": f"{ep['id']}_{shot['id']}",
        })
    write_queue(f"{ep['id']}_keyframes.json", tasks)
    print(f"Next: ./run.sh queues/{ep['id']}_keyframes.json keyframes/{ep['id']}/raw")
    print(f"Then copy the best still for each shot to keyframes/{ep['id']}/<shot>.png "
          "(otherwise the first candidate is used).")


def shot_outputs(folder, stem, exts):
    """Files for exactly this shot: `stem.ext` or WanGP's duplicate form `stem(2).ext`.
    A plain `stem*` glob is wrong: s06 would also match s06a's files."""
    import re
    pat = re.compile(rf"^{re.escape(stem)}(\(\d+\))?\.({'|'.join(exts)})$", re.IGNORECASE)
    return sorted(os.path.join(folder, f) for f in os.listdir(folder) if pat.match(f)) if os.path.isdir(folder) else []


IMAGE_EXTS = ("png", "jpg", "jpeg", "webp")


def pick_keyframe(ep_id, shot_id):
    chosen = shot_outputs(os.path.join(ROOT, "keyframes", ep_id), shot_id, IMAGE_EXTS)
    if chosen:
        return chosen[0]
    raw = shot_outputs(os.path.join(ROOT, "keyframes", ep_id, "raw"), f"{ep_id}_{shot_id}", IMAGE_EXTS)
    return raw[0] if raw else None


def cmd_clips(args):
    ep = load_episode(args.ep)
    res = RES["final" if args.final else "draft"]
    tasks, missing = [], []
    for shot in ep["shots"]:
        if args.only and shot["id"] not in args.only:
            continue
        if shot.get("still_only"):
            continue  # shown as a slow zoom on the still at assembly time
        image = pick_keyframe(ep["id"], shot["id"])
        if not image:
            missing.append(shot["id"])
            continue
        task = {
            "prompt": f"{cast_text(shot)}. {shot['motion']}{talking_cue(shot)} {STYLE}",
            "negative_prompt": negative_for(shot),
            "image_prompt_type": "S",
            "image_start": [image],
            "seed": -1,
            "output_filename": f"{ep['id']}_{shot['id']}",
        }
        if args.profile == "cloud":
            task.update(CLOUD_CLIP)
        else:
            task.update({
                "model_type": CLIP_MODEL,
                "resolution": res,
                "video_length": frames_for(shot.get("seconds", args.seconds)),
                # FastWan at 60% + 6 steps: smoother texture than the stock 100% / 3 steps (tested Oct 2026)
                "activated_loras": [FASTWAN_LORA],
                "loras_multipliers": "0.6",
                "num_inference_steps": 6,
                # guidance > 1 makes the negative prompt (extra legs, on all fours...) apply to clips;
                # costs ~30% more time, so it's per shot: "guidance": 3 on shots with limb trouble
                "guidance_scale": shot.get("guidance", ep.get("clip_guidance", 1)),
                "flow_shift": 3,
            })
        tasks.append(task)
    if missing:
        print(f"Skipped (no keyframe yet): {', '.join(missing)}")
    write_queue(f"{ep['id']}_clips.json", tasks)
    print(f"Next: ./run.sh queues/{ep['id']}_clips.json clips/{ep['id']}")


def ffmpeg_exe():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: `brew install ffmpeg` or run with the wan2gp conda env")


def latest_clip(ep_id, shot_id):
    clips = shot_outputs(os.path.join(ROOT, "clips", ep_id), f"{ep_id}_{shot_id}", ("mp4",))
    return max(clips, key=os.path.getmtime) if clips else None


def drawtext_escape(text):
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")


FONTS = "/System/Library/Fonts/Supplemental"


def name_card_filters(card, start=0.4, hold=2.6, fade=0.35):
    """First-appearance card, lower right: bold name with an italic tagline under it, fading in and out."""
    end = start + hold
    alpha = (f"if(lt(t,{start}),0,if(lt(t,{start + fade}),(t-{start})/{fade},"
             f"if(lt(t,{end - fade}),1,if(lt(t,{end}),({end}-t)/{fade},0))))")
    common = "fontcolor=white:shadowcolor=black@0.65:shadowx=2:shadowy=2:x=w-tw-w*0.05"
    out = [f"drawtext=fontfile='{FONTS}/Georgia Bold.ttf':text='{drawtext_escape(card['name'])}':"
           f"fontsize=h/14:y=h*0.80-th:{common}:alpha='{alpha}'"]
    if card.get("tagline"):
        out.append(f"drawtext=fontfile='{FONTS}/Georgia Italic.ttf':text='{drawtext_escape(card['tagline'])}':"
                   f"fontsize=h/26:y=h*0.82:{common}:alpha='{alpha}'")
    return out


def _duration(ff, path):
    out = subprocess.run([ff, "-i", path], capture_output=True, text=True).stderr
    h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


MUSIC_VOLUME = 0.8    # music is the main track
BABBLE_VOLUME = 0.35  # animalese sits softly on top of the music, no ducking
LOUDNESS_LUFS = -14   # final mix loudness (YouTube's playback target)


def episode_music(ep):
    """The episode's own track (music/<ep>_*.wav|mp3|m4a from the music job), else None."""
    import re
    folder = os.path.join(ROOT, "music")
    if not os.path.isdir(folder):
        return None
    pat = re.compile(rf"^{re.escape(ep['id'])}_.*\.(wav|mp3|m4a|flac)$", re.IGNORECASE)
    found = sorted(f for f in os.listdir(folder) if pat.match(f))
    return os.path.join(folder, found[0]) if found else None


def _babble_track(shots, starts, total, work):
    """One mono wav of every shot's dialogue placed on the episode timeline, or None if nobody talks."""
    lines = [(starts[k] + line.get("at", 0.3), line["speaker"], line.get("babble", line["line"]))
             for k, shot in enumerate(shots) for line in shot.get("dialogue", [])]
    if not lines:
        return None
    import babble
    import numpy as np
    track = np.zeros(int((total + 1) * babble.SR))
    for t, speaker, text in lines:
        clip = babble.render_line(text, speaker)
        i = int(t * babble.SR)
        j = min(len(track), i + len(clip))
        track[i:j] += clip[: j - i]
    path = os.path.join(work, "babble.wav")
    babble.write_wav(path, track)
    return path


def _srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def _captions(shots, starts, total, path):
    """Closed captions (.srt, uploaded to YouTube separately) for every dialogue line, or None if nobody talks.
    Each caption starts with its chatter and stays up long enough to read, without running into the next one."""
    import babble
    cues = sorted((starts[k] + line.get("at", 0.3), line) for k, shot in enumerate(shots)
                  for line in shot.get("dialogue", []))
    if not cues:
        return None
    entries = []
    for i, (t, line) in enumerate(cues):
        heard = len(babble.render_line(line.get("babble", line["line"]), line["speaker"])) / babble.SR
        end = t + max(heard + 0.3, 1.2 + 0.06 * len(line["line"]))  # ~15 characters a second, kid pace
        end = min(end, cues[i + 1][0] - 0.05 if i + 1 < len(cues) else total)
        name = CAST.get(line["speaker"], line["speaker"]).split(",")[0].upper()
        entries.append(f"{i + 1}\n{_srt_time(t)} --> {_srt_time(end)}\n{name}: {line['line']}\n")
    with open(path, "w") as f:
        f.write("\n".join(entries))
    return path


def _render(ep, args, sources, out_name):
    """Normalize each (shot, input_args, filters) segment, add caption, dissolve them together, add music."""
    ff = ffmpeg_exe()
    font = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    work = tempfile.mkdtemp(prefix=f"{ep['id']}_")
    parts, shots = [], []
    for shot, input_args, pre_vf in sources:
        # every shot to exactly 16:9 (clips are 832x480, stills 1280x720): fill, then center-crop
        w, h = args.width, args.width * 9 // 16 // 2 * 2
        vf = pre_vf + [f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={FPS},format=yuv420p,setsar=1"]
        if shot.get("caption"):
            vf.append(f"drawtext=fontfile={font}:text='{drawtext_escape(shot['caption'])}':"
                      "fontcolor=white:fontsize=h/18:x=w*0.05:y=h*0.88:"
                      "shadowcolor=black@0.6:shadowx=2:shadowy=2:enable='lt(t,3)'")
        if shot.get("name_card") and getattr(args, "name_cards", False):
            vf += name_card_filters(shot["name_card"])
        out = os.path.join(work, f"{len(parts):03d}.mp4")
        subprocess.run([ff, "-y", "-loglevel", "error", *input_args, "-an", "-vf", ",".join(vf),
                        "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-color_range", "tv", "-movflags", "+faststart", out], check=True)
        parts.append(out)
        shots.append(shot)
    if not parts:
        sys.exit("Nothing to render.")

    os.makedirs(os.path.join(ROOT, "renders"), exist_ok=True)
    silent = os.path.join(work, "silent.mp4")
    # Dissolve each shot into the next (a shot with "transition": "cut" gets a 1-frame blend, i.e. a cut),
    # then fade in/out at the very start and end of the episode only.
    durations = [_duration(ff, p) for p in parts]
    inputs = [x for p in parts for x in ("-i", p)]
    chain, prev, offset = [], "[0:v]", 0.0
    starts = [0.0]
    for k in range(1, len(parts)):
        d = 1 / FPS if shots[k].get("transition") == "cut" or args.dissolve <= 0 else args.dissolve
        offset += durations[k - 1] - d
        starts.append(offset)
        chain.append(f"{prev}[{k}:v]xfade=transition=fade:duration={d:.3f}:offset={offset:.3f}[x{k}]")
        prev = f"[x{k}]"
    total = offset + durations[-1]  # offset already subtracts every overlap
    chain.append(f"{prev}fade=t=in:d=0.6,fade=t=out:st={max(total - 0.8, 0):.3f}:d=0.8,scale=out_range=tv,format=yuv420p[v]")
    subprocess.run([ff, "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(chain),
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-color_range", "tv", "-movflags", "+faststart", silent], check=True)

    final = os.path.join(ROOT, "renders", out_name)
    music = args.music or episode_music(ep)
    babble_wav = _babble_track(shots, starts, total, work) if getattr(args, "babble", False) else None
    srt = _captions(shots, starts, total, os.path.splitext(final)[0] + ".srt") if getattr(args, "captions", False) else None
    if srt:
        print(f"  captions -> {os.path.relpath(srt, ROOT)} (upload as subtitles on YouTube)")
    audio_in, mix = [], []
    if music:
        audio_in += ["-stream_loop", "-1", "-i", music]
        mix.append(f"[1:a]atrim=0:{total:.3f},volume={MUSIC_VOLUME},"
                   f"afade=t=in:d=1.5,afade=t=out:st={max(total - 2, 0):.3f}:d=2,aformat=channel_layouts=stereo[m]")
    if babble_wav:
        audio_in += ["-i", babble_wav]
        mix.append(f"[{1 + (1 if music else 0)}:a]volume={BABBLE_VOLUME},aformat=channel_layouts=stereo[b]")
    if not audio_in:
        shutil.copy(silent, final)
        print("  (no music in music/ and no dialogue -- rendered silent)")
    else:
        labels = ("[m]" if music else "") + ("[b]" if babble_wav else "")
        n = labels.count("[")
        mix.append(f"{labels}amix=inputs={n}:duration=longest:normalize=0[mx]" if n > 1 else f"{labels}anull[mx]")
        # YouTube turns loud uploads down but never quiet ones up, so land near its -14 LUFS target
        mix.append(f"[mx]loudnorm=I={LOUDNESS_LUFS}:TP=-1.5:LRA=11,aresample=44100[a]")
        subprocess.run([ff, "-y", "-loglevel", "error", "-i", silent, *audio_in, "-filter_complex", ";".join(mix),
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-t", f"{total:.3f}", "-movflags", "+faststart", final], check=True)
        if not music:
            print("  (no music in music/ -- dialogue babble only)")
    shutil.rmtree(work, ignore_errors=True)
    print(f"Rendered {len(parts)} shots -> {os.path.relpath(final, ROOT)}")


def cmd_assemble(args):
    ep = load_episode(args.ep)
    if getattr(args, "cloud", False):
        global FPS
        args.colormatch, args.grade = False, False
        FPS = 48  # cloud clips are RIFE-smoothed to 48 fps; keep it
    sources = []
    for shot in ep["shots"]:
        if shot.get("still_only"):
            image = pick_keyframe(ep["id"], shot["id"])
            if image:
                sources.append((shot, *kenburns(image, shot.get("seconds", 4))))
            else:
                print(f"  missing still for {shot['id']}, skipping")
            continue
        clip = latest_clip(ep["id"], shot["id"])
        if not clip:
            print(f"  missing clip for {shot['id']}, skipping")
            continue
        if args.colormatch:
            import colormatch
            fixed = os.path.join(tempfile.gettempdir(), f"cm_{os.path.basename(clip)}")
            colormatch.match(clip, fixed, COLORMATCH_STRENGTH)
            clip = fixed
        # "trim": keep only the first N seconds of a clip (for clips that go wrong partway through)
        trim = ["-t", str(shot["trim"])] if shot.get("trim") else []
        sources.append((shot, [*trim, "-i", clip], [GRADE] if args.grade else []))
    _render(ep, args, sources, f"{ep['id']}.mp4")


def kenburns(image, seconds, push_in=True):
    """(input_args, filters) for a slow zoom on a still; upscale first so the move doesn't jitter."""
    frames = int(seconds * FPS)
    zoom = f"1+0.08*on/{frames}" if push_in else f"1.08-0.08*on/{frames}"
    pan = [f"scale=2560:-2,zoompan=z='{zoom}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
           f"d={frames}:s=1280x720:fps={FPS}"]
    return ["-i", image], pan  # zoompan emits `frames` frames from the single image


def cmd_animatic(args):
    """Rough cut from the stills: slow Ken Burns move per shot, same captions/timing as the real edit."""
    ep = load_episode(args.ep)
    sources = []
    for n, shot in enumerate(ep["shots"]):
        image = pick_keyframe(ep["id"], shot["id"])
        if not image:
            print(f"  missing still for {shot['id']}, skipping")
            continue
        sources.append((shot, *kenburns(image, shot.get("seconds", args.seconds), push_in=n % 2 == 0)))
    _render(ep, args, sources, f"{ep['id']}_animatic.mp4")


MUSIC_MODEL = "stable_audio3_small"   # Stable Audio 3 Small (music): instrumentals up to 120 s, 8 steps


def cmd_music(args):
    """Queue the episode's background track; WanGP writes it to music/<ep>_music.*"""
    ep = load_episode(args.ep)
    n = len(ep["shots"])
    seconds = sum(sh.get("seconds", 4) for sh in ep["shots"]) - 0.4 * (n - 1)
    task = {
        "model_type": MUSIC_MODEL,
        "prompt": ep.get("music_prompt", "Cozy lo-fi hip hop instrumental, warm piano, soft drums, mellow bass, no vocals"),
        "negative_prompt": "poor quality, distorted, noisy, vocals, singing, lyrics",
        "duration_seconds": int(min(120, seconds + 4)),
        "num_inference_steps": 8,
        "guidance_scale": 1.0,
        "audio_scale": 0.9,
        "sample_solver": "pingpong",
        "seed": -1,
        "output_filename": f"{ep['id']}_music",
    }
    write_queue(f"{ep['id']}_music.json", [task])
    print(f"  {task['duration_seconds']} s. Next: ./run.sh queues/{ep['id']}_music.json music")


def cmd_missing(args):
    ep = load_episode(args.ep)
    find = pick_keyframe if args.kind == "stills" else latest_clip
    shots = [sh for sh in ep["shots"] if not (args.kind == "clips" and sh.get("still_only"))]
    print(" ".join(sh["id"] for sh in shots if not find(ep["id"], sh["id"])))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    k = sub.add_parser("keyframes", help="build the still-image queue")
    k.add_argument("ep")
    k.add_argument("--variants", type=int, default=2, help="candidate stills per shot")
    k.add_argument("--only", nargs="*", help="shot ids, e.g. s03 s07")
    k.set_defaults(fn=cmd_keyframes)

    c = sub.add_parser("clips", help="build the image-to-video queue")
    c.add_argument("ep")
    c.add_argument("--final", action="store_true", help=f"render at {RES['final']} instead of {RES['draft']}")
    c.add_argument("--seconds", type=float, default=4, help="default clip length")
    c.add_argument("--only", nargs="*", help="shot ids, e.g. s03 s07")
    c.add_argument("--profile", choices=["mac", "cloud"], default="mac", help="mac: 5B FastWan 480p; cloud: 14B Lightning 720p")
    c.set_defaults(fn=cmd_clips)

    a = sub.add_parser("assemble", help="stitch clips into renders/<ep>.mp4")
    a.add_argument("ep")
    a.add_argument("--music", help="audio file (default: first file in music/)")
    a.add_argument("--width", type=int, default=1280)
    a.add_argument("--no-grade", dest="grade", action="store_false", help="skip the light denoise")
    a.add_argument("--name-cards", action="store_true", help="show first-appearance name cards (off by default)")
    a.add_argument("--cloud", action="store_true", help="cloud clips: skip colormatch and denoise")
    a.add_argument("--babble", action="store_true", help="mix the animalese dialogue babble over the music")
    a.add_argument("--captions", action="store_true", help="also write renders/<ep>.srt from the dialogue lines")
    a.add_argument("--no-colormatch", dest="colormatch", action="store_false", help="skip matching each clip to its first frame")
    a.add_argument("--dissolve", type=float, default=0.4, help="seconds of dissolve between shots (0 = hard cuts)")
    a.set_defaults(fn=cmd_assemble)

    m = sub.add_parser("animatic", help="rough cut from stills -> renders/<ep>_animatic.mp4")
    m.add_argument("ep")
    m.add_argument("--music", help="audio file (default: first file in music/)")
    m.add_argument("--width", type=int, default=1280)
    m.add_argument("--dissolve", type=float, default=0.4, help="seconds of dissolve between shots (0 = hard cuts)")
    m.add_argument("--seconds", type=float, default=4, help="default shot length")
    m.set_defaults(fn=cmd_animatic)

    mu = sub.add_parser("music", help="queue the episode's background music track")
    mu.add_argument("ep")
    mu.set_defaults(fn=cmd_music)

    x = sub.add_parser("missing", help="print shot ids that have no still / clip yet")
    x.add_argument("ep")
    x.add_argument("kind", choices=["stills", "clips"])
    x.set_defaults(fn=cmd_missing)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
