# coding: utf-8
"""
This module implements the "init" command which is used to create the
scaffolding for a new Minecraft Mod.
"""
from __future__ import print_function

import errno
import io
import json
import logging
import os
import string # pylint: disable=W0402
import sys
import traceback

import pkg_resources

from . import __name__ as MCPACKAGE

#: The template mcmod info file.
MCMOD_TEMPLATE_FILE = 'data/templates/mcmod.info'

#: The template mcpackage configuration file.
MCPACKAGE_TEMPLATE_FILE = 'data/templates/mcpackage.yaml'

#: The template java mod file.
JAVA_TEMPLATE_FILE = 'mod.java'

#: The template python mod file.
PYTHON_TEMPLATE_FILE = 'mod.py'

def command(**args):
	"""
	Creates the scaffolding for a new Minecraft Mod.

	`**args` is the keyword arguments to send to ``InitCommand()``.

		Returns the exit code (``int``).
	"""
	return InitCommand(**args).run()


class InitCommand(object):
	"""
	The ``InitCommand`` class is used to create the scaffolding for a new
	Minecraft Mod.
	"""

	def __init__(self, mod_package, mod_dir, config_file, forge_dir, build_dir, library_dir, source_dir, mod_id=None, mod_class=None, verbose=None):
		"""
		Initializes the ``InitCommand`` instance.

		*mod_package* (``str``) is the Java Package name for the Minecraft
		Mod.

		*mod_dir* (``str``) is the directory to create the Minecraft Mod in.

		*config_file* (``str``) is the **mcpackage** configuration file to
		generate.

		*forge_dir* (``str``) is the Minecraft Forge source directory.

		*build_dir* (``str``) is the directory to build the mod in.

		*library_dir* (``str``) is the directory containing additional
		libraries required by the mod.

		*source_dir* (``str``) is the directory containing the source code
		for the mod.

		*mod_id* (``str``) is the ID for the Minecraft Mod. Default is
		``None`` for the last segment in *mod_package*.

		*mod_class* (``str``) is the class name for the Minecraft Mod.
		Default is ``None`` for *mod_id* concatenated with 'Mod'.

		*verbose* (``int``) is the level of verbose debugging information to
		be printed. Default is ``None`` for `0`.

		- `0`: print no debugging information.

		- `1`: print some debugging information.

		- `2`: print lots of debugging information.
		"""

		self.build_dir = build_dir
		"""
		*build_dir* (``str``) is the directory to build the mod in.
		"""

		self.config_file = config_file
		"""
		*config* (``str``) is the mcpackage configuration file to generate.
		"""

		self.forge_dir = forge_dir
		"""
		*forge_dir* (``str``) is the Minecraft Forge source directory.
		"""

		self.library_dir = library_dir
		"""
		*library_dir* (``str``) is the directory containing additional
		libraries required by the mod.
		"""

		self.mod_dir = mod_dir
		"""
		*mod_dir* (``str``) is the directory to create the Minecraft Mod in.
		"""

		self.mod_id = None
		"""
		*mod_id* (``str``) is the ID of the mod.
		"""

		self.mod_package = mod_package
		"""
		*mod_package* (``str``) is the Java Package for the Minecraft Mod.
		"""

		self.log = None
		"""
		*log* (``logging.Logger``) is the main logger.
		"""

		self.source_dir = source_dir
		"""
		*source_dir* (``str``) is the directory containing the source code
		for the mod.
		"""

		self.verbose = verbose or 0
		"""
		*verbose* (``int``) is the level of verbose debugging information to
		be printed.
		"""

		if not mod_id:
			mod_id = mod_package.rsplit('.', 1)[1]

		if not mod_class:
			mod_class = mod_id + 'Mod'

		self.mod_id = mod_id
		self.mod_class = mod_class

	def init_logging(self):
		"""
		Initialize logging.
		"""
		if self.verbose >= 2:
			log_level = logging.DEBUG
		elif self.verbose >= 1:
			log_level = logging.INFO
		else:
			log_level = logging.WARNING

		self.log = logging.getLogger()
		self.log.setLevel(logging.NOTSET)

		if self.verbose >= 1:
			print("Log to stdout.")
		stream_handler = logging.StreamHandler(stream=sys.stdout)
		stream_handler.setLevel(log_level)
		stream_handler.setFormatter(logging.Formatter(fmt='[%(name)s] %(levelname)s: %(message)s'))
		self.log.addHandler(stream_handler)

	def run(self):
		"""
		Runs the "init" command.

		Returns the exit code (``int``).
		"""
		# Initialze logging.
		try:
			self.init_logging()
		except:
			traceback.print_exc(file=sys.stderr)
			print("Failed to initialize logging.", file=sys.stderr)
			if self.verbose >= 1:
				print("Exiting because of error.")
			return 1

		# Create mod.
		try:
			result = self.run_work()
		except:
			self.log.exception()
			self.log.error("Failed to create mod.")
			result = 1
		if result:
			self.log.info("Exiting because of error.")
		return result

	def run_work(self):
		"""
		Perform the actual work of the "init" command.

		Returns the exit code (``int``).
		"""
		# Create mod directory.
		self.log.info("Create mod directory {!r}.".format(self.mod_dir))
		try:
			os.makedirs(self.mod_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

		# If mod directory is not empty, report error and stop. This is so
		# we do not accidently overwrite files belonging an existing mod.
		for _ in os.walk(self.mod_dir):
			self.log.error("Mod directory {!r} is not empty.".format(self.mod_dir))
			return 1

		# Display warning if forge directory does not exist.
		forge_dir = os.path.normpath(os.path.join(self.mod_dir, self.forge_dir))
		if not os.path.isdir(forge_dir):
			self.log.warning("The Minecraft Forge directory {!r} does not exist. Ensure it gets created before building.".format(forge_dir))
		del forge_dir

		# Create library directory.
		library_dir = os.path.normpath(os.path.join(self.mod_dir, self.library_dir))
		self.log.info("Create library directory {!r}.".format(library_dir))
		try:
			os.makedirs(library_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		del library_dir

		# Create source directory.
		source_dir = os.path.normpath(os.path.join(self.mod_dir, self.source_dir))
		self.log.info("Create source directory {!r}.".format(source_dir))
		try:
			os.makedirs(source_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		del source_dir

		# Encode values as JSON because they are compatible in both JSON and
		# YAML files.
		encode = json.JSONEncoder(ensure_ascii=False).encode

		# Load mcpackage configuration template.
		self.log.info("Load {!r}.".format(MCPACKAGE_TEMPLATE_FILE))
		config_tpl = pkg_resources.resource_string(MCPACKAGE, MCPACKAGE_TEMPLATE_FILE)

		# Generate mcpackage configuration.
		self.log.info("Generate {!r}.".format(os.path.basename(self.config_file)))
		config_str = string.Template(config_tpl).substitute(
			build_dir=encode(self.build_dir),
			forge_dir=encode(self.forge_dir),
			library_dir=encode(self.library_dir),
			mod_id=encode(self.mod_id),
			source_dir=encode(self.source_dir),
		)
		del config_tpl

		# Save mcpackage configuration file.
		config_file = os.path.normpath(os.path.join(self.mod_dir, self.config_file))
		self.log.info("Create {!r}.".format(config_file))
		with io.open(config_file, mode='w', encoding='UTF-8') as fh:
			fh.write(config_str)
		del config_str
		del config_file

		# Load mcmod info template.
		self.log.info("Load {!r}.".format(MCMOD_TEMPLATE_FILE))
		info_tpl = pkg_resources.resource_string(MCPACKAGE, MCMOD_TEMPLATE_FILE)

		# Generate mcmod info.
		self.log.info("Generate 'mcmod.info'.")
		info_str = string.Template(info_str).substitute(
			mc_version=encode('1.6.2'), # TODO: Read the minecraft version from Forge.
			mod_id=encode(self.mod_id),
		)
		del info_tpl

		# Save mcmod info file.
		info_file = os.path.normpath(os.path.join(self.mod_dir, self.source_dir, 'mcmod.info'))
		self.log.info("Create {!r}.".format(info_file))
		with io.open(info_file, mode='w', encoding='UTF-8') as fh:
			fh.write(info_str)
		del info_str
		del info_file

		# Load java mod template.
		# - TODO: Finalize format of Java mod and names of Java classes.
		self.log.info("Load {!r}.".format(JAVA_TEMPLATE_FILE))
		java_tpl = pkg_resources.resource_string(MCPACKAGE, JAVA_TEMPLATE_FILE)

		# TODO: Generate mod java file.

		# TODO: Generate mod python file.

		raise NotImplementedError("TODO")
