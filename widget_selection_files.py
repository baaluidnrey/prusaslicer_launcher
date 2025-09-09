from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

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
        [self.files.addItem(file) for file in files]

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