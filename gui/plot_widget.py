import pyqtgraph as pg
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSpinBox
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtCore import Qt, QPointF, QRectF

pg.setConfigOption('background', 'w')

class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.setParent(parent)

        # Set default plotting settings
        self.plotItem.showGrid(True, True, 0.7)
        self.plotItem.setLabel('left', 'Y-axis')
        self.plotItem.setLabel('bottom', 'X-axis')
        self.plotItem.setTitle('Custom Plot')
        
        # Create label to display coordinates
        self.hover_label = QLabel(self)
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setGeometry(10, 10, 150, 20)

        # Enable user interaction
        self.setMouseEnabled(x=True, y=True)
        self.setAntialiasing(True)

        # Add legend to the plot
        # self.legend = pg.LegendItem(offset=(70, 30))
        # self.plotItem.addItem(self.legend)

        # Enable dragging
        self.dragging = False
        self.drag_start = None
        self.plot_item = self.getPlotItem()

        self.plot_item.scene().sigMouseMoved.connect(self.hoveredEvent)

        self.apply_matplotlib_color_cycle()

    def hoveredEvent(self, pos):

        # Map the mouse cursor position to the plot's coordinate system
        data_pos = self.plot_item.getViewBox().mapSceneToView(pos)
        # Do something with the data position, such as update a tooltip or display additional information

        # For example, update a label with the data coordinates
        self.hover_label.setText("({:.3f}, {:.3f})".format(data_pos.x(), data_pos.y() ))

    def get_xy_data(self, item_index=0):
        """Get the x and y data from the plot."""    
        item = self.getPlotItem().dataItems[item_index]
        x_data = item.xData
        y_data = item.yData
        return x_data, y_data


    def plot(self, *args, **kwargs):
        # Translate Matplotlib-style arguments to Pyqtgraph-style arguments
        if 'color' in kwargs:
            kwargs['pen'] = pg.mkPen(kwargs['color'])
            del kwargs['color']
        else:
            # Get the number of PlotDataItem instances attached to the PlotWidget
            num_items = len([item for item in self.getPlotItem().items if isinstance(item, pg.PlotDataItem)])
            # Get the next color from the color cycle
            col = self.color_cycle[num_items % len(self.color_cycle)]
            print(col)
            kwargs['pen'] = pg.mkPen(col)

        if 'linestyle' in kwargs:
            if kwargs['linestyle'] == '-':
                kwargs['pen'] = pg.mkPen(kwargs.get('pen', None), width=1)
            elif kwargs['linestyle'] == '--':
                kwargs['pen'] = pg.mkPen(kwargs.get('pen', None), width=1, style=pg.QtCore.Qt.DashLine)
            elif kwargs['linestyle'] == ':':
                kwargs['pen'] = pg.mkPen(kwargs.get('pen', None), width=1, style=pg.QtCore.Qt.DotLine)
            elif kwargs['linestyle'] == '-.':
                kwargs['pen'] = pg.mkPen(kwargs.get('pen', None), width=1, style=pg.QtCore.Qt.DashDotLine)
            del kwargs['linestyle']
        if 'marker' in kwargs:
            brush = pg.mkBrush(kwargs.get('color', 'k'))
            pen = pg.mkPen(kwargs.get('markeredgecolor', 'k'), width=1)
            size = kwargs.get('markersize', 8)
            if kwargs['marker'] == 'o':
                kwargs['symbol'] = 'o'
                kwargs['symbolBrush'] = brush
                kwargs['symbolPen'] = pen
                kwargs['size'] = size
            elif kwargs['marker'] == 's':
                kwargs['symbol'] = 's'
                kwargs['symbolBrush'] = brush
                kwargs['symbolPen'] = pen
                kwargs['size'] = size
            del kwargs['marker']

        # Call the original plot() method with translated arguments
        self.plot_item.plot(*args, **kwargs)


    def apply_matplotlib_color_cycle(self):
        from matplotlib import pyplot as plt
        
        # Get the default color cycle from Matplotlib
        prop_cycle = plt.rcParams['axes.prop_cycle']
        self.color_cycle = prop_cycle.by_key()['color']


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QMainWindow()

    # Create a custom plot widget
    plot_widget = CustomPlotWidget()

    # Add the plot widget to the main window
    window.setCentralWidget(plot_widget)
    window.setGeometry(100, 100, 800, 600)
    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    plot_widget.plot(x, y, pen='r', symbol='o', name='data1')

    window.show()
    sys.exit(app.exec_())

