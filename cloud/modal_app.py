"""Run WanGP queues on a Modal H100. The look is pinned: same WanGP commit, same model files, same settings.

    modal run cloud/modal_app.py::main --queue queues/test.json --job test1      # upload, render, download
    modal run --detach cloud/modal_app.py::main --queue ... --job ... --no-wait    # render in the background
    modal run cloud/modal_app.py::check                                            # verify GPU + install (~1 min)
    modal run cloud/modal_app.py::fetch --job test1                                # download a finished job

Inputs (stills referenced by "image_start") are uploaded with the queue; outputs come back to cloud_out/<job>/.
Models live on the "corgi-models" volume, so they download once and are reused by every job.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

import modal

WANGP_REPO = "https://github.com/deepbeepmeep/Wan2GP.git"
WANGP_COMMIT = "fdc63bdf89358fb13c93cf6b38693fd89a859f00"  # same version as the Mac (minus the Mac-only patch)
WANGP = "/opt/Wan2GP"
GPU = "H100"

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libgl1", "libglib2.0-0", "libsndfile1", "portaudio19-dev", "build-essential")
    .pip_install("torch==2.10.0", "torchvision==0.25.0", "torchaudio==2.10.0",
                 index_url="https://download.pytorch.org/whl/cu128")
    .run_commands(
        f"git clone {WANGP_REPO} {WANGP} && cd {WANGP} && git checkout {WANGP_COMMIT}",
        f"cd {WANGP} && pip install -r requirements.txt",
    )
)

app = modal.App("corgi-town", image=image)
models = modal.Volume.from_name("corgi-models", create_if_missing=True)
work = modal.Volume.from_name("corgi-work", create_if_missing=True)


@app.function(gpu=GPU, timeout=6 * 3600, memory=131072, cpu=8,
              volumes={"/models": models, "/work": work})
def render(job: str):
    """Run one uploaded queue. Model downloads land on the models volume and persist."""
    for name in ("ckpts", "loras"):
        target = pathlib.Path("/models") / name
        target.mkdir(parents=True, exist_ok=True)
        link = pathlib.Path(WANGP) / name
        if link.is_symlink() or not link.exists():
            if link.is_symlink():
                link.unlink()
            link.symlink_to(target)
        else:  # repo ships a loras/ folder: merge it in once, then link
            subprocess.run(f"cp -rn {link}/. {target}/ && rm -rf {link}", shell=True, check=True)
            link.symlink_to(target)

    work.reload()
    jobdir = pathlib.Path("/work/jobs") / job
    out = jobdir / "out"
    out.mkdir(parents=True, exist_ok=True)
    log = open(jobdir / "render.log", "a")
    t0 = time.time()
    proc = subprocess.Popen([sys.executable, "wgp.py", "--process", str(jobdir / "queue.json"),
                             "--output-dir", str(out)], cwd=WANGP,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    last_commit = time.time()
    for line in proc.stdout:
        print(line, end="")
        log.write(line)
        if time.time() - last_commit > 60:  # make progress and finished clips visible from outside
            log.flush()
            work.commit()
            models.commit()
            last_commit = time.time()
    code = proc.wait()
    log.write(f"\n[exit {code} after {time.time() - t0:.0f}s]\n")
    log.close()
    work.commit()
    models.commit()
    return {"exit": code, "seconds": round(time.time() - t0), "outputs": sorted(p.name for p in out.iterdir())}


@app.function(gpu=GPU, timeout=600)
def gpu_check():
    import torch
    out = {"torch": str(torch.__version__), "cuda": str(torch.version.cuda), "available": bool(torch.cuda.is_available())}
    if out["available"]:
        out["gpu"] = torch.cuda.get_device_name(0)
        out["vram_gb"] = round(torch.cuda.get_device_properties(0).total_memory / 1e9)
    r = subprocess.run([sys.executable, "wgp.py", "--help"], cwd=WANGP, capture_output=True, text=True, timeout=300,
                       input="")
    out["wgp_startup"] = "ok" if r.returncode == 0 else (r.stderr or r.stdout)[-1500:]
    return out


def _upload(queue_path: str, job: str):
    tasks = json.load(open(queue_path))
    inputs = {}
    for t in tasks:
        for key in ("image_start", "image_end", "image_refs"):
            vals = t.get(key)
            if not vals:
                continue
            vals = vals if isinstance(vals, list) else [vals]
            remote = []
            for v in vals:
                name = f"{len(inputs):03d}_{os.path.basename(v)}"
                inputs[name] = v
                remote.append(f"/work/jobs/{job}/inputs/{name}")
            t[key] = remote
    with work.batch_upload(force=True) as batch:
        for name, local in inputs.items():
            batch.put_file(local, f"/jobs/{job}/inputs/{name}")
        tmp = pathlib.Path(f"/tmp/{job}_queue.json")
        tmp.write_text(json.dumps(tasks, indent=2))
        batch.put_file(str(tmp), f"/jobs/{job}/queue.json")
    print(f"uploaded {len(tasks)} tasks and {len(inputs)} input files for job {job}")


def _download(job: str, dest_root="cloud_out"):
    dest = pathlib.Path(dest_root) / job
    dest.mkdir(parents=True, exist_ok=True)
    got = 0
    for entry in work.listdir(f"/jobs/{job}/out"):
        name = os.path.basename(entry.path)
        with open(dest / name, "wb") as f:
            for chunk in work.read_file(entry.path):
                f.write(chunk)
        got += 1
    with open(dest / "render.log", "wb") as f:
        for chunk in work.read_file(f"/jobs/{job}/render.log"):
            f.write(chunk)
    print(f"downloaded {got} files to {dest}")


@app.local_entrypoint()
def main(queue: str, job: str, wait: bool = True):
    _upload(queue, job)
    if wait:
        print(render.remote(job))
        _download(job)
    else:
        call = render.spawn(job)
        print(f"started job {job} (call {call.object_id}); fetch later with: modal run cloud/modal_app.py::fetch --job {job}")


@app.local_entrypoint()
def check():
    print(gpu_check.remote())


@app.local_entrypoint()
def fetch(job: str):
    _download(job)
