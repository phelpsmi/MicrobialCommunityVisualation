
uifile = 'gui-scripts/loadingview.ui'
form, base = uic.loadUiType(uifile)
features = ModelGenerator.getFeatureList()

class loadingWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = form()
        
        self.ui.setupUi(self)

        self.ui.table.setColumnWidth(0, 600)
        self.ui.table.setColumnWidth(1, 250)
        
        #Set triggers for buttons
        self.ui.SelectDataFile.clicked.connect(self.setDataFile)
        self.ui.SelectGroupFile.clicked.connect(self.setGroupFile)
        self.ui.Cancel.clicked.connect(self.close)
        self.ui.Generate.clicked.connect(self.generate)

        self.features = features
        self.prog_vars = {}

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
        box.addItem("")
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

        selected_features = filter(bool, self.getSelectedFeatures())
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

        

        self.prog_vars['feature_map'] = self.getFeatureMap()
        self.prog_vars['samples'] = self.samples
        self.prog_vars['groups'] = self.groups
        normalization = self.getNormalization()
        ModelGenerator.generateModels(normalization, self.prog_vars['feature_map'])

        self.hide()
        self.loadThumbnail()
        


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

            if self.samples:
                orgs = self.samples[0].getOrgList()
                self.setOrganisms(orgs, self.features)

    def loadThumbnail(self):
        ThumbnailInterface.thumbnailWindow(self.prog_vars, self).show()
