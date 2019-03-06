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

    def __init__(self, itemMenu, parent=None, pipeline=None, blocks=[]):
        super(QtPipeline, self).__init__(itemMenu)

        self.itemsConnected.connect(self.on_blocks_connected)
        self.itemInserted.connect(self.on_block_inserted)

        self._blocks = blocks  # this holds the function references to the items that make up the pipeline
        
        if isinstance(pipeline, ip.Pipeline):
            self._pipeline = pipeline
        else:
            self._pipeline = ip.Pipeline(blocks=self._blocks)

        self.name = self._pipeline.name

        # TODO decide this scaling.
        self.setSceneRect(QtCore.QRectF(0, 0, 5000, 5000))
        self.display_pipeline()

    def verify_pipeline(self):
        pass
        # verify the pipeline connections

        # turn arrows to green if OK, red if not

        # turn blocks red if they need an input, maybe highlight a field?

    def on_blocks_connected(self, b1, b2):
        # when two blocks are connected, then insert it into the pipeline (if it belongs)

        # turn the arrow connection yellow   
        pass

    def on_block_inserted(self, block):
        if isinstance(block, QtBlock):
            print('TODO add the block to the pipeline')

        pass    

    def save(self, filename):
        self._pipeline.save(filename)

    def process(self):
        self._pipeline.process()

    def display_pipeline(self):
        for item in self.items():
            self.removeItem(item)

        position = np.asarray(
            [self.sceneRect().width()/2, self.sceneRect().height()/2])

        #print(position)
        self._blocks = [self.make_block(block=None, itemType=DiagramItem.Start)]

        for block in self._pipeline.blocks:
            qblock = self.make_block(block, DiagramItem.Block)
            qblock.setPos(*position)

            self._blocks.append(qblock)

            position += [300, 0]   # TODO make this robust

        for i in range(len(self._blocks) - 1):
            self.connect_blocks(self._blocks[i], self._blocks[i+1])

    def make_block(self, block, itemType):
        qblock = QtBlock(block=block, contextMenu=self.myItemMenu, scene=self, itemType=itemType)
        qblock.setBrush(self.myItemColor)

        qblock.textItem.setFont(self.myFont)
        qblock.textItem.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        qblock.textItem.setZValue(1000.0)
        # qblock.textItem.lostFocus.connect(self.editorLostFocus)
        qblock.textItem.selectedChange.connect(self.itemSelected)
        qblock.textItem.setDefaultTextColor(self.myTextColor)
        
        self.addItem(qblock)
        self.textInserted.emit(qblock.textItem)
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
        self.itemsConnected.emit(blockitem1, blockitem2)

        return arrow
