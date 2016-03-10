"""
Qt GUI for the FaceView software

"""

from PyQt4 import QtGui, uic, QtCore
import sys
import glob, os
import math

if __name__=="__main__":
    os.chdir('..')

import AnalysisInterface

sys.path.append('./objViewer')

import objWindow
import objModel
import grouping

# replace 'c:/test.ui' with real path to ui-file created in QtDesigner
uifile = 'gui-scripts/thumbnailview.ui'
form, base = uic.loadUiType(uifile)

class thumbnailWindow(QtGui.QMainWindow):
    def __init__(self, sample_count, samples, groups, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        self.ui.setupUi(self)

        self.sample_count = 0
        self.samples = samples
        self.groups = groups

        self.initGroupList()
        self.loadObjects()

        self.ui.CreateGroup.clicked.connect(self.createGroup)
        self.ui.AddSelected.clicked.connect(self.addToGroup)
        self.ui.RemoveSelected.clicked.connect(self.removeFromGroup)
        self.ui.DeleteGroup.clicked.connect(self.deleteGroup)
        self.ui.ViewSelect.activated.connect(self.selectGroup)
        self.ui.Analyze.clicked.connect(self.analyze)
        self.objWidgets = []

    # Checks if the mouse was hovered over a face on click.
    # If it is we toggle the highlight which requires reloading
    # the widget.
    def mouseReleaseEvent(self, event):
        grid = self.ui.Grid

        widget, row, col = self.hoveredWidget(event)
        if not widget is None:
            if widget.highlighted:
				widget.setHighlighted(False)
                #new_widget = objWindow.ObjWidget(widget.data, False)
            else:
				widget.setHighlighted(True)
                #new_widget = objWindow.ObjWidget(widget.data, True)

            #grid.removeWidget(widget)
            #grid.addWidget(new_widget, row, col)

    def hoveredWidget(self, event):
        grid = self.ui.Grid
        for i in range(self.sample_count):
            item = grid.itemAtPosition(i/self.size, i%self.size)

            if item.geometry().contains(event.pos()):
                return (item.widget(), i/self.size, i%self.size)

        return (None, None, None)

    def selectGroup(self):
        group = self.groups[self.ui.ViewSelect.currentIndex()]
        self.clearAllWidgets()
        for g_sample in group.getSamples():
            for idx, sample in enumerate(self.samples):
                if g_sample.getName() == sample.getName():
                    self.highlightWidget(idx)

    def highlightWidget(self, idx):
        row = idx/self.size
        col = idx%self.size
        print idx

        grid = self.ui.Grid
        widget = grid.itemAtPosition(row, col).widget()
        if not widget.highlighted:
			widget.setHighlighted(True)
            #new_widget = objWindow.ObjWidget(widget.data, True)
            #grid.removeWidget(widget)
            #grid.addWidget(new_widget, row, col)

    def clearWidget(self, idx):
        row = idx/self.size
        col = idx%self.size

        grid = self.ui.Grid
        widget = grid.itemAtPosition(row, col).widget()
        if widget.highlighted:
			widget.setHighlighted(False)
            #new_widget = objWindow.ObjWidget(widget.data, False)
            #grid.removeWidget(widget)
            #grid.addWidget(new_widget, row, col)

    def clearAllWidgets(self):
        for i in range(self.sample_count):
            self.clearWidget(i)

    def initGroupList(self):
        self.ui.ViewSelect.clear()
        self.ui.ModifySelect.clear()
        for group in self.groups:
            self.ui.ViewSelect.addItem(group.getName())
            self.ui.ModifySelect.addItem(group.getName())

    def createGroup(self):
        if not str(self.ui.CreateName.text()):
            QtGui.QMessageBox.about(self, "Error", "Name cannot be blank!")
            return
        
        name = str(self.ui.CreateName.text())
        group = grouping.Group(name)

        self.groups.append(group)
        self.ui.ViewSelect.addItem(name)
        self.ui.ModifySelect.addItem(name)

    def getSelectedSamples(self):
        selected = []
        for i in range(self.sample_count):
            row = i/self.size
            col = i%self.size
            if self.ui.Grid.itemAtPosition(row, col).widget().highlighted:
                print "widget at " + str(row) + ", " + str(col) + " is highlighted"
                selected.append(self.samples[i])
        return selected

    def getSelectedWidgets(self):
        widgets = []
        for i in range(self.sample_count):
            row = i/self.size
            col = i%self.size
            widget = self.ui.Grid.itemAtPosition(row, col).widget()
            if widget.highlighted:
                widgets.append(widget)
        return widgets
    
    def addToGroup(self):
        selected = self.getSelectedSamples()
        group = self.groups[self.ui.ModifySelect.currentIndex()]
        group.addSamples(selected)

    def removeFromGroup(self):
        selected = self.getSelectedSamples()
        group = self.groups[self.ui.ModifySelect.currentIndex()]
        group.remSamples(selected)

    def deleteGroup(self):
        del self.groups[self.ui.ModifySelect.currentIndex()]
        self.initGroupList()
            

    def loadObjects(self):
        if not hasattr(self, 'objWidgets'):
            self.objWidgets = []
        self.size = int(math.ceil(math.sqrt(len(glob.glob("../models/*.obj")))))
        grid = self.ui.Grid
        for idx, files in enumerate(glob.glob("../models/*.obj")):
            model = objModel.ObjModel(files)
            widget = objWindow.ObjWidget(model)
            self.objWidgets.append(widget)
            grid.addWidget(widget, idx/self.size, idx%self.size)
            self.sample_count = idx+1

    def analyze(self):
        samples = self.getSelectedSamples()
        if len(samples) > 6:
            return

        widgets = self.getSelectedWidgets()
        self.loadAnalysis(widgets)
        

    def loadAnalysis(self, widgets):
        self.analysis_app = AnalysisInterface.analysisWindow(widgets)
        self.analysis_app.show()
        

def main():
    app = QtGui.QApplication(sys.argv)
    myapp = thumbnailWindow(8, None)
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    
    main()


