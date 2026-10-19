import json
from pathlib import Path
import subprocess
import sys
import os
import wave

import pytest

from openmotion.cli import create_project, probe
from openmotion.config import load_config
from openmotion.score import synthesize


def test_project_paths_and_existing_work(tmp_path, monkeypatch):
    root = tmp_path / 'film with spaces & quotes'
    title = 'An "unusual" title — with Unicode'
    create_project(root, title)
    monkeypatch.chdir(tmp_path.parent)
    config = load_config(root)
    assert config.title == title
    assert config.scene == root / "scene.py"
    before = config.scene.read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        create_project(root, "Replacement")
    assert config.scene.read_bytes() == before


def test_invalid_palette_is_rejected(tmp_path):
    root = tmp_path / "film"
    create_project(root, None)
    path = root / "film.toml"
    path.write_text(path.read_text().replace('"#67E8C1"', '"mint"'))
    with pytest.raises(ValueError, match="hex color"):
        load_config(root)


def test_generated_audio_duration_and_limits(tmp_path):
    output = tmp_path / "score.wav"
    synthesize(output, 0.7)
    with wave.open(str(output)) as stream:
        assert stream.getnchannels() == 2
        assert stream.getnframes() / stream.getframerate() == pytest.approx(0.7)
    with pytest.raises(ValueError):
        synthesize(output, -1)


@pytest.mark.skipif(os.environ.get("OPENMOTION_RUN_RENDER_TESTS") != "1", reason="opt-in native rendering")
def test_render_from_unrelated_directory_with_short_audio(tmp_path):
    project = tmp_path / "external film with spaces"
    create_project(project, "Portable rendering")
    # Deliberately shorter than the film: the exporter must pad, not truncate video.
    audio = tmp_path / "short music.wav"
    synthesize(audio, 0.5)
    subprocess.run([sys.executable, "-m", "openmotion.cli", "render", str(project),
                    "--preview", "--audio", str(audio)], cwd=tmp_path, check=True)
    outputs = project / "outputs/preview"
    metadata = probe(outputs / "film.mp4")
    video = next(s for s in metadata["streams"] if s["codec_type"] == "video")
    assert (video["width"], video["height"], video["r_frame_rate"]) == (854, 480, "15/1")
    assert float(metadata["format"]["duration"]) >= 7.9
    assert any(s["codec_type"] == "audio" for s in metadata["streams"])
    assert not any(s["codec_type"] == "audio" for s in probe(outputs / "silent.mp4")["streams"])
    for artifact in ["poster.png", "contact-sheet.jpg", "manifest.json"]:
        assert (outputs / artifact).stat().st_size > 0
    manifest = json.loads((outputs / "manifest.json").read_text())
    assert manifest["audio"] == "supplied"
    assert str(tmp_path) not in json.dumps(manifest)
