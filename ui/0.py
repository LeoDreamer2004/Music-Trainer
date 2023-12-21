from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QLabel

app = QApplication([])

# 创建一个 QLabel（标签）控件，并设置其图标
label = QLabel()
open("../rsc/img/icon.png")
icon = QIcon("../rsc/img/icon.png")  # 图标文件的路径
label.setPixmap(icon.pixmap(50, 50))  # 使用图标创建一个 QPixmap 对象，并将其作为标签的图像

# 显示标签
label.show()

# 运行程序
app.exec_()
