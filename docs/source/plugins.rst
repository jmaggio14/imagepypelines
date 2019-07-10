====================================
How to make an ImagePypelines plugin
====================================

ImagePypelines provides support for other developers to add accessory
functionality. Plugins will be loaded and accessible under their own namespace

Encourage your users to use the function *ip.require_plugin("<your_plugin>")*
at the top level of their scripts to ensure the plugin is loaded correctly.

Simply Define an entrypoint 'imagepypelines.plugins' in your setup.py

.. code-block:: python

    >>> setup(
    ...        entry_points={'imagepypelines.plugins': '<plugin_name> = <package_name>'}
    ...     ) # doctest: +SKIP

please check out the following link for more information:
https://packaging.python.org/guides/creating-and-discovering-plugins/

**Modules are loaded by alphabetical order**

Requirements
============


Plugin modules must meet the following requirements:
----------------------------------------------------

1) They must provide a module-level function 'help', which should return a string
which would provide a naive user with a short description, links to
documentation, and any other information the developer deems important



Plugin Modules SHOULD meet the following requirements:
------------------------------------------------------

1) Do all their own dependency checking


WARNING:
~~~~~~~~
Many ImagePypelines users will require your Pipelines and Blocks to be
picklable and unpickable. This is critical for core functionality such as
server deployment and saving to disk. Please make sure your Pipelines and Blocks
are picklable
