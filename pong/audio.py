"""
Procedural sound manager for PongWithIssues.

Generates all game sounds at init time using numpy — no external audio files needed.
Works on desktop (Pygame) and web (Pygbag/WebAssembly) with OGG-compatible output.
Falls back silently if audio initialization fails.
"""

import sys
import numpy as np

try:
    import pygame
except ImportError:
    pygame = None

SAMPLE_RATE = 44100
IS_WEB = sys.platform == "emscripten"


# ---------------------------------------------------------------------------
# Waveform primitives
# ---------------------------------------------------------------------------

def _sine_wave(freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a sine wave. Returns float64 array in [-1.0, 1.0]."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def _square_wave(freq, duration, sample_rate=SAMPLE_RATE):
    """Generate a square wave. Returns float64 array in [-1.0, 1.0]."""
    return np.sign(_sine_wave(freq, duration, sample_rate))


def _noise(duration, sample_rate=SAMPLE_RATE):
    """Generate white noise. Returns float64 array in [-1.0, 1.0]."""
    return np.random.uniform(-1.0, 1.0, int(sample_rate * duration))


# ---------------------------------------------------------------------------
# Envelope helpers
# ---------------------------------------------------------------------------

def _envelope(samples, attack=0.01, decay=0.1):
    """Apply an attack-decay envelope to samples."""
    n = len(samples)
    env = np.ones(n, dtype=np.float64)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)

    if attack_samples > 0:
        attack_samples = min(attack_samples, n)
        env[:attack_samples] = np.linspace(0.0, 1.0, attack_samples)

    if decay_samples > 0:
        decay_start = max(n - decay_samples, attack_samples)
        length = n - decay_start
        if length > 0:
            env[decay_start:] = np.linspace(1.0, 0.0, length)

    return samples * env


def _fade_out(samples, fade_duration=0.05):
    """Apply a fade-out to the tail of the samples."""
    fade_samples = int(fade_duration * SAMPLE_RATE)
    fade_samples = min(fade_samples, len(samples))
    if fade_samples > 0:
        fade = np.linspace(1.0, 0.0, fade_samples)
        samples = samples.copy()
        samples[-fade_samples:] *= fade
    return samples


# ---------------------------------------------------------------------------
# Numpy array -> pygame.mixer.Sound
# ---------------------------------------------------------------------------

def _generate_sound(samples, sample_rate=SAMPLE_RATE):
    """Convert a float64 mono numpy array to a pygame.mixer.Sound (stereo 16-bit)."""
    # Clip to [-1, 1] and convert to int16
    samples = np.clip(samples, -1.0, 1.0)
    int_samples = (samples * 32767).astype(np.int16)

    # Pygame mixer expects stereo (N, 2) for make_sound
    stereo = np.column_stack((int_samples, int_samples))

    return pygame.sndarray.make_sound(stereo)


# ---------------------------------------------------------------------------
# Sound generation recipes
# ---------------------------------------------------------------------------

def _make_paddle_hit():
    """Classic Pong paddle hit — short 480Hz sine beep, punchy and clean."""
    duration = 0.06
    wave = _sine_wave(480, duration)
    wave = _envelope(wave, attack=0.001, decay=0.05)
    return _generate_sound(wave * 0.8)


def _make_wall_bounce():
    """Classic Pong wall bounce — shorter, lower-pitched beep than paddle hit."""
    duration = 0.04
    wave = _sine_wave(320, duration)
    wave = _envelope(wave, attack=0.001, decay=0.03)
    return _generate_sound(wave * 0.6)


def _make_score():
    """Dramatic upward sweep — 300ms, sine from 300Hz to 800Hz."""
    duration = 0.3
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = np.linspace(300, 800, n)
    wave = np.sin(2 * np.pi * freq * t)
    wave = _envelope(wave, attack=0.01, decay=0.15)
    return _generate_sound(wave * 0.7)


def _make_win():
    """Triumphant jingle — three ascending notes: C5, E5, G5 (each ~150ms)."""
    notes = [523.25, 659.25, 783.99]  # C5, E5, G5
    parts = []
    for freq in notes:
        note = _sine_wave(freq, 0.15)
        note = _envelope(note, attack=0.005, decay=0.08)
        parts.append(note)
    # Small gap between notes (10ms silence)
    gap = np.zeros(int(SAMPLE_RATE * 0.01))
    combined = np.concatenate([parts[0], gap, parts[1], gap, parts[2]])
    return _generate_sound(combined * 0.7)


def _make_lose():
    """Sad descending — three descending notes: G4, E4, C4."""
    notes = [392.00, 329.63, 261.63]  # G4, E4, C4
    parts = []
    for freq in notes:
        note = _sine_wave(freq, 0.12)
        note = _envelope(note, attack=0.005, decay=0.07)
        parts.append(note)
    gap = np.zeros(int(SAMPLE_RATE * 0.01))
    combined = np.concatenate([parts[0], gap, parts[1], gap, parts[2]])
    return _generate_sound(combined * 0.6)


