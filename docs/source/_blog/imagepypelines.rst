
.. post:: 24 Oct, 2020
   :tags: science, imagepypelines, portability
   :category: Motivation
   :author: Maggio, Jeff
   :location: Rochester, NY
   :excerpt: 2
   :image: 1

Let's by honest, code in science isn't portable
===============================================

I recently read an excellent `blog post by Ishan Mishra <https://astrobites.org/2020/10/23/towards-better-research-code-and-software/>, on Astrobites:`_. He lays out a compelling case for changing the way we code in science.

As a student, and a research engineer, I frequently encountered the "messy monster codes" he describes. I've written plenty of them myself. The competitive and sometimes snotty nature of academia prioritizes results. We focus on how we can get our code to run now. We write code in scripts, updated incrementally with print statements and confusing comments.

As a research engineer at the University of Rochester, I was actively discouraged from writing professional code, and for an understandable reason - not enough scientists know how to use modules or object oriented programming. We were encouraged to write code that looked familiar - with as few files as possible, to not use classes, and discouraged from using servers, no installation required. In other words, the typical software development environment was discouraged.

There is good reason to avoid overcomplicating software - we need students and scientists to be able to work with these tools without such a steep learning curve. But no one can deny that we pay a price for it too. Too often scientific tools are hardcoded and impossible to port over to your colleagues computer.



What we need is a middle ground between the messy monster scripts that are ubiquitous in science, and the prim and professionally managed software.


Clearly something has to change in scientific programming. ImagePypelines offers a potential solution.


ImagePypelines
