
*mcpackage*: Minecraft Mod Packaging Tool
=========================================

*mcpackage* is used to compile, obfuscate, and package Minecraft Mods by using
`Forge`_ and `MCP`_. Its primary use is to build and package `PyMod`_ and any
other mods depending on `PyMod`_ for `Minecraft`_.

.. _`Forge`: http://www.minecraftforge.net
.. _`MCP`: http://mcp.ocean-labs.de
.. _`PyMod`: https://github.com/cpburnz/minecraft-mod-python
.. _`Minecraft`: https://minecraft.net


NOTICE
------

This is still under development, not necessarily stable, lacks formal
documentation, and has no examples.


TODO
----

- Create "init" command to generate skeleton project.

- Refactor "build" command.

- Create "install" command to copy jar to minecraft directory.

- Create "run" command to run minecraft using proper Forge profile.

- Tutorial for how to build and package *pymod*.

- Generate documentation.

  - https://github.com/MinecraftForge/FML/wiki/FML-mod-information-file

- Later:

  - Make "init" command interactive.


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

- and release any custom changes made to *mcpackage*.

.. _`Mozilla Public License Version 2.0`: http://www.mozilla.org/MPL/2.0
.. _`FAQ`: http://www.mozilla.org/MPL/2.0/FAQ.html


Source
------

The source code for *mcpackage* is available from the GitHub repo
`cpburnz/minecraft-mod-package`_.

.. _`cpburnz/minecraft-mod-package`: https://github.com/cpburnz/minecraft-mod-package


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


.. image:: https://d2weczhvl823v0.cloudfront.net/cpburnz/minecraft-mod-package/trend.png
   :alt: Bitdeli badge
   :target: https://bitdeli.com/free