def _make_powerup_collect():
    """Sparkle — 200ms, high-freq shimmer with vibrato."""
    duration = 0.2
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Frequency sweep 1000 -> 2000 Hz with vibrato
    freq = np.linspace(1000, 2000, n) + 80 * np.sin(2 * np.pi * 30 * t)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    wave = _envelope(wave, attack=0.005, decay=0.12)
    return _generate_sound(wave * 0.5)


def _make_powerup_activate():
    """Whoosh — 250ms, noise with bandpass sweep low to high."""
    duration = 0.25
    n = int(SAMPLE_RATE * duration)
    raw = _noise(duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Simulate bandpass sweep by multiplying noise with a moving sine
    center_freq = np.linspace(200, 3000, n)
    bandpass = np.sin(2 * np.pi * np.cumsum(center_freq) / SAMPLE_RATE)
    wave = raw * np.abs(bandpass)
    wave = _envelope(wave, attack=0.01, decay=0.15)
    return _generate_sound(wave * 0.5)


def _make_powerup_expire():
    """Tick-tick — two short 800Hz clicks, 150ms total."""
    click_dur = 0.025
    gap_dur = 0.05
    click = _sine_wave(800, click_dur)
    click = _envelope(click, attack=0.002, decay=0.02)
    gap = np.zeros(int(SAMPLE_RATE * gap_dur))
    combined = np.concatenate([click, gap, click])
    # Pad to roughly 150ms
    target_len = int(SAMPLE_RATE * 0.15)
    if len(combined) < target_len:
        combined = np.concatenate([combined, np.zeros(target_len - len(combined))])
    return _generate_sound(combined * 0.5)


def _make_freeze():
    """Ice crack — 200ms, white noise burst with fast high-freq decay."""
    duration = 0.2
    n = int(SAMPLE_RATE * duration)
    raw = _noise(duration)
    # Emphasize high frequencies at the start, decay quickly
    t = np.linspace(0, duration, n, endpoint=False)
    hf = np.sin(2 * np.pi * 4000 * t)
    wave = (raw * 0.5 + hf * 0.5) * np.exp(-t * 20)
    wave = _envelope(wave, attack=0.001, decay=0.05)
    return _generate_sound(wave * 0.6)


def _make_countdown_tick():
    """Short beep for 3-2-1 countdown — 100ms, 600Hz sine."""
    wave = _sine_wave(600, 0.1)
    wave = _envelope(wave, attack=0.005, decay=0.06)
    return _generate_sound(wave * 0.5)


def _make_cursed_event():
    """Dramatic alarm/whoosh for cursed events — 400ms descending noise sweep."""
    duration = 0.4
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Descending frequency sweep with noise
    freq = np.linspace(2000, 200, n)
    sweep = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    noise = np.random.uniform(-0.3, 0.3, n)
    wave = sweep * 0.6 + noise * 0.4
    wave = _envelope(wave, attack=0.005, decay=0.2)
    return _generate_sound(wave * 0.6)


def _make_countdown_go():
    """Higher beep for GO — 150ms, 900Hz sine."""
    wave = _sine_wave(900, 0.15)
    wave = _envelope(wave, attack=0.005, decay=0.08)
    return _generate_sound(wave * 0.6)


def _make_force_push():
    """Deep bass whomp — 300ms, sine sweep 120->40Hz + noise burst."""
    duration = 0.3
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = np.linspace(120, 40, n)
    sweep = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    burst = _noise(duration) * np.exp(-t * 12)
    wave = sweep * 0.7 + burst * 0.3
    wave = _envelope(wave, attack=0.005, decay=0.15)
    return _generate_sound(wave * 0.7)


def _make_force_pull():
    """Rising suction whoosh — 350ms, sine sweep 60->300Hz + filtered noise."""
    duration = 0.35
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = np.linspace(60, 300, n)
    sweep = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    raw = _noise(duration)
    # Simple filter: multiply noise by rising sine for bandpass effect
    filt = np.sin(2 * np.pi * np.cumsum(np.linspace(100, 600, n)) / SAMPLE_RATE)
    filtered = raw * np.abs(filt)
    wave = sweep * 0.6 + filtered * 0.4
    wave = _envelope(wave, attack=0.01, decay=0.2)
    return _generate_sound(wave * 0.6)


def _make_lightsaber_clash():
    """Electric clash — 150ms, square wave 800Hz + sine 2400Hz + noise decay."""
    duration = 0.15
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    sq = _square_wave(800, duration)
    hi = _sine_wave(2400, duration)
    nz = _noise(duration) * np.exp(-t * 30)
    wave = sq * 0.3 + hi * 0.3 + nz * 0.4
    wave = _envelope(wave, attack=0.001, decay=0.1)
    return _generate_sound(wave * 0.6)


def _make_lightsaber_ignite():
    """Rising hum 80->220Hz, 0.5s — saber powering up."""
    duration = 0.5
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = np.linspace(80, 220, n)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    # Add slight buzz overtone
    wave += 0.2 * np.sin(2 * np.pi * np.cumsum(freq * 2.5) / SAMPLE_RATE)
    wave = _envelope(wave, attack=0.02, decay=0.1)
    return _generate_sound(wave * 0.6)


def _make_lightsaber_sheathe():
    """Descending hum 220->70Hz, 0.4s — saber powering down."""
    duration = 0.4
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    freq = np.linspace(220, 70, n)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / SAMPLE_RATE)
    wave += 0.15 * np.sin(2 * np.pi * np.cumsum(freq * 2.5) / SAMPLE_RATE)
    wave = _envelope(wave, attack=0.005, decay=0.2)
    return _generate_sound(wave * 0.5)


