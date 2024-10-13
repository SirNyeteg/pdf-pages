from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QFileDialog, QTableWidgetItem, QHeaderView,
                             QAbstractItemView, QMessageBox, QHBoxLayout, QLabel,
                             QTableWidgetSelectionRange, QMenu)
from PyQt5.QtGui import QContextMenuEvent

from pdf import PdfReader
from settings import Settings
from table import TableWidget

from typing import Iterable, List

import os
import sys


BUILD_VERSION = "2024-10-13"


class SurfaceLabel(QLabel):
    def __init__(self):
        super().__init__("")
        self.surface:int = 0
        self.updateText()

    def setSurface(self, surface:int):
        self.surface = surface
        self.updateText()
        
    def updateText(self):
        self.setText(f"The surface of selected pages: {self.getFormattedSurface()} dm<sup>2</sup>")

    def getFormattedSurface(self) -> str:
        return f"{self.surface / (100*100):.1f}"

    def contextMenuEvent(self, event:QContextMenuEvent):
        menu = QMenu(self)
        copy_action = menu.addAction(f"Copy {self.getFormattedSurface()} to clipboard")
        copy_action.triggered.connect(self.copyToClipboard)
        menu.exec_(event.globalPos())

    def copyToClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.getFormattedSurface())


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

        self.table = TableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { background-color: silver;}")
        self.table.itemSelectionChanged.connect(self.calculateBigPagesSurface)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.table.setColumnCount(6)
        layout.addWidget(self.table)

        headers = ['Page count', 'Dimensions', 'Short', 'Long', 'Paper size', 'Pages']
        self.table.setHorizontalHeaderLabels(headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setWordWrap(False)

        self.table.setColumnWidth(0, 70)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 40)
        self.table.setColumnWidth(3, 40)
        self.table.setColumnWidth(4, 70)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        surfaceLayout = QHBoxLayout()
        self.surfaceButton = QPushButton('Select big pages')
        self.surfaceButton.clicked.connect(self.selectBigPages)
        surfaceLayout.addWidget(self.surfaceButton)
        self.surfaceLabel = SurfaceLabel()
        surfaceLayout.addWidget(self.surfaceLabel)
        surfaceLayout.setStretch(0, 1)
        surfaceLayout.setStretch(1, 1)
        layout.addLayout(surfaceLayout)

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
            stats = sorted(reader.getStats(), key=lambda x: (
                min(x.dimension.width, x.dimension.height), max(x.dimension.width, x.dimension.height))) 

            self.table.clearContents()
            self.table.setRowCount(0)
            for row, stat in enumerate(stats):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(len(stat.pages))))
                w = min(stat.dimension.width, stat.dimension.height)
                h = max(stat.dimension.width, stat.dimension.height)
                paperSize = f"unknown" if stat.dimension not in self.settings.pageSizes else self.settings.pageSizes[stat.dimension]
                self.table.setItem(row, 1, QTableWidgetItem(f"{w}x{h} mm"))
                self.table.setItem(row, 2, QTableWidgetItem(f"{w}"))
                self.table.setItem(row, 3, QTableWidgetItem(f"{h}"))
                self.table.setItem(row, 4, QTableWidgetItem(paperSize))
                self.table.setItem(row, 5, QTableWidgetItem(self.printPages(stat.pages)))

    def selectBigPages(self):
        self.table.clearSelection()
        rowCount = self.table.rowCount()
        for row in range(rowCount):
            short = int(self.table.item(row, 2).text())
            long = int(self.table.item(row, 3).text())
            for rule in self.settings.bigPages:
                minShort, minLong = rule
                if short >= minShort and long >= minLong:
                    selectionRange = QTableWidgetSelectionRange(row, 0, row, self.table.columnCount() - 1)
                    self.table.setRangeSelected(selectionRange, True)
                    break
        self.table.setFocus()

    def calculateBigPagesSurface(self):
        selectedRanges = self.table.selectedRanges()
        selectedRows = set()
        for selectedRange in selectedRanges:
            for row in range(selectedRange.topRow(), selectedRange.bottomRow() + 1):
                selectedRows.add(row)
        surface = 0
        for row in selectedRows:
            count = int(self.table.item(row, 0).text())
            short = int(self.table.item(row, 2).text())
            long = int(self.table.item(row, 3).text())
            surface += count * (short * long)

        self.surfaceLabel.setSurface(surface)


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
    window.setWindowTitle(f"PDF page size reader ({BUILD_VERSION})")
    window.show()
    sys.exit(app.exec_())
