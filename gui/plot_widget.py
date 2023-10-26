import pyqtgraph as pg
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt

pg.setConfigOption('background', 'w')


class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        self.setParent(parent)

        self.plotItem.showGrid(True, True, 0.7)
        self.set_xlabel('X-axis')
        self.set_ylabel('Y-axis')
        self.set_title('Custom Plot')

        self.hover_label = QLabel(self)
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setGeometry(10, 10, 150, 20)

        self.setMouseEnabled(x=True, y=True)
        self.setAntialiasing(True)

        self._dragging = False
        self._drag_start = None
        self.plot_item = self.getPlotItem()
        self.plot_item.scene().sigMouseMoved.connect(self._hoveredEvent)

        self._apply_matplotlib_color_cycle()



    def _hoveredEvent(self, pos):
        """Update hover label with data coordinates."""
        data_pos = self.plot_item.getViewBox().mapSceneToView(pos)
        self.hover_label.setText(
            "({:.3f}, {:.3f})".format(data_pos.x(), data_pos.y()))


    def get_xy_data(self, item_index=0):
        """Retrieve x and y data from the plot for a given index."""
        try:
            item = self.getPlotItem().dataItems[item_index]
            return item.xData, item.yData
        except IndexError:
            print(f"No item at index {item_index}.")
            return [], []

    def plot(self, *args, **kwargs):
        """Plot data with arguments similar to Matplotlib."""
        kwargs = self._handle_color(kwargs)
        kwargs = self._handle_linestyle(kwargs)
        kwargs = self._handle_marker(kwargs)
        self.plot_item.plot(*args, **kwargs)

    def _handle_color(self, kwargs):
        """Handle color arguments and return modified kwargs."""
        if 'color' in kwargs:
            kwargs['pen'] = pg.mkPen(kwargs['color'])
        else:
            num_items = len([item for item in self.getPlotItem(
            ).items if isinstance(item, pg.PlotDataItem)])
            col = self._color_cycle[num_items % len(self._color_cycle)]
            kwargs['pen'] = pg.mkPen(col)
        return kwargs

    def _handle_linestyle(self, kwargs):
        """Handle linestyle arguments and return modified kwargs."""
        linestyle_mapping = {
            '-': pg.QtCore.Qt.SolidLine,
            '--': pg.QtCore.Qt.DashLine,
            ':': pg.QtCore.Qt.DotLine,
            '-.': pg.QtCore.Qt.DashDotLine,
        }
        style = linestyle_mapping.get(kwargs.get(
            'linestyle', '-'), pg.QtCore.Qt.SolidLine)
        kwargs['pen'] = pg.mkPen(kwargs.get('pen', None), width=1, style=style)
        return kwargs

    def _handle_marker(self, kwargs):
        """Handle marker arguments and return modified kwargs."""
        marker_mapping = {
            'o': 'o',
            's': 's',
            'd': 'd',
            '^': '^'
            # Extend with more marker types if needed
        }
        symbol = marker_mapping.get(kwargs.get('marker', None), None)
        if symbol:
            kwargs['symbol'] = symbol
            kwargs['symbolBrush'] = pg.mkBrush(kwargs.get('color', 'k'))
            kwargs['symbolPen'] = pg.mkPen(
                kwargs.get('markeredgecolor', 'k'), width=1)
            kwargs['size'] = kwargs.get('markersize', 8)
        return kwargs

    def _apply_matplotlib_color_cycle(self):
        """Apply default Matplotlib color cycle to the plot."""
        prop_cycle = plt.rcParams['axes.prop_cycle']
        self._color_cycle = prop_cycle.by_key()['color']

    def set_xlabel(self, label):
        """Set x-axis label."""
        self.plotItem.setLabel('bottom', label)

    def set_ylabel(self, label):
        """Set y-axis label."""
        self.plotItem.setLabel('left', label)

    def set_title(self, title):
        """Set plot title."""
        self.plotItem.setTitle(title)

    def set_xlim(self, xmin, xmax):
        """Set x-axis limits."""
        self.plotItem.setXRange(xmin, xmax)

    def set_ylim(self, ymin, ymax):
        """Set y-axis limits."""
        self.plotItem.setYRange(ymin, ymax)

    def set_xscale(self, scale):
        """Set x-axis scale ('linear' or 'log')."""
        is_log = scale == 'log'
        self.plotItem.setLogMode(x=is_log)

    def set_yscale(self, scale):
        """Set y-axis scale ('linear' or 'log')."""
        is_log = scale == 'log'
        self.plotItem.setLogMode(y=is_log)

# Usage can be similar, and extending this further will enhance its capabilities.



if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create a custom plot widget
    plot_widget = CustomPlotWidget()

    # Add the plot widget to the main window
    window.setCentralWidget(plot_widget)
    window.setGeometry(100, 100, 800, 600)
    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    plot_widget.plot(x, y, color='r', linestyle='--', marker='o', label='data')

    window.show()
    sys.exit(app.exec_())

