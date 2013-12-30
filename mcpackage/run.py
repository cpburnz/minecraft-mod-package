# coding: utf-8
"""
This module implements the "run" command which is used to run Minecraft.
"""

def command(**args):
	"""
	Runs Minecraft.

	`**args` is the keyword arguments to send to ``RunCommand()``.

		Returns the exit code (``int``).
	"""
	return RunCommand(**args).run()


class RunCommand(object):
	"""
	The ``RunCommand`` class is used to run Minecraft.
	"""

	def __init__(self, config_file, verbose=None):
		"""
		Initializes the ``RunCommand`` instance.

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
		Runs the "run" command.

		Returns the exit code (``int``).
		"""
		raise NotImplementedError("TODO")
