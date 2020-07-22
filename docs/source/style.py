################################################################################
# set our own custom syntax highlighting stlyer
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

# SEE DETAILS HERE: https://pygments.org/docs/styles/#creating-own-styles
class ImagePypelinesStyle(Style):
    default_style = ""
    styles = {
            Comment: 'italic #080808',
            Keyword: 'bold #000005',
            Name: '#0000ff',
            Name.Function: '#00ff00',
            Name.Class: 'bold #00ff00',
            String: '#E95420 bg: '
            }

# see Sphinx: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-pygments_style
################################################################################
