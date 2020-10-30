################################################################################
# set our own custom syntax highlighting stlyer
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Punctuation

# SEE DETAILS HERE: https://pygments.org/docs/styles/#creating-own-styles
class ImagePypelinesLight(Style):
    default_style = ""
    # background_color = "#EBDCC1"
    # highlight_color = "#EBDCC1"

    # define colors as variables
    cream = "#FFFDD0"
    gray = "#9ea6a8"

    bright_orange = "#FF5D00"
    orange = "#FF4D00"
    red = "#FF0000"
    blue = "#09aee6"
    purple = "#77216F"

    dark_orange = "#E95420" # ubuntu orange
    dark_red = "#BF0000"
    dark_purple = "#2C001E"
    dark_blue = "#3A87AD"

    light_gray = ""
    light_blue = "#7BABE0"
    light_purple = "#BB94A9"
    light_orange = "#F4AA90"

    decorator = "bold #af7dff"


    styles = {
            Comment: 'italic '+ gray,
            Keyword: 'bold '+orange,
            Name: purple,
            Name.Function: 'bold '+dark_red,
            Name.Decorator: decorator,
            # Name.Namespace: light_orange,
            Name.Class: 'bold '+red,
            String: 'bold ' +blue,
            Number: blue,
            Operator: 'bold '+orange,
            Generic: orange,
            Text: orange,
            Punctuation: orange,
            Error: 'bg:'+dark_blue+' '+cream
            }

# see Sphinx: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-pygments_style
################################################################################
