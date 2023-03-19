import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    window.plot_widget.plot(x, y, symbol='o', name='data1')
    window.show()
    sys.exit(app.exec_())
