# main.py — Pygbag entry point
# Pygbag requires a main.py in the root with an async main() function.
# This file wraps the existing launcher for web deployment.
#
# NOTE: Pygbag scans this file for imports to decide what to bundle.
# All packages used anywhere in the game must be imported here.
# However, actual initialization must happen INSIDE async main()
# so the WASM runtime and browser display are ready.

import asyncio
import pygame
import numpy
import sys
import os


async def main():
    # Defer all initialization to inside async main —
    # Pygbag's WASM runtime and virtual filesystem aren't fully
    # ready during module-level execution.
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    if not pygame.get_init():
        pygame.init()

    from launcher import launcher
    await launcher()

asyncio.run(main())
