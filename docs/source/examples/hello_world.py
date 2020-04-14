import imagepypelines as ip
@ip.blockify(void=True)
def print_msg(msg):
    print(msg)

tasks = {'msg':ip.Input(),
         'null':(print_msg, 'msg')}
msg_printer = ip.Pipeline(tasks)

processed = msg_printer.process(["Hello World!"])

# Hello World!

processed = msg_printer.process(['we','can','print','anything','individually!'])

# we
# can
# print
# anything
# individually!

@ip.blockify(batch_type="all", void=True)
def print_all(msg):
    print(msg)

tasks = {'msg':ip.Input(),
         'null':(print_all, 'msg')}
print_all_pipeline = ip.Pipeline(tasks)

processed = print_all_pipeline.process(['we','can','print','everything','at','once!'])

# ['we', 'can', 'print', 'everything', 'at', 'once!']
