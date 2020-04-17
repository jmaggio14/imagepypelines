=======
Plugins
=======

About Plugins
-------------
All tools in ImagePypelines are developed and maintained in the form of plugins.
We maintain several :ref:`offical-plugins` for applications in Imaging Science
and Astronomy.



Section to cross-reference
--------------------------

This is the text of the section.

It refers to the section itself, see :ref:`my-reference-label`.


We encourage 3rd parties to make plugins for other applications, but **cannot
speak for their specific licensing restrictions or usability.**


How to make an ImagePypelines plugin
************************************
We provide a template for you to construct your own plugins. Just copy and paste
your code, and change a few variables!

Click on this `link <https://github.com/RyanHartzell/imagepypelines_template>`_
to get started.



Already made your own plugin?
-----------------------------

`Email us! <mailto:jmaggio14@gmail.com>`_ We can talk about hosting your documentation on this site! Or we'll link
to your official documentation :p.

.. WARNING:
.. ~~~~~~~~
.. Many ImagePypelines users will require your Pipelines and Blocks to be
.. picklable and unpickable. This is critical for core functionality such as
.. server deployment and saving to disk. Please keep this in mind, especially if
.. your blocks use tools like `tensorflow`
