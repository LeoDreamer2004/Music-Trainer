import sys
import os
from time import time
from multiprocessing import Process, Pipe
from multiprocessing.connection import PipeConnection

from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPlainTextEdit,
    QFormLayout,
)
from PyQt5.QtGui import QFont
from qfluentwidgets import (
    PushButton,
    PrimaryPushButton,
    InfoBar,
    MessageBox,
    MessageBoxBase,
    BodyLabel,
    LineEdit,
    SpinBox,
    CompactSpinBox,
    DoubleSpinBox,
    CompactDoubleSpinBox,
    SwitchButton,
)

from midoWrapper import Midi
from train import train


class TrainInterface(QWidget):
    """The interface for training with GA."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("trainInterface")
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
        self.fileWidget = QWidget()
        self.fileLayout = QHBoxLayout(self.fileWidget)
        self.fileLayout.setContentsMargins(0, 0, 0, 0)
        self.fileWidget.setLayout(self.fileLayout)
        self.fileBtn = PushButton("选择参考midi")
        self.fileBtn.setFixedWidth(150)
        self.clearBtn = PushButton("清空midi")
        self.clearBtn.setFixedWidth(150)
        self.fileLayout.addWidget(self.fileBtn)
        self.fileLayout.addWidget(self.clearBtn)
        self.fileLayout.addStretch(1)

        self.trainWidget = QWidget()
        self.trainLayout = QHBoxLayout(self.trainWidget)
        self.trainLayout.setContentsMargins(0, 0, 0, 0)
        self.trainWidget.setLayout(self.trainLayout)
        self.startBtn = PrimaryPushButton("开始训练")
        self.startBtn.setFixedWidth(150)
        self.paramBtn = PushButton("参数设置")
        self.paramBtn.setFixedWidth(150)
        self.trainLayout.addWidget(self.startBtn)
        self.trainLayout.addWidget(self.paramBtn)
        self.trainLayout.addStretch(1)

        # output
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.output.setFont(QFont("Consolas", 10))

        self.form.addWidget(self.fileWidget)
        self.form.addSpacing(10)
        self.form.addWidget(self.fileLabel)
        self.form.addSpacing(20)
        self.form.addWidget(self.trainWidget)
        self.form.addSpacing(20)
        self.form.addWidget(self.output)
        self.setLayout(self.form)

    def connectSignalToSlot(self):
        self.fileBtn.clicked.connect(self.fileDialog)
        self.clearBtn.clicked.connect(self.clearFile)
        self.startBtn.clicked.connect(self.startTrain)
        self.paramBtn.clicked.connect(self.showParamWindow)

    def initParameters(self):
        self.population = 20
        self.mutation = 0.8
        self.iteration = 1000
        self.withCompany = True

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
        self.fileLabel.setText("未选择")

    def startTrain(self):
        if self.filename is None:
            InfoBar.error("未选择文件", "请先选择参考midi文件！", duration=1500, parent=self)
            return
        self.trainThr = TrainConnectionThread(self)
        self.trainThr.start()
        self.trainThr.setPriority(QThread.LowestPriority)

    def showParamWindow(self):
        paramWindow = ParameterWindow(self)
        if paramWindow.exec():
            self.population = paramWindow.populationEdit.value()
            self.mutation = paramWindow.mutationEdit.value()
            self.iteration = paramWindow.iterationEdit.value() * 100
            self.withCompany = paramWindow.withCompany

    def writeBuf(self, buf: str):
        if buf == "\n":
            return
        elif buf.startswith("----"):
            self.output.appendHtml(f"<font color=blue><b>{buf}</b></font>")
        elif buf.startswith(("[!]", "Final")):
            self.output.appendHtml(f"<font color=red><b>{buf}</b></font>")
        else:
            self.output.appendPlainText(buf)

    def trainStatus(self, status: int, info: str):
        if status == "1":
            InfoBar.success(
                "训练完成", "训练已完成，可在midi/result.mid查看结果", duration=1500, parent=self
            )
        elif status == "0":
            warning = "请检查midi文件是否符合规范或参数是否正确\n此解析不兼容转调变速，同时需要使用midiEditor导出文件！\n"
            warning += f"错误信息: {info}"
            box = MessageBox("训练失败", warning, parent=self)
            box.exec_()


class TrainConnectionThread(QThread):
    trainStatus = pyqtSignal(str, str)
    outputBuf = pyqtSignal(str)

    def __init__(self, parent: TrainInterface):
        super().__init__(parent)
        self.trainStatus.connect(parent.trainStatus)
        self.outputBuf.connect(parent.writeBuf)
        self.recv, self.send = Pipe()
        self.process = Process(
            target=TrainProcess.run,
            args=(
                self.send,
                parent.filename,
                os.path.join(os.path.dirname(os.getcwd()), "midi/result.mid"),
                parent.population,
                parent.mutation,
                parent.iteration,
                parent.withCompany,
            ),
        )

    def run(self):
        self.process.start()
        while True:
            if self.recv.poll():
                msg: Protocol = self.recv.recv()
                if msg.type == "status":  # train finished
                    self.trainStatus.emit(msg.value, msg.info)
                    break
                elif msg.type == "buf":
                    self.outputBuf.emit(msg.value)


class Protocol:
    def __init__(self, msg_type: str, value: str, info: str = None):
        self.type = msg_type
        self.value = value
        self.info = info


class TrainProcess:
    @staticmethod
    def run(
        connect: PipeConnection,
        reference_file: str,
        output_file: str,
        population_size: int,
        mutation_rate: float,
        iteration_num: int,
        with_accompaniment: bool,
    ):
        orignal = sys.stdout
        sys.stdout = RedirectStdout(connect)

        try:
            t_start = time()

            refmidi = Midi.from_midi(reference_file)
            ref_track, left_hand = refmidi.tracks
            result = train(ref_track, population_size, mutation_rate, iteration_num)

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
            connect.send(Protocol("status", "1"))

        except Exception as e:
            connect.send(Protocol("status", "0", str(e)))

        finally:
            sys.stdout = orignal


class RedirectStdout:
    def __init__(self, connect: PipeConnection):
        self.stdout = sys.stdout
        self.connect = connect

    def write(self, text: str):
        self.connect.send(Protocol("buf", text))

    def flush(self):
        pass


class ParameterWindow(MessageBoxBase):
    """Custom message box"""

    def __init__(self, parent: TrainInterface = None):
        super().__init__(parent)
        self.form = QFormLayout()

        self.populationLabel = BodyLabel("种群数量")
        self.populationEdit = SpinBox()
        self.populationEdit.setValue(parent.population)
        self.mutationLabel = BodyLabel("变异率")
        self.mutationEdit = DoubleSpinBox()
        self.mutationEdit.setValue(parent.mutation)
        self.iterationLabel = BodyLabel("迭代次数(*100)")
        self.iterationEdit = SpinBox()
        self.iterationEdit.setValue(parent.iteration // 100)
        self.companyLabel = BodyLabel("伴奏")
        self.companyEdit = SwitchButton()
        self.companyEdit.setChecked(parent.withCompany)
        self.withCompany = parent.withCompany
        self.companyEdit.checkedChanged.connect(self.updateCommpany)

        self.form.addRow(self.populationLabel, self.populationEdit)
        self.form.addRow(self.mutationLabel, self.mutationEdit)
        self.form.addRow(self.iterationLabel, self.iterationEdit)
        self.form.addRow(self.companyLabel, self.companyEdit)
        self.viewLayout.addLayout(self.form)

    def updateCommpany(self, choose: bool):
        self.withCompany = choose
