from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFileDialog
from qfluentwidgets import (
    LineEdit,
    BodyLabel,
    NavigationBar,
    FluentIcon,
    FlowLayout,
    PushButton,
    NavigationInterface,
    NavigationItemPosition,
    OpacityAniStackedWidget,
    PopUpAniStackedWidget,
    FolderListDialog,
)
from qframelesswindow import FramelessWindow
from .parse import ParseInterface


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = PopUpAniStackedWidget(self)

        self.homeInterface = QWidget(self)
        self.appInterface = ParseInterface(self)
        self.videoInterface = QWidget(self)
        self.libraryInterface = QWidget(self)

        self.initLayout()
        self.initNavigation()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FluentIcon.PLAY, "训练")
        self.addSubInterface(self.appInterface, FluentIcon.DOWNLOAD, "解析")
        self.addSubInterface(self.videoInterface, FluentIcon.VIDEO, "视频")
        self.addSubInterface(self.libraryInterface, FluentIcon.BOOK_SHELF, "库")
        # self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.homeInterface.objectName())

    def addSubInterface(
        self,
        interface,
        icon,
        text: str,
        position=NavigationItemPosition.TOP,
        selectedIcon=None,
    ):
        self.stackWidget.addWidget(interface)
        self.navigationBar.addItem(
            routeKey=interface.objectName(),
            icon=icon,
            text=text,
            onClick=lambda: self.stackWidget.setCurrentWidget(interface),
            selectedIcon=selectedIcon,
            position=position,
        )
