from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QEasingCurve
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QFileDialog
from qfluentwidgets import (
    setTheme,
    theme,
    Theme,
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
from .parseInterface import ParseInterface
from .trainInterface import TrainInterface

# import darkdetect


class StackedWidget(QFrame):
    """Stacked widget"""

    currentChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget):
        """add widget to view"""
        self.view.addWidget(widget)

    def widget(self, index: int):
        return self.view.widget(index)

    def setCurrentWidget(self, widget, popOut=False):
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        # self.setQss()

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationBar = NavigationBar(self)
        self.stackWidget = StackedWidget(self)

        self.trainInterface = TrainInterface(self)
        self.parseInterface = ParseInterface(self)

        self.initLayout()
        self.initNavigation()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 48, 0, 0)
        self.hBoxLayout.addWidget(self.navigationBar)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

    def initNavigation(self):
        self.addSubInterface(self.trainInterface, FluentIcon.SEND, "训练")
        self.addSubInterface(self.parseInterface, FluentIcon.MUSIC_FOLDER, "解析")
        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.navigationBar.setCurrentItem(self.trainInterface.objectName())

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

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationBar.setCurrentItem(widget.objectName())

    # def setQss(self):
    #     isDark = darkdetect.isDark()
    #     if isDark:
    #         setTheme(Theme.DARK)
    #     color = "dark" if isDark else "light"
    #     with open(f"ui/resource/{color}.qss", encoding='utf-8') as f:
    #         self.setStyleSheet(f.read())
