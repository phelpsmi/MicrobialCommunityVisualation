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

        self.parent = parent
        self.ui = form()

        
        self.ui.setupUi(self)
        self.faces = widgets
        self.feature_map = feature_map
        self.size = math.ceil(math.sqrt(len(widgets))) or 1
        self.loadWidgets()
        self.loadMap()
        self.setMouseTracking(False)

        self.ui.Table.setColumnWidth(0, 228)
        self.ui.Table.setColumnWidth(1, 200)

        self.ui.FrontView.clicked.connect(self.frontView)
        self.ui.SideView.clicked.connect(self.sideView)
        self.ui.TopView.clicked.connect(self.topView)
        self.ui.IsoView.clicked.connect(self.isoView)
        self.ui.Back.clicked.connect(self.back)

    def mouseMoveEvent(self, event):
        x_dif = self.x - event.x()
        y_dif = self.y - event.y()
        self.x = event.x()
        self.y = event.y()
        
        for widget in self.faces:    
            widget.relativeRotate(y_dif/4, x_dif/4)

    def mousePressEvent(self, event):
        self.x = event.x()
        self.y = event.y()

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
            widget.rotate(0, -90)

    def isoView(self):
        for widget in self.faces:
            widget.rotate(-30, 30)

    def loadMap(self):
        i = 0
        table = self.ui.Table
        table.clearContents()
        table.setRowCount(len(self.feature_map))
        for org, feature in self.feature_map.iteritems():
            org_item = QtGui.QTableWidgetItem(org)
            feature_item = QtGui.QTableWidgetItem(feature)
            table.setItem(i, 0, org_item)
            table.setItem(i, 1, feature_item)
            i += 1

    def back(self):
        self.parent.show()
        self.close()
        

def main():
    app = QtGui.QApplication(sys.argv)

    model = objModel.ObjModel('../models/Sample 1.obj')
    widget = objWindow.ObjWidget(model, True)
    widget.show()

    test_map = {"org1":"feature1", "org2":"feature2", "org3":"feature3"}
    myapp = analysisWindow([widget], test_map)
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    main()


