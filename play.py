#!/usr/bin/env python3
"""
PongWithIssues — One-click launcher
Automatically sets up a virtual environment, installs dependencies,
and starts the game. Works on Linux, macOS, and Windows.

Usage: python play.py   (or python3 play.py)
"""

import sys
import os
import subprocess
import venv

# Suppress the "Hello from the pygame community" message
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

# ── Project root is wherever this script lives ──
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(PROJECT_ROOT, ".venv")
REQUIREMENTS = os.path.join(PROJECT_ROOT, "requirements.txt")

PONG_ASCII = r"""
██████╗   ██████╗  ███╗   ██╗  ██████╗   ██╗
██╔══██╗ ██╔═══██╗ ████╗  ██║ ██╔════╝   ██║
██████╔╝ ██║   ██║ ██╔██╗ ██║ ██║  ███╗  ██║
██╔═══╝  ██║   ██║ ██║╚██╗██║ ██║   ██║  ╚═╝
██║      ╚██████╔╝ ██║ ╚████║ ╚██████╔╝  ██╗
╚═╝       ╚═════╝  ╚═╝  ╚═══╝  ╚═════╝   ╚═╝
"""


def get_venv_python():
    """Return the path to the venv's Python executable (platform-aware)."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def get_venv_pip():
    """Return the path to the venv's pip executable (platform-aware)."""
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def is_inside_venv():
    """Check if we're already running inside the project's venv."""
    return (
        sys.prefix != sys.base_prefix
        and os.path.abspath(sys.prefix) == os.path.abspath(VENV_DIR)
    )


def print_step(msg):
    """Print a formatted setup step."""
    print(f"  >> {msg}", flush=True)


def create_venv():
    """Create the virtual environment."""
    print_step("Creating virtual environment (.venv) ...")
    venv.create(VENV_DIR, with_pip=True)
    print_step("Virtual environment created.")


def install_dependencies():
    """Install project dependencies from requirements.txt."""
    pip = get_venv_pip()
    print_step("Installing dependencies (pygame, numpy) ...")
    subprocess.check_call(
        [pip, "install", "--upgrade", "pip"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        [pip, "install", "-r", REQUIREMENTS],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print_step("Dependencies installed.")


def needs_install():
    """Check if deps are missing by trying to import them in the venv."""
    py = get_venv_python()
    try:
        result = subprocess.run(
            [py, "-c", "import pygame; import numpy"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode != 0
    except Exception:
        return True


def launch_game():
    """Launch the game using the venv Python."""
    py = get_venv_python()
    launcher = os.path.join(PROJECT_ROOT, "launcher.py")

    print(flush=True)
    print("  Starting PongWithIssues ...", flush=True)
    print("  ─────────────────────────", flush=True)
    print(flush=True)

    os.chdir(PROJECT_ROOT)
    env = os.environ.copy()
    env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    result = subprocess.call([py, launcher], env=env)
    return result


def main():
    os.chdir(PROJECT_ROOT)

    # ── Banner ──
    print(flush=True)
    print(PONG_ASCII, flush=True)
    print("  PongWithIssues — Multi-mode Pong Game", flush=True)
    print("  ─────────────────────────────────────", flush=True)
    print(flush=True)

    venv_python = get_venv_python()

    # ── Step 1: Create venv if it doesn't exist ──
    if not os.path.exists(venv_python):
        print_step("First-time setup detected!")
        print()
        create_venv()
        install_dependencies()
        print()
        print_step("Setup complete!")
    elif needs_install():
        # Venv exists but deps are missing (e.g. after a clean)
        print_step("Updating dependencies ...")
        install_dependencies()
        print()
        print_step("Dependencies up to date!")
    else:
        print_step("Environment ready.")

    # ── Step 2: Launch the game ──
    launch_game()


if __name__ == "__main__":
    main()
