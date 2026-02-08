# main.py — Pygbag entry point
# Pygbag requires a main.py in the root with an async main() function.
# This file wraps the existing launcher for web deployment.
#
# NOTE: Pygbag scans this file for imports to decide what to bundle.
# All packages used anywhere in the game must be imported here.

import asyncio
import pygame
import numpy
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
pygame.init()

from launcher import launcher

async def main():
    await launcher()

asyncio.run(main())
