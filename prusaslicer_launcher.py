#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import yaml
from pathlib import Path

class WidgetSelectionFiles(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        
        self.files = QListWidget()
        self.files.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.setAcceptDrops(True)
        self.createWidget()


    def createWidget(self):
    
        buttonAddition = QPushButton('+')
        buttonDeletion = QPushButton('-')
        buttonClearing = QPushButton('Remove all')

        # layout
        vbox = QVBoxLayout()
        vbox.addWidget(buttonAddition)
        vbox.addWidget(buttonDeletion)
        vbox.addWidget(buttonClearing)

        hbox = QHBoxLayout()
        hbox.addWidget(self.files)
        hbox.addLayout(vbox)

        groupbox = QGroupBox('Selection of the 3D files')
        groupbox.setLayout(hbox)

        box = QVBoxLayout()
        box.addWidget(groupbox)

        self.setLayout(box)

        # behavior
        buttonAddition.clicked.connect(self.addFiles)
        buttonDeletion.clicked.connect(self.deleteFiles)
        buttonClearing.clicked.connect(self.clearFiles)

    def addFiles(self):
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        files, _ = fileDialog.getOpenFileNames(self,'Selection of the  files')
        for file in files:
            self.files.addItem(file)

    def deleteFiles(self):
        item = self.files.selectedItems()[0]
        if item is not None:
            index = self.files.row(item)
            self.files.takeItem(index)
            
    def clearFiles(self):
        self.files.clear()
        
    def files(self):
        files = []
        for index in range(self.files.count()):
            files.append(self.files.item(index).text())
        return files

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        for url in event.mimeData().urls():
            file = url.toLocalFile()
            self.files.addItem(file)

class PrusaSlicerLauncher(QMainWindow):
    
    def __init__(self, parent=None):
        super(PrusaSlicerLauncher, self).__init__(parent)
        
        self.printerName = QComboBox()
        self.nozzle = QComboBox()
        self.filament = QComboBox()
        self.profile = QComboBox()
        self.fillPattern = QComboBox()
        self.fillDensity = QComboBox()
        
        self.buttonPrusa = QPushButton("Open PrusaSlicer")
        
        self.config = yaml.safe_load(Path("config.yaml").read_text())
        self.files = WidgetSelectionFiles()
        
        # commands
        self.prusa_path = "\"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe\""
        self.config_path = "\".\config\""
        
        # create application
        self.createGUI()


    def createGUI(self):
        
        # labels
        labelPrinter = QLabel("Name :")
        labelNozzle = QLabel("Nozzle :")
        labelFilament = QLabel("Filament :")
        labelProfile = QLabel("Profile :")
        labelFillPattern = QLabel("Fill Pattern :")
        labelFillDensity = QLabel("Fill Density :")
        
        # layout
        groupboxSettings = QGroupBox("Settings")
        grid = QGridLayout()
        grid.addWidget(labelPrinter,1,1)
        grid.addWidget(labelNozzle,2,1)
        grid.addWidget(labelFilament,3,1)
        grid.addWidget(labelProfile,4,1)
        grid.addWidget(labelFillPattern,5,1)   
        grid.addWidget(labelFillDensity,6,1) 
    
        grid.addWidget(self.printerName,1,2)
        grid.addWidget(self.nozzle,2,2)
        grid.addWidget(self.filament,3,2)
        grid.addWidget(self.profile,4,2)
        grid.addWidget(self.fillPattern,5,2)   
        grid.addWidget(self.fillDensity,6,2) 

        groupboxSettings.setLayout(grid)
    
        vbox = QVBoxLayout()
        vbox.addWidget(groupboxSettings)
        vbox.addWidget(self.files)
        vbox.addWidget(self.buttonPrusa)
        
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)
        
        self.setWindowTitle("PrusaSlicer pour les fainéants")
        self.setWindowIcon(QIcon("./logo_isir.png"))       

def main():
   app = QApplication(sys.argv)
   window = PrusaSlicerLauncher()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()