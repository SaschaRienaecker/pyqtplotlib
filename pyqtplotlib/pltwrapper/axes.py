#%%
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGraphicsItem
from PyQt5.QtCore import Qt, QPointF
from matplotlib import pyplot as plt

pg.setConfigOption('background', 'w')
pg.setConfigOption('leftButtonPan', False)


class MovableTextItem(pg.TextItem):
    def __init__(self, *args, **kwargs):
        super(MovableTextItem, self).__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        
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
        self.hover_label.setGeometry(10, 10, 150, 15)

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
        # to be implemented: hide if mouse is outside the plot
        data_pos = self.plot_item.getViewBox().mapSceneToView(pos)
        self.hover_label.setText(
            "({:.3g}, {:.3g})".format(data_pos.x(), data_pos.y()))

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
        kwargs_pen = {}
        kwargs_pen.update(self._handle_color(kwargs))
        kwargs_pen.update(self._handle_linestyle(kwargs))
        kwargs_pen.update(self._handle_linewidth(kwargs))
        # kwargs = self._handle_fmt(*args, **kwargs)
        pen = pg.mkPen(**kwargs_pen)
        
        # ... other handle methods which do not comncern the pen ...
        kwargs = self._handle_marker(kwargs, kwargs_pen)
        kwargs = self._handle_legend_label(kwargs)
        
        plot_item = self.plot_item.plot(*args, **kwargs, pen=pen)
        return plot_item

    def axvline(self, x, **kwargs):
        """
        Add a vertical line at position x using matplotlib-like syntax.
        """
        kwargs_pen = {}
        kwargs_pen.update(self._handle_color(kwargs))
        kwargs_pen.update(self._handle_linestyle(kwargs))
        kwargs_pen.update(self._handle_linewidth(kwargs))
        
        pen = pg.mkPen(**kwargs_pen)
        line = pg.InfiniteLine(pos=x, angle=90, pen=pen)
        self.addItem(line)
        return line

    def axhline(self, y, **kwargs):
        """
        Add a horizontal line at position y using matplotlib-like syntax.
        """
        kwargs_pen = {}
        kwargs_pen.update(self._handle_color(kwargs))
        kwargs_pen.update(self._handle_linestyle(kwargs))
        kwargs_pen.update(self._handle_linewidth(kwargs))
        
        pen = pg.mkPen(**kwargs_pen)
        line = pg.InfiniteLine(pos=y, angle=0, pen=pen)
        self.addItem(line)
        return line
    
    def text(self, x, y, text, transform='data', **kwargs):
        """
        Add text to the plot at specified coordinates with Matplotlib-like syntax.
        """
        # Handle anchor (alignment)
        anchor = self._handle_anchor(kwargs)

        textItem = MovableTextItem(text, anchor=anchor, **kwargs)
        # Handle transform (coordinate system)
        # textItem.setPos(x, y)  # Axes fraction coordinates
        if transform == 'axes':
            raise NotImplementedError("Axes fraction coordinates not implemented yet.")
            # Convert axes fraction coordinates to view coordinates
            view_x = self.plotItem.viewRect().left() + x * self.plotItem.viewRect().width()
            view_y = self.plotItem.viewRect().top() + y * self.plotItem.viewRect().height()
            # Map view coordinates to scene coordinates
            scene_pos = self.plotItem.vb.mapFromView(QPointF(view_x, view_y))
            textItem.setPos(scene_pos)
        else:
            textItem.setPos(x, y)  # Data coordinates
        self.addItem(textItem)
        return textItem

    
    def _handle_fmt(self, *args, **kwargs):
        """
        Handle Matplotlib-style format strings.

        Args:
            args: The arguments passed to the plot method.
            kwargs: The keyword arguments passed to the plot method.

        Returns:
            Updated kwargs with color, marker, and linestyle extracted from format string.
        """
        if args and isinstance(args[-1], str) and len(args) > 1:
            fmt = args[-1]
            args = args[:-1]

            # Color shorthand (e.g., 'r' for red)
            color_shorthand = {'b': 'blue', 'g': 'green', 'r': 'red', 'c': 'cyan',
                               'm': 'magenta', 'y': 'yellow', 'k': 'black', 'w': 'white'}

            # Marker shorthand
            marker_shorthand = {'o': 'o', 's': 'square', '^': 't', 'd': 'd',
                                '+': 'plus', 'x': 'x', '*': 'star'}

            # Line style shorthand
            linestyle_shorthand = {'-': '-', '--': '--', '-.': '-.', ':': ':'}

            for key in color_shorthand:
                if key in fmt:
                    kwargs['color'] = color_shorthand[key]
                    fmt = fmt.replace(key, '', 1)
                    break

            for key in marker_shorthand:
                if key in fmt:
                    kwargs['marker'] = marker_shorthand[key]
                    fmt = fmt.replace(key, '', 1)
                    break

            for key in linestyle_shorthand:
                if key in fmt:
                    kwargs['linestyle'] = linestyle_shorthand[key]
                    fmt = fmt.replace(key, '', 1)
                    break

        return args, kwargs

    def _handle_color(self, kwargs):
        """Handle color arguments and return modified kwargs_pen."""
        kwargs_pen = kwargs.get(
            'pen', {})  # Retrieve existing pen kwargs or initialize an empty dict
        if 'color' in kwargs:
            kwargs_pen['color'] = kwargs.pop('color')
        else:
            num_items = len([item for item in self.getPlotItem(
            ).items if isinstance(item, pg.PlotDataItem)])
            col = self._color_cycle[num_items % len(self._color_cycle)]
            kwargs_pen['color'] = col
        return kwargs_pen


    def _handle_linestyle(self, kwargs):
        """Handle linestyle arguments and return modified kwargs_pen."""
        linestyle_mapping = {
            '-': pg.QtCore.Qt.SolidLine,
            '--': pg.QtCore.Qt.DashLine,
            ':': pg.QtCore.Qt.DotLine,
            '-.': pg.QtCore.Qt.DashDotLine,
        }
        kwargs_pen = kwargs.get('pen', {})  # Retrieve existing pen kwargs or initialize an empty dict
        
        ls = kwargs.pop('linestyle', kwargs.pop('ls', '-'))
        style = linestyle_mapping.get(ls, pg.QtCore.Qt.SolidLine)
        kwargs_pen['style'] = style
        return kwargs_pen

    
    def _handle_linewidth(self, kwargs):
        """
        Handle the linewidth argument, accepting either 'lw' or 'linewidth'.
        """
        kwargs_pen = kwargs.get('pen', {})  # Retrieve existing pen kwargs or initialize an empty dict
        if 'lw' in kwargs or 'linewidth' in kwargs:
            lw = kwargs.pop('lw', None) or kwargs.pop('linewidth', None)
            kwargs_pen['width'] = lw  # Set the linewidth in the pen kwargs
        return kwargs_pen


    def _handle_marker(self, kwargs, kwargs_pen):
        """Handle marker arguments and return modified kwargs."""
        marker_mapping = {
            'o': 'o', 's': 's', 'd': 'd', '^': '^', 'x': 'x', '+': '+','|': 't1', 'v': 'v', '>': '>',
            # Extend with more marker types if needed
        }
        symbol = marker_mapping.get(kwargs.pop('marker', None), None)
        if symbol:
            # Use color from kwargs_pen for consistency
            color = kwargs_pen.get('color', 'k')
            markeredgecolor = kwargs.pop('markeredgecolor', color)
            markersize = kwargs.pop('markersize', kwargs.pop('ms', 8))

            kwargs['symbol'] = symbol
            # kwargs['symbolBrush'] = pg.mkBrush(color)
            kwargs['symbolPen'] = pg.mkPen(markeredgecolor, width=markersize)
            # kwargs['size'] = kwargs.pop('markersize', kwargs.pop('ms', 8))
        return kwargs

    def _handle_legend_label(self, kwargs):
        """Handle legend label arguments and return modified kwargs."""
        if 'label' in kwargs:
            kwargs['name'] = kwargs['label']
        return kwargs
    
    def _handle_anchor(self, kwargs):
        """
        Handle alignment arguments and return anchor position for pyqtgraph TextItem.

        Converts matplotlib's 'va' and 'ha' to pyqtgraph's anchor.
        """
        va = kwargs.pop('vertical_alignment', kwargs.pop('va','center')).lower()
        ha = kwargs.pop('horizontal_alignment', kwargs.pop('ha','center')).lower()

        # Map Matplotlib's alignment options to pyqtgraph's anchor
        va_map = {'top': 0, 'center': 0.5, 'bottom': 1}
        ha_map = {'left': 0, 'center': 0.5, 'right': 1}

        anchor = (ha_map.get(ha, 0.5), va_map.get(va, 0.5))
        return anchor
    
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
    

    def imshow(self, data, cmap=None, levels=None, aspect='auto', extent=None, autoRange=True, interpolation='nearest', antialias=False, **kwargs):
        """
        Display an image on the AxesWidget.

        Parameters:
        - data: 2D numpy array
        - cmap: a pyqtgraph.ColorMap, a string specifying the colormap (e.g. 'viridis'), or a matplotlib colormap
        - levels: (min, max) tuple specifying the data range that corresponds to the 
                minimum and maximum display brightness levels
        - aspect: 'square' to enforce square pixels, 'auto' to stretch the image to fill the axis
        - extent : floats (left, right, bottom, top), optional
        - autoRange: bool, whether to automatically adjust the view to fit image dimensions
        - interpolation: string, specifies the interpolation method ('nearest', 'bilinear', etc.)
        - antialias: bool, whether to enable antialiasing (note: limited support for images)
        - **kwargs: other keyword arguments to customize the ImageItem
        """

        from pyqtgraph import ImageItem, colormap as pg_colormap
        import matplotlib as mpl
        import numpy as np
        
        # need to transpose the data to match the image orientation in matplotlib
        _data = np.array(data).T
        
        
        rect = kwargs.pop('rect', None)
        
        if rect is None:
            if extent is None:
                extent = (0, _data.shape[1], 0, _data.shape[0])
            # translate extent to pyqtgraph's rect (x0, y0, width, height):
            rect = (extent[0], extent[2], extent[1]-extent[0], extent[3]-extent[2])
            
        
        # Create an ImageItem with the data and additional options
        img_item = ImageItem(_data, antialias=antialias, rect=rect, **kwargs)

        # Set color map
        if cmap is not None:
            
            cmap = mpl_to_pg_cmap(cmap)
            img_item.setLookupTable(cmap.getLookupTable())
            img_item.cmap = cmap

        # Set levels if provided
        if levels:
            img_item.setLevels(levels)

        # Add the image to the plot
        self.addItem(img_item)

        # Set aspect ratio
        if aspect == 'square':
            self.setAspectLocked(True)
        elif aspect == 'auto':
            self.setAspectLocked(False)

        # Adjust view range if autoRange is True
        if autoRange:
            self.autoRange()

        # Set interpolation method
        img_item.setOpts(interpolate=interpolation == 'bilinear')

        return img_item



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
        
    def get_xlim(self):
        """Get x-axis limits."""
        return self.plotItem.viewRange()[0]
    
    def get_ylim(self):
        """Get y-axis limits."""
        return self.plotItem.viewRange()[1]
               
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

