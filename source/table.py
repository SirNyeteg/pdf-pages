from PyQt5.QtWidgets import QApplication, QTableWidget
from PyQt5.QtGui import QKeyEvent, QKeySequence


class TableWidget(QTableWidget):
    def keyPressEvent(self, event:QKeyEvent):
        if event.matches(QKeySequence.StandardKey.Copy) and self.hasFocus():
            self.copyToClipboard()
            return

        super().keyPressEvent(event)

    def copyToClipboard(self):
        selectedIndexes = self.selectedIndexes()

        if not selectedIndexes:
            return

        selectedCells = {}
        for index in selectedIndexes:
            row = index.row()
            col = index.column()
            cellValue = str(self.item(row, col).text())
            selectedCells[(row, col)] = cellValue

        clipboardData = ""
        maxRow = max([row for row, _ in selectedCells.keys()])
        maxCol = max([col for _, col in selectedCells.keys()])
        for row in range(maxRow + 1):
            for col in range(maxCol + 1):
                cellValue = selectedCells.get((row, col), "")
                clipboardData += cellValue + "\t"
            clipboardData += "\n"

        clipboard = QApplication.clipboard()
        clipboard.setText(clipboardData.strip())
