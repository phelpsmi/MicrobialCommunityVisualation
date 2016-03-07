"""
Qt GUI for the FaceView software

"""

from PyQt4 import QtGui, uic, QtCore
import sys

import main as parent
import fvParser
import otuParser
import ModelGenerator
import modelGeneratorTranslator

import ThumbnailInterface

# replace 'c:/test.ui' with real path to ui-file created in QtDesigner
uifile = 'gui-scripts/loadingview.ui'
form, base = uic.loadUiType(uifile)
features = ModelGenerator.getFeatureList()

class loadingWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        
        self.ui.setupUi(self)
        
        #Set triggers for buttons
        self.ui.SelectDataFile.clicked.connect(self.setDataFile)
        self.ui.SelectGroupFile.clicked.connect(self.setGroupFile)
        self.ui.Cancel.clicked.connect(self.close)
        self.ui.Generate.clicked.connect(self.generate)

        #Testing Code, don't forget to remove!!!
        self.features = features

        self.samples = 0
        self.groups = 0

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

    def getNormalizationSelection(self):
        if self.ui.Norm1.isChecked():
            return 1
        elif self.ui.Norm2.isChecked():
            return 2
        elif self.ui.Norm3.isChecked():
            return 3
        else:
            return False

    def getNormalization(self):
        selection = self.getNormalizationSelection()
        orgs = self.samples[0].getOrgList()
        if selection == 1:
            return modelGeneratorTranslator.normalizeSampleAbsolute(self.samples, orgs)
        elif selection == 2:
            return modelGeneratorTranslator.normalizeSampleRatio(self.samples, orgs)
        elif selection == 3:
            scale = int(self.ui.NormVal.text())
            return modelGeneratorTranslator.normalizeSampleManual(self.samples, orgs, scale)

    def validateForGenerate(self):
        errors = ""
        if self.getNormalizationSelection() == 3:
            if not str(self.ui.NormVal.text()).isdigit():
                errors += ("Must enter digit for manual normalization.\n")

        selected_features = self.getSelectedFeatures()
        if len(selected_features) != len(set(selected_features)):
            errors += ("Repeated feature detected.\n")

        if self.samples == 0:
            errors += ("No samples have been added.\n")

        return errors

    def generate(self):
        errors = self.validateForGenerate()
        if errors:
            QtGui.QMessageBox.about(self, "Validation Failture!", errors)
            return

        

        maps = self.getFeatureMap()
        normalization = self.getNormalization()
        ModelGenerator.generateModels(normalization, maps)

        self.loadThumbnail(len(self.samples), self.samples, self.groups)
        self.close()


    def getFeatureMap(self):
        selected_features = self.getSelectedFeatures()
        orgs = self.samples[0].getOrgList()
        return dict(zip(orgs, selected_features))
            
            
    def getSelectedFeatures(self):
        selected_features = []
        table = self.ui.table
        for row in range(table.rowCount()):
            selection = table.cellWidget(row, 1).currentText()
            selected_features.append(str(selection))

        return selected_features
        

    def setDataFile(self):
        self.ui.DataFilePath.setText(QtGui.QFileDialog.getOpenFileName())
        self.updateTable()
        
    def setGroupFile(self):
        self.ui.GroupingFilePath.setText(QtGui.QFileDialog.getOpenFileName())
        self.updateTable()

    def addItemsToList(self, listWidget, itemList):
        for item in itemList:
            listWidget.addItem(QtGui.QListWidgetItem(item))

    def updateTable(self):
        data_file = str(self.ui.DataFilePath.text())
        group_file = str(self.ui.GroupingFilePath.text())

        if data_file and group_file:
            self.samples, self.groups = fvParser.pReg.parse(data_file, group_file)

            orgs = self.samples[0].getOrgList()
            self.setOrganisms(orgs, self.features)

    def loadThumbnail(self, sample_count, samples, groups):
        self.thumbnail_app = ThumbnailInterface.thumbnailWindow(sample_count, samples, groups)
        self.thumbnail_app.show()     


def main():
    app = QtGui.QApplication(sys.argv)
    myapp = loadingWindow()
    myapp.show()
    sys.exit(app.exec_())


if __name__=="__main__":
    main()

