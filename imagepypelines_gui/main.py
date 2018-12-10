import sys

from PyQt4 import QtGui

from MainWindow import MainWindow


def main():
    app = QtGui.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.setGeometry(100, 100, 800, 500)   # TODO figure this out. Should not need to be set here
    # TODO: add logo properly
    mainWindow.setWindowIcon(QtGui.QIcon(':/images/ImSciUtils-Favicon.png'))
    app.setWindowIcon(QtGui.QIcon(':/images/ImSciUtils-Favicon.png'))
    mainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':

    main()

    # test code
    # classa = ip.builtin_pipelines.SimpleImageClassifier();addPipeline(classa)
    # 

    # qscene.display_pipeline(ip.SimpleImageClassifier())
    # import QtPipeline as p;qscene.display_pipeline(p.exp())