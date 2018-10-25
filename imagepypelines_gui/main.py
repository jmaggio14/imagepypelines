from PyQt5 import QtWidgets, QtCore, QtGui

from QtInterp import Interpreter


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(self)
        self.commands = Commands(self)
        self.setup_ui()

    def setup_ui(self):
        #self.setWindowTitle('SignalShow(er)')
        #self.setWindowIcon(QtGui.QIcon('logo.png'))
        self.main_widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QHBoxLayout(self.main_widget)

        self.interp = Interpreter(self.main_widget, variables={'commands':self.commands})
        self.layout.addWidget(self.interp)

        self.tree_widget = Variables(self.main_widget)
        self.layout.addWidget(self.tree_widget)

        # connect slots and fire signal once so that builtins appear
        self.interp.variables.connect(self.tree_widget.get_items)
        self.interp.variables.emit(self.interp.locals)

        # set focus and main widget
        self.setCentralWidget(self.main_widget)
        self.main_widget.setFocus()


def main():

    app = QtWidgets.QApplication(sys.argv)

    # set up main display window

    display = ApplicationWindow()
    display.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
