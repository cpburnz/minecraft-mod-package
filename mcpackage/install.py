# coding: utf-8
"""
This module implements the "install" command which is used  to install
the Minecraft Mod.
"""

def command(**args):
	"""
	Installs the Minecraft Mod.

	`**args` is the keyword arguments to send to ``InstallCommand()``.

		Returns the exit code (``int``).
	"""
	return InstallCommand(**args).run()


class InstallCommand(object):
	"""
	The ``InstallCommand`` class is used to install the Minecraft Mod.
	"""

	def __init__(self, config_file, verbose=None):
		"""
		Initializes the ``InstallCommand`` instance.

		*config_file* (``str``) is the **mcpackage** configuration file to
		use.

		*verbose* (``int``) is the level of verbose debugging information to
		be printed. Default is ``None`` for `0`.

		- `0`: print no debugging information.

		- `1`: print some debugging information.

		- `2`: print lots of debugging information.
		"""

		self.config_file = config_file
		"""
		*config_file* (``str``) is the mcpackage configuration file to use.
		"""

		self.log = None
		"""
		*log* (``logging.Logger``) is the main logger.
		"""

		self.verbose = verbose or 0
		"""
		*verbose* (``int``) is the level of verbose debugging information to
		be printed.
		"""

	def run(self):
		"""
		Runs the "install" command.

		Returns the exit code (``int``).
		"""
		raise NotImplementedError("TODO")
