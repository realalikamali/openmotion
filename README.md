# OpenMotion

Create editable motion explainers with Python, Manim and an AI coding assistant.
OpenMotion packages a repeatable **brief → storyboard → preview → review → final
export** workflow. It can be used for scientific methods, products, algorithms,
or other ideas; no particular research project or source repository is required.

The assistant writes and revises the animation. Manim renders the frames.
FFmpeg assembles the deliverables. You can also edit and render everything
without an AI assistant or API key.

## Set up a computer

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and the native
dependencies below. Python 3.12 is selected by `.python-version`; `uv` can download
it automatically. Manim 0.22.0 and its Python dependencies are pinned in `uv.lock`.

### macOS

With [Homebrew](https://brew.sh) installed:

```sh
brew install uv ffmpeg cairo pango pkg-config
git clone https://github.com/realalikamali/openmotion.git
cd openmotion
uv sync --locked
uv run openmotion doctor
```

### Ubuntu / Debian

Install `uv` using its official instructions, then:

```sh
sudo apt-get update
sudo apt-get install -y ffmpeg build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev
git clone https://github.com/realalikamali/openmotion.git
cd openmotion
uv sync --locked
uv run openmotion doctor
```

### Windows

Install `uv` and FFmpeg (including `ffprobe`) and put them on `PATH`. Run the same
`git clone`, `uv sync --locked`, and `uv run openmotion doctor` commands in
PowerShell. If a native dependency needs compilation, follow the Windows section
of the [Manim installation guide](https://docs.manim.community/en/stable/installation/uv.html).
The CLI uses Python subprocesses rather than shell scripts, so rendering does not
require Bash. Windows is not yet covered by automated render tests.

No LaTeX installation is needed for the starter. Install it separately if your
own scenes use `Tex` or `MathTex`.

## Make a film

From the OpenMotion checkout:

```sh
uv run openmotion new projects/my-film --title "My new idea"
uv run openmotion render projects/my-film --preview
```

This creates an eight-second generic example to check the setup. It is a starting
point, not a finished explainer. Edit the generated files with your assistant:

```text
projects/my-film/
  film.toml       # Title, scene class and palette
  storyboard.md   # Audience, sources, visual argument and scene plan
  scene.py        # Editable Manim animation
  assets/         # Approved images, aggregate data and other local inputs
  .openmotion/    # Render cache (ignored)
  outputs/        # Deliverables (ignored)
```

Use absolute or relative project paths, including paths outside this checkout.
Resolve source assets relative to `__file__`, not the terminal's working directory.
Keep scientific facts in project-local inputs with provenance; the toolkit does
not fetch manuscript files or depend on sibling repositories.

Render the final version with an optional original ambient soundtrack:

```sh
uv run openmotion render projects/my-film --music
```

Or supply your own audio, or omit both flags for silent output:

```sh
uv run openmotion render projects/my-film --audio /path/to/music.wav
```

`--music` and `--audio` are mutually exclusive. Supplied audio is padded or trimmed
to the film duration and faded at the end; adjust its mix level before importing.
Generated music supports films up to 10 minutes. These commands do not generate narration.

## Outputs and review

Preview renders use **854×480 at 15fps**; final renders use **1920×1080 at 30fps**.
Each writes into its own `outputs/preview/` or `outputs/final/` folder:

| File | Purpose |
| --- | --- |
| `film.mp4` | H.264 MP4, with AAC audio when selected |
| `silent.mp4` | Video-only presentation master |
| `poster.png` | Frame near the end; replace with a chosen poster if needed |
| `contact-sheet.jpg` | Twelve sampled frames for visual review |
| `manifest.json` | Render settings, source hashes and media metadata |
| `score.wav` | Original generated score when `--music` is selected |

The exporter verifies decoding before replacing the named deliverables. Repeated
renders overwrite those deliverables, so copy versions you want to preserve.
Native graphics libraries and video encoders can vary between computers; the
lockfile and bundled font improve consistency, but do not promise byte-identical video.

Inspect the contact sheet **and watch the video**. Sampling cannot catch every
collision, transition, pacing or audio problem. Technical checks do not verify
scientific claims or guarantee good design.

## Work with Codex or Cursor

Open this repository in your coding assistant. `AGENTS.md` describes the working
conventions. An original, self-contained skill lives at
`.agents/skills/openmotion/SKILL.md`; Codex discovers this repository-scoped skill.
In another editor, explicitly ask it to read that file if it does not discover it.

Example request:

> Use the OpenMotion workflow to create a 60–90 second explainer for the sources
> I provide. First establish the central visual idea and storyboard. Build a
> preview, inspect the frames, revise the animation, and export 1080p video,
> a silent master and a poster. Keep measured findings distinct from examples
> and future plans. Put this film in projects/my-film.

The skill is written for this package; it does not require downloading or
redistributing any third-party skill collections. You may additionally install
your preferred Manim skills.

## Portability and source control

- Clone the toolkit on each computer and run `uv sync --locked`; do not copy `.venv`.
- The bundled **Atkinson Hyperlegible** font removes dependence on proprietary
  system fonts. Its SIL Open Font License is included under `src/openmotion/assets/fonts/`.
- `projects/`, outputs and caches are ignored in this toolkit repository. Keep each
  film's source in a separate repository or transfer it as a folder. The generated
  `.gitignore` excludes only caches, outputs and `.env`; review source assets before sharing.
- Copy the film's `film.toml`, `scene.py`, storyboard and assets to move it. Keep
  the toolkit commit used for the render with your project notes.
- A package wheel can also be installed in a Python 3.12 environment with `uv pip
  install path/to/openmotion-*.whl`. Native dependencies are still required, and
  repository-level skills/instructions travel with the checkout, not the wheel.

## Development

```sh
uv sync --locked
uv run pytest
OPENMOTION_RUN_RENDER_TESTS=1 uv run pytest
uv build
```

The opt-in render test builds a film from an unrelated directory containing
spaces and checks video/audio dimensions, duration and output artifacts.
Linux CI runs it automatically. For PowerShell, set
`$env:OPENMOTION_RUN_RENDER_TESTS="1"` before `uv run pytest`.

The bundled font is sourced from the [Google Fonts collection](https://github.com/google/fonts/tree/main/ofl/atkinsonhyperlegible)
and retains its SIL Open Font License. Dependency licenses remain with their respective projects.
