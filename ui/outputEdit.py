from PyQt5.QtGui import QFont
from qfluentwidgets import isDarkTheme, PlainTextEdit

from .config import cfg


class OutputEdit(PlainTextEdit):
    """Common output text edit"""

    def __init__(self, outputFile: str, parent=None):
        super().__init__(parent)
        self.outputFile = outputFile
        self.setReadOnly(True)
        self.setLineWrapMode(PlainTextEdit.NoWrap)
        self.setFont(QFont("Consolas", 11))

    @property
    def outputPath(self) -> str:
        return cfg.files["outputFolder"] + self.outputFile

    def mousePressEvent(self, e):
        pass

    def mouseDoubleClickEvent(self, e):
        pass

    def contextMenuEvent(self, e):
        pass

    def appendLine(self, output: str, color: str = None, bold: bool = False) -> None:
        html = output
        if color is not None:
            realColor = self.translateColor(color)
            html = f'<span style="color:{realColor};">{html}</span>'
        if bold:
            html = f"<b>{html}</b>"
        self.appendHtml(html)

    def printFinal(self):
        finalLine = "Finished. Result saved to " + self.outputPath
        self.appendLine(finalLine, "green", True)

    def translateColor(self, color: str):
        """Translate the color to the corresponding color in the theme.
        If not found, return the original color."""
        lightMap = {
            "red": "#FF0000",
            "green": "#00AA00",
            "blue": "#0000FF",
        }
        darkMap = {
            "red": "#FF5555",
            "green": "#33FF33",
            "blue": "#00CCFF",
        }
        if isDarkTheme():
            return darkMap.get(color, color)
        else:
            return lightMap.get(color, color)
