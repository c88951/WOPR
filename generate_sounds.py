#!/usr/bin/env python3
"""Generate sound effects for WOPR."""

import numpy as np
from scipy.io import wavfile
from pathlib import Path
import os

SAMPLE_RATE = 44100
SOUNDS_DIR = Path(__file__).parent / "wopr" / "assets" / "sounds"


def normalize(audio: np.ndarray, volume: float = 0.8) -> np.ndarray:
    """Normalize audio to specified volume."""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * volume
    return audio


def to_int16(audio: np.ndarray) -> np.ndarray:
    """Convert float audio to int16."""
    return (audio * 32767).astype(np.int16)


def generate_tone(frequency: float, duration: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Generate a pure sine wave tone."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)


def generate_dtmf(digit: str, duration: float = 0.15) -> np.ndarray:
    """Generate DTMF tone for a digit."""
    # DTMF frequency pairs
    dtmf_freqs = {
        '1': (697, 1209), '2': (697, 1336), '3': (697, 1477),
        '4': (770, 1209), '5': (770, 1336), '6': (770, 1477),
        '7': (852, 1209), '8': (852, 1336), '9': (852, 1477),
        '*': (941, 1209), '0': (941, 1336), '#': (941, 1477),
    }
    if digit not in dtmf_freqs:
        return np.zeros(int(SAMPLE_RATE * duration))

    f1, f2 = dtmf_freqs[digit]
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)
    return tone / 2


def apply_envelope(audio: np.ndarray, attack: float = 0.01, decay: float = 0.01) -> np.ndarray:
    """Apply attack/decay envelope to audio."""
    attack_samples = int(SAMPLE_RATE * attack)
    decay_samples = int(SAMPLE_RATE * decay)

    envelope = np.ones(len(audio))
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0:
        envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)

    return audio * envelope


def generate_modem_dial() -> np.ndarray:
    """Generate modem dial sequence - dial tone + DTMF digits."""
    parts = []

    # Dial tone (350 Hz + 440 Hz) for 0.5 seconds
    t = np.linspace(0, 0.5, int(SAMPLE_RATE * 0.5), False)
    dial_tone = (np.sin(2 * np.pi * 350 * t) + np.sin(2 * np.pi * 440 * t)) / 2
    parts.append(dial_tone)

    # Brief silence
    parts.append(np.zeros(int(SAMPLE_RATE * 0.1)))

    # Dial a phone number (like in the movie: 311-767-1200 area)
    phone_number = "3117671200"
    for digit in phone_number:
        tone = generate_dtmf(digit, 0.12)
        tone = apply_envelope(tone, 0.005, 0.005)
        parts.append(tone)
        parts.append(np.zeros(int(SAMPLE_RATE * 0.08)))  # Gap between digits

    # Ringing tone (440 Hz + 480 Hz, 2 seconds on, 4 seconds off pattern - just do one ring)
    t = np.linspace(0, 0.8, int(SAMPLE_RATE * 0.8), False)
    ring = (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)) / 2
    ring = apply_envelope(ring, 0.05, 0.05)
    parts.append(np.zeros(int(SAMPLE_RATE * 0.3)))
    parts.append(ring)
    parts.append(np.zeros(int(SAMPLE_RATE * 0.5)))
    parts.append(ring)

    return normalize(np.concatenate(parts))


def generate_modem_connect() -> np.ndarray:
    """Generate modem handshake screech."""
    duration = 2.5
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Carrier tone (around 1200-2400 Hz typical for modems)
    carrier = np.sin(2 * np.pi * 1200 * t)

    # Frequency sweep for handshake
    sweep_freq = 1200 + 1200 * np.sin(2 * np.pi * 3 * t)  # Oscillating frequency
    sweep = np.sin(2 * np.pi * np.cumsum(sweep_freq) / SAMPLE_RATE)

    # Add some noise for that classic modem sound
    noise = np.random.randn(len(t)) * 0.15

    # High frequency components
    high_freq = np.sin(2 * np.pi * 2100 * t) * 0.3  # Answer tone

    # FSK-like modulation
    fsk = np.sin(2 * np.pi * (1200 + 200 * np.sign(np.sin(2 * np.pi * 150 * t))) * t)

    # Mix components with time-varying weights
    mix = np.zeros_like(t)

    # Initial answer tone
    mask1 = t < 0.5
    mix[mask1] = high_freq[mask1]

    # Handshake negotiation
    mask2 = (t >= 0.5) & (t < 1.5)
    mix[mask2] = (sweep[mask2] * 0.5 + fsk[mask2] * 0.3 + noise[mask2])

    # Final carrier establishment
    mask3 = t >= 1.5
    mix[mask3] = (carrier[mask3] * 0.4 + fsk[mask3] * 0.4 + noise[mask3] * 0.5)

    return normalize(apply_envelope(mix, 0.01, 0.1), 0.7)


