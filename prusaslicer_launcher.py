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
            # 'nozzles': {'label': "Nozzle", 'value': QComboBox()},
            'filaments': {'label': "Filament", 'value': QComboBox()},
            'profiles': {'label': "Profile",'value': QComboBox()},
            'extruder': {'label': "Extruder", 'value': QComboBox()},   
        }
        self.apply_filament_settings = False
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
        self.apply_filament_settings = printer["apply_filament_settings"]
        self.nb_extruders = printer["nb_extruders"]
        # for key in ["nozzles", "filaments", "profiles"]:
        for key in ["filaments", "profiles"]:
            self.printerSettings[key]["value"].clear()
            [self.printerSettings[key]["value"].addItem(item) for item in printer[key]]
        for key in ["extruder"]:
            self.printerSettings[key]["value"].clear()
            [self.printerSettings[key]["value"].addItem(f"{i+1}") for i in range(self.nb_extruders)]
            
            
    def selectedPrinter(self):
        return self.printerSettings["name"]["value"].currentText()    
        
    def selectedProfile(self):
        return self.printerSettings["profiles"]["value"].currentText()
    
    def selectedFilament(self):
        return self.printerSettings["filaments"]["value"].currentText()
    
    
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
        config_path = self.config["prusa_config_path"]
        profile_src = f"{config_path}/print/{self.selectedProfile()}.ini"
        filament_src = f"{config_path}/filament/{self.selectedFilament()}.ini"
        printer_src = f"{config_path}/printer/{self.selectedPrinter()}.ini"
        profile_dst = "config.ini"
        
        # 1. get options
        options = self.getOptions(profile_src)
        options_filament = self.getOptions(filament_src)
        options_printer = self.getOptions(printer_src)
        
        # 2. concatenate options
        options = self.concatenateOptions(options, options_filament)
        options = self.concatenateOptions(options, options_printer)
        
        # 3. add the selected printer, filament and profile to the options
        options[f"printer_settings_id"] = f'{self.selectedPrinter()}'
        # options[f"filament_settings_id"] = f'{self.selectedFilament()}'
        options[f"print_settings_id"] = f'{self.selectedProfile()}'
        
        # 4. add the selected extruder to the options
        extruder_index = self.printerSettings["extruder"]["value"].currentIndex()
        # options[f"infill_extruder"] = f'{extruder_index}'
        # options[f"perimeter_extruder"] = f'{extruder_index}'
        # options[f"solid_infill_extruder"] = f'{extruder_index}'
        # options[f"filament_extruder_id"] = f'{extruder_index}'
        # options[f"default_filament_profile"] = f'{self.selectedFilament()}'
        filament_settings_id = f'\"{self.selectedFilament()}\"'
        for i in range(0, self.nb_extruders-1):
            filament_settings_id += f';\"{self.selectedFilament()}\"'
            print(f'i: {i}')
        print(f'filament_settings_id: {filament_settings_id}')
        options[f"filament_settings_id"] = f'{filament_settings_id}'
        
        # options[f"support_material_extruder"] = f'{extruder_index}'
        
        
        # 5. apply options to the profile
        with open(profile_dst, "w") as file_dst:
            for option in options.keys():
                file_dst.write(f'{option} = {options[option]}\n')
                
        print(f'options successfully applied')
        
        # 6. open prusa slicer with all the options
        cmd = [
            self.config["prusa_path"],
            '--load', "config.ini",
            '--fill-pattern', list(self.config["fill_pattern"].keys())[self.fillSettings["pattern"]["value"].currentIndex()],
            '--fill-density', self.fillSettings["density"]["value"].currentText(),
            '--infill-extruder', self.printerSettings["extruder"]["value"].currentText(),
            '--perimeter-extruder', self.printerSettings["extruder"]["value"].currentText(),
            # '--filament-extruder-id', self.printerSettings["extruder"]["value"].currentText(), 
            # '--solid_infill_extruder', self.printerSettings["extruder"]["value"].currentText(),
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