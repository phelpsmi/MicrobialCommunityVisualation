"""
Qt GUI for the FaceView software

"""

from PyQt4 import QtGui, uic, QtCore
import sys

# replace 'c:/test.ui' with real path to ui-file created in QtDesigner
uifile = './mainwindow.ui'
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

        #Testing Code, don't forget to remove!!!
        items = ['org1asdfadsfasdfasdf', 'org2', 'org3']
        features = ['feature1', 'feature2', 'feature3']
        self.setOrganisms(items, features)

    def setOrganisms(self, orgs, features):
        table = self.ui.table
        table.clearContents()
        table.setRowCount(len(orgs))
        
        for idx, org in enumerate(orgs):
            item = QtGui.QTableWidgetItem(org)
            table.setItem(idx, 0, item)
            table.setCellWidget(idx, 1, self.newFeatureBox(features))

    def newFeatureBox(self, features):
        box = QtGui.QComboBox()

        for feature in features:
            box.addItem(feature)
        return box

    def getNormalization(self):
        if self.ui.norm1.isChecked():
            return 1
        elif self.ui.norm1.isChecked():
            return 2
        elif self.ui.norm1.isChecked():
            return 3
        else:
            return False
            
        

    def setDataFile(self):
        self.ui.DataFilePath.setText(QtGui.QFileDialog.getOpenFileName())
        
    def setGroupFile(self):
        self.ui.GroupingFilePath.setText(QtGui.QFileDialog.getOpenFileName())

    def addItemsToList(self, listWidget, itemList):
        for item in itemList:
            listWidget.addItem(QtGui.QListWidgetItem(item))

def main():
    app = QtGui.QApplication(sys.argv)
    myapp = loadingWindow()
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    main()

