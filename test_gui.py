import sys
from PyQt6.QtWidgets import QApplication, QWidget

app = QApplication(sys.argv)
w = QWidget()
w.resize(250, 150)
w.setWindowTitle('环境测试')
w.show()
sys.exit(app.exec())