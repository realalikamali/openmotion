"""An eight-second render check and editable starting point, not a finished explainer."""
from pathlib import Path
from manim import Scene, VGroup, Dot, FadeIn, Create, LaggedStart, UP
from openmotion.config import load_config
from openmotion.design import text, panel, connector


class Film(Scene):
    def construct(self):
        film = load_config(Path(__file__).with_name("film.toml"))
        self.camera.background_color = film.background
        title = text(film.title, 48, film.foreground, max_width=12).move_to([0, 2.1, 0])
        subtitle = text(film.subtitle, 23, film.accent, max_width=12).move_to([0, 1.25, 0])
        self.play(FadeIn(title, shift=UP * 0.15), FadeIn(subtitle), run_time=1)
        cards = VGroup(*[
            VGroup(panel(3.2, 1.3), text(word, 28, film.foreground)).move_to([x, -0.2, 0])
            for word, x in [("Question", -4.3), ("Evidence", 0), ("Insight", 4.3)]
        ])
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in cards], lag_ratio=0.2), run_time=1.2)
        links = VGroup(*[
            connector([x, -0.2, 0], [x + 1.1, -0.2, 0], film.accent)
            for x in [-2.7, 1.6]
        ])
        self.play(Create(links), run_time=0.8)
        dots = VGroup(*[Dot([x, -0.2, 0], color=film.accent, radius=0.06) for x in [-2.7, 1.6]])
        self.add(dots)
        self.play(*[d.animate.shift([1.1, 0, 0]) for d in dots], run_time=1)
        note = text("Replace this example with your own visual argument.", 20, film.secondary, max_width=12)
        note.move_to([0, -2.1, 0])
        self.play(FadeIn(note), run_time=0.6)
        self.wait(3.4)
