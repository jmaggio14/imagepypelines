import sys
sys.path.insert(0, '..')
import imagepypelines as ip

from PyQt4 import QtGui, QtCore
import numpy as np

from diagram_items import Arrow, DiagramTextItem, DiagramItem
from diagramscene import DiagramScene
from QtBlock import QtBlock


def make_example_pipeline():
    image_loader = iu.ImageLoader()
    resizer = iu.Resizer(512,512)
    color2gray = iu.Color2Gray()
    orb = iu.Orb()
    # creating pipeline with all blocks
    pipeline = iu.Pipeline(blocks=[image_loader,resizer,color2gray,orb])

    return pipeline

exp = make_example_pipeline


class QtPipeline(DiagramScene):

    blockInserted = QtCore.pyqtSignal(QtGui.QGraphicsItem)
    blocksConnected = QtCore.pyqtSignal(QtGui.QGraphicsItem, QtGui.QGraphicsItem)

    def __init__(self, itemMenu, parent=None, pipeline=None):
        super(QtPipeline, self).__init__(itemMenu)
        
        if pipeline:
            self._pipeline = pipeline
        else:
            self._pipeline = ip.Pipeline()

        self.name = self._pipeline.name

        self.setSceneRect(QtCore.QRectF(0, 0, 5000, 5000))
        self.display_pipeline()

    def save(self, filename):
        self._pipeline.save(filename)

    def process(self):
        self._pipeline.process()

    def display_pipeline(self):
        for item in self.items():
            self.removeItem(item)

        position = np.asarray(
            [self.sceneRect().width()/2, self.sceneRect().height()/2])

        print(position)

        blockitems = []
        for block in self._pipeline.blocks:
            qblock = self.make_block(block)
            qblock.setPos(*position)

            blockitems.append(qblock)

            position += [300, 0]   # TODO make this robust

        for i in range(len(blockitems) - 1):
            self.connect_blocks(blockitems[i], blockitems[i+1])

    def make_block(self, block):
        qblock = QtBlock(block=block, diagramType=DiagramItem.Step, contextMenu=self.myItemMenu, scene=self)
        qblock.setBrush(self.myItemColor)

        qblock.textItem.setFont(self.myFont)
        qblock.textItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        qblock.textItem.setZValue(1000.0)
        # qblock.textItem.lostFocus.connect(self.editorLostFocus)
        qblock.textItem.selectedChange.connect(self.itemSelected)
        qblock.textItem.setDefaultTextColor(self.myTextColor)
        self.textInserted.emit(qblock.textItem)

        self.addItem(qblock)
        self.itemInserted.emit(qblock)
        
        return qblock

    def connect_blocks(self, blockitem1, blockitem2):
        arrow = Arrow(blockitem1, blockitem2)
        arrow.setColor(self.myLineColor)
        blockitem1.addArrow(arrow)
        blockitem2.addArrow(arrow)
        arrow.setZValue(-1000.0)
        self.addItem(arrow)
        arrow.updatePosition()
        return arrow
