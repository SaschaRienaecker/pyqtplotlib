import sys
from PyQt5.QtWidgets import QApplication
from guiwindows.scatter_plot import ScatterPlot

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScatterPlot()
    window.show()
    sys.exit(app.exec_())
