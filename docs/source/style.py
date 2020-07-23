################################################################################
# set our own custom syntax highlighting stlyer
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic

# SEE DETAILS HERE: https://pygments.org/docs/styles/#creating-own-styles
class ImagePypelinesStyle(Style):
    default_style = ""
    styles = {
            Comment: 'italic #FF5D00',
            Keyword: 'bold #BF0000',
            Name: '#FF4D00',
            Name.Function: '#380915',
            Name.Class: 'bold #191C3A',
            String: '#AED9E8',
            Number: '#AED9E8',
            Operator: '#BF0000',
            Generic: '#FF5D00 bg: #EBDCC1',
            Error: '#380915 bg: #191C3A'
            }

# see Sphinx: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-pygments_style
################################################################################
