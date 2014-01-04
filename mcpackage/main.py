# coding: utf-8
"""
Minecraft Mod Packaging Tool.
"""

import argparse
import gettext

import pkg_resources

from . import __name__ as MCPACKAGE, __project__, __version__
from .build import command as build_command
from .init import command as init_command
from .install import command as install_command
from .run import command as run_command

# Override argparse messages.
LOCALE_DIR = pkg_resources.resource_filename(MCPACKAGE, 'data/locale')
gettext.bindtextdomain('messages', LOCALE_DIR)

#: The default build configuration file.
DEFAULT_CONFIG_FILE = 'mcpackage.yaml'

#: The default directory to create a mod in.
DEFAULT_MOD_DIR = '.'

#: The default path to the Minecraft Forge directory.
DEFAULT_FORGE_DIR = 'forge'

#: THe default directory to build the mod in.
DEFAULT_BUILD_DIR = 'build'

#: The default directory to contain additional libraries for the mod.
DEFAULT_LIBRARY_DIR = 'lib'

#: The default directory to create the mod source in.
DEFAULT_SOURCE_DIR = 'src'

def run(argv):
	"""
	Runs the *mcpackage* command-line interface.

	*argv* (**sequence**) contains the script arguments.

	Returns the exit code (``int``).
	"""
	parser = argparse.ArgumentParser(
		prog='python -m mcpackage',
		description=__doc__,
	)
	parser.add_argument('--version', action='version', version="{} {}".format(__project__, __version__), help="""
		Show the mcpackage version number and exit.
	""")
	subparsers = parser.add_subparsers(title="Commands", metavar="command")

	# Init command.
	parser_init = subparsers.add_parser('init', help="Creates the scaffolding for a new Minecraft Mod.")
	parser_init.set_defaults(func=lambda args: init_command(**vars(args)))

	group = parser_init.add_argument_group(title="Required Arguments")
	group.add_argument('--mod-name', required=True, metavar="NAME", help="""
		The name of the Minecraft Mod. This can contain letters, numbers,
		and symbols. E.g., 'My Awesome Mod'.
	""")
	group.add_argument('--mod-namespace', required=True, metavar="NS", help="""
		The Java package namespace for the Minecraft Mod. This should only
		contain lowercase letters and periods. E.g., 'myname.myawesomemod'.
	""")
	group.add_argument('--mod-type', choices=['java', 'python'], required=True, metavar="TYPE", help="""
		The type of Minecraft Mod scaffolding to create. *java* is for a
		normal mod written in Java. *python* is for a mod written primarily
		in Python with Java bootstrapping (requires PyMod).
	""")

	group = parser_init.add_argument_group(title="Default Arguments", description="""
		All relative paths are relative to *mod-dir*.
	""")
	group.add_argument('--mod-id', default=None, metavar="ID", help="""
		The ID for the Minecraft Mod. This should begin with a lowercase
		letter followed by lowercase letters, numbers, or underscores. E.g.,
		'myawesomemod'. Default is to lowercase letters and remove
		non-alphanumeric characters from *mod-name*.
	""")
	group.add_argument('--mod-class', default=None, metavar="CLASS", help="""
		The class name for the Minecraft Mod. This should begin with an
		uppercase letter followed by letters, numbers, or underscores. E.g.,
		'MyAwesomeMod'. Default is to remove non-alphanumeric characters
		from *mod-name* and append with 'Mod' if it does not end with 'Mod'.
	""")
	group.add_argument('--mod-dir', default=DEFAULT_MOD_DIR, metavar="DIR", help="""
		The directory to create the Minecraft Mod in. Default is %(default)r.
	""")
	group.add_argument('--config-file', default=DEFAULT_CONFIG_FILE, metavar="FILE", help="""
		The mcpackage configuration file to generate. Default is %(default)r.
	""")
	group.add_argument('--forge-dir', default=DEFAULT_FORGE_DIR, metavar="DIR", help="""
		The path to the Minecraft Forge source directory. Default is
		%(default)r.
	""")
	group.add_argument('--build-dir', default=DEFAULT_BUILD_DIR, metavar="DIR", help="""
		The directory to build the Minecraft Mod in. Default is %(default)r.
	""")
	group.add_argument('--library-dir', default=DEFAULT_LIBRARY_DIR, metavar="DIR", help="""
		The directory to contain additional libraries required by the
		Minecraft Mod. Default is %(default)r.
	""")
	group.add_argument('--source-dir', default=DEFAULT_SOURCE_DIR, metavar="DIR", help="""
		The directory to contain the source code for the Minecraft Mod.
		Default is %(default)r.
	""")

	group = parser_init.add_argument_group(title="Optional Arguments")
	parser_init.add_argument('-v', '--verbose', action='count', help="""
		Print verbose debugging information.
	""")

	# Build command.
	parser_build = subparsers.add_parser('build', help="Build and package the Minecraft Mod.")
	parser_build.set_defaults(func=lambda args: build_command(**vars(args)))
	parser_build.add_argument('-c', '--config-file', default=DEFAULT_CONFIG_FILE, metavar="FILE", help="""
		The mcpackage configuration file to use. Default is %(default)r.
	""")
	parser_build.add_argument('-v', '--verbose', action='count', help="""
		Print verbose debugging information.
	""")

	# Install command.
	# - TODO: Determine proper arguments.
	parser_install = subparsers.add_parser('install', help="Install the Minecraft Mod.")
	parser_install.set_defaults(func=lambda args: install_command(**vars(args)))
	parser_install.add_argument('-c', '--config-file', default=DEFAULT_CONFIG_FILE, metavar="FILE", help="""
		The mcpackage configuration file to use. Default is %(default)r.
	""")
	parser_install.add_argument('-v', '--verbose', action='count', help="""
		Print verbose debugging information.
	""")

	# Run command.
	# - TODO: Determine proper arguments.
	parser_run = subparsers.add_parser('run', help="Run Minecraft.")
	parser_run.set_defaults(func=lambda args: run_command(**vars(args)))
	parser_run.add_argument('-c', '--config-file', default=DEFAULT_CONFIG_FILE, metavar="FILE", help="""
		The mcpackage configuration file to use. Default is %(default)r.
	""")
	parser_run.add_argument('-v', '--verbose', action='count', help="""
		Print verbose debugging information.
	""")

	# Parse command-line arguments.
	args = parser.parse_args(argv[1:])
	return args.func(args)