def mpl_to_pg_cmap(mpl_cmap):
    """ Convert a Matplotlib colormap to a PyQTGraph colormap.
    Args:
        mpl_cmap: A Matplotlib colormap, or a string with the name of a Matplotlib colormap.
    Example:
        pg_cmap = mpl_to_pg_cmap(plt.cm.get_cmap('seismic'))
    """
    import numpy as np
    import pyqtgraph as pg
    import matplotlib.pyplot as plt
    
    if isinstance(mpl_cmap, str):
        # Get the Matplotlib colormap
        mpl_cmap = plt.cm.get_cmap(mpl_cmap)


    # Sample colors from the colormap
    num_colors = 256  # Number of colors to sample
    positions = np.linspace(0, 1, num_colors)  # Positions where we sample the colormap
    colors = (mpl_cmap(positions)[:,:3] * 255).astype(np.uint8)  # Convert to 0-255 RGB values

    # Create a PyQTGraph ColorMap
    pg_cmap = pg.ColorMap(positions, colors, mapping=pg.ColorMap.CLIP)
    
    return pg_cmap

import pyqtgraph as pg
from PyQt5.QtWidgets import QVBoxLayout, QSlider, QWidget
from PyQt5.QtCore import Qt

def add_colorbar_with_interaction(img_item, colormap='viridis'):
    # Create a layout for the ImageView and the sliders
    layout = QVBoxLayout()
    # layout.addWidget(image_view)

    # Create and configure sliders for vmin and vmax
    vmin_slider = QSlider(Qt.Horizontal)
    vmax_slider = QSlider(Qt.Horizontal)
    vmin_slider.setRange(-200, 200)
    vmax_slider.setRange(-200, 200)
    vmin_slider.setValue(0)
    vmax_slider.setValue(100)

    layout.addWidget(vmin_slider)
    layout.addWidget(vmax_slider)

    # Create a colorbar as a separate GraphicsLayoutWidget
    colorbar_layout = pg.GraphicsLayoutWidget()
    colorbar_plot = colorbar_layout.addPlot()
    # colorbar_plot.hideAxis('bottom')
    colorbar_plot.hideAxis('left')
    colorbar_plot.showAxis('right')
    colorbar_plot.getAxis('right').setTicks([])

    # Create a gradient for the colorbar
    gradient = pg.GradientWidget(orientation='right')
    gradient.loadPreset(colormap)
    # Create an ImageItem for the gradient
    gradItem = pg.ImageItem()
    colorbar_plot.addItem(gradItem)
    
    gradItem.setImage(img_item.cmap.getLookupTable())

    # Add colorbar to layout
    layout.addWidget(colorbar_layout)

    # Container widget
    container = QWidget()
    container.setLayout(layout)

    # Function to update image with new vmin and vmax
    def update_image():
        vmin = vmin_slider.value() / 100
        vmax = vmax_slider.value() / 100
        img_item.setLevels([vmin, vmax])

    # Connect sliders to update function
    vmin_slider.valueChanged.connect(update_image)
    vmax_slider.valueChanged.connect(update_image)
    
    return container

