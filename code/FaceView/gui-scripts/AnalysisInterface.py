"""
Qt GUI for the FaceView software

"""

from PyQt4 import QtGui, uic, QtCore
import sys, os, math

if __name__=="__main__":
    os.chdir('..')

sys.path.append('./objViewer')

import objWindow
import objModel

# replace 'c:/test.ui' with real path to ui-file created in QtDesigner
uifile = './gui-scripts/analysisview.ui'
form, base = uic.loadUiType(uifile)

class analysisWindow(QtGui.QMainWindow):
    def __init__(self, widgets=[], feature_map={}, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        
        self.ui.setupUi(self)
        self.faces = widgets
        self.feature_map = feature_map
        self.size = math.ceil(math.sqrt(len(widgets))) or 1
        self.loadWidgets()

        self.ui.FrontView.clicked.connect(self.frontView)
        self.ui.SideView.clicked.connect(self.sideView)
        self.ui.TopView.clicked.connect(self.topView)
        self.ui.IsoView.clicked.connect(self.isoView)

    def loadWidgets(self):
        grid = self.ui.Grid
        for idx, widget in enumerate(self.faces):
            grid.addWidget(widget, idx/self.size, idx%self.size)

    def frontView(self):
        for widget in self.faces:
            widget.rotate(0,0)

    def sideView(self):
        for widget in self.faces:
            widget.rotate(0,90)
    
    def topView(self):
        for widget in self.faces:
            widget.rotate(-90, 0)

    def isoView(self):
        for widget in self.faces:
            widget.rotate(-30, 30)

def main():
    app = QtGui.QApplication(sys.argv)

    model = objModel.ObjModel('../models/Sample 1.obj')
    widget = objWindow.ObjWidget(model, True)
    widget.show()
    
    myapp = thumbnailWindow([widget], {})
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    main()


