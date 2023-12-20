import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPlainTextEdit,
)
from PyQt5.QtGui import QFont, QDesktopServices
from qfluentwidgets import (
    PushButton,
    InfoBar,
    MessageBox,
    BodyLabel,
    StrongBodyLabel,
    CardWidget,
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

        self.authorCard = SoftwareCard(self)
        self.licenseCard = LicenseCard(self)

        self.mainLayout.addWidget(self.authorCard)
        self.mainLayout.addWidget(self.licenseCard)
        self.setWidget(self.view)

        self.setStyleSheet("QScrollArea {border: none; background:transparent}")
        self.view.setStyleSheet("QWidget {background:transparent}")


class SoftwareCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUi()
        self.connectSignalToSlot()

    def initUi(self):
        self.setTitle("关于")
        # self.setFixedWidth(650)

        self.authorLabel = StrongBodyLabel("Github: LeoDreamer2004, crlcrl1", self)
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
        # self.setFixedWidth(650)

        self.authorLabel = BodyLabel("真的有人会在意这种小程序的许可吗？")

        self.viewLayout.addWidget(self.authorLabel)
