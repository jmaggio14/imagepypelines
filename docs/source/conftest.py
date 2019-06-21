from os import chdir, getcwd
from shutil import rmtree
from tempfile import mkdtemp
import pytest
from sybil import Sybil
from sybil.parsers.codeblock import CodeBlockParser
from sybil.parsers.doctest import DocTestParser
from doctest import ELLIPSIS
import doctest

doctest.ELLIPSIS_MARKER = '[...]'

pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        CodeBlockParser(),
    ],
    pattern='*.rst',
).pytest()
