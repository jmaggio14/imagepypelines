"""
Syntax Intro
============

How to leverage the syntax of ImagePypelines effectively!
"""

###############################################################################
# Let's try blockifying vs using a FuncBlock vs using a Block subclass

# NOTE: can't blockify built-ins or c-functions *directly* (they don't have a signature!!!)

import imagepypelines as ip

def print_msg(msg):
    print(msg)

print_msg1 = ip.FuncBlock(print_msg, void=True)

@ip.blockify(void=True)
def print_msg2(msg):
    print(msg)

class PrintMsg(ip.Block):
    def __init__(self, **block_kwargs):
        super().__init__(name="PrintMsg", **block_kwargs)
    def process(self, msg):
        print_msg(msg)

print_msg3 = PrintMsg()

print_msg("Blah blah")
print_msg1("Blah1 blah1!")
print_msg2("Blah2 blah2!!")
print_msg3.process("Blah3 blah3!!!")
print_msg3("Blah4 blah4!!!!")

###############################################################################
# tasks = {'msg':ip.Input(),
#          'null':(print_msg, 'msg')}
#
#
# msg_printer = ip.Pipeline(tasks)

###############################################################################
# processed = msg_printer.process(["Hello World!"])

###############################################################################
# We can pass in any data we want! In this example, we call this function
# once for every datum passed in
# processed = msg_printer.process(['we','can','print','anything','individually!'])

###############################################################################
# We can also print everything at once with the `batch_type` variable
# -------------------------------------------------------------------
#
# @ip.blockify(batch_type="all", void=True)
# def print_all(msg):
#     print(msg)
#
# tasks = {'msg':ip.Input(),
#          'null':(print_all, 'msg')}
# print_all_pipeline = ip.Pipeline(tasks)
#
# processed = print_all_pipeline.process(['we','can','print','everything','at','once!'])
