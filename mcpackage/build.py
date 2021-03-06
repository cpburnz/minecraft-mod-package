# coding: utf-8
"""
This script compiles, obfuscates, and packages a Minecraft Mod.
"""
from __future__ import print_function, unicode_literals

import distutils.version
import errno
import io
import itertools
import logging
import os
import os.path
import subprocess
import sys
import traceback
import zipfile
from distutils.version import StrictVersion
try:
	import configparser # pylint: disable=F0401
except ImportError:
	import ConfigParser as configparser

import pathspec
if StrictVersion(pathspec.__version__) < StrictVersion('0.3'):
	raise ImportError("pathspec version {!r} is installed, version {!r} is required.".format(pathspec.__version__, '0.3'))

from . import util

#: The file to log to.
LOG_FILE = 'mcpackage.log'

#: The name of the MCP configuration.
MCP_CONFIG_FILE = 'mcp.cfg'

#: Whether we are running Windows or another OS.
IS_WINDOWS = util.get_system() == 'Windows'

#: The default configuration.
DEFAULT_CONFIG = {
	# The name of the mod.
	'name': 'mod',
	# Settings for the build directory.
	'build': {
		# The directory to build the mod in.
		'dir': 'build',
	},
	# Settings for Minecraft Forge.
	'forge': {
		# The Minecraft Forge source directory.
		'dir': 'forge',
		# The Minecraft Coder Pack toolkit directory. This gets set to the
		# MCP directory under the Forge directory.
		'mcp_dir': None,
	},
	# Settings for additional libraries.
	'library': {
		# The directory containing additional libraries required by the mod.
		'dir': 'lib',
		# Patterns used to match libraries (JAR or ZIP) to package (merge)
		# with the built mod JAR.
		'package': [],
	},
	# Settings pertaining to the mod source code.
	'source': {
		# The directory containing the Java and Python source code for the
		# mod.
		'dir': 'src',
		# Patterns to match java files.
		'java': ['*.java'],
		# Patterns used to match python files.
		'python': ['*.py'],
		# Patterns to match assets or any additional files to package.
		'extra': [],
	},
	# Settings for Jython.
	'jython': {
		# The Jython executable. If this is null, it will be searched for in
		# standard locations. If the jython executable cannot be found, set
		# *jython_jar* and optionally *java_exe* will be attempted.
		'jython_exe': None,
		# The Jython JAR to execute using *java_exe*. If *jython_exe* could
		# not be found, this must be set.
		'jython_jar': None,
		# The Java executable to execute the *jython_jar* with. If this is
		# null, it will be searched for in standard locations. If this can
		# not be found, you must manually specify its location.
		'java_exe': None,
	},
}

#: The keys in the configuration that are directory paths which need to
#: be normalized.
CONFIG_PATHS = [
	('build', 'dir'),
	('forge', 'dir'),
	('library', 'dir'),
	('source', 'dir'),
]

#: The keys in the configuration that are path-specs which need to be
#: compiled.
CONFIG_PATHSPECS = [
	('library', 'package'),
	('source', 'extra'),
	('source', 'java'),
	('source', 'python'),
]

def command(**args):
	"""
	Builds and packages the Minecraft Mod.

	`**args` is the keyword arguments to send to ``BuildCommand()``.

	Returns the exit code (``int``).
	"""
	return BuildCommand(**args).run()


