from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
)
from PyQt5.QtGui import QDesktopServices, QPixmap, QColor
from qfluentwidgets import (
    setThemeColor,
    InfoBar,
    PushButton,
    BodyLabel,
    CaptionLabel,
    HyperlinkLabel,
    ComboBox,
    PrimaryPushButton,
    ColorDialog,
    FluentIcon,
    IconWidget,
    HeaderCardWidget,
    SingleDirectionScrollArea,
)
from .config import cfg


class InfoInterface(SingleDirectionScrollArea):
    """The interface for information."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("InfoInterface")
        self.filename = None
        self.initUi()

    def initUi(self):
        self.view = QWidget(self)
        self.mainLayout = QVBoxLayout(self.view)
        self.mainLayout.setAlignment(Qt.AlignTop)
        self.mainLayout.setContentsMargins(16, 20, 16, 20)

        self.usageCard = UsageCard(self)
        self.personalCard = PersonalizationCard(self)
        self.authorCard = LinkCard(self)
        self.licenseCard = LicenseCard(self)

        self.mainLayout.addWidget(self.usageCard, 0)
        self.mainLayout.addWidget(self.personalCard, 0)
        self.mainLayout.addWidget(self.authorCard, 0)
        self.mainLayout.addWidget(self.licenseCard, 0)

        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet("QWidget {background:transparent}")


class MyCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.interface = parent
        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(self.vLayout)
        self.initUi()

    def initUi(self):
        raise NotImplementedError


class UsageCard(MyCard):
    def initUi(self):
        self.setTitle("使用说明")

        self.usageText = BodyLabel()
        self.usageText.setContentsMargins(0, 0, 0, 0)
        self.usageText.setWordWrap(True)
        usage = (
            "本程序是一个基于遗传算法的音乐生成器，可以生成一段音乐的 midi 文件。"
            "训练过程基于一个参考 midi 文件，通过遗传算法不断迭代，生成音乐。<br />"
            "<b>参考 midi 文件必须是双音轨的，主旋律不可以有和弦。同时尽量不要出现转调、变速。</b>"
            "训练结束后，如果开启伴奏，生成的 midi 伴奏将直接复制参考 midi 的伴奏。<br />"
            "对于参考 midi 文件，由于库的限制，请在导出 midi 后使用 midiEditor 打开并保存一次。"
        )
        self.usageText.setText(usage)

        self.linkLayout = QHBoxLayout()
        self.reportLabel = HyperlinkLabel(
            QUrl(
                "https://github.com/LeoDreamer2004/PKU-MathInMusic-2023/blob/main/report/report.pdf"
            ),
            "详细信息",
            self,
        )
        self.downloadLabel = HyperlinkLabel(
            QUrl("http://www.midieditor.org/index.php?category=download"),
            "下载 midiEditor",
            self,
        )
        self.linkLayout.addWidget(self.reportLabel)
        self.linkLayout.addSpacing(20)
        self.linkLayout.addWidget(self.downloadLabel)
        self.linkLayout.addStretch(1)

        self.vLayout.addWidget(self.usageText)
        self.vLayout.addLayout(self.linkLayout)


class PersonalizationCard(MyCard):
    def initUi(self):
        self.setTitle("个性化")

        self.themeDict = {
            "auto": "跟随系统",
            "light": "浅色",
            "dark": "深色",
        }
        self.themeBox = ComboBox(self)
        self.themeBox.addItems(self.themeDict.values())
        self.themeBox.setCurrentText(self.themeDict[cfg.ui["theme"]])
        self.themeBox.currentTextChanged.connect(self.updateTheme)
        self.themeLabel = BodyLabel("选择模式")
        self.themeCaption = CaptionLabel("重启软件生效")

        self.colorBtn = PushButton()
        self.colorBtn.clicked.connect(self.chooseColorSlot)
        self.updateColor(QColor(cfg.ui["themeColor"]))
        self.colorLabel = BodyLabel("主题色")

        self.outputBtn = PushButton("选择文件夹")
        self.outputBtn.clicked.connect(self.chooseOutputSlot)
        self.outputLabel = BodyLabel("导出文件夹")
        self.outputCaption = CaptionLabel(cfg.files["outputFolder"])

        self.vLayout.setSpacing(10)
        self.addLine(self.themeBox, self.themeLabel, self.themeCaption)
        self.addLine(self.colorBtn, self.colorLabel)
        self.addLine(self.outputBtn, self.outputLabel, self.outputCaption)

    def addLine(self, widget: QWidget, label: BodyLabel, caption: CaptionLabel = None):
        labelLayout = QVBoxLayout()
        labelLayout.setSpacing(2)
        labelLayout.addWidget(label)
        if caption is not None:
            labelLayout.addWidget(caption)

        lineLayout = QHBoxLayout()
        lineLayout.setContentsMargins(0, 0, 0, 0)
        widget.setFixedWidth(120)
        lineLayout.addLayout(labelLayout)
        lineLayout.addWidget(widget, alignment=Qt.AlignRight)
        self.vLayout.addLayout(lineLayout)

    def chooseColorSlot(self):
        w = ColorDialog(self.color, "选择主题颜色", self.interface)
        w.editLabel.setText("编辑颜色")
        w.yesButton.setText("确定")
        w.cancelButton.setText("取消")
        w.colorChanged.connect(self.updateColor)
        w.exec()

    def updateColor(self, color: QColor):
        cfg.ui["themeColor"] = color.name()
        setThemeColor(color)
        self.color = color
        showSquare = QPixmap(20, 20)
        showSquare.fill(self.color)
        self.colorBtn.setIcon(showSquare)
        self.colorBtn.setText(self.color.name())

    def updateTheme(self, text: str):
        for key, value in self.themeDict.items():
            if value == text:
                cfg.ui["theme"] = key
                break

    def chooseOutputSlot(self):
        path = QFileDialog.getExistingDirectory(
            self, "导出至", "", QFileDialog.ShowDirsOnly
        )
        cfg.files["outputFolder"] = path
        self.outputCaption.setText(path)


class LinkCard(MyCard):
    def initUi(self):
        self.setTitle("关于")

        # self.authorLabel = StrongBodyLabel("作者Github: LeoDreamer2004, crlcrl1", self)
        # self.authorLabel.setFixedHeight(30)
        self.githubIcon = IconWidget(FluentIcon.GITHUB, self)

        self.githubIcon.setFixedSize(30, 30)
        self.githubBtn = PrimaryPushButton("项目代码", self)
        self.githubBtn.setFixedWidth(150)
        self.issueBtn = PushButton("问题反馈", self)
        self.issueBtn.setFixedWidth(150)
        self.authorBtn = PushButton("作者主页", self)
        self.authorBtn.setFixedWidth(150)

        self.hLayout = QHBoxLayout()
        self.hLayout.setSpacing(20)
        self.vLayout.setSpacing(20)
        self.hLayout.setContentsMargins(0, 0, 0, 0)

        self.hLayout.addWidget(self.githubIcon)
        self.hLayout.addWidget(self.githubBtn)
        self.hLayout.addWidget(self.issueBtn)
        self.hLayout.addWidget(self.authorBtn)
        self.hLayout.addStretch(1)

        # self.vBoxLayout.addWidget(self.authorLabel)
        self.vLayout.addLayout(self.hLayout)

        self.connectSignalToSlot()

    def connectSignalToSlot(self):
        sourceUrl = "https://github.com/LeoDreamer2004/PKU-MathInMusic-2023"
        self.githubBtn.clicked.connect(self.openUrlSlot(sourceUrl))
        issueUrl = "https://github.com/LeoDreamer2004/PKU-MathInMusic-2023/issues"
        self.issueBtn.clicked.connect(self.openUrlSlot(issueUrl))
        authorUrl = "https://github.com/LeoDreamer2004"
        self.authorBtn.clicked.connect(self.openUrlSlot(authorUrl))

    def openUrlSlot(self, url: str):
        def wrapper():
            QDesktopServices.openUrl(QUrl(url))
            InfoBar.new(
                icon=FluentIcon.INFO,
                title="正在打开网页",
                content=url,
                orient=Qt.Vertical,
                duration=3000,
                parent=self.interface,
            )

        return wrapper


class LicenseCard(MyCard):
    def initUi(self):
        self.setTitle("法律与版权许可")
        announcement = "Copyright (c) 2023 LeoDreamer2004, crlcrl1 / MIT License"
        self.authorLabel = BodyLabel("真的有人会在意这种小程序的许可吗？")
        self.licenseText = CaptionLabel(announcement)
        self.vLayout.addWidget(self.authorLabel)
        self.vLayout.addWidget(self.licenseText)
