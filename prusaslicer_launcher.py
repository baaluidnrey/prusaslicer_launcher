import sys
import subprocess

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QComboBox, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout

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
        self.selectionFiles = WidgetSelectionFiles()
        
        # commands
        self.prusa_path = "\"C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe\""
        self.config_path = "\".\config\""
        
        # create application
        self.createGUI()
        self.setInitialSettings()
        self.printerSettings["name"]["value"].currentIndexChanged.connect(self.setPrinterSettings)
        self.buttonPrusa.clicked.connect(self.openPrusaSlicer)


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
        vbox.addWidget(self.selectionFiles)
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
        _, printer = list(self.config["printers"].items())[self.printerSettings["name"]["value"].currentIndex()]
        for key in ["nozzles", "filaments", "profiles"]:
            self.printerSettings[key]["value"].clear()
            [self.printerSettings[key]["value"].addItem(item) for item in printer[key]]
            
            
    def selectedProfile(self):
        printer = list(self.config["printers"].keys())[self.printerSettings["name"]["value"].currentIndex()]
        profile = self.printerSettings["profiles"]["value"].currentText()
        return printer + "_" + profile


    def optionsFilament(self):
        options = dict()
        file_path = f'.\\filaments\{self.printerSettings["filaments"]["value"].currentText()}.ini'
        with open(file_path, "r") as file:
            for line in file:
                option, val = line.replace('\n', '').split(" = ")
                options[option] = val
        return options
    
    
    def optionsFill(self):
        pattern = list(self.config["fill_pattern"].keys())[self.fillSettings["pattern"]["value"].currentIndex()]
        density = self.fillSettings["density"]["value"].currentText()
        return "--fill-pattern " + pattern + " --fill-density " + density   


    def openPrusaSlicer(self):
          
        profile_src = f".\profiles\{self.selectedProfile()}.ini"
        profile_dst = ".\profiles\\tmp.ini"
        
        # apply filament settings
        options_filament = self.optionsFilament()
        with open(profile_dst, "w") as file_dst:
            for line in open(profile_src, "r"):
                if " = " in line:
                    option, _ = line.replace('\n', '').split(" = ", 1)
                    if option in options_filament.keys():
                        file_dst.write(f'{option} = {options_filament[option]}\n')
                    else:
                        file_dst.write(line)
                        
        # 3D files
        cad_files = " ".join(f'"{file}"' for file in self.selectionFiles.getFiles())

        # open prusa slicer with all the options
        cmd = f'{self.prusa_path} {cad_files} --load {profile_dst} {self.optionsFill()}'
        subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)

def main():
   app = QApplication(sys.argv)
   window = PrusaSlicerLauncher()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()