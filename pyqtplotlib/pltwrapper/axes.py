#%%
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt
from matplotlib import pyplot as plt

pg.setConfigOption('background', 'w')
pg.setConfigOption('leftButtonPan', False)


class AxesWidget(pg.PlotWidget):
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent=parent, **kwargs)
        
        self.setParent(parent)
        self.plotItem.showGrid(True, True, 0.7)
        self.set_xlabel('X-axis')
        self.set_ylabel('Y-axis')
        self.set_title('')

        self.hover_label = QLabel(self)
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setGeometry(10, 10, 150, 20)

        self.setMouseEnabled(x=True, y=True)
        self.setAntialiasing(True)

        self.plot_item = self.getPlotItem()
        self.plot_item.scene().sigMouseMoved.connect(self._hoveredEvent)
        
        # Get the ViewBox
        vb = self.plot_item.getViewBox()

        # Change the mouse mode of the ViewBox to use the middle button for panning
        # vb.setMouseMode(vb.RectMode) # This is just to ensure RectMode isn't active since it uses the left button
        vb.setMouseMode(vb.PanMode)  # This is the default
        # vb.mouseModes[QtCore.Qt.MidButton] = vb.PanMode
        # vb.mouseModes[QtCore.Qt.LeftButton] = None  # Disable panning with the left button
        
        self.default_legend = self.add_legend()
        self.default_legend.hide()


        self._apply_matplotlib_color_cycle()
        
        self.figure = None



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
        # kwargs = self._handle_fmt(*args, **kwargs)
        kwargs = self._handle_color(kwargs)
        kwargs = self._handle_linestyle(kwargs)
        kwargs = self._handle_marker(kwargs)
        kwargs = self._handle_legend_label(kwargs)
        curve = self.plot_item.plot(*args, **kwargs)
        return curve
    
    def add_legend(self, *args, **kwargs):
        """
        Add a legend to the plot.

        Args and kwargs are passed on to pyqtgraph's LegendItem.
        """
        legend_item = self.plotItem.addLegend(*args, **kwargs)
        legend_item.setParentItem(self.plotItem) # This makes the legend part of the plot
        return legend_item
        
    def legend(self, *args, **kwargs):
        """Displays the legend."""
        self.default_legend.show()
    

    def imshow(self, data, colormap=None, levels=None, aspect='square', autoRange=True, **kwargs):
        """
        Display an image on the AxesWidget.

        Parameters:
        - data: 2D numpy array
        - colormap: a pyqtgraph.ColorMap or string specifying the colormap (e.g. 'viridis')
        - levels: (min, max) tuple specifying the data range that corresponds to the 
                  minimum and maximum display brightness levels
        - aspect: 'square' to enforce square pixels, 'auto' to stretch the image to fill the axis
        - autoRange: bool, whether to automatically adjust the view to fit image dimensions
        - **kwargs: other keyword arguments to customize the ImageItem
        """
        
        from pyqtgraph import ImageItem, ColorMap
        # Create an ImageItem with the data
        img_item = ImageItem(data, **kwargs)

        if colormap:
            if isinstance(colormap, str):
                # Get colormap from string
                colormap = pg.colormap.getFromMatplotlib(colormap)
            img_item.setLookupTable(colormap.getLookupTable())

        if levels:
            img_item.setLevels(levels)

        # Add the image to the plot
        self.addItem(img_item)

        # Set aspect
        if aspect == 'square':
            self.setAspectLocked(True)
        elif aspect == 'auto':
            self.setAspectLocked(False)

        # Adjust view
        if autoRange:
            self.autoRange()

        return img_item

    # def _handle_fmt(self, *args, **kwargs):
    #     """Handle fmt argument and return modified kwargs."""
    #     if len(args) == 2:
    #         fmt = args[1]
    #     elif len(args) == 3:
    #         fmt = args[2]
    #     else:
    #         fmt = kwargs.get('fmt', None)
            
    #     if not isinstance(fmt, str):
    #         fmt = None
            
    #     if fmt is not None:
    #         # fmt is a positional argument, e.g. plot(x, y, 'ro')
    #         kwargs['color'] = fmt[0]
    #         kwargs['marker'] = fmt[1]
    #         kwargs['linestyle'] = fmt[2:]
    #     return kwargs

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
    
    def _handle_legend_label(self, kwargs):
        """Handle legend label arguments and return modified kwargs."""
        if 'label' in kwargs:
            kwargs['name'] = kwargs['label']
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

    def set_xlim(self, left=None, right=None):
        """Set x-axis limits."""
        [[xmin, xmax], [_, _]] = self.plotItem.viewRange()
        
        if left and right:
            self.plotItem.setXRange(left, right)
        elif left:
            self.plotItem.setXRange(left, xmax)
        elif right:
            self.plotItem.setXRange(xmin,   right)
        else:
            raise ValueError("Must specify at least one of 'left' or 'right'.")

    def set_ylim(self, bottom=None, top=None):
        """Set y-axis limits."""
        [[_, _], [ymin, ymax]] = self.plotItem.viewRange()
        
        if bottom and top:
            self.plotItem.setYRange(bottom, top)
        elif bottom:
            self.plotItem.setYRange(bottom, ymax)
        elif top:
            self.plotItem.setYRange(ymin,   top)
        else:
            raise ValueError("Must specify at least one of 'bottom' or 'top'.")
               
    def set_yscale(self, scale_type):
        """
        Set the y-axis scale.

        Parameters:
        - scale_type: str
            Either 'log' or 'linear'
        """
        if scale_type == 'log':
            self.plot_item.setLogMode(y=True)
            # self.getAxis('left').setLogMode(True)
        elif scale_type == 'linear':
            self.plot_item.setLogMode(y=False)
            # self.getAxis('left').setLogMode(False)
        else:
            raise ValueError("Invalid y-scale type. Choose 'linear' or 'log'.")

    def set_xscale(self, scale_type):
        """
        Set the x-axis scale.

        Parameters:
        - scale_type: str
            Either 'log' or 'linear'
        """
        if scale_type == 'log':
            # self.getAxis('bottom').setLogMode(True)
            self.plot_item.setLogMode(x=True)
        elif scale_type == 'linear':
            # self.getAxis('bottom').setLogMode(False)
            self.plot_item.setLogMode(x=False)
        else:
            raise ValueError("Invalid x-scale type. Choose 'linear' or 'log'.")
        
    def assign_figure(self, figure):
        self.figure = figure
        
    def get_figure(self):
        return self.figure
        
    def keyPressEvent(self, event):
        if event.key() == pg.Qt.QtCore.Qt.Key_Escape:
            # Trigger auto scaling when "Esc" is pressed
            self.autoBtnClicked()
        super(AxesWidget, self).keyPressEvent(event)

# Usage can be similar, and extending this further will enhance its capabilities.



if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create a custom plot widget
    ax = AxesWidget()

    # Add the plot widget to the main window
    window.setCentralWidget(ax)
    window.setGeometry(100, 100, 800, 600)
    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    curve = ax.plot(x, y, color='r', linestyle='--', marker='o', label='data')
    
    ax.plot(x, y, color='r', linestyle='--', marker='o', label='data')
    ax.set_xlim(left=-1)
    ax.set_ylim(-1, top=20)
    # ax.set_ylim(bottom=-1)

    window.show()
    sys.exit(app.exec_())


# %%
