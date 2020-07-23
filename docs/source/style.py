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
            Keyword: 'bold #AED9E8',
            Name: '#FF4D00',
            Name.Function: '#FF5D00',
            Name.Class: 'bold #191C3A',
            String: '#AED9E8 bg: '
            }

# see Sphinx: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-pygments_style
################################################################################
