"""Project configuration, resolved relative to the project rather than the shell."""

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib


@dataclass(frozen=True)
class FilmConfig:
    root: Path
    config_path: Path
    title: str
    subtitle: str
    scene: Path
    scene_class: str
    background: str
    foreground: str
    accent: str
    secondary: str


def load_config(project: str | Path) -> FilmConfig:
    path = Path(project).expanduser().resolve()
    if path.is_dir():
        path /= "film.toml"
    with path.open("rb") as stream:
        raw = tomllib.load(stream)
    film = raw.get("film", {})
    style = raw.get("style", {})
    title = film.get("title", "A new perspective")
    subtitle = film.get("subtitle", "Turn a complex idea into a clear visual story.")
    scene_class = film.get("scene_class", "Film")
    scene_name = film.get("scene", "scene.py")
    if not all(isinstance(v, str) and v.strip() for v in (title, subtitle, scene_class, scene_name)):
        raise ValueError("film title, subtitle, scene and scene_class must be nonempty strings")
    if not scene_class.isidentifier():
        raise ValueError("scene_class must be a Python identifier")
    scene = (path.parent / scene_name).resolve()
    if not scene.is_file():
        raise ValueError(f"Scene file does not exist: {scene}")
    colors = {}
    for name, default in {
        "background": "#0B1320", "foreground": "#F4F1E9",
        "accent": "#67E8C1", "secondary": "#9AA8FF",
    }.items():
        value = style.get(name, default)
        if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"style.{name} must be a six-digit hex color")
        colors[name] = value
    return FilmConfig(path.parent, path, title, subtitle, scene, scene_class, **colors)
