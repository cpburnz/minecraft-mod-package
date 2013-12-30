# coding: utf-8
"""
Executes *mcpackage* to compile, obfuscate, and package a Minecraft Mod
using Forge and MCP.
"""

import sys

from . import main

sys.exit(main.run(sys.argv))
