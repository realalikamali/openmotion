"""An optional original ambient bed synthesized without external samples."""
from pathlib import Path
import wave
import numpy as np


def synthesize(path: Path, duration: float) -> None:
    if not 0.1 <= duration <= 600:
        raise ValueError("Generated music supports films from 0.1 to 600 seconds")
    rate = 24000
    audio = np.zeros((int(duration * rate), 2), dtype=np.float32)

    def note(start, length, midi, amplitude, pan, bell=False):
        offset = int(start * rate)
        count = min(int(length * rate), len(audio) - offset)
        if count <= 0:
            return
        t = np.arange(count, dtype=np.float32) / rate
        frequency = 440 * 2 ** ((midi - 69) / 12)
        if bell:
            envelope = (1 - np.exp(-t * 70)) * np.exp(-t * 2.2)
        else:
            envelope = np.minimum(t / 1.2, 1) * np.minimum((length - t) / 1.8, 1)
        signal = (np.sin(2 * np.pi * frequency * t) + 0.22 * np.sin(4 * np.pi * frequency * t))
        signal *= envelope * amplitude
        audio[offset:offset + count, 0] += signal * np.sqrt((1 - pan) / 2)
        audio[offset:offset + count, 1] += signal * np.sqrt((1 + pan) / 2)

    chords = [[50, 57, 61, 64, 69], [47, 54, 57, 62, 66], [43, 50, 54, 57, 62], [45, 52, 57, 59, 64]]
    for bar, start in enumerate(np.arange(0, duration, 7.5)):
        chord = chords[bar % len(chords)]
        for j, midi in enumerate(chord):
            note(start, 9, midi, 0.026, (j - 2) * 0.25)
        for k, index in enumerate([0, 2, 3, 4, 2, 3, 1, 3]):
            note(start + k * 0.9375, 3, chord[index] + 12, 0.03, 0.35 if k % 2 else -0.35, True)
    t = np.arange(len(audio)) / rate
    fade = np.minimum(t / min(2, duration / 3), 1) * np.minimum((duration - t) / min(3, duration / 3), 1)
    audio *= fade[:, None]
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio *= 0.22 / peak
    with wave.open(str(path), "w") as stream:
        stream.setnchannels(2)
        stream.setsampwidth(2)
        stream.setframerate(rate)
        stream.writeframes((audio * 32767).astype("<i2").tobytes())
