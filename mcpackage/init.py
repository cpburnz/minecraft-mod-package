# coding: utf-8
"""
This module implements the "init" command which is used to create the
scaffolding for a new Minecraft Mod.
"""
from __future__ import print_function, unicode_literals

import errno
import io
import json
import logging
import os
import re
import string # pylint: disable=W0402
import sys
import traceback

import pkg_resources

from . import __name__ as MCPACKAGE

#: The template mcmod info file.
MCMOD_TEMPLATE_FILE = {
	'java': 'data/templates/mcmod.info',
	'python': 'data/templates/mcmod.info',
}

#: The template mcpackage configuration file.
MCPACKAGE_TEMPLATE_FILE = {
	'java': 'data/templates/java/mcpackage.yaml',
	'python': 'data/templates/python/mcpackage.yaml',
}

#: The template java mod file.
JAVA_MOD_TEMPLATE_FILE = {
	'java': 'data/templates/java/mod.java',
	'python': 'data/templates/python/mod.java',
}

#: The template python init file.
PYTHON_INIT_TEMPLATE_FILE = {
	'python': 'data/templates/python/__init__.py'
}

#: The template python mod file.
PYTHON_MOD_TEMPLATE_FILE = {
	'python': 'data/templates/python/mod.py'
}

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

	def __init__(self, mod_name, mod_namespace, mod_type, mod_dir, config_file, forge_dir, build_dir, library_dir, source_dir, mod_id=None, mod_class=None, verbose=None, force=None, **_):
		"""
		Initializes the ``InitCommand`` instance.

		*mod_name* (``str``) is the name of the Minecraft Mod.

		*mod_namespace* (``str``) is the Java package namespace for the
		Minecraft Mod.

		*mod_type* (``str``) is the type of Minecraft Mod scaffolding to
		create. This must be either 'java' or 'python'.

		*mod_dir* (``str``) is the directory to create the Minecraft Mod in.

		*config_file* (``str``) is the mcpackage configuration file to
		generate.

		*forge_dir* (``str``) is the Minecraft Forge source directory.

		*build_dir* (``str``) is the directory to build the mod in.

		*library_dir* (``str``) is the directory containing additional
		libraries required by the mod.

		*source_dir* (``str``) is the directory containing the source code
		for the mod.

		*mod_id* (``str``) is the ID for the Minecraft Mod. Default is
		``None`` to lowercase letters and remove non-alphanumeric characters
		from *mod_name*.

		*mod_class* (``str``) is the Java class name for the Minecraft Mod.
		Default is ``None`` to remove non-alphanumeric characters from
		*mod_name* and append with 'Mod' if it does not end with 'Mod'.

		*verbose* (``int``) is the level of verbose debugging information to
		be printed. Default is ``None`` for `0`.

		- `0`: print no debugging information.

		- `1`: print some debugging information.

		- `2`: print lots of debugging information.

		*force* (``bool``) forces the initialization of a new Minecraft Mod.
		If ``False``, a new Mod cannot be initialized if *mod_dir* is not
		empty. Default is ``None`` for ``False``.
		"""

		self.build_dir = build_dir
		"""
		*build_dir* (``str``) is the directory to build the mod in.
		"""

		self.config_file = config_file
		"""
		*config* (``str``) is the mcpackage configuration file to generate.
		"""

		self.force = force or False
		"""
		*force* (``bool``) forces the initialization of a new Minecraft Mod.
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

		self.mod_name = mod_name
		"""
		*mod_name* (``str``) is the name of the Minecraft Mod.
		"""

		self.mod_namespace = mod_namespace
		"""
		*mod_namespace* (``str``) is the Java package namespace for the
		Minecraft Mod.
		"""

		self.mod_type = None
		"""
		*mod_type* (``str``) is the type of Minecraft Mod scaffolding to
		create. This must be either 'java' or 'python'.
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

		assert mod_type in ('java', 'python'), "mod_type:{!r} must be:{!r}.".format(mod_type, ['java', 'python'])

		if not mod_id:
			# Generate mod ID from name.
			mod_id = re.sub('\\W', '', mod_name).lower()

		if not mod_class:
			# Generate mod class from name.
			mod_class = re.sub('\\W', '', mod_name)
			if not mod_class.endswith('Mod'):
				mod_class += 'Mod'

		self.mod_class = mod_class
		self.mod_id = mod_id
		self.mod_type = mod_type

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
			self.log.error("Failed to create mod.", exc_info=sys.exc_info())
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

		if not self.force:
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

		# Create source directory.
		source_dir = os.path.normpath(os.path.join(self.mod_dir, self.source_dir))
		self.log.info("Create source directory {!r}.".format(source_dir))
		try:
			os.makedirs(source_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

		# Create namespace directory.
		namespace_dir = os.path.join(source_dir, *self.mod_namespace.split('.'))
		self.log.info("Create namespace directory {!r}.".format(namespace_dir))
		try:
			os.makedirs(namespace_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

		# Encode values as JSON because they are compatible in both JSON and
		# YAML files.
		json_encode = json.JSONEncoder(ensure_ascii=False).encode

		# Load mcpackage configuration template.
		config_file = MCPACKAGE_TEMPLATE_FILE[self.mod_type]
		self.log.info("Load {!r}.".format(config_file))
		config_tpl = pkg_resources.resource_string(MCPACKAGE, config_file)
		config_tpl = config_tpl.decode('UTF-8')
		del config_file

		# Generate mcpackage configuration.
		config_file = os.path.normpath(os.path.join(self.mod_dir, self.config_file))
		self.log.info("Generate {!r}.".format(os.path.basename(config_file)))
		config_str = string.Template(config_tpl).substitute(
			build_dir=json_encode(self.build_dir),
			forge_dir=json_encode(self.forge_dir),
			library_dir=json_encode(self.library_dir),
			mod_id=json_encode(self.mod_id),
			source_dir=json_encode(self.source_dir),
		)
		del config_tpl

		# Save mcpackage configuration file.
		self.log.info("Create {!r}.".format(config_file))
		with io.open(config_file, mode='w', encoding='UTF-8') as fh:
			fh.write(config_str)
		del config_str
		del config_file

		# Load mcmod info template.
		info_file = MCMOD_TEMPLATE_FILE[self.mod_type]
		self.log.info("Load {!r}.".format(info_file))
		info_tpl = pkg_resources.resource_string(MCPACKAGE, info_file)
		info_tpl = info_tpl.decode('UTF-8')
		del info_file

		# Generate mcmod info.
		info_file = os.path.join(source_dir, 'mcmod.info')
		self.log.info("Generate {!r}.".format(os.path.basename(info_file)))
		mod_hard_deps = ['Forge']
		if self.mod_type == 'python':
			mod_hard_deps.append('pymod')
		info_str = string.Template(info_tpl).substitute(
			mc_version=json_encode('1.6.2'), # TODO: Read the minecraft version from Forge.
			mod_id=json_encode(self.mod_id),
			mod_name=json_encode(self.mod_name),
			mod_hard_deps=json_encode(mod_hard_deps),
			mod_soft_deps=json_encode(mod_hard_deps),
		)
		del info_tpl

		# Save mcmod info file.
		self.log.info("Create {!r}.".format(info_file))
		with io.open(info_file, mode='w', encoding='UTF-8') as fh:
			fh.write(info_str)
		del info_str
		del info_file

		# Load java mod template.
		mod_file = JAVA_MOD_TEMPLATE_FILE[self.mod_type]
		self.log.info("Load {!r}.".format(mod_file))
		mod_tpl = pkg_resources.resource_string(MCPACKAGE, mod_file)
		mod_tpl = mod_tpl.decode('UTF-8')
		del mod_file

		# Generate java mod file.
		mod_file = os.path.join(namespace_dir, self.mod_class + '.java')
		self.log.info("Generate {!r}.".format(os.path.basename(mod_file)))
		mod_str = string.Template(mod_tpl).substitute(
			mod_class=self.mod_class,
			mod_id=self.mod_id,
			mod_name=self.mod_name,
			mod_package=self.mod_namespace,
		)
		del mod_tpl

		# Save java mod file.
		self.log.info("Create {!r}.".format(mod_file))
		with io.open(mod_file, mode='w', encoding='UTF-8') as fh:
			fh.write(mod_str)
		del mod_str
		del mod_file

		if self.mod_type == 'python':
			# Create python directory.
			python_dir = os.path.join(namespace_dir, 'py')
			self.log.info("Create python directory {!r}.".format(python_dir))
			try:
				os.makedirs(python_dir)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise

			# Load python init template.
			init_file = PYTHON_INIT_TEMPLATE_FILE[self.mod_type]
			self.log.info("Load {!r}.".format(init_file))
			init_tpl = pkg_resources.resource_string(MCPACKAGE, init_file)
			init_tpl = init_tpl.decode('UTF-8')
			del init_file

			# Generate python init file.
			init_file = os.path.join(python_dir, '__init__.py')
			self.log.info("Generate {!r}.".format(os.path.basename(init_file)))
			init_str = string.Template(init_tpl).substitute(
				mod_class=self.mod_class,
				mod_namespace=self.mod_namespace,
			)
			del init_tpl

			# Save python init file.
			self.log.info("Create {!r}.".format(init_file))
			with io.open(init_file, mode='w', encoding='UTF-8') as fh:
				fh.write(init_str)
			del init_str
			del init_file

			# Load python mod template.
			mod_file = PYTHON_MOD_TEMPLATE_FILE[self.mod_type]
			self.log.info("Load {!r}.".format(mod_file))
			mod_tpl = pkg_resources.resource_string(MCPACKAGE, mod_file)
			mod_tpl = mod_tpl.decode('UTF-8')
			del mod_file

			# Generate python mod file.
			mod_file = os.path.join(python_dir, 'mod.py')
			self.log.info("Generate {!r}.".format(os.path.basename(mod_file)))
			mod_str = string.Template(mod_tpl).substitute(
				mod_class=self.mod_class,
				mod_name=self.mod_name,
			)
			del mod_tpl

			# Save python mod file.
			self.log.info("Create {!r}.".format(mod_file))
			with io.open(mod_file, mode='w', encoding='UTF-8') as fh:
				fh.write(mod_str)
			del mod_str
			del mod_file

		self.log.info("Done.")
		return 0
