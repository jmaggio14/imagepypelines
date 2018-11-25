import sys

from PyQt4 import QtGui

from MainWindow import MainWindow


def main():
    app = QtGui.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.setGeometry(100, 100, 800, 500)
    mainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':

    main()

    # test code
    # qscene.display_pipeline(ip.SimpleImageClassifier())
    # import QtPipeline as p;qscene.display_pipeline(p.exp())