# coding: utf-8
"""
${mod_name}.
"""

from cpburnz.minecraft.pymod.py import PythonMod

class ${mod_class}(PythonMod):
	"""
	${mod_name}.
	"""

	def preInit(self, event):
		"""
		Called when the pre-initialization event occurs. This is run before
		anything else. Read your config, create blocks, items, etc., and
		register them with the ``GameRegistery``.

		*event* (``cpw.mods.fml.common.event.FMLPreInitializationEvent``) is
		the pre-initialization event.
		"""
		pass

	def init(self, event):
		"""
		Called when the initialization event occurs. Do your mod setup.
		Build whatever data structures you care about. Register recipes,
		send inter-mod communication messages to other mods.

		*event* (``cpw.mods.fml.common.event.FMLInitializationEvent``) is
		the initialization event.
		"""
		pass

	def postInit(self, event):
		"""
		Called when the post-initialization event occurs. Handle interaction
		with other mods, complete your setup based on this.

		*event* (``cpw.mods.fml.common.event.FMLPostInitializationEvent``)
		is the post-initialization event.
		"""
		pass