def _make_lightning_strike():
    """Electric crack + hiss + rumble, 0.65s — lightning bolt kill move."""
    duration = 0.65
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    # Initial crack: short noise burst
    crack = _noise(duration) * np.exp(-t * 25)
    # Electric hiss: high-freq sine with random modulation
    hiss_freq = 3000 + 1500 * np.sin(2 * np.pi * 40 * t)
    hiss = np.sin(2 * np.pi * np.cumsum(hiss_freq) / SAMPLE_RATE) * np.exp(-t * 6)
    # Low rumble
    rumble = _sine_wave(50, duration) * np.exp(-t * 3)
    wave = crack * 0.4 + hiss * 0.3 + rumble * 0.3
    wave = _envelope(wave, attack=0.001, decay=0.3)
    return _generate_sound(wave * 0.7)


# ---------------------------------------------------------------------------
# SoundManager class
# ---------------------------------------------------------------------------

class SoundManager:
    """Manages all game sounds with volume control and graceful fallback."""

    def __init__(self):
        self._sounds = {}
        self._available = False
        self.master_volume = 0.7
        self.sfx_volume = 1.0
        self.music_volume = 0.5

        if pygame is None:
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512)
            self._available = True
        except Exception:
            # Audio init can fail in some web environments or headless setups
            self._available = False
            return

        # Generate all sounds
        generators = {
            "paddle_hit": _make_paddle_hit,
            "wall_bounce": _make_wall_bounce,
            "score": _make_score,
            "win": _make_win,
            "lose": _make_lose,
            "powerup_collect": _make_powerup_collect,
            "powerup_activate": _make_powerup_activate,
            "powerup_expire": _make_powerup_expire,
            "freeze": _make_freeze,
            "countdown_tick": _make_countdown_tick,
            "countdown_go": _make_countdown_go,
            "cursed_event": _make_cursed_event,
            "force_push": _make_force_push,
            "force_pull": _make_force_pull,
            "lightsaber_clash": _make_lightsaber_clash,
            "lightsaber_ignite": _make_lightsaber_ignite,
            "lightsaber_sheathe": _make_lightsaber_sheathe,
            "lightning_strike": _make_lightning_strike,
        }

        for name, gen_func in generators.items():
            try:
                self._sounds[name] = gen_func()
            except Exception:
                # If a single sound fails to generate, skip it silently
                pass

    @property
    def available(self):
        """True if audio is working."""
        return self._available

    def play(self, sound_name):
        """Play a named sound effect. No-op if audio unavailable or sound unknown."""
        if not self._available:
            return
        sound = self._sounds.get(sound_name)
        if sound is None:
            return
        try:
            effective_volume = self.master_volume * self.sfx_volume
            sound.set_volume(max(0.0, min(1.0, effective_volume)))
            sound.play()
        except Exception:
            pass

    def set_volume(self, master=None, sfx=None, music=None):
        """Update volume levels. Pass None to leave a level unchanged."""
        if master is not None:
            self.master_volume = max(0.0, min(1.0, float(master)))
        if sfx is not None:
            self.sfx_volume = max(0.0, min(1.0, float(sfx)))
        if music is not None:
            self.music_volume = max(0.0, min(1.0, float(music)))


# ---------------------------------------------------------------------------
# Module-level convenience API
# ---------------------------------------------------------------------------

_manager = None


def init():
    """Initialize the global SoundManager singleton. Safe to call multiple times."""
    global _manager
    if _manager is None:
        _manager = SoundManager()
    return _manager


def play(name):
    """Play a named sound. No-op if not initialized or sound unavailable."""
    if _manager is not None:
        _manager.play(name)


def set_volume(master=None, sfx=None, music=None):
    """Update global volume levels."""
    if _manager is not None:
        _manager.set_volume(master=master, sfx=sfx, music=music)


def get_manager():
    """Return the global SoundManager (or None if not initialized)."""
    return _manager
