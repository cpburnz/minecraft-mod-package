# coding: utf-8
"""
Executes *mcpackage* to compile, obfuscate, and package a Minecraft Mod
using Forge and MCP.
"""

import sys

from .package import main

sys.exit(main(sys.argv))
