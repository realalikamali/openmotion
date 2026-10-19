"""Create projects and render reviewable video artifacts with one command."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from .config import load_config


def run(args, **kwargs):
    return subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def probe(path):
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", path,
    ], capture_output=True, text=True)
    return json.loads(result.stdout)


def require_tools():
    missing = [tool for tool in ("ffmpeg", "ffprobe") if not shutil.which(tool)]
    if missing:
        raise ValueError(f"Missing system tools: {', '.join(missing)}. See README installation steps.")


def doctor():
    require_tools()
    from .design import register_font
    print(f"Python: {sys.version.split()[0]}")
    print(f"Manim: {importlib.metadata.version('manim')}")
    print(f"Font: {register_font()} (bundled)")
    result = run(["ffmpeg", "-version"], capture_output=True, text=True)
    print(result.stdout.splitlines()[0])
    print("Ready. Run a preview to verify the complete rendering pipeline.")


def create_project(path, title):
    root = Path(path).expanduser().resolve()
    if root.exists():
        raise ValueError(f"Destination already exists; choose a new directory: {root}")
    templates = Path(__file__).parent / "templates"
    root.mkdir(parents=True)
    for name in ("film.toml", "scene.py", "storyboard.md"):
        shutil.copyfile(templates / name, root / name)
    if title:
        config = root / "film.toml"
        config.write_text(config.read_text().replace(
            'title = "A new perspective"', f"title = {json.dumps(title, ensure_ascii=False)}", 1
        ), encoding="utf-8")
    (root / "assets").mkdir()
    (root / "assets/.gitkeep").touch()
    (root / ".gitignore").write_text(".openmotion/\noutputs/\n__pycache__/\n.env\n", encoding="utf-8")
    print(f"Created {root}\nNext: openmotion render {str(root)!r} --preview")


def render(project, preview=False, music=False, audio=None):
    require_tools()
    film = load_config(project)
    soundtrack = Path(audio).expanduser().resolve() if audio else None
    if soundtrack and not soundtrack.is_file():
        raise ValueError(f"Audio file does not exist: {soundtrack}")
    preset = "preview" if preview else "final"
    fps, resolution = (15, "854,480") if preview else (30, "1920,1080")
    cache = film.root / ".openmotion" / preset
    cache.mkdir(parents=True, exist_ok=True)
    # Isolate artifacts from a failed or older render; Manim owns the cache only.
    media = cache / "media"
    command = [sys.executable, "-m", "manim", "-ql" if preview else "-qh",
               "--fps", fps, "--resolution", resolution, "--format", "mp4",
               "--media_dir", media, "--output_file", "master", film.scene, film.scene_class]
    run(command, cwd=film.root)
    candidates = list((media / "videos").glob(f"{film.scene.stem}/*/master.mp4"))
    if len(candidates) != 1:
        raise ValueError(f"Expected one Manim master, found {len(candidates)} under {media}")
    master = candidates[0]
    metadata = probe(master)
    duration = float(metadata["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Rendered video has no positive finite duration")
    output = film.root / "outputs" / preset
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache, prefix="export-") as temporary:
        stage = Path(temporary)
        ffmpeg = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
        run(ffmpeg + ["-i", master, "-map", "0:v:0", "-c:v", "copy", "-an",
                      "-movflags", "+faststart", stage / "silent.mp4"])
        if music:
            from .score import synthesize
            soundtrack = stage / "score.wav"
            synthesize(soundtrack, duration)
        if soundtrack:
            # Pad short music to the video duration; never truncate the film to the audio.
            run(ffmpeg + ["-i", stage / "silent.mp4", "-i", soundtrack,
                          "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                          "-af", f"apad,afade=t=out:st={max(0, duration-1)}:d=1",
                          "-t", duration, "-c:a", "aac", "-b:a", "192k",
                          "-movflags", "+faststart", stage / "film.mp4"])
        else:
            shutil.copyfile(stage / "silent.mp4", stage / "film.mp4")
        run(ffmpeg + ["-ss", max(0, duration - 1.5), "-i", stage / "film.mp4",
                      "-frames:v", "1", "-update", "1", stage / "poster.png"])
        run(ffmpeg + ["-i", stage / "film.mp4", "-vf",
                      f"fps={12/duration},scale=480:-2,tile=4x3",
                      "-frames:v", "1", "-update", "1", stage / "contact-sheet.jpg"])
        run(["ffmpeg", "-v", "error", "-xerror", "-i", stage / "film.mp4", "-f", "null", "-"])
        final_info = probe(stage / "film.mp4")
        source_hash = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
        manifest = {
            "title": film.title, "preset": preset,
            "python": sys.version.split()[0], "manim": importlib.metadata.version("manim"),
            "scene_sha256": source_hash(film.scene),
            "config_sha256": source_hash(film.config_path),
            "audio": "generated" if music else "supplied" if audio else "none",
            "media": final_info,
        }
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        # Promote only after all exports and decoding pass. Leave unrelated user files alone.
        for artifact in stage.iterdir():
            os.replace(artifact, output / artifact.name)
        if not music:
            (output / "score.wav").unlink(missing_ok=True)
    print(f"Exported {duration:.2f}s to {output}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Portable motion explainers powered by Manim")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor", help="Check render dependencies and the bundled font")
    init = commands.add_parser("new", help="Create a self-contained editable film project")
    init.add_argument("directory")
    init.add_argument("--title")
    rendering = commands.add_parser("render", help="Render, export and verify a film")
    rendering.add_argument("project", help="Project directory containing film.toml")
    rendering.add_argument("--preview", action="store_true", help="480p15 instead of 1080p30")
    sound = rendering.add_mutually_exclusive_group()
    sound.add_argument("--music", action="store_true", help="Add an original generated ambient bed")
    sound.add_argument("--audio", help="Use an existing audio file (relative to the current directory)")
    args = parser.parse_args(argv)
    try:
        if args.command == "doctor":
            doctor()
        elif args.command == "new":
            create_project(args.directory, args.title)
        else:
            render(args.project, args.preview, args.music, args.audio)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f"openmotion: {exc}\n")


if __name__ == "__main__":
    main()
