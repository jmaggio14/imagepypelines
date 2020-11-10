.. post:: 24 Oct, 2020
   :tags: science, imagepypelines, portability
   :category: Motivation
   :author: Jeff
   :excerpt: 2
   :image: 1

.. _XKCD: https://xkcd.com/054/

Let's be honest, code in science isn't portable
===============================================


By `Jeff Maggio <https://www.jeffmagg.io>`_
-------------------------------------------


I recently read an excellent `blog post by Ishan Mishra <https://astrobites.org/2020/10/23/towards-better-research-code-and-software/>`_ on `Astrobites <https://astrobites.org/>`_. He lays out a compelling case for changing the way we code in science.

As a student, and a research engineer, I frequently encountered the "messy monster codes" he describes. I've written plenty of them myself. The competitive and sometimes snotty nature of academia prioritizes results. We focus on how we can get our code to run now. We interlace our code with print statement. We run our code again and again after each incremental change. Too often our comments are out of date or confusing. Ishan points out four ways we can make these codes better:

    #. Modularity
    #. Documentation
    #. Testing
    #. Version Control

Sounds easy and obvious right? Except it isn't...

As a research engineer at the University of Rochester, I was actively discouraged from writing professional code, and for an understandable reason - not enough scientists know how to use modules or object oriented programming. We were encouraged to write code that looked familiar - with as few files as possible, to not use classes, and discouraged from using servers, and locked into what 3rd party tools people were already familiar with. In other words, the typical software development environment was discouraged.

When the pressure is on to write code quickly to solve one specific task, good software practices always take a back seat. In addition, there is good reason to avoid overcomplicating software - we need students and scientists to be able to work with these tools without being held back by a steep technical learning curve. But no one can deny that we pay a price for it too...

*How often do we write hardcoded scripts that are impossible to port over to your colleagues computer? How often do we have to rewrite code we've written a dozen times before because we never wrote them in a modular way? How often do our scripts break the moment an input does anything weird???*


.. figure:: https://imgs.xkcd.com/comics/data_pipeline.png
    :align: center
    :target: https://xkcd.com/054/
    :alt: XKCD data pipeline
    :figclass: align-center

    XKCD_ sums it up better than I can


What we need is a middle ground between the messy monster scripts that are ubiquitous in science, and the prim and professionally managed software that demands so much time and skill. That's why I started **ImagePypelines**.


Turn a script into a powerful tool
-----------------------------------


ImagePypelines is a library to turn scripts into a robust processing pipeline. **It was designed by scientists, for scientists.**

Let's imagine a short messy script where we want to read in fits files, and perform image reduction on them. *(I'm an aspiring astronomer... just saying for anyone on the lookout for graduate students)*


*work in progress*

You can imagine how this may be difficult to read or reuse.

We can clean it up somewhat by reorganizing things into functions


This is where ImagePypelines really shines!


With ImagePypelines, one of most aggravating parts of astronomy is a breeze.
