# coding: utf-8

import io

from setuptools import find_packages, setup

from mcpackage import __author__, __email__, __license__, __project__, __version__

# Read readme and changes files.
with io.open('README.rst', mode='r', encoding='UTF-8') as fh:
	readme = fh.read().strip()
with io.open('CHANGES.rst', mode='r', encoding='UTF-8') as fh:
	changes = fh.read().strip()

setup(
	name=__project__,
	version=__version__,
	author=__author__,
	author_email=__email__,
	url="https://github.com/cpburnz/minecraft-mod-package",
	description="Minecraft Mod Packaging Tool.",
	long_description=readme + "\n\n" + changes,
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
		"Operating System :: Microsoft :: Windows",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2 :: 2.7",
		"Programming Language :: Python :: 3",
		"Topic :: Games/Entertainment",
		"Topic :: Software Development :: Build Tools",
	],
	license=__license__,
	packages=find_packages(),
	include_package_data=True,
)
