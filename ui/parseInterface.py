import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
)
from PyQt5.QtGui import QDesktopServices
from qfluentwidgets import (
    PushButton,
    PrimaryPushButton,
    InfoBar,
    MessageBox,
    BodyLabel,
    CardWidget,
)

from midoWrapper import Midi
from .config import cfg
from .outputEdit import OutputEdit


class ParseInterface(QWidget):
    """The interface for parsing the music."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ParseInterface")
        self.filename = None
        self.initUi()
        self.connectSignalToSlot()
        self.initParameters()

    def initUi(self):
        # layout
        self.form = QVBoxLayout(self)
        self.form.setContentsMargins(16, 20, 16, 20)
        self.form.setSpacing(0)
        self.form.setAlignment(Qt.AlignTop)

        # label
        self.fileLabel = BodyLabel("未选择", self)

        # button
        self.fileLayout = QHBoxLayout()
        self.fileLayout.setContentsMargins(0, 0, 0, 0)
        self.fileBtn = PushButton("选择midi")
        self.fileBtn.setFixedWidth(150)
        self.clearBtn = PushButton("清空midi")
        self.clearBtn.setFixedWidth(150)
        self.refreshBtn = PushButton("清空控制台")
        self.refreshBtn.setFixedWidth(150)
        self.fileLayout.addWidget(self.fileBtn)
        self.fileLayout.addWidget(self.clearBtn)
        self.fileLayout.addWidget(self.refreshBtn)
        self.fileLayout.addStretch(1)

        self.startBtn = PrimaryPushButton("开始解析", self)
        self.startBtn.setFixedWidth(150)

        # output
        self.output = OutputEdit("parse.txt", self)

        # card
        self.card = CardWidget(self)
        self.cardVbox = QVBoxLayout()
        self.cardVbox.setContentsMargins(25, 20, 25, 20)
        self.card.setLayout(self.cardVbox)
        self.cardVbox.addLayout(self.fileLayout)
        self.cardVbox.addSpacing(10)
        self.cardVbox.addWidget(self.fileLabel)
        self.cardVbox.addSpacing(20)
        self.cardVbox.addWidget(self.startBtn)

        self.form.addWidget(self.card)
        self.form.addSpacing(20)
        self.form.addWidget(self.output)
        self.setLayout(self.form)

    def initParameters(self):
        self.filename = cfg.files["parseMidi"]
        if self.filename is not None:
            self.fileLabel.setText(self.filename)
        else:
            self.fileLabel.setText("未选择")

    def connectSignalToSlot(self):
        self.fileBtn.clicked.connect(self.fileDialog)
        self.clearBtn.clicked.connect(self.clearFile)
        self.refreshBtn.clicked.connect(self.clearOutput)
        self.startBtn.clicked.connect(self.startParse)

    def fileDialog(self):
        title = "Midi解析"
        w = QFileDialog(self, title, filter="midi files (*.mid)")
        w.setFileMode(QFileDialog.ExistingFile)
        if w.exec_():
            files = w.selectedFiles()
            if files == []:
                return
            self.filename = files[0]
            self.fileLabel.setText(self.filename)

    def clearFile(self):
        self.filename = None
        self.fileLabel.setText("未选择")

    def clearOutput(self):
        self.output.clear()

    def startParse(self):
        if self.filename is None:
            InfoBar.error("未选择文件", "请先选择midi文件！", duration=3000, parent=self)
            return

        cfg.files["parseMidi"] = self.filename

        try:
            self.parseMidi()
            InfoBar.success("解析完成！", "请查看你的midi文件夹", duration=3000, parent=self)
            if cfg.openWhenDone:
                qurl = QUrl.fromLocalFile(cfg.files["outputFolder"])
                QDesktopServices.openUrl(qurl)

        except Exception as e:
            warning = "请检查midi文件是否符合规范\n此解析不兼容转调变速，同时需要使用midiEditor导出文件！\n"
            warning += "错误信息: " + str(e).replace("\n", " ")
            wrongBox = MessageBox("解析失败", warning, self)
            wrongBox.exec()

    def parseMidi(self):
        filename = cfg.files["outputFolder"] + "parse.txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        midi = Midi.from_midi(self.filename)

        header = midi.brief_info()
        for line in header.split("\n"):
            self.output.appendLine(line, "green", True)

        info = str(midi)
        for line in info.split("\n"):
            if line.startswith(("Track", "=========")):
                self.output.appendLine(line, "red", True)
            elif line.startswith("instrument"):
                self.output.appendLine(line, "red")
            elif line.startswith("-----"):
                self.output.appendLine(line, "blue", True)
            else:
                self.output.appendLine(line)

        self.output.printFinal()

        with open(filename, "w") as f:
            f.write(header)
            f.write(info)