class BuildCommand(object):
	"""
	The ``BuildCommand`` class is used to build and package the Minecraft
	Mod.
	"""

	def __init__(self, config_file, verbose=None, **_):
		"""
		Initializes the ``BuildCommand`` instance.

		*config_file* (``str``) is the mcpackage configuration file to
		generate.

		*verbose* (``int``) is the level of verbose debugging information to
		be printed. Default is ``None`` for `0`.

		- `0`: print no debugging information.

		- `1`: print some debugging information.

		- `2`: print lots of debugging information.
		"""

		self.config = None
		"""
		*config* (``dict``) is the loaded mcpackage configuration.
		"""

		self.config_file = config_file
		"""
		*config_file* (``str``) is the mcpackage configuration file to
		generate.
		"""

		self.name = None
		"""
		*name* (``str``) is the name of the mod being built.
		"""

		self.log = None
		"""
		*log* (``logging.Logger``) is the logger for this script.
		"""

		self.verbose = verbose or 0
		"""
		*verbose* (``int``) is the level of verbose debugging information to
		be printed.
		"""

	def init_config(self):
		"""
		Loads the configuration.
		"""
		# Load config.
		if self.verbose >= 1:
			print("Load {!r}.".format(self.config_file))
		with io.open(self.config_file, mode='r', encoding='UTF-8') as fh:
			config = util.load_config(fh)

		# Merge defaults into loaded config.
		self.config = util.merge_config(DEFAULT_CONFIG, config)
		del config

		# Expand paths.
		path_keys, path = None, None
		for path_keys in CONFIG_PATHS:
			path = util.get_nested_value(self.config, path_keys)
			path = os.path.abspath(os.path.expandvars(path))
			util.set_nested_value(self.config, path_keys, path)
		del path_keys, path

		# Compile path-specs.
		pathspec_keys, lines, spec = None, None, None
		for pathspec_keys in CONFIG_PATHSPECS:
			lines = util.get_nested_value(self.config, pathspec_keys)
			spec = pathspec.PathSpec.from_lines('gitignore', lines)
			util.set_nested_value(self.config, pathspec_keys, spec)
		del pathspec_keys, lines, spec

		# Set MCP directory.
		self.config['forge']['mcp_dir'] = os.path.join(self.config['forge']['dir'], 'mcp')

		# Make sure forge and mcp directories exist.
		forge_dir = self.config['forge']['dir']
		mcp_dir = self.config['forge']['mcp_dir']
		assert os.path.exists(forge_dir), "Forge directory {!r} does not exist.".format(forge_dir)
		assert os.path.exists(mcp_dir), "MCP directory {!r} does not exist.".format(mcp_dir)

		# Setup build directory.
		build_dir = self.config['build']['dir']
		if not os.path.exists(build_dir):
			# Make sure build directory exists.
			if self.verbose >= 1:
				print("Create {!r}.".format(build_dir))
			try:
				os.makedirs(build_dir)
			except OSError as e:
				if e.errno != errno.EEXIST:
					raise

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

		build_dir = self.config['build']['dir']
		log_dir = os.path.join(build_dir, 'log')
		log_file = os.path.join(log_dir, LOG_FILE)
		if self.verbose >= 1:
			print("Create {!r}.".format(log_file))
		try:
			os.mkdir(log_dir)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

		if self.verbose >= 1:
			print("Log to {!r}.".format(log_file))
		stream_handler = logging.StreamHandler(stream=sys.stdout)
		stream_handler.setLevel(log_level)
		stream_handler.setFormatter(logging.Formatter(fmt='[%(name)s] %(levelname)s: %(message)s'))
		self.log.addHandler(stream_handler)
		file_handler = logging.FileHandler(log_file)
		file_handler.setLevel(log_level)
		file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s [%(name)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S%z'))
		self.log.addHandler(file_handler)

	def run(self):
		"""
		Runs the "build" command.

		Returns the exit code (``int``).
		"""
		# Load config.
		try:
			self.init_config()
		except:
			traceback.print_exc(file=sys.stderr)
			print("Failed to load configuration.", file=sys.stderr)
			if self.verbose >= 1:
				print("Exiting because of error.")
			return 1

		# Initialize logging.
		try:
			self.init_logging()
		except:
			traceback.print_exc(file=sys.stderr)
			print("Failed to initialize logging.", file=sys.stderr)
			if self.verbose >= 1:
				print("Exiting because of error.")
			return 1

		# Build mod.
		try:
			result = self.run_work()
		except:
			self.log.error("Failed to build mod.", exc_info=sys.exc_info())
			result = 1
		if result:
			self.log.info("Exiting because of error.")
		return result

	def run_work(self):
		"""
		Perform the actual work of the "build" command.

		Returns the exit code (``int``).
		"""
		# Generate MCP configuration.
		build_dir = self.config['build']['dir']
		lib_dir = self.config['library']['dir']
		mcp_file = os.path.join(build_dir, MCP_CONFIG_FILE)
		self.log.info("Create MCP config at {!r}.".format(util.short_path(mcp_file, build_dir)))
		config = configparser.SafeConfigParser()
		config.optionxform = str # Make options case sensitive.
		config.set('DEFAULT', 'DirBin', os.path.join(build_dir, 'bin'))
		#config.set('DEFAULT', 'DirConf', 'mcp/conf')
		config.set('DEFAULT', 'DirEclipse', os.path.join(build_dir, 'eclipse'))
		#config.set('DEFAULT', 'DirJars', 'mcp/jars')
		config.set('DEFAULT', 'DirLib', lib_dir)
		config.set('DEFAULT', 'DirLogs', os.path.join(build_dir, 'log', 'mcp'))
		config.set('DEFAULT', 'DirModSrc', os.path.join(build_dir, 'modsrc'))
		config.set('DEFAULT', 'DirReobf', os.path.join(build_dir, 'reobf'))
		#config.set('DEFAULT', 'DirRuntime', 'mcp/runtime')
		config.set('DEFAULT', 'DirSrc', os.path.join(build_dir, 'src'))
		config.set('DEFAULT', 'DirTemp', os.path.join(build_dir, 'temp'))
		config.set('DEFAULT', 'DirTempBin', os.path.join(build_dir, 'temp', 'bin'))
		config.set('DEFAULT', 'DirTempCls', os.path.join(build_dir, 'temp', 'cls'))
		config.set('DEFAULT', 'DirTempSrc', os.path.join(build_dir, 'temp', 'src'))
		with open(mcp_file, mode='wb') as fh:
			config.write(fh)

		mcp_dir = self.config['forge']['mcp_dir']
		mcp_args = {'close_fds': True, 'cwd': mcp_dir}

		# Copy MCP directories.
		# - "bin" is where all of the java classes get compiled to,
		#   including those belonging to the mod.
		# - "temp" contains some miscellaneous files, and recompile and
		#   reobfuscate generate a couple jars here.
		forge_dir = self.config['forge']['dir']
		src_dir, dest_dir = None, None
		for src_dir, dest_dir in [
			(os.path.join(mcp_dir, 'bin'), os.path.join(build_dir, 'bin')),
			(os.path.join(mcp_dir, 'temp'), os.path.join(build_dir, 'temp')),
		]:
			self.log.info("Copy from {!r} to {!r}.".format(util.short_path(src_dir, forge_dir), util.short_path(dest_dir, build_dir)))
			util.sync_files(src_dir, dest_dir)
		del src_dir, dest_dir

		# Find Forge and MCP source files.
		mcp_src_dir = os.path.join(mcp_dir, 'src', 'minecraft')
		self.log.info("Scan {!r}.".format(util.short_path(mcp_src_dir, forge_dir)))
		mcp_src_files = list(pathspec.iter_tree(mcp_src_dir))

		# Find java source files.
		source_dir = self.config['source']['dir']
		self.log.info("Scan {!r}.".format(os.path.basename(source_dir)))
		dest_dir = os.path.join(build_dir, 'src', 'minecraft')
		java_spec = self.config['source']['java']
		java_class_files = {}
		java_source_files = []
		file_path, class_file, src_file, dest_file = None, None, None, None
		for file_path in java_spec.match_tree(source_dir):
			# Record java source file to be copied later.
			java_source_files.append(file_path)

			# Record source and destination of java source file for java class
			# file.
			class_file = os.path.splitext(file_path)[0] + '.class'
			src_file = os.path.join(source_dir, file_path)
			#dest_file = os.path.join(dest_dir, file_path)
			java_class_files[class_file] = {
				'src': src_file,
				#'dest': dest_file,
			}
		del file_path, class_file, src_file, dest_file
		del java_spec

		# Find python source files.
		python_spec = self.config['source']['python']
		python_class_files = {}
		python_source_files = []
		file_path, class_file, src_file, dest_file = None, None, None, None
		for file_path in python_spec.match_tree(source_dir):
			# Record python source file to be copied later.
			python_source_files.append(file_path)

			# Record source and destination of python source file for python
			# class file.
			class_file = os.path.splitext(file_path)[0] + '$py.class'
			src_file = os.path.join(source_dir, file_path)
			#dest_file = os.path.join(dest_dir, file_path)
			python_class_files[class_file] = {
				'src': src_file,
				#'dest': dest_file,
			}
		del file_path, class_file, src_file, dest_file
		del python_spec

		# Copy source files to the "src" directory. This is the aggregation
		# of all java source code which includes the source for Forge, MCP,
		# and the project source code (including the python source code).
		dest_files = set()
		dest_files.update(mcp_src_files)
		dest_files.update(java_source_files)
		dest_files.update(python_source_files)

		# Copy Forge and MCP source.
		self.log.info("Copy from {!r} to {!r}.".format(util.short_path(mcp_src_dir, forge_dir), util.short_path(dest_dir, build_dir)))
		util.sync_files(mcp_src_dir, dest_dir, files=mcp_src_files, keep=dest_files)

		# Copy java and python source files to build directory.
		self.log.info("Copy from {!r} to {!r}.".format(os.path.basename(source_dir), util.short_path(dest_dir, build_dir)))
		util.sync_files(source_dir, dest_dir, files=itertools.chain(java_source_files, python_source_files), keep=dest_files)

		# Compile mod.
		self.log.info("Compile mod.")
		if IS_WINDOWS:
			command = ['recompile.bat']
		else:
			command = ['./recompile.sh']
		command += ['-c', mcp_file]
		try:
			subprocess.check_call(command, **mcp_args)
		except OSError as e:
			# Add the executed file to the error.
			e.args += (command[0],)
			e.filename = command[0]
			raise

		# Obfuscate mod.
		# - NOTE: I do not have a particularly good reason to use the SRG
		#   variation to obfuscate other than that is the one I got working
		#   from an example.
		self.log.info("Obfuscate mod.")
		if IS_WINDOWS:
			command = ['reobfuscate_srg.bat']
		else:
			command = ['./reobfuscate_srg.sh']
		command += ['-c', mcp_file]
		try:
			subprocess.check_call(command, **mcp_args)
		except OSError as e:
			# Add the executed file to the error.
			e.args += (command[0],)
			e.filename = command[0]
			raise

		# Compile python source files to class files.
		if python_class_files:
			# Find jython.
			self.log.info("Find Jython.")
			command = None
			jython_exe = self.config['jython']['jython_exe'] or util.find_exe('jython')
			if jython_exe:
				if not os.path.isfile(jython_exe):
					self.log.error("Jython executable could not be found at {!r}.".format(jython_exe))
					self.log.error("You must set the Jython executable in the configuration {!r}.".format(self.config_file))
					return 1
				self.log.debug("jython:{!r}".format(jython_exe))
				command = [jython_exe]

			else:
				# Find java.
				java_exe = self.config['jython']['java_exe'] or util.find_exe('java')
				if not java_exe:
					java_error = "Java executable could not be found."
				elif not os.path.isfile(java_exe):
					java_error = "Java executable could not be found at {!r}.".format(java_exe)
				else:
					java_error = None

				jython_jar = self.config['jython']['jython_jar']
				if not jython_jar:
					jar_error = "Jython JAR could not be found."
				elif not os.path.isfile(jython_jar):
					jar_error = "Jython JAR could not be found at {!r}.".format(jython_jar)
				else:
					jar_error = None
				jython_error = "Jython executable could not be found."

				if java_error and jar_error:
					# No java executable and no jython jar.
					self.log.error(jython_error)
					self.log.error(java_error)
					self.log.error(jar_error)
					self.log.error("You must set either the Jython executable or the Java executable with the Jython JAR in the configuration {!r}.".format(self.config_file))
					return 1
				elif not java_error and jar_error:
					# Found java executable but not jython jar.
					self.log.error(jython_error)
					self.log.error(jar_error)
					self.log.error("You must set either the Jython executable or the Jython JAR in the configuration {!r}.".format(self.config_file))
					return 1
				elif java_error and not jar_error:
					# No java executable but we found jython jar.
					self.log.error(java_error)
					self.log.error("You must set the Java executable in the configuration {!r}.".format(self.config_file))
					return 1
				self.log.debug("java:{!r}".format(java_exe))
				self.log.debug("jar:{!r}".format(jython_jar))
				command = [java_exe, '-jar', jython_jar]

			# Compile python source with jython.
			self.log.info("Compile python source.")
			command += ['-m', 'compileall', dest_dir]
			try:
				subprocess.check_call(command, close_fds=True)
			except OSError as e:
				# Add the executable file to the error.
				e.args += (command[0],)
				e.filename = command[0]
				raise

		# Package mod in JAR.
		name = self.config['name']
		mod_jar_file = os.path.join(build_dir, name + '.jar')
		self.log.info("Create mod jar at {!r}.".format(util.short_path(mod_jar_file, build_dir)))
		with zipfile.ZipFile(mod_jar_file, 'w', zipfile.ZIP_DEFLATED) as mod_fh:

			# Package compiled java code. Only copy compiled java classes
			# originating from the source directory.
			# - NOTE: Forge version 1.6.2-9.10.0.804 fills the reobf directory
			#   with the Forge, MCP, and Minecraft compiled classes while
			#   Forge version 1.6.4-9.11.0.881 only has the mod's compiled
			#   classes.
			self.log.info("Package compiled java code.")
			reobf_dir = os.path.join(build_dir, 'reobf', 'minecraft')
			self.log.info("Copy {!r} into {!r}.".format(util.short_path(reobf_dir, build_dir), util.short_path(mod_jar_file, build_dir)))
			class_file, class_info, src_file = None, None, None
			for class_file, class_info in java_class_files.items():
				src_file = os.path.join(reobf_dir, class_file)
				if os.path.exists(src_file):
					self.log.debug("Copy {!r} to {!r}.".format(util.short_path(src_file, reobf_dir), class_file))
					mod_fh.write(src_file, arcname=class_file)
				else:
					self.log.warning("Source file {!r} was not compiled to class file {!r}.".format(util.short_path(class_info['src'], source_dir), util.short_path(src_file, reobf_dir)))
			del class_file, class_info, src_file
			del java_class_files

			# Package compiled python code.
			# - TODO: Copy source file as well.
			if python_class_files:
				self.log.info("Package compiled python code.")
				class_file, class_info, src_file = None, None, None
				for class_file, class_info in python_class_files.items():
					# Copy python class file.
					src_file = os.path.join(dest_dir, class_file)
					if os.path.exists(src_file):
						self.log.debug("Copy {!r} to {!r}.".format(util.short_path(src_file, dest_dir), class_file))
						mod_fh.write(src_file, arcname=class_file)
					else:
						self.log.warning("Source file {!r} was not compiled to class file {!r}.".format(util.short_path(class_info['src'], source_dir), util.short_path(src_file, dest_dir)))
					# Copy python source file.
					# - TODO: class_info['src'] needs to be relative not absolute.
					if os.path.exists(class_info['src']):
						self.log.debug("Copy {!r} to {!r}.".format(util.short_path(class_info['src'], source_dir), ))
						mod_fh.write() # TODO
				del class_file, class_info, src_file

			# Copy assets/extra files.
			extra_spec = self.config['source']['extra']
			if extra_spec:
				self.log.info("Package extra files.")
				file_path, src_file, dest_file = None, None, None
				for file_path in extra_spec.match_tree(source_dir):
					src_file = os.path.join(source_dir, file_path)
					dest_file = file_path
					self.log.debug("Copy {!r} to {!r}.".format(util.short_path(src_file, source_dir), dest_file))
					mod_fh.write(src_file, arcname=dest_file)
				del file_path, src_file, dest_file
			del extra_spec

			# Merge (package) additional libraries into JAR.
			lib_spec = self.config['library']['package']
			if lib_spec:
				self.log.info("Package libraries.")
				path, lib_file, info = None, None, None
				for path in lib_spec.match_tree(lib_dir):
					lib_file = os.path.join(lib_dir, path)
					self.log.info("Copy {!r} into {!r}.".format(util.short_path(lib_file, lib_dir), util.short_path(mod_jar_file, build_dir)))
					with zipfile.ZipFile(lib_file, 'r') as lib_fh:
						for info in lib_fh.infolist():
							if not info.filename.startswith('META-INF'):
								mod_fh.writestr(info.filename, lib_fh.read(info.filename), compress_type=info.compress_type)
				del path, lib_file, info
			del lib_spec

		return 0
