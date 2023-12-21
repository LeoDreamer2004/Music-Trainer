import sys


def module_check():
    try:
        # flake8: noqa
        import numpy, mido, PyQt5, qfluentwidgets, qframelesswindow
        from PyQt5 import QtCore, QtWidgets, QtGui
    except ImportError as e:
        from tkinter import messagebox

        error_msg = "缺乏相关模块依赖\n请查看README.md文件安装所需模块"
        error_msg += "\n\n错误信息：\n" + str(e)
        messagebox.showerror("错误", error_msg)
        sys.exit(1)
    else:
        del numpy, mido, PyQt5, qfluentwidgets, qframelesswindow
        del QtCore, QtWidgets, QtGui


if __name__ == "__main__":
    module_check()

    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
    from .ui.mainWindow import MainWindow

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
