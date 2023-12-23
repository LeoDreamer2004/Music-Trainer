# This is a simple application which use genetic algorithm to generate music.
# Copyright © 2023 LeoDreamer2004, crlcrl1

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.



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
    from ui.mainWindow import MainWindow

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
