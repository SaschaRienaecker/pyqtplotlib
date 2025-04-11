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
    
    def __init__(self, parent=None,  **kwargs):
        super().__init__(parent=parent, **kwargs)
        
        self.setParent(parent)
        self.plotItem.showGrid(True, True, 0.7)
        self.set_xlabel('X-axis')
        self.set_ylabel('Y-axis')
        self.set_title('')

        self.hover_label = QLabel(self)
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setGeometry(0, 0, 150, 15)
        

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
        # if not self.plot_item.sceneBoundingRect().contains(pos):
        #     self.hover_label.hide()
        # else:
            # self.hover_label.show()
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

        linestyle_pen = self._handle_linestyle(kwargs)
        if linestyle_pen is None:
            pen = None  # No line should be drawn
        else:
            kwargs_pen.update(linestyle_pen)
            kwargs_pen.update(self._handle_linewidth(kwargs))
            pen = pg.mkPen(**kwargs_pen)
        
        # ... other handle methods which do not comncern the pen ...
        kwargs = self._handle_marker(kwargs, kwargs_pen)
        kwargs = self._handle_legend_label(kwargs)
        
        plot_item = self.plot_item.plot(*args, **kwargs, pen=pen)
        return plot_item
    
    def scatter(self, x, y, c=None, s=10, cmap='viridis', vmin=None, vmax=None, **kwargs):
        """
        Create a scatter plot on the AxesWidget, similar to matplotlib.pyplot.scatter.

        Parameters:
        - x, y: 1D arrays or lists of coordinates
        - c: color(s) of points; can be a single color or a sequence mapped through a colormap
        - s: size of points (single value or array of values)
        - cmap: colormap name or matplotlib colormap
        - vmin, vmax: normalization range for colormap when 'c' is numeric
        - **kwargs: passed to pyqtgraph.ScatterPlotItem
        """

        from pyqtgraph import ScatterPlotItem
        import numpy as np
        import matplotlib.cm as cm
        import matplotlib.colors as mcolors

        x = np.asarray(x)
        y = np.asarray(y)

        if np.isscalar(s):
            sizes = np.full_like(x, s, dtype=float)
        else:
            sizes = np.asarray(s)

        # Handle color
        brushes = None
        if c is None:
            # Use default marker color
            kwargs_brush = self._handle_color({})
            color = kwargs_brush.get('color', 'w')  # fallback to white
            brushes = [color] * len(x)
        elif isinstance(c, (str, tuple)) or (isinstance(c, np.ndarray) and c.ndim == 1 and np.issubdtype(c.dtype, np.str_)):
            # Single or array of color names
            brushes = c if np.iterable(c) else [c] * len(x)
        else:
            # Numeric array mapped to colormap
            c = np.asarray(c)
            norm = mcolors.Normalize(vmin=vmin if vmin is not None else np.min(c),
                                    vmax=vmax if vmax is not None else np.max(c))
            colormap = cm.get_cmap(cmap)
            rgba_colors = colormap(norm(c))
            brushes = [tuple((color[:3] * 255).astype(int)) for color in rgba_colors]

        # Allow marker shape (symbol) and legend
        kwargs_pen = {}
        kwargs_pen.update(self._handle_color(kwargs))
        kwargs_pen.update(self._handle_linestyle(kwargs))
        kwargs_pen.update(self._handle_linewidth(kwargs))

        spots = [{'pos': (x_, y_), 'size': s_, 'brush': b}
                for x_, y_, s_, b in zip(x, y, sizes, brushes)]

        scatter_item = ScatterPlotItem(spots=spots, **kwargs_pen)
        self.addItem(scatter_item)
        return scatter_item

    def axvline(self, x, ymin=None, ymax=None, **kwargs):
        """
        Add a vertical line at position x.
        If ymin and ymax are specified, draw a finite line segment.
        """
        from pyqtgraph import InfiniteLine, PlotDataItem
        import numpy as np

        kwargs_pen = {}
        kwargs_pen.update(self._handle_color(kwargs))
        kwargs_pen.update(self._handle_linestyle(kwargs))
        kwargs_pen.update(self._handle_linewidth(kwargs))
        pen = pg.mkPen(**kwargs_pen)

        if ymin is not None and ymax is not None:
            # Finite vertical line segment
            line = PlotDataItem(x=np.array([x, x]), y=np.array([ymin, ymax]), pen=pen)
        else:
            # Infinite vertical line
            line = InfiniteLine(pos=x, angle=90, pen=pen)

        self.addItem(line)
        return line

    def axhline(self, y, xmin=None, xmax=None, **kwargs):
        """
        Add a horizontal line at position y.
        If xmin and xmax are specified, draw a finite line segment.
        """
        from pyqtgraph import InfiniteLine, PlotDataItem
        import numpy as np

        kwargs_pen = {}
        kwargs_pen.update(self._handle_color(kwargs))
        kwargs_pen.update(self._handle_linestyle(kwargs))
        kwargs_pen.update(self._handle_linewidth(kwargs))
        pen = pg.mkPen(**kwargs_pen)

        if xmin is not None and xmax is not None:
            # Finite horizontal line segment
            line = PlotDataItem(x=np.array([xmin, xmax]), y=np.array([y, y]), pen=pen)
        else:
            # Infinite horizontal line
            line = InfiniteLine(pos=y, angle=0, pen=pen)

        self.addItem(line)
        return line
    
    def vlines(self, x, ymin, ymax, **kwargs):
        """
        Draw vertical lines at each x from ymin to ymax.

        Parameters:
        - x: scalar or array-like of x positions
        - ymin, ymax: scalars or array-like of same shape as x
        - kwargs: passed to axvline (e.g. color, linestyle, linewidth)
        """
        import numpy as np

        x = np.atleast_1d(x)
        ymin = np.broadcast_to(ymin, x.shape)
        ymax = np.broadcast_to(ymax, x.shape)

        items = []
        for xi, y0, y1 in zip(x, ymin, ymax):
            item = self.axvline(x=xi, ymin=y0, ymax=y1, **kwargs)
            items.append(item)
        
        return items
        
    def hlines(self, y, xmin, xmax, **kwargs):
        """
        Draw horizontal lines at each y from xmin to xmax.

        Parameters:
        - y: scalar or array-like of y positions
        - xmin, xmax: scalars or array-like of same shape as y
        - kwargs: passed to axhline (e.g. color, linestyle, linewidth)
        """
        import numpy as np

        y = np.atleast_1d(y)
        xmin = np.broadcast_to(xmin, y.shape)
        xmax = np.broadcast_to(xmax, y.shape)

        items = []
        for yi, x0, x1 in zip(y, xmin, xmax):
            item = self.axhline(y=yi, xmin=x0, xmax=x1, **kwargs)
            items.append(item)

        return items
    
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
        kwargs_pen = kwargs.get('pen', {})  # Retrieve existing pen kwargs or initialize an empty dict

        if 'color' in kwargs:
            color = kwargs.pop('color')
            if isinstance(color, str) and color.startswith('C') and color[1:].isdigit():
                # Interpret 'C0', 'C1', etc. as matplotlib-like color cycle
                index = int(color[1:])
                if index < len(self._mpl_color_cycle):
                    color = self._mpl_color_cycle[index]
            kwargs_pen['color'] = color
        else:
            num_items = len([item for item in self.getPlotItem().items if isinstance(item, pg.PlotDataItem)])
            col = self._mpl_color_cycle[num_items % len(self._mpl_color_cycle)]
            kwargs_pen['color'] = col
            
        # translate color to pen color:
        kwargs_pen['color'] = pg.mkColor(kwargs_pen['color'])
            
        if 'alpha' in kwargs:
            kwargs_pen['color'].setAlphaF(kwargs.pop('alpha'))

        return kwargs_pen


    def _handle_linestyle(self, kwargs):
        """Handle linestyle arguments and return modified kwargs_pen."""
        from pyqtgraph.Qt import QtCore

        linestyle_mapping = {
            '-': QtCore.Qt.SolidLine,
            '--': QtCore.Qt.DashLine,
            ':': QtCore.Qt.DotLine,
            '-.': QtCore.Qt.DashDotLine,
        }

        kwargs_pen = kwargs.get('pen', {})  # Retrieve existing pen kwargs or initialize an empty dict

        ls = kwargs.pop('linestyle', kwargs.pop('ls', '-'))

        if ls in ['', 'None', None]:
            return None  # Signal that no line should be drawn

        style = linestyle_mapping.get(ls, QtCore.Qt.SolidLine)
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
    

    def imshow(self, data, cmap=None, levels=None, aspect='auto', extent=None, autoRange=True, 
               interpolation='bilinear', antialias=True, vmin=None, vmax=None, **kwargs):
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
        - vmin: float, minimum data value that corresponds to the minimum colormap level
        - vmax: float, maximum data value that corresponds to the maximum colormap level
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

        # Determine levels using levels, vmin, and vmax
        if levels is not None:
            img_item.setLevels(levels)
        else:
            if vmin is not None or vmax is not None:
                levels = [vmin, vmax]
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
        
        img_item.setOpts(autoDownsample=True) # image automatically downsampled to match the screen resolution
        
        return img_item



    def _apply_matplotlib_color_cycle(self):
        """Apply default Matplotlib color cycle to the plot."""
        prop_cycle = plt.rcParams['axes.prop_cycle']
        self._mpl_color_cycle = prop_cycle.by_key()['color']

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
        
        
    def set_xticks(self, ticks):
        """Set the x-axis ticks of the plot."""
        if ticks == []:
            # Hide x-axis ticks
            self.plot_item.getAxis('bottom').setTicks([])
        else:
            # Set specific ticks
            # self.plot_item.getAxis('bottom').setTicks(ticks)
            raise NotImplementedError("Setting specific x-ticks is not implemented yet.")
        
    def set_yticks(self, ticks):
        """Set the y-axis ticks of the plot."""
        if ticks == []:
            # Hide y-axis ticks
            self.plot_item.getAxis('left').setTicks([])
        else:
            # Set specific ticks
            # self.plot_item.getAxis('left').setTicks(ticks)
            raise NotImplementedError("Setting specific y-ticks is not implemented yet.")
    
    def set_xticklabels(self, labels):
        """Set the x-axis tick labels of the plot."""
        if labels == []:
            # Hide x-axis tick labels
            self.plot_item.getAxis('bottom').setStyle(showValues=False)
        else:
            # Set specific labels
            # tick_positions = plot.getAxis('bottom').ticks()[0]
            # tick_labels = [(pos, labels[i]) for i, (pos, _) in enumerate(tick_positions)]
            # self.plot_item.getAxis('bottom').setTicks(tick_labels)
            raise NotImplementedError("Setting specific x-tick labels is not implemented yet.")
            
    def set_yticklabels(self, labels):
        """Set the y-axis tick labels of the plot."""
        if labels == []:
            # Hide y-axis tick labels
            self.plot_item.getAxis('left').setStyle(showValues=False)
        else:
            # Set specific labels
            raise NotImplementedError("Setting specific y-tick labels is not implemented yet.")

    
    def fill_between(self, x, y1, y2=0, where=None, color=None, alpha=1.0, label=None, **kwargs):
        """
        Mimics matplotlib's fill_between using a QGraphicsPathItem.
        Supports optional 'where' masking with recursive-style segmented fill.

        Parameters:
        - x: 1D array of x values
        - y1: 1D array of y values (upper boundary)
        - y2: 1D array or scalar (lower boundary, default 0)
        - where: Optional boolean mask (fill only where True)
        - color: Fill color (can be name or RGB tuple)
        - alpha: Transparency (0.0 to 1.0)
        - label: Optional legend label
        - kwargs: Reserved for future use
        """
        import numpy as np
        from PyQt5.QtWidgets import QGraphicsPathItem
        from PyQt5.QtGui import QPainterPath, QBrush, QPen, QColor
        from PyQt5.QtCore import QPointF, Qt

        x = np.asarray(x)
        y1 = np.asarray(y1)
        y2 = np.asarray(y2 if not np.isscalar(y2) else np.full_like(y1, y2))

        # Handle segmented recursive-like fill when 'where' is provided
        if where is not None:
            where = np.asarray(where, dtype=bool)
            # Pad edges to catch transitions
            padded = np.concatenate([[False], where, [False]])
            edges = np.flatnonzero(padded[1:] != padded[:-1])
            segments = list(zip(edges[::2], edges[1::2]))

            items = []
            for start, end in segments:
                # Slice the arrays for this segment
                xs = x[start:end]
                y1s = y1[start:end]
                y2s = y2[start:end]
                # Recursively call fill_between without 'where'
                item = self.fill_between(xs, y1s, y2s, None, color, alpha, label, **kwargs)
                items.append(item)
            return items

        # Base case: fill the area between y1 and y2 without masking
        if len(x) < 2:
            return  # Not enough points to draw a region

        path = QPainterPath()
        path.moveTo(QPointF(x[0], y2[0]))
        for xi, yi in zip(x, y2):
            path.lineTo(QPointF(xi, yi))
        for xi, yi in zip(x[::-1], y1[::-1]):
            path.lineTo(QPointF(xi, yi))
        path.closeSubpath()

        # Set up color and transparency
        if color is None:
            color = QColor(100, 100, 255)
        else:
            color = QColor(*color) if isinstance(color, (tuple, list)) else QColor(color)
        color.setAlphaF(alpha)

        brush = QBrush(color)
        item = QGraphicsPathItem(path)
        item.setBrush(brush)
        item.setPen(QPen(Qt.NoPen))

        self.addItem(item)

        if label and hasattr(self, "_legend"):
            self._legend.addItem(item, label)

        return item
    
    
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
    curve = ax.plot(x, y, color='C1', linestyle='--', marker='+', markersize=1, lw=1, label='data')
    axs[0,1].scatter(y,x, marker='x', color='r', ls='-')
    line = ax.axvline(2, color='k', linestyle='--', lw=1)
    line2 = axs[0,1].axvline(2, 1,2, color='r', linestyle='--', lw=5)
    lines  = axs[0,1].vlines([0.5, 1.5], ymin=-1, ymax=1, color='cyan', linestyle='--', lw=5)
    ax.hlines([1, 2], xmin=0, xmax=4, color='magenta', linewidth=2)

    txtitem = ax.text(2, 4, "Sample Text", color='red', transform='data', horizontal_alignment='left', va='bottom')
    ax.set_xlim(left=-1)
    ax.set_ylim(-1, top=20)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    import numpy as np


    x = np.linspace(0, 10, 500)
    y1 = np.sin(x)
    y2 = 0.3
    mask = y1 > y2

    ax.fill_between(x, y1, y2, where=mask, color='green', alpha=0.4)

    
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
