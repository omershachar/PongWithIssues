# main.py — Pygbag entry point
# Pygbag requires a main.py in the root with an async main() function.
# This file simply wraps the existing launcher for web deployment.

import asyncio
import pygame
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
pygame.init()

from launcher import launcher

async def main():
    await launcher()

asyncio.run(main())
