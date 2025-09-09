#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import subprocess
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import yaml
from pathlib import Path

from widget_selection_files import WidgetSelectionFiles

class PrusaSlicerLauncher(QMainWindow):
    
    def __init__(self, parent=None):
        super(PrusaSlicerLauncher, self).__init__(parent)
        
        self.printerSettings = {
            'name': {'label': "Name", 'value': QComboBox()},
            'nozzles': {'label': "Nozzle", 'value': QComboBox()},
            'filaments': {'label': "Filament", 'value': QComboBox()},
            'profiles': {'label': "Profile",'value': QComboBox()},          
        }
        self.fillSettings = {
            'pattern': {'label': "Pattern", 'value': QComboBox()},
            'density': {'label': "Density", 'value': QComboBox()},         
        }
        
                    
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
        self.setInitialSettings()
        self.printerName.currentIndexChanged.connect(self.setPrinterSettings)
        self.printerSettings["name"]["value"].currentIndexChanged.connect(self.setPrinterSettings)


    def createGUI(self):
        
        # labels
        labelPrinter = QLabel("Printer :")
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
        
        # test : printer settings, with automatic fill
        grid = QGridLayout()
        for index, setting in enumerate(self.printerSettings.values(), start=1):
            grid.addWidget(QLabel(setting["label"]), index, 1)
            grid.addWidget(setting["value"], index, 2)
        printer_group = QGroupBox("Printer")
        printer_group.setLayout(grid)

        grid = QGridLayout()
        for index, setting in enumerate(self.fillSettings.values(), start=1):
            grid.addWidget(QLabel(setting["label"]), index, 1)
            grid.addWidget(setting["value"], index, 2)
        fill_group = QGroupBox("Fill")
        fill_group.setLayout(grid)

        vbox = QVBoxLayout()
        vbox.addWidget(groupboxSettings)
        vbox.addWidget(printer_group)
        vbox.addWidget(fill_group)
        vbox.addWidget(self.files)
        vbox.addWidget(self.buttonPrusa)
        
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)
        
        self.setWindowTitle("PrusaSlicer pour les fainéants")
        self.setWindowIcon(QIcon("./logo_isir.png"))       


    def setInitialSettings(self):
        [self.printerName.addItem(printer["name"]) for printer in self.config["printers"].values()]        
        self.setPrinterSettings()   # first as default
        [self.fillPattern.addItem(item) for item in self.config["fill_pattern"].values()]
        [self.fillDensity.addItem(item) for item in self.config["fill_density"]]
        self.fillDensity.setCurrentIndex(2)
        
        # test : printer settings, with automatic fill
        [self.printerSettings["name"]["value"].addItem(printer["name"]) for printer in self.config["printers"].values()]
        [self.fillSettings["pattern"]["value"].addItem(item) for item in self.config["fill_pattern"].values()]
        [self.fillSettings["density"]["value"].addItem(item) for item in self.config["fill_density"]]
        self.fillSettings["density"]["value"].setCurrentIndex(2)
        
        
    def setPrinterSettings(self):
        _, printer = list(self.config["printers"].items())[self.printerName.currentIndex()]
        [item.clear() for item in [self.nozzle, self.filament, self.profile]]
        [self.nozzle.addItem(item) for item in printer["nozzles"]]
        [self.filament.addItem(item) for item in printer["filaments"]]
        [self.profile.addItem(item) for item in printer["profiles"]]
        
        # test : printer settings, with automatic fill
        _, printer = list(self.config["printers"].items())[self.printerSettings["name"]["value"].currentIndex()]
        self.printerSettings["nozzles"]["value"].clear()
        self.printerSettings["filaments"]["value"].clear()
        self.printerSettings["profiles"]["value"].clear()
        [self.printerSettings["nozzles"]["value"].addItem(item) for item in printer["nozzles"]]
        [self.printerSettings["filaments"]["value"].addItem(item) for item in printer["filaments"]]
        [self.printerSettings["profiles"]["value"].addItem(item) for item in printer["profiles"]]

            
def main():
   app = QApplication(sys.argv)
   window = PrusaSlicerLauncher()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()