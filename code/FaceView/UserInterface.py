"""
Qt GUI for the FaceView software

"""

from PyQt4 import QtGui, uic, QtCore
import sys

# replace 'c:/test.ui' with real path to ui-file created in QtDesigner
uifile = '../QtCreator/FaceView/mainwindow.ui'
form, base = uic.loadUiType(uifile)

class loadingWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        
        self.ui.setupUi(self)

        #Set triggers for buttons
        self.ui.SelectDataFile.clicked.connect(self.setDataFile)
        self.ui.SelectGroupFile.clicked.connect(self.setGroupFile)
        self.ui.Cancel.clicked.connect(QtCore.QCoreApplication.instance().quit)


    def setDataFile(self):
        self.ui.DataFilePath.setText(QtGui.QFileDialog.getOpenFileName())
        
    def setGroupFile(self):
        self.ui.GroupingFilePath.setText(QtGui.QFileDialog.getOpenFileName())


def main():
    app = QtGui.QApplication(sys.argv)
    myapp = loadingWindow()
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    main()

