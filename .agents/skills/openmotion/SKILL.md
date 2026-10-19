---
name: openmotion
description: Create and revise code-driven motion explainers with the OpenMotion Manim toolkit, including storyboards, animated diagrams, preview review, and final video exports. Use for a rendered film or animation, not a static illustration or slide deck.
---

# OpenMotion workflow

Start with the user's sources and intended audience. Infer reasonable defaults
from the conversation: a short landscape film, readable without narration, is
often a useful starting point. Ask only for missing choices that materially
affect the story. Separate verified claims from schematic examples and plans.

## Compose before rendering

Write the central visual thesis and a scene plan in the film's `storyboard.md`.
Each scene should show a specific change or relationship. Describe the mechanism
of the motion, the on-screen copy and the reading hold. Choose visual metaphors
from the subject: anchoring and look-back for chronology, splitting and re-routing
for changing scope, or linked views for data representations. A succession of
boxes is not automatically an explanation.

Use `uv run openmotion new projects/<name> --title "..."` from the toolkit
checkout, or target an external folder. The generic example is only a setup
check. Replace it with a deliberate narrative. Keep assets beside the film and
resolve paths from the scene file; do not introduce dependencies on personal
filesystem layouts. Use approved aggregate or synthetic material when real
records are unnecessary.

## Animate and inspect

Use `openmotion.design` primitives when helpful; the bundled font travels with
the package. Keep generous margins, consistent color meanings and legible labels.
Carry important objects across transitions when it clarifies the explanation.
Show structural changes rather than adding motion merely for decoration.

For open curves, use `set_stroke(opacity=...)` to dim lines; `set_opacity(...)`
can also change fill opacity and create unwanted filled regions.

Render with `uv run openmotion render <project> --preview`. Inspect the generated
contact sheet and frames at dense or transitional moments, and assess timing in
the video when playback is available. Correct clipping, ambiguous connectors,
unsupported claims and rushed holds. Do not imply an audio audition or full
playback if only still frames and technical metadata were inspected.

## Deliver

Render with `uv run openmotion render <project>` for 1080p30. Add `--music` only
when a generated instrumental bed suits the brief, or `--audio <file>` for an
authorized supplied track. The exporter produces the film, silent master,
poster, contact sheet and manifest and checks decoding. Review visual output
again after substantive changes; a successful render alone is not quality assurance.

Link the finished film and relevant alternate outputs. Briefly state what changed,
what was verified and any material limitation. Preserve prior versions when
revising a film the user may want to compare. Publishing or pushing requires
authorization separate from the creative brief.
