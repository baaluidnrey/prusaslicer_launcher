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
            'physical_printers': {'label': "Physical printer", 'value': QComboBox()},
        }
        self.nozzleSettings = {
            'diameter': {'label': "Diameter", 'value': QComboBox()},
            'filaments': {'label': "Filament", 'value': QComboBox()},
            'profiles': {'label': "Profile",'value': QComboBox()},
        }
        self.nb_extruders = 1
        self.fillSettings = {
            'pattern': {'label': "Pattern", 'value': QComboBox()},
            'density': {'label': "Density", 'value': QComboBox()},   
        }
        self.prusa_folders = {
            'name': 'printer',
            'filaments': 'filament',
            'profiles': 'print',
        }
        self.buttonPrusa = QPushButton("Open PrusaSlicer")
        self.config = yaml.safe_load(Path("config/config.yaml").read_text())
        self.selectionFiles = WidgetSelectionFiles()
                
        # create application
        self.createGUI()
        self.setInitialSettings()
        self.printerSettings["name"]["value"].currentIndexChanged.connect(self.setPrinterSettings)
        self.nozzleSettings["diameter"]["value"].currentIndexChanged.connect(self.setNozzleSettings)
        self.buttonPrusa.clicked.connect(self.openPrusaSlicer)


    def createGUI(self):
        
        # layout
        vbox = QVBoxLayout()
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle("PrusaSlicer pour les fainéants")
        self.setWindowIcon(QIcon("./logo_isir.ico"))
        
        # settings
        for settings, legend in zip([self.printerSettings, self.nozzleSettings, self.fillSettings],
                                            ["Printer settings", "Nozzle settings", "Fill settings"]):
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

    def setInitialSettings(self):
        """
        Set the initial settings for the GUI
        """
        [self.printerSettings["name"]["value"].addItem(printer["name"]) for printer in self.config["printers"].values()]
        self.setPrinterSettings()   # first as default
        
        for item in self.config["fill_pattern"].values():
            self.fillSettings["pattern"]["value"].addItem(item)
            
        for item in self.config["fill_density"]:
            self.fillSettings["density"]["value"].addItem(item)
        self.fillSettings["density"]["value"].setCurrentIndex(2)
        

    def setPrinterSettings(self):
        """
        Update the printer settings based on the selected printer in the GUI
        """
        _, printer = list(self.config["printers"].items())[self.printerSettings["name"]["value"].currentIndex()]

        # printer
        for key in ["physical_printers"]:
            self.printerSettings[key]["value"].clear()
            [self.printerSettings[key]["value"].addItem(item) for item in printer[key]]
            
        # nozzle
        self.nozzleSettings["diameter"]["value"].clear()
        for diameter in printer["nozzles"].keys():
            self.nozzleSettings["diameter"]["value"].addItem(diameter)
        self.setNozzleSettings()    # first as default

            
    def setNozzleSettings(self):
        """
        Update the nozzle settings based on the selected nozzle in the GUI
        """
        _, printer = list(self.config["printers"].items())[self.printerSettings["name"]["value"].currentIndex()]
        _, nozzle = list(printer["nozzles"].items())[self.nozzleSettings["diameter"]["value"].currentIndex()]

        for key in ["filaments", "profiles"]:
            self.nozzleSettings[key]["value"].clear()
            [self.nozzleSettings[key]["value"].addItem(item) for item in nozzle[key]]
          
            
    def selectedPrinter(self):
        return self.printerSettings["name"]["value"].currentText()
    
    def selectedPhysicalPrinter(self):
         return self.printerSettings["physical_printers"]["value"].currentText()
     
    def selectedNozzle(self):
        return self.nozzleSettings["diameter"]["value"].currentText()
        
    def selectedProfile(self):
        return self.nozzleSettings["profiles"]["value"].currentText()
    
    def selectedFilament(self):
        return self.nozzleSettings["filaments"]["value"].currentText()
    
    
    def getOptions(self, file_path):
        options = dict()
        with open(file_path, "r") as file_src:
            for line in file_src:
                if " = " in line:
                    option, val = line.replace('\n', '').split(" = ", maxsplit=1)
                    options[option] = val
        return options
    
    
    def concatenateOptions(self, options_1, options_2):
        """
        Concatenate two dictionaries, giving priority to the second one
        """
        options = dict()
        for option, val in options_1.items():
            if option in options_2.keys():
                options[option] = options_2[option]
            else:
                options[option] = val
        for option, val in options_2.items():
            if option not in options.keys():
                options[option] = val
        return options
    

    def openPrusaSlicer(self):
        config_path = self.config["prusa_datadir"]
        profile_src = f"{config_path}/print/{self.selectedProfile()}.ini"
        filament_src = f"{config_path}/filament/{self.selectedFilament()}.ini"
        printer_src = f"{config_path}/printer/{self.selectedPrinter()}.ini"
        physical_printer_src = f"{config_path}/physical_printer/{self.selectedPhysicalPrinter()}.ini"
        profile_dst = "config.ini"
        
        # 1. get options
        options = self.getOptions(profile_src)
        options_filament = self.getOptions(filament_src)
        options_printer = self.getOptions(printer_src)
        # options_physical_printer = self.getOptions(physical_printer_src)
        
        # 2. handle multi-extruders machines
        _, printer = list(self.config["printers"].items())[self.printerSettings["name"]["value"].currentIndex()]
        options_filament = dict()
        options_all_filaments = dict()
        for extruder in printer["extruders"]:
            if extruder == self.selectedNozzle():
                filament = self.selectedFilament()
            else:
                filament = printer["nozzles"][extruder]["filaments"][0]
            options_filament[extruder] = self.getOptions(
                f"{config_path}/filament/{filament}.ini"
            )
         
        # concatenate filament options
        for index, extruder in enumerate(printer["extruders"]):
            for key in options_filament[extruder].keys():
                if index == 0:
                    options_all_filaments[key] = f'{options_filament[extruder][key]}'  # creation for first occurence
                else:
                    options_all_filaments[key] += f',{options_filament[extruder][key]}' # else, concatenate
        
        # 3. concatenate options
        options = self.concatenateOptions(options, options_all_filaments)
        options = self.concatenateOptions(options, options_printer)
        
        # 4. add the selected printer, filament and profile to the options
        options[f"printer_settings_id"] = f'{self.selectedPrinter()}'
        options[f"print_settings_id"] = f'{self.selectedProfile()}'
        filament_settings_id = ""
        for index, extruder in enumerate(printer["extruders"]):
            if index != 0:
                filament_settings_id += f';'
            if extruder == self.selectedNozzle():
                filament_settings_id += f'\"{self.selectedFilament()}\"'
            else:
                filament_settings_id += f'{printer["nozzles"][extruder]["filaments"][0]}'     # first as default for non-selected nozzle
        options[f"filament_settings_id"] = f'{filament_settings_id}'
        
        # 5. apply options to the profile
        with open(profile_dst, "w") as file_dst:
            for option in options.keys():
                file_dst.write(f'{option} = {options[option]}\n')
                
        print(f'options successfully applied')
        
        # 6. open prusa slicer with all the options
        cmd = [
            self.config["prusa_path"],
            '--datadir', self.config["prusa_datadir"],
            '--load', "config.ini",
            '--fill-pattern', list(self.config["fill_pattern"].keys())[self.fillSettings["pattern"]["value"].currentIndex()],
            '--fill-density', self.fillSettings["density"]["value"].currentText(),
        ]
        for index, file in enumerate(self.selectionFiles.getFiles()):
            cmd.insert(1+index, file)
            
        print(f'cmd: {cmd}')
            
        subprocess.Popen(cmd, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)


def main():
   app = QApplication(sys.argv)
   window = PrusaSlicerLauncher()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()