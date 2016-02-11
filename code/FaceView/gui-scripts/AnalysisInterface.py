"""
Qt GUI for the FaceView software

"""

from PyQt4 import QtGui, uic, QtCore
import sys

# replace 'c:/test.ui' with real path to ui-file created in QtDesigner
uifile = './analysisview.ui'
form, base = uic.loadUiType(uifile)

class thumbnailWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        
        self.ui.setupUi(self)

def main():
    app = QtGui.QApplication(sys.argv)
    myapp = thumbnailWindow()
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    main()


