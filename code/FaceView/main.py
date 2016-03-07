from PyQt4 import QtCore
from PyQt4 import QtGui
import sys
import os

sys.path.append('./gui-scripts')

import LoadingInterface

app = QtGui.QApplication(sys.argv)

def loadLoading():
    app = QtGui.QApplication(sys.argv)
    loading_app = LoadingInterface.loadingWindow()
    loading_app.show()
    app.exec_()
        

if __name__=="__main__":
    loadLoading()

