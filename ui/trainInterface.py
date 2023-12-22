import sys
from time import time
from multiprocessing import Process, Pipe, freeze_support
from multiprocessing.connection import PipeConnection

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QFormLayout,
)
from PyQt5.QtGui import QFont, QDesktopServices
from qfluentwidgets import (
    PushButton,
    PrimaryPushButton,
    InfoBar,
    MessageBox,
    MessageBoxBase,
    BodyLabel,
    PlainTextEdit,
    SpinBox,
    CardWidget,
    DoubleSpinBox,
    SwitchButton,
)

from midoWrapper import Midi
from train import train
from .config import cfg


TRAIN_OUTPUT = "result.mid"


def outputPath() -> str:
    return cfg.files["outputFolder"] + TRAIN_OUTPUT


class TrainInterface(QWidget):
    """The interface for training with GA."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("trainInterface")
        self.refName = None
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
        self.fileLabel = BodyLabel(self)

        # button
        self.fileLayout = QHBoxLayout()
        self.fileLayout.setContentsMargins(0, 0, 0, 0)
        self.fileBtn = PushButton("选择参考midi")
        self.fileBtn.setFixedWidth(150)
        self.clearBtn = PushButton("清空midi")
        self.clearBtn.setFixedWidth(150)
        self.refreshBtn = PushButton("清空控制台")
        self.refreshBtn.setFixedWidth(150)
        self.fileLayout.addWidget(self.fileBtn)
        self.fileLayout.addWidget(self.clearBtn)
        self.fileLayout.addWidget(self.refreshBtn)
        self.fileLayout.addStretch(1)

        self.trainLayout = QHBoxLayout()
        self.trainLayout.setContentsMargins(0, 0, 0, 0)
        self.startBtn = PrimaryPushButton("开始训练")
        self.startBtn.setFixedWidth(150)
        self.paramBtn = PushButton("参数设置")
        self.paramBtn.setFixedWidth(150)
        self.stopBtn = PushButton("停止训练")
        self.stopBtn.setFixedWidth(150)
        self.stopBtn.setVisible(False)
        self.trainLayout.addWidget(self.startBtn)
        self.trainLayout.addWidget(self.paramBtn)
        self.trainLayout.addWidget(self.stopBtn)
        self.trainLayout.addStretch(1)

        # output
        self.output = PlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setLineWrapMode(PlainTextEdit.NoWrap)
        self.output.setFont(QFont("Consolas", 10))

        # card
        self.card = CardWidget(self)
        self.cardVbox = QVBoxLayout()
        self.cardVbox.setContentsMargins(25, 20, 25, 20)
        self.card.setLayout(self.cardVbox)
        self.cardVbox.addLayout(self.fileLayout)
        self.cardVbox.addSpacing(10)
        self.cardVbox.addWidget(self.fileLabel)
        self.cardVbox.addSpacing(20)
        self.cardVbox.addLayout(self.trainLayout)

        self.form.addWidget(self.card)
        self.form.addSpacing(20)
        self.form.addWidget(self.output)
        self.setLayout(self.form)

    def connectSignalToSlot(self):
        self.fileBtn.clicked.connect(self.fileDialog)
        self.clearBtn.clicked.connect(self.clearFile)
        self.refreshBtn.clicked.connect(self.clearOutput)
        self.startBtn.clicked.connect(self.startTrain)
        self.stopBtn.clicked.connect(self.stopTrain)
        self.paramBtn.clicked.connect(self.showParamWindow)

    def initParameters(self):
        self.population = cfg.trainPrams["population"]
        self.mutation = cfg.trainPrams["mutation"]
        self.iteration = cfg.trainPrams["iteration"]
        self.withCompany = cfg.trainPrams["withCompany"]
        self.refName = cfg.files["trainReference"]
        if self.refName is not None:
            self.fileLabel.setText(self.refName)
        else:
            self.fileLabel.setText("未选择")

    def fileDialog(self):
        title = "机器作曲训练"
        dialog = QFileDialog(self, title, filter="midi files (*.mid)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            files = dialog.selectedFiles()
            if files == []:
                return
            self.refName = files[0]
            self.fileLabel.setText(self.refName)

    def clearFile(self):
        self.refName = None
        self.fileLabel.setText("未选择")

    def clearOutput(self):
        self.output.clear()

    def startTrain(self):
        if self.refName is None:
            InfoBar.error("未选择文件", "请先选择参考midi文件！", duration=3000, parent=self)
            return

        self.startBtn.setEnabled(False)
        self.stopBtn.setVisible(True)
        cfg.trainPrams["population"] = self.population
        cfg.trainPrams["mutation"] = self.mutation
        cfg.trainPrams["iteration"] = self.iteration
        cfg.trainPrams["withCompany"] = self.withCompany
        cfg.files["trainReference"] = self.refName

        self.trainThr = TrainConnectionThread(self)
        self.trainThr.start()
        self.trainThr.setPriority(QThread.LowestPriority)

    def stopTrain(self):
        self.trainThr.stopTrain()

    def showParamWindow(self):
        w = ParameterWindow(self)
        w.yesButton.setText("确定")
        w.cancelButton.setText("取消")
        if w.exec():
            self.population = w.populationEdit.value()
            self.mutation = w.mutationEdit.value()
            self.iteration = w.iterationEdit.value()
            self.withCompany = w.withCompany

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
        if status == "0":
            InfoBar.success("训练完成", f"可查看结果{TRAIN_OUTPUT}", duration=3000, parent=self)
            if cfg.openWhenDone:
                qurl = QUrl.fromLocalFile(cfg.files["outputFolder"])
                QDesktopServices.openUrl(qurl)
        elif status == "1":
            warning = "请检查midi文件是否符合规范或参数是否正确\n此解析不兼容转调变速，同时需要使用midiEditor导出文件！\n"
            warning += f"错误信息: {info}"
            box = MessageBox("训练失败", warning, parent=self)
            box.exec_()
        elif status == "2":
            InfoBar.warning("训练已终止", "训练被用户打断", duration=3000, parent=self)
        self.startBtn.setEnabled(True)
        self.stopBtn.setVisible(False)


class TrainConnectionThread(QThread):
    trainStatus = pyqtSignal(str, str)
    outputBuf = pyqtSignal(str)

    def __init__(self, parent: TrainInterface):
        super().__init__(parent)
        self.trainStatus.connect(parent.trainStatus)
        self.outputBuf.connect(parent.writeBuf)
        self.recv, self.send = Pipe()
        freeze_support()
        self.process = Process(
            target=TrainProcess.run,
            args=(
                self.send,
                parent.refName,
                outputPath(),
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

    def stopTrain(self):
        self.trainStatus.emit("2", None)
        self.process.terminate()
        self.terminate()


class Protocol:
    def __init__(self, msg_type: str, value: str, info: str = None):
        self.type = msg_type
        self.value = value
        self.info = info


class TrainProcess:
    @staticmethod
    def run(
        connect: PipeConnection,
        referenceFile: str,
        outputFile: str,
        population: int,
        mutation: float,
        iteration: int,
        withCompany: bool,
    ):
        orignal = sys.stdout
        sys.stdout = RedirectStdout(connect)

        try:
            t_start = time()

            refmidi = Midi.from_midi(referenceFile)
            ref_track, left_hand = refmidi.tracks
            result = train(ref_track, population, mutation, iteration)

            s = Midi(ref_track.sts)
            s.sts.bpm = 120
            s.tracks.append(result)

            # accompaniment (stolen from reference)
            if withCompany:
                for note in left_hand.note:
                    note.velocity = ref_track.sts.velocity
                s.tracks.append(left_hand)

            s.save_midi(outputFile)
            print(f"Time cost: {time() - t_start}s")
            print(f"Result saved to {outputFile}")
            connect.send(Protocol("status", "0"))

        except Exception as e:
            connect.send(Protocol("status", "1", str(e)))

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
        self.mutationEdit.setRange(0, 1)
        self.mutationEdit.setSingleStep(0.1)
        self.mutationEdit.setValue(parent.mutation)

        self.iterationLabel = BodyLabel("迭代次数")
        self.iterationEdit = SpinBox()
        self.iterationEdit.setRange(1, 10000)
        self.iterationEdit.setSingleStep(100)
        self.iterationEdit.setValue(parent.iteration)

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
