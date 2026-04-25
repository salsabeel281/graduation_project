# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.login_page import LoginPage

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginPage()
    window.show()
    sys.exit(app.exec_())