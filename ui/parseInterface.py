import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPlainTextEdit,
)
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    PushButton,
    InfoBar,
    FluentIcon,
    SmoothScrollArea,
    MessageBox,
    BodyLabel,
)

from midoWrapper import *


class ParseInterface(QWidget):
    """The interface for parsing the music."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ParseInterface")
        self.filename = None
        self.initUi()
        self.connectSignalToSlot()

    def initUi(self):
        # layout
        self.form = QVBoxLayout(self)
        self.form.setContentsMargins(16, 20, 16, 20)
        self.form.setSpacing(0)
        self.form.setAlignment(Qt.AlignTop)

        # label
        self.fileLabel = BodyLabel("未选择", self)

        # button
        self.fileWidget = QWidget()
        self.fileLayout = QHBoxLayout(self.fileWidget)
        self.fileWidget.setLayout(self.fileLayout)
        self.fileBtn = PushButton("选择文件")
        self.fileBtn.setFixedWidth(200)
        self.clearBtn = PushButton("清空文件")
        self.clearBtn.setFixedWidth(200)
        self.fileLayout.addWidget(self.fileBtn)
        self.fileLayout.addWidget(self.clearBtn)
        self.fileLayout.addStretch(1)

        self.startBtn = PushButton("开始解析", self)
        self.startBtn.setFixedWidth(200)

        # output
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.output.setFont(QFont("Consolas", 10))

        self.form.addWidget(self.fileWidget)
        self.form.addWidget(self.fileLabel)
        self.form.addSpacing(20)
        self.form.addWidget(self.startBtn)
        self.form.addSpacing(20)
        self.form.addWidget(self.output)
        self.setLayout(self.form)

    def connectSignalToSlot(self):
        self.fileBtn.clicked.connect(self.fileDialog)
        self.clearBtn.clicked.connect(self.clearFile)
        self.startBtn.clicked.connect(self.startParse)

    def fileDialog(self):
        title = "Midi解析"
        dialog = QFileDialog(self, title, filter="midi files (*.mid)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            files = dialog.selectedFiles()
            if files == []:
                return
            self.filename = files[0]
            self.fileLabel.setText(f"选择midi: {self.filename}")

    def clearFile(self):
        self.filename = None
        self.fileLabel.setText("未选择")

    def startParse(self):
        if self.filename is None:
            InfoBar.error("未选择文件", "请先选择midi文件！", duration=2000, parent=self)
            return
        try:
            self._parseMidi()
            InfoBar.success("解析完成！", "请查看你的midi文件夹", duration=2000, parent=self)
        except Exception as e:
            warning = "请检查midi文件是否符合规范\n此解析不兼容转调变速，同时需要使用midiEditor导出文件！\n"
            warning += f"错误信息: {e}"
            wrongBox = MessageBox("解析失败", warning, self)
            wrongBox.exec()

    def _parseMidi(self):
        filename = "./midi/parseline.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        midi = Midi.from_midi(self.filename)

        output = "####################\n"
        header = midi.brief_info()
        output += header
        output += "####################\n"
        for line in output.split("\n"):
            self.output.appendHtml(f"<font color=green><b>{line}</b></font>")

        for idx, track in enumerate(midi.tracks):
            output += "========================\n"
            output += "Track " + str(idx + 1) + "\n"
            output += "instrument: " + str(track.instrument) + "\n"
            output += "========================\n\n"
            output += str(track)
            output += "\n\n\n"

        for line in output.split("\n")[len(header.split("\n")) + 1 :]:
            if line.startswith(("Track", "=========")):
                self.output.appendHtml(f"<font color=red><b>{line}</b></font>")
            elif line.startswith("instrument"):
                self.output.appendHtml(f"<font color=red>{line}</font>")
            elif line.startswith("-----"):
                self.output.appendHtml(f"<font color=blue><b>{line}</b></font>")
            else:
                self.output.appendPlainText(line)

        with open(filename, "w") as f:
            f.write(output)
