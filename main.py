import sys
from PyQt5.QtWidgets import QApplication
from views import BallStabilizerDashboard


def main():
    app = QApplication(sys.argv)
    window = BallStabilizerDashboard()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
