"""
Hello World!
============

Learn the basics with Hello World!
"""

###############################################################################
# At it's core ImagePypelines is just a way to string functions and algorithms
# together.

import imagepypelines as ip
@ip.blockify(void=True)
def print_msg(msg):
    print(msg)

tasks = {'msg':ip.Input(),
         'null':(print_msg, 'msg')}
msg_printer = ip.Pipeline(tasks)

processed = msg_printer.process(["Hello World!"])

###############################################################################
# We can pass in any data we want! In this example, we call this function
# once for every datum passed in
processed = msg_printer.process(['we','can','print','anything','individually!'])

###############################################################################
# We can also print everything at once with the `batch_type` variable
# -------------------------------------------------------------------
#
@ip.blockify(batch_type="all", void=True)
def print_all(msg):
    print(msg)

tasks = {'msg':ip.Input(),
         'null':(print_all, 'msg')}
print_all_pipeline = ip.Pipeline(tasks)

processed = print_all_pipeline.process(['we','can','print','everything','at','once!'])