def generate_terminal_beep() -> np.ndarray:
    """Generate a soft terminal beep."""
    duration = 0.1
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Classic terminal beep around 800-1000 Hz
    tone = np.sin(2 * np.pi * 880 * t)

    # Soft envelope
    envelope = np.exp(-t * 30)  # Exponential decay

    return normalize(tone * envelope, 0.5)


def generate_missile_launch() -> np.ndarray:
    """Generate missile launch whoosh + rumble."""
    duration = 1.2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Low frequency rumble
    rumble = np.sin(2 * np.pi * 60 * t) + np.sin(2 * np.pi * 80 * t) * 0.5

    # Whoosh - rising frequency with noise
    whoosh_freq = 200 + 800 * (t / duration) ** 0.5  # Rising frequency
    whoosh = np.sin(2 * np.pi * np.cumsum(whoosh_freq) / SAMPLE_RATE)

    # Filtered noise for jet/rocket sound
    noise = np.random.randn(len(t))
    # Simple low-pass effect by averaging
    noise_filtered = np.convolve(noise, np.ones(100)/100, mode='same')

    # Combine with envelope
    envelope = np.ones_like(t)
    envelope[:int(SAMPLE_RATE * 0.1)] = np.linspace(0, 1, int(SAMPLE_RATE * 0.1))
    envelope[int(SAMPLE_RATE * 0.8):] = np.linspace(1, 0.3, len(envelope[int(SAMPLE_RATE * 0.8):]))

    mix = (rumble * 0.4 + whoosh * 0.3 + noise_filtered * 0.5) * envelope

    return normalize(mix, 0.75)


def generate_explosion() -> np.ndarray:
    """Generate a deep boom explosion."""
    duration = 0.8
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Initial transient - sharp attack
    transient = np.random.randn(int(SAMPLE_RATE * 0.05))
    transient = transient * np.exp(-np.linspace(0, 10, len(transient)))

    # Low frequency boom
    boom_freq = 80 * np.exp(-t * 3)  # Decaying frequency
    boom = np.sin(2 * np.pi * np.cumsum(boom_freq) / SAMPLE_RATE)

    # Sub bass
    sub = np.sin(2 * np.pi * 40 * t)

    # Rumble noise
    noise = np.random.randn(len(t))
    noise_filtered = np.convolve(noise, np.ones(200)/200, mode='same')

    # Decay envelope
    envelope = np.exp(-t * 4)

    # Combine
    mix = np.zeros(len(t))
    mix[:len(transient)] = transient * 2
    mix += (boom * 0.5 + sub * 0.3 + noise_filtered * 0.3) * envelope

    return normalize(mix, 0.8)


def generate_typing() -> np.ndarray:
    """Generate a terminal keystroke click."""
    duration = 0.05
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)

    # Sharp click - multiple high frequency components
    click = (
        np.sin(2 * np.pi * 4000 * t) * 0.3 +
        np.sin(2 * np.pi * 2500 * t) * 0.3 +
        np.random.randn(len(t)) * 0.2
    )

    # Very fast decay
    envelope = np.exp(-t * 150)

    return normalize(click * envelope, 0.4)


def main():
    """Generate all sound files."""
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

    sounds = [
        ("modem_dial.wav", generate_modem_dial, "Modem dial sequence"),
        ("modem_connect.wav", generate_modem_connect, "Modem handshake"),
        ("terminal_beep.wav", generate_terminal_beep, "Terminal beep"),
        ("missile_launch.wav", generate_missile_launch, "Missile launch"),
        ("explosion.wav", generate_explosion, "Explosion"),
        ("typing.wav", generate_typing, "Keystroke"),
    ]

    for filename, generator, description in sounds:
        print(f"Generating {description}... ", end="", flush=True)
        audio = generator()
        audio_int16 = to_int16(audio)
        filepath = SOUNDS_DIR / filename
        wavfile.write(str(filepath), SAMPLE_RATE, audio_int16)
        print(f"OK ({filepath})")

    print(f"\nAll sound files generated in {SOUNDS_DIR}")


if __name__ == "__main__":
    main()
