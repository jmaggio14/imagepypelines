import sys
import traceback
from termcolor import colored
import inspect

def find_between_substrings(s,start,end):
    remaining = s
    subs = []
    while True:
        i = remaining.find(start)
        j = remaining[i+len(start):].find(end) + i + len(start)
        if j == -1 or i == -1:
            break
        elif not j <= i:
            subs.append( remaining[i+len(start):j] )

        remaining = remaining[j:]

    return subs






def main(readme_path):
    # JM: open readme as string
    with open(readme_path,'r') as f:
        text = f.read()

    # JM: find sections of code between "```python" and ```
    code_blocks = find_between_substrings(text,"```python","```")

    print("found {} code blocks".format( len(code_blocks) ))
    # JM: testing each code block for errors
    success = []
    for i,code in enumerate(code_blocks):
        # JM: wrapping our test code in a try statement statements
        try:
            print('>>>> readme example {}'.format(i) )
            code_locals = {}
            code_globals = {}
            exec(code,code_locals,code_locals)
            print( colored(">>>>> readme example %s ran without errors" % i,'green',attrs=['bold']) )
            print("\n\n")
            success.append(True)

        except Exception as e:
            # printing out the failed code and the traceback
            print( colored(">>>>> readme example %s failed, code below:" % i,'red') )
            print( code )
            print("\n\n")
            success.append(False)

    sys.exit(not all(success))



if __name__ == '__main__':
    import argparse
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--readme_path',
                        help='the path to the readme file',
                        default='./README.md',
                        )
    args = parser.parse_args()
    main(args.readme_path)
