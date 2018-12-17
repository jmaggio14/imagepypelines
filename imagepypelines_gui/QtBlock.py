# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)
import math
from PyQt4 import QtCore, QtGui


from diagram_items import DiagramItem, DiagramTextItem, Arrow

class QtBlock(DiagramItem):
    def __init__(self, contextMenu=None, parent=None, block=None, scene=None, itemType=DiagramItem.Block):
        super(QtBlock, self).__init__(itemType, contextMenu, parent, scene)

        self.start = itemType == DiagramItem.Start

        self._block = block

        if self.start:
            self.name = "Start"
        else:
            self.name = self._block.name

        self.textItem = DiagramTextItem(parent, scene)
        self.textItem.setPlainText(self.name)

    def setPos(self, y, x):
        #print(y,x)
        super(QtBlock, self).setPos(y, x)

        # TODO center the text (use boundingRect on self and on the textItem)?
        # TODO add other info
        self.textItem.setPos(y, x)
        self.textItem.setPlainText(self._block.name)
