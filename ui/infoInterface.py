from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import QFont, QDesktopServices
from qfluentwidgets import (
    PushButton,
    InfoBar,
    MessageBox,
    TextEdit,
    BodyLabel,
    StrongBodyLabel,
    CardWidget,
    PlainTextEdit,
    HyperlinkLabel,
    PrimaryPushButton,
    FluentIcon,
    IconWidget,
    HeaderCardWidget,
    SingleDirectionScrollArea,
)


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
        self.authorCard = SoftwareCard(self)
        self.licenseCard = LicenseCard(self)

        self.mainLayout.addWidget(self.usageCard)
        self.mainLayout.addWidget(self.authorCard)
        self.mainLayout.addWidget(self.licenseCard)
        self.setWidget(self.view)

        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet("QWidget {background:transparent}")


class UsageCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        self.setTitle("使用说明")

        self.usageText = BodyLabel()
        self.usageText.setFont(QFont("Microsoft YaHei", 10))
        self.usageText.setContentsMargins(0, 0, 0, 0)
        self.usageText.setWordWrap(True)
        usage = (
            "本程序是一个基于遗传算法的音乐生成器，可以生成一段音乐的 midi 文件。"
            "训练过程基于一个参考 midi 文件，通过遗传算法不断迭代，生成音乐。<br />"
            "<b>参考 midi 文件必须是双音轨的，主旋律不可以有和弦。同时尽量不要出现转调、变速。</b><br />"
            "对于参考 midi 文件，由于库的限制，请在导出 midi 后使用 midiEditor 打开并保存一次。"
        )
        self.usageText.setText(usage)

        self.linkLabel = HyperlinkLabel(
            QUrl(
                "https://github.com/LeoDreamer2004/PKU-MathInMusic-2023/blob/main/report.pdf"
            ),
            "点击查看详细信息",
            self,
        )

        self.vLayout = QVBoxLayout()
        self.vLayout.setContentsMargins(0, 0, 0, 0)
        self.vLayout.addWidget(self.usageText)
        self.vLayout.addWidget(self.linkLabel)
        self.viewLayout.addLayout(self.vLayout)


class SoftwareCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()
        self.connectSignalToSlot()

    def initUi(self):
        self.setTitle("关于")

        self.authorLabel = StrongBodyLabel("作者Github: LeoDreamer2004, crlcrl1", self)
        self.authorLabel.setFixedHeight(30)
        self.githubIcon = IconWidget(FluentIcon.GITHUB, self)
        self.githubIcon.setFixedSize(30, 30)
        self.githubBtn = PrimaryPushButton("项目代码", self)
        self.githubBtn.setFixedWidth(150)
        self.issueBtn = PushButton("问题反馈", self)
        self.issueBtn.setFixedWidth(150)
        self.authorBtn = PushButton("作者主页", self)
        self.authorBtn.setFixedWidth(150)

        self.vBoxLayout = QVBoxLayout()
        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.setSpacing(20)
        self.vBoxLayout.setSpacing(20)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.hBoxLayout.addWidget(self.githubIcon)
        self.hBoxLayout.addWidget(self.githubBtn)
        self.hBoxLayout.addWidget(self.issueBtn)
        self.hBoxLayout.addWidget(self.authorBtn)

        self.vBoxLayout.addWidget(self.authorLabel)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.viewLayout.addLayout(self.vBoxLayout)

    def connectSignalToSlot(self):
        self.githubBtn.clicked.connect(self.openGithub)
        self.issueBtn.clicked.connect(self.openIssue)
        self.authorBtn.clicked.connect(self.openAuthor)

    def openGithub(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/LeoDreamer2004/PKU-MathInMusic-2023")
        )

    def openIssue(self):
        QDesktopServices.openUrl(
            QUrl("https://github.com/LeoDreamer2004/PKU-MathInMusic-2023/issues")
        )

    def openAuthor(self):
        QDesktopServices.openUrl(QUrl("https://github.com/LeoDreamer2004"))


class LicenseCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()

    def initUi(self):
        self.setTitle("法律与版权许可")
        self.authorLabel = BodyLabel("真的有人会在意这种小程序的许可吗？")
        self.viewLayout.addWidget(self.authorLabel)
