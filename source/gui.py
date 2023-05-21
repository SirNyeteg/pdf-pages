from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QMessageBox)
from pdf import PdfReader, PageDimension
from settings import Settings

from typing import Dict, Iterable, List

import os
import sys
import yaml


class MainWindow(QWidget):
    def __init__(self, settings:Settings):
        super().__init__()
        self.settings = settings
        self.initUI()


    def initUI(self):
        self.resize(self.settings.width, self.settings.height)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.file_button = QPushButton('Open PDF')
        self.file_button.clicked.connect(self.openFile)
        layout.addWidget(self.file_button)

        # Create the table widget with 4 columns
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: silver;}")

        self.table.setColumnCount(4)
        layout.addWidget(self.table)

        headers = ['Page count', 'Dimension', 'Paper size', 'Pages']
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)

        # Set the width of the first three columns
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(1, 120)
        self.table.setColumnWidth(2, 80)

        # Allow the last column to expand
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.Stretch)

    def printPages(self, pages:Iterable[int]):
        if len(pages) == 0:
            return "-"
        ordered = sorted(pages)
        if not self.settings.groupPages:
            return ",".join([str(p) for p in ordered])
        ranges:List[str] = []
        start = ordered[0]
        prev = ordered[0]
        for i in range(1, len(ordered)):
            page = ordered[i]
            if page - prev > 1:
                if prev == start:
                    ranges.append(f"{prev}")
                else:
                    ranges.append(f"{start}-{prev}")
                start = page
            prev = page
        if prev == start:
            ranges.append(f"{prev}")
        else:
            ranges.append(f"{start}-{prev}")

        
        return ",".join(ranges)

    def openFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open PDF', '', 'PDF Files (*.pdf)')
        if file_path:
            reader = PdfReader(file_path)
            stats = reader.getStats()
            self.table.clearContents()
            self.table.setRowCount(0)
            for row, stat in enumerate(stats):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(len(stat.pages))))
                w = stat.dimension.width
                h = stat.dimension.height
                paperSize = f"unknown" if stat.dimension not in self.settings.pageSizes else self.settings.pageSizes[stat.dimension]
                self.table.setItem(row, 1, QTableWidgetItem(f"{w}x{h} mm"))
                self.table.setItem(row, 2, QTableWidgetItem(paperSize))
                self.table.setItem(row, 3, QTableWidgetItem(self.printPages(stat.pages)))


def showAlert(text:str):
    messageBox = QMessageBox()
    messageBox.setWindowTitle("Error")
    messageBox.setText(text)
    messageBox.setIcon(QMessageBox.Information)
    messageBox.setStandardButtons(QMessageBox.Ok)
    messageBox.exec_()


def loadSettings() -> Settings:
    if getattr(sys, 'frozen', False):
        scriptPath = sys.executable
    else:
        scriptPath = os.path.abspath(__file__)
    scriptDir = os.path.dirname(scriptPath)
    filePath = os.path.join(scriptDir, "settings.yaml")
    return Settings(filePath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    settings = loadSettings()
    if settings.error is not None:
        showAlert(settings.error)
    window = MainWindow(settings)
    window.setWindowTitle("PDF page size reader")
    window.show()
    sys.exit(app.exec_())
