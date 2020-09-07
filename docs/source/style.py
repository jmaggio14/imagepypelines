################################################################################
# set our own custom syntax highlighting stlyer
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic

# SEE DETAILS HERE: https://pygments.org/docs/styles/#creating-own-styles
class ImagePypelinesStyle(Style):
    default_style = ""
    background_color = "bg:#EBDCC1"
    # highlight_color = "#49483e"
    styles = {
            Comment: 'italic #BF0000',
            Keyword: 'bold #BF0000',
            Name: 'bg:#EBDCC1 #FF4D00',
            Name.Function: '#380915',
            Name.Class: 'bold #191C3A',
            String: '#7BABE0',
            Number: '#7BABE0',
            Operator: '#BF0000',
            Generic: 'bg:#EBDCC1 #FF5D00 ',
            Error: 'bg:#191C3A #380915'
            }

# see Sphinx: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-pygments_style
################################################################################
