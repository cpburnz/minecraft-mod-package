

NOTICE
======

This is still under development, not necessarily stable, lacks formal
documentation, and has no examples.


*mcpackage*: Minecraft Mod Packaging Tool
=========================================

*mcpackage* is used to compile, obfuscate, and package Minecraft Mods by using
`Forge`_ and `MCP`_. Its primary use is to build `PyMod`_ and any other mods
depending on `PyMod`_ for `Minecraft`_.

.. _`Forge`: http://www.minecraftforge.net
.. _`MCP`: http://mcp.ocean-labs.de
.. _`PyMod`: https://github.com/cpburnz/minecraft-mod-python
.. _`Minecraft`: https://minecraft.net


Tutorial
--------

TODO: Copy how to build PyMod.


License
-------

*mcpackage* is licensed under the `Mozilla Public License Version 2.0`_. See
*LICENSE* or the `FAQ`_ for more information.

In summary, you may use *mcpackage* with any closed or open source project
without affecting the license of the larger work so long as you:

- give credit where credit is due,

- and release any custom changes to *mcpackage*.

.. _`Mozilla Public License Version 2.0`: http://www.mozilla.org/MPL/2.0
.. _`FAQ`: http://www.mozilla.org/MPL/2.0/FAQ.html


Source
------

The source code for *mcbuild* is available from the GitHub repo
`cpburnz/minecraft-python-build`_.

.. _`cpburnz/minecraft-python-build`: https://github.com/cpburnz/minecraft-python-build


Requirements
------------

Required Python Modules:

- `setuptools`_ for installation.

- `PyYAML`_ for configuration files.

- `pathspec`_ for file pattern matching.

Required Development Environment:

- Forge (TODO: DOCUMENT USE)
- MCP (TODO: DOCUMENT USE)

.. _`setuptools`: https://pypi.python.org/pypi/setuptools
.. _`PyYAML`: https://pypi.python.org/pypi/PyYAML
.. _`pathspec`: https://pypi.python.org/pypi/pathspec
.. _`Forge`: http://files.minecraftforge.net
.. _`MCP`: http://mcp.ocean-labs.de/download.php?list.2


Installation
------------

*mcpackage* can be installed from source with::

	python setup.py install


Documentation
-------------

TODO
