import os
import threading
from io import StringIO
from time import time


from midoWrapper import Midi
from ..train import train

from PyQt5 import QtCore
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


class TrainInterface(QWidget):
    """The interface for training with GA."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("trainInterface")
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
        self.fileLabel = BodyLabel("", self)

        # button
        self.fileWidget = QWidget()
        self.fileLayout = QHBoxLayout(self.fileWidget)
        self.fileWidget.setLayout(self.fileLayout)
        self.fileBtn = PushButton("选择参考midi")
        self.fileBtn.setFixedWidth(200)
        self.clearBtn = PushButton("清空midi")
        self.clearBtn.setFixedWidth(200)
        self.fileLayout.addWidget(self.fileBtn)
        self.fileLayout.addWidget(self.clearBtn)
        self.fileLayout.addStretch(1)

        self.startBtn = PushButton("开始训练", self)
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
        self.startBtn.clicked.connect(self.startTrain)

    def fileDialog(self):
        title = "机器作曲训练"
        dialog = QFileDialog(self, title, filter="midi files (*.mid)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            files = dialog.selectedFiles()
            if files == []:
                return
            self.filename = files[0]
            self.fileLabel.setText(f"参考midi: {self.filename}")

    def clearFile(self):
        self.filename = None
        self.fileLabel.setText("")

    def startTrain(self):
        if self.filename is None:
            InfoBar.error("未选择文件", "请先选择参考midi文件！", duration=2000, parent=self)
            return
        try:
            self._trainMidi()
            InfoBar.success("训练完成！", "请查看你的midi文件夹", duration=2000, parent=self)
        except Exception as e:
            warning = "请检查midi文件是否符合规范\n此解析不兼容转调变速，同时需要使用midiEditor导出文件！\n"
            warning += f"错误信息: {e}"
            wrongBox = MessageBox("解析失败", warning, self)
            wrongBox.exec()

    def _trainMidi(self):
        read_buf_thread = threading.Thread(target=self._read_buf)

        reference_file = "midi/reference.mid"
        output_file = "midi/result.mid"
        with_accompaniment = True

        t_start = time()

        refmidi = Midi.from_midi(reference_file)
        ref_track, left_hand = refmidi.tracks
        result = train(ref_track)

        s = Midi(ref_track.sts)
        s.sts.bpm = 120
        s.tracks.append(result)

        # accompaniment (stolen from reference)
        if with_accompaniment:
            for note in left_hand.note:
                note.velocity = ref_track.sts.velocity
            s.tracks.append(left_hand)

        s.save_midi(output_file)
        print(f"Time cost: {time() - t_start}s")

    def _read_buf(self):
        buf = StringIO()
        while True:
            buf.write(self.output.readAll())
            self.output.clear()
            self.output.insertPlainText(buf.getvalue())
            buf.truncate(0)
            buf.seek(0)
            QtCore.QThread.msleep(100)
