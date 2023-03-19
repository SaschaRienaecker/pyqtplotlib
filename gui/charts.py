import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtChart import QChart, QChartView, QScatterSeries
from PyQt5.QtGui import QMouseEvent, QPainter
from PyQt5.QtCore import Qt

class Chart(QChart):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAnimationOptions(QChart.SeriesAnimations)
        self.legend().hide()
        self.setAcceptHoverEvents(True)

        self.series = QScatterSeries(self)
        self.addSeries(self.series)

        self.createDefaultAxes()

        self.chart_view = QChartView(self)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.setPlotAreaBackgroundBrush(Qt.white)

        self.chart_view.setRubberBand(QChartView.RectangleRubberBand)

        self.chart_view.setMouseTracking(True)
    
    def wheelEvent(self, event):
        # Calculate the new zoom level based on the wheel delta
        new_zoom = 1.0 + 0.1 * event.angleDelta().y() / 120
        # Set the new zoom level
        self.chart_view.chart().zoom(new_zoom)

    def add_data(self, x_data, y_data):
        self.series.clear()
        for x, y in zip(x_data, y_data):
            self.series.append(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    chart = Chart()
    chart.add_data([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    window.setCentralWidget(chart.chart_view)
    window.show()
    sys.exit(app.exec_())
