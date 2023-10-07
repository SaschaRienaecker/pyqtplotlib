#%%
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSpinBox
from PyQt5.QtChart import QChart, QChartView, QScatterSeries, QLineSeries
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtCore import Qt, QPointF, QRectF


class ScatterPlot(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Scatter Plot")

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
        

        # Create the scatter plot
        self.series = QScatterSeries()
        for i in range(100):
            self.series.append(
                QPointF(np.random.uniform(-10, 10), np.random.uniform(-10, 10)))
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        # self.chart.setTitle('Scatter Plot')

        # Create the chart view
        self.chart_view = QChartView(self.chart)

        # Create the "Fit Gaussian" action
        fit_gaussian_action = QAction(QIcon(
            '/home/sascha/Desktop/220_Free_Flat_Vector_Icons/PNG/64px/Flat Vector Icons 4.png'), 'Fit Gaussian', self)
        fit_gaussian_action.triggered.connect(self.fit_gaussian)
        toolbar.addAction(fit_gaussian_action)


        # Connect chart view signals for zooming
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setDragMode(QChartView.RubberBandDrag)

        self.chart_view.mousePressEvent = self.mousePressEvent
        self.chart_view.mouseMoveEvent = self.mouseMoveEvent
        self.chart_view.mouseReleaseEvent = self.mouseReleaseEvent
        self.chart_view.wheelEvent = self.wheelEvent


        # Create label to display coordinates
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(10, 10, 150, 20)

        # Connect signal for data point hovering
        self.series.hovered.connect(self.update_label)
        self.series.hovered.connect(self.update_label)

        # Store original viewport rectangle
        self.original_viewport = self.chart_view.chart().plotArea()


        # Create a parameter box
        parameter_box = self.get_parameter_box()


        # Add the parameter box to the layout
        layout.addWidget(self.chart_view)
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
        from gui.utils.fit import fit_curve
        x_data = [point.x() for point in self.series.pointsVector()]
        y_data = [point.y() for point in self.series.pointsVector()]
        curve_func, curve_params = fit_curve(x_data, y_data, 'gaussian')

        # Create a curve series and add it to the chart
        curve_series = QLineSeries()
        for x in np.linspace(np.min(x_data), np.max(x_data), 100):
            curve_series.append(QPointF(x, curve_func(x, *curve_params)))
        self.chart.addSeries(curve_series)
    
    def update_label(self, point, state):
        if state:
            self.label.setText(f"X: {point.x()}, Y: {point.y()}")
            self.label.move(
                point.toPoint() + self.series.chart().plotArea().topLeft().toPoint())
            self.label.show()
        else:
            self.label.hide()

    def mousePressEvent(self, event):
        self.origin = event.pos()

        if event.button() == Qt.LeftButton:
            self.rubber_band = self.chart_view.scene().addRect(0, 0, 0, 0, Qt.red)
            self.rubber_band.show()

        elif event.button() == Qt.MiddleButton:
            # Store the position of the mouse press
            self.last_drag_pos = event.pos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'rubber_band'):
            rect = self.selectionRect(self.origin, event.pos())
            self.rubber_band.setRect(rect)

        if event.buttons() == Qt.MiddleButton:
            # Get the difference between the current and last mouse position
            diff = - event.pos() + self.last_drag_pos
            # Move the chart by the difference
            self.chart_view.chart().scroll(diff.x(), -diff.y())
            # Update the last drag position
            self.last_drag_pos = event.pos()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if hasattr(self, 'rubber_band'):
                self.rubber_band.hide()
                rect = self.selectionRect(self.origin, event.pos())
                self.chart_view.chart().zoomIn(rect)

        if event.button() == Qt.MiddleButton:
            # Do any cleanup necessary when the mouse is released
            pass

    def wheelEvent(self, event):
        # Calculate the new zoom level based on the wheel delta
        new_zoom = 1.0 + 0.1 * event.angleDelta().y() / 120
        # Set the new zoom level
        self.chart_view.chart().zoom(new_zoom)

    def selectionRect(self, origin, current):
        left = min(origin.x(), current.x())
        right = max(origin.x(), current.x())
        top = min(origin.y(), current.y())
        bottom = max(origin.y(), current.y())
        return QRectF(left, top, right - left, bottom - top)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.chart.zoomReset()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScatterPlot()
    window.show()
    sys.exit(app.exec_())

# %%
