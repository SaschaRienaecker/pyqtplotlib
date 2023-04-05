from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from gui.plot_widget import CustomPlotWidget

# class CustomPlotWidget(pg.PlotWidget):
#     def __init__(self, parent=None, **kwargs):
#         super().__init__(parent=parent, **kwargs)
#         # Add custom initialization code here


# class MultiCustomPlotWidget(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent=parent)
#         # Create a box layout
#         layout = QtWidgets.QGridLayout()
#         self.setLayout(layout)
        

#         # Add 9 CustomPlotWidget instances to the layout
#         for i in range(3):
#             for j in range(3):
#                 plot_widget = CustomPlotWidget()
#                 layout.addWidget(plot_widget, i, j)


class MultiCustomPlotWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Create a grid layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        splitter_width = 10 # width of the splitter handle

        # Create a vertical splitter for each row
        row_splitters = []
        for i in range(3):
            v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            v_splitter.setHandleWidth(splitter_width)
            row_splitters.append(v_splitter)
            layout.addWidget(v_splitter, i, 0, 1, 3)

        # Add 9 CustomPlotWidget instances to the layout
        for i in range(3):
            for j in range(3):
                plot_widget = CustomPlotWidget()
                row_splitters[i].addWidget(plot_widget)

        # Create a horizontal splitter for the entire layout
        h_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        for splitter in row_splitters:
            h_splitter.addWidget(splitter)
            h_splitter.setHandleWidth(splitter_width)
        layout.addWidget(h_splitter, 0, 0, 3, 3)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Set up the main window
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 1200, 900)

        # Create the main widget and set it as the central widget
        main_widget = MultiCustomPlotWidget()
        self.setCentralWidget(main_widget)

        # Get all child widgets of the main window
        child_widgets = self.findChildren(QtWidgets.QWidget)

        # Filter the child widgets to only get instances of CustomPlotWidget
        custom_plot_widgets = [
            w for w in child_widgets if isinstance(w, CustomPlotWidget)]

        # Do something with the list of CustomPlotWidget instances
        for plot_widget in custom_plot_widgets:
            x = np.linspace(0, 10, 100)
            y = np.random.rand(100)
            plot_widget.plot(x, y)

        # Register the signal handler for keyboard interrupt (Ctrl+C)
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

# to do: add class for a custom main window:


if __name__ == "__main__":
    import sys
    import numpy as np
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
