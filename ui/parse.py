from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from qfluentwidgets import PushButton, InfoBar, FluentIcon, MessageBox, BodyLabel

from midoWrapper import *


class ParseInterface(QWidget):
    """The interface for parsing the music."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ParseInterface")
        self.initUi()
        self.filename = None
        self.fileBtn.clicked.connect(self.fileDialog)
        self.startBtn.clicked.connect(self.startParse)

    def initUi(self):
        # layout
        self.form = QVBoxLayout(self)
        self.form.setContentsMargins(16, 20, 16, 20)
        self.form.setSpacing(0)
        self.form.setAlignment(Qt.AlignTop)

        # label
        self.fileLabel = BodyLabel("未选择", self)

        # button
        self.fileBtn = PushButton("选择文件", self)
        self.fileBtn.setFixedWidth(200)
        self.startBtn = PushButton("开始解析", self)
        self.startBtn.setFixedWidth(200)

        self.form.addWidget(self.fileBtn)
        self.form.addSpacing(10)
        self.form.addWidget(self.fileLabel)
        self.form.addSpacing(20)
        self.form.addWidget(self.startBtn)
        self.setLayout(self.form)

    def fileDialog(self):
        title = "Midi解析"
        dialog = QFileDialog(self, title, filter="midi files (*.mid)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            self.filename = dialog.selectedFiles()[0]
            self.fileLabel.setText(f"选择midi: {self.filename}")

    def startParse(self):
        try:
            self._parseMidi()
            InfoBar.success("解析完成！", "请查看你的midi文件夹", duration=2000, parent=self)
        except Exception as e:
            warning = "请检查midi文件是否符合规范\n此解析不兼容转调变速，同时需要使用midiEditor导出文件！\n"
            warning += f"错误信息: {e}"
            wrongBox = MessageBox("解析失败", warning, self)
            wrongBox.exec()

    def _parseMidi(self):
        midi = Midi.from_midi(self.filename)
        for track in midi.tracks:
            print(track)
