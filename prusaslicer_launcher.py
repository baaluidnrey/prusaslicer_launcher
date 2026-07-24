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
        }
        self.apply_filament_settings = False
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
        # for key in ["nozzles", "filaments", "profiles"]:
        for key in ["filaments", "profiles"]:
            self.printerSettings[key]["value"].clear()
            [self.printerSettings[key]["value"].addItem(item) for item in printer[key]]
            
    def selectedPrinter(self):
        return self.printerSettings["name"]["value"].currentText()    
        
    def selectedProfile(self):
        return self.printerSettings["profiles"]["value"].currentText()
    
    def selectedFilament(self):
        return self.printerSettings["filaments"]["value"].currentText()
    
    def getOptions(self, type):
        options = dict()
        options_file_path = f'{self.config["prusa_config_path"]}/{self.prusa_folders[type]}/{self.printerSettings[type]["value"].currentText()}.ini'
        print(f"Reading options from {options_file_path}")
        with open(options_file_path, "r") as file_src:
            for line in file_src:
                if " = " in line:
                    option, val = line.replace('\n', '').split(" = ", maxsplit=1)
                    options[option] = val
        return options
    
    
    def applyOptions(self, options, output_file_path, input_file_path):
        with open(output_file_path, "w") as file_dst:
            for line in open(input_file_path, "r"):
                if " = " in line:
                    option, _ = line.replace('\n', '').split(" = ", 1)
                    if option in options.keys():
                        file_dst.write(f'{option} = {options[option]}\n')
                    else:
                        file_dst.write(line)
        # the application of the options does not work.
        # the added options are not taken into acccount
        # the problem is because the options used in this method should be the current options and not the added options
    
    def openPrusaSlicer(self):
        config_path = self.config["prusa_config_path"]
        profile_src = f"{config_path}/print/{self.selectedProfile()}.ini"
        
        output_step_1 = "step_1.ini"
        output_step_2 = "step_2.ini"
        profile_dst = "config.ini"
        
        # 1. apply print settings
        options = self.getOptions('profiles')
        print(f"options: {options}")
        options[f"print_settings_id"] = f'{self.selectedProfile()}'
        print_src = f"{config_path}/print/{self.selectedProfile()}.ini"
        self.applyOptions(options, output_step_1, print_src)
        
        # 2. apply filament settings
        options = self.getOptions('filaments')
        print(f"options: {options}")
        options[f"filament_settings_id"] = f'{self.selectedFilament()}'
        profile_src = f"{config_path}/filament/{self.selectedFilament()}.ini"
        if self.apply_filament_settings:
            self.applyOptions(options, output_step_2, output_step_1)
        
        # 3. apply printer settings
        options = self.getOptions('name')
        print(f"options: {options}\n---")
        options[f"printer_settings_id"] = f'{self.selectedPrinter()}'
        options[f"filament_settings_id"] = f'{self.selectedFilament()}'
        options[f"print_settings_id"] = f'{self.selectedProfile()}'
        printer_src = f"{config_path}/printer/{self.selectedPrinter()}.ini"
        self.applyOptions(options, profile_dst, output_step_2)
        
        # self.applyOptions()
        
        # apply filament settings
        # options_filament = self.optionsFilament()
        # with open(profile_dst, "w") as file_dst:
        #     for line in open(profile_src, "r"):
        #         if " = " in line:
        #             option, _ = line.replace('\n', '').split(" = ", 1)
        #             if option in options_filament.keys():
        #                 file_dst.write(f'{option} = {options_filament[option]}\n')
        #             else:
        #                 file_dst.write(line)
            
        # open prusa slicer with all the options
        cmd = [
            self.config["prusa_path"],
            '--load', "config.ini",
            '--fill-pattern', list(self.config["fill_pattern"].keys())[self.fillSettings["pattern"]["value"].currentIndex()],
            '--fill-density', self.fillSettings["density"]["value"].currentText(),
        ]
        for index, file in enumerate(self.selectionFiles.getFiles()):
            cmd.insert(1+index, file)
            
        subprocess.Popen(cmd, shell=False, creationflags=subprocess.CREATE_NEW_CONSOLE)


def main():
   app = QApplication(sys.argv)
   window = PrusaSlicerLauncher()
   window.show()
   sys.exit(app.exec_())

if __name__ == '__main__':
   main()