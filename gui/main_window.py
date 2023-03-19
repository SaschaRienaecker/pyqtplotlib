import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSpinBox
from PyQt5.QtChart import QChart, QChartView, QScatterSeries, QLineSeries
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtCore import Qt, QPointF, QRectF

from gui.plot_widget import CustomPlotWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("")

        # Set the default window size
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget for the window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QHBoxLayout()

        # Create a toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        
        # Create the "Fit Gaussian" action
        fit_gaussian_action = QAction(QIcon(
            '/home/sascha/Desktop/220_Free_Flat_Vector_Icons/PNG/64px/Flat Vector Icons 4.png'), 'Fit Gaussian', self)
        fit_gaussian_action.triggered.connect(self.fit_gaussian)
        toolbar.addAction(fit_gaussian_action)

        # Create the a plot
        self.plot_widget = CustomPlotWidget()
        
        # Create a parameter box
        parameter_box = self.get_parameter_box()


        # Add the parameter box to the layout
        layout.addWidget(self.plot_widget)
        layout.addWidget(parameter_box)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

    def get_parameter_box(self):
        # Create a parameter box
        parameter_box = QGroupBox('Parameters')

        # Create a layout for the parameter box
        layout = QFormLayout()

        layout = QFormLayout()
        # Create spin boxes for the amplitude, mean, and stddev parameters
        amplitude_spinbox = QSpinBox()
        amplitude_spinbox.setRange(0, 100)
        amplitude_spinbox.setValue(1)

        mean_spinbox = QSpinBox()
        mean_spinbox.setRange(-10, 10)
        mean_spinbox.setValue(0)

        stddev_spinbox = QSpinBox()
        stddev_spinbox.setRange(0, 10)
        stddev_spinbox.setValue(1)

        layout.addRow("Amplitude:", amplitude_spinbox)
        layout.addRow("Mean:", mean_spinbox)
        layout.addRow("Std Dev:", stddev_spinbox)

        # Set the layout for the parameter box
        parameter_box.setLayout(layout)

        return parameter_box

    def fit_gaussian(self):
        # Fit a Gaussian curve to the data
        print('Fitting Gaussian curve...')
        from utils.fit import fit_curve
        x_data, y_data = self.plot_widget.get_xy_data()
        curve_func, curve_params = fit_curve(x_data, y_data, 'gaussian')

        # create and plot fitted curve
        x = np.linspace(np.min(x_data), np.max(x_data), 100)
        y = curve_func(x, *curve_params)
        self.plot_widget.plot(x, y, pen='r', symbol='o', name='fit')

    def mousePressEvent(self, event):
        self.origin = event.pos()


    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MiddleButton:
            # Do any cleanup necessary when the mouse is released
            pass

    def wheelEvent(self, event):
        pass


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    window.plot_widget.plot(x, y, pen='r', symbol='o', name='data1')
    window.show()
    sys.exit(app.exec_())
