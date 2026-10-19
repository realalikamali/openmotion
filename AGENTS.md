# Working in OpenMotion

This is a reusable motion toolkit, not a repository for one scientific project.
Read `.agents/skills/openmotion/SKILL.md` when creating or editing a film.

- Keep user films and their private inputs outside tracked toolkit source;
  `projects/` is ignored for convenient local work.
- Do not embed machine-specific paths, credentials, personal repositories, real
  patient records or project-specific claims in package code or examples.
- Use project-local assets and source provenance. Make illustrations and proposed
  behavior distinguishable from measured results and implemented features.
- Preserve the user's brief and existing edits. Use a preview/review loop before
  final export; report what was actually inspected, not an assumed quality pass.
- The bundled font is available through `openmotion.design.text`; reuse primitives
  where helpful without making every film look like the starter.
- Python dependencies are managed by `uv`; update `uv.lock` with dependency changes.
- Run `uv run pytest` after toolkit changes. For changes to rendering/export, run
  `OPENMOTION_RUN_RENDER_TESTS=1 uv run pytest` and inspect resulting frames.
- Creating or rendering a film does not authorize commits, uploads or publication.
