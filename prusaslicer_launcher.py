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
        self.buttonPrusa = QPushButton("Open PrusaSlicer")
        
        self.config = yaml.safe_load(Path("config.yaml").read_text())
        self.files = WidgetSelectionFiles()
        
        # commands
        self.prusa_path = "\"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe\""
        self.config_path = "\".\config\""
        
        # create application
        self.createGUI()
        self.setInitialSettings()
        self.printerSettings["name"]["value"].currentIndexChanged.connect(self.setPrinterSettings)


    def createGUI(self):
        
        vbox = QVBoxLayout()
        
        # settings
        for settings, legend in zip([self.printerSettings, self.fillSettings],
                                    ["Printer settings", "Fill settings"]):
            grid = QGridLayout()
            for index, setting in enumerate(settings.values(), start=1):
                grid.addWidget(QLabel(setting["label"]), index, 1)
                grid.addWidget(setting["value"], index, 2)
            groupbox = QGroupBox(legend)
            groupbox.setLayout(grid)
            vbox.addWidget(groupbox)

        # other elements
        vbox.addWidget(self.files)
        vbox.addWidget(self.buttonPrusa)
        
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)
        
        self.setWindowTitle("PrusaSlicer pour les fainéants")
        self.setWindowIcon(QIcon("./logo_isir.png"))       


    def setInitialSettings(self):
        [self.printerSettings["name"]["value"].addItem(printer["name"]) for printer in self.config["printers"].values()]
        self.setPrinterSettings()   # first as default
        
        [self.fillSettings["pattern"]["value"].addItem(item) for item in self.config["fill_pattern"].values()]
        [self.fillSettings["density"]["value"].addItem(item) for item in self.config["fill_density"]]
        self.fillSettings["density"]["value"].setCurrentIndex(2)
        

    def setPrinterSettings(self):
        self.printerSettings["nozzles"]["value"].clear()
        self.printerSettings["filaments"]["value"].clear()
        self.printerSettings["profiles"]["value"].clear()
        
        _, printer = list(self.config["printers"].items())[self.printerSettings["name"]["value"].currentIndex()]
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