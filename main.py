import sys
from PyQt5.QtWidgets import QApplication

from ui.login_page import LoginPage
from ui.register_page import RegisterPage

if __name__ == "__main__":
    app = QApplication(sys.argv)

    login = LoginPage()
    register = RegisterPage(login)

    login.register_page = register   # ✅ الربط الصح

    login.show()

    sys.exit(app.exec_())