if __name__ == "__main__":
    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = 0
    app = QApplication(sys.argv)

    import pyqtplotlib as qtplt
    fig, axs = qtplt.subplots(1,2, figsize=(8,4))
    
    # Create a custom plot widget
    # ax1 = AxesWidget()
    ax = axs[0,0]

    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    curve = ax.plot(x, y, color='r', linestyle='--', marker='+', markersize=10, lw=1, label='data')
    line = ax.axvline(2, color='k', linestyle='--', lw=1)
    txtitem = ax.text(2, 4, "Sample Text", color='red', transform='data', horizontal_alignment='left', va='bottom')
    ax.set_xlim(left=-1)
    ax.set_ylim(-1, top=20)
    # ax.set_ylim(bottom=-1)
    
    print(ax.get_xlim())
    print(ax.get_ylim())

    # import numpy as np
    # # ax2 = AxesWidget()
    # ax = axs[0,1]
    # im = ax.imshow(np.random.rand(10,10), extent=(-10,5,-3,3), cmap='viridis')
    
    # container = add_colorbar_with_interaction(im)
    # container.show()
    # window = QMainWindow()
    # Add the plot widget to the main window
    # window.setCentralWidget(ax)
    # window.setGeometry(100, 100, 800, 600)
    # window.show()
    
    fig.show()
    app.exec_()



# %%
