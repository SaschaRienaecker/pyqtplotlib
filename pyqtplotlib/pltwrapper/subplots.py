#%%
from pyqtplotlib.pltwrapper import AxesWidget
from PyQt5 import QtCore, QtWidgets
import numpy as np

from typing import Tuple
from pyqtplotlib.pltwrapper.figure import Figure
from pyqtplotlib.pltwrapper.axes import AxesWidget

class Subplots(Figure):
    
    ppy = 96 # typical pixels per inch (for conversion from matplotlib inches to Qt pixels)
    
    def __init__(self, nrows=1, ncols=1, sharex=False, sharey=False, figsize=None, axwidget=AxesWidget, parent=None, **figure_kwargs):
        super().__init__(parent=parent, **figure_kwargs)
            
        self.axs = np.empty((nrows, ncols), dtype=object)

        main_splitter = QtWidgets.QSplitter(
            QtCore.Qt.Vertical)  # Main splitter to hold rows
        self.layout.addWidget(main_splitter)

        for i in range(nrows):
            row_splitter = QtWidgets.QSplitter(
                QtCore.Qt.Horizontal)  # Splitter for each row
            main_splitter.addWidget(row_splitter)
            for j in range(ncols):
                ax = axwidget()
                ax.figure = self
                row_splitter.addWidget(ax)
                self.axs[i, j] = ax

        # Synchronize axes if necessary
        if sharex:
            # self._sync_axes('x')
            share_axes(self.axs, axis='x')
        if sharey:
            # self._sync_axes('y')
            share_axes(self.axs, axis='y')
            
        if figsize is not None:
            # convert from matplotlib inches to Qt pixels:
            geom = (0, 0, int(figsize[0]*Subplots.ppy), int(figsize[1]*Subplots.ppy))
            print(geom)
            self.setGeometry(*geom)
            
            
    def get_fig_and_axs(self):
        """Return the figure and a 2D numpy array of Axes unless there is only one axis."""
        
        fig = self.axs[0, 0].get_figure()
        
        if self.axs.shape==(1,1):
            return fig, self.axs[0,0]
        else:
            return fig, self.axs

def share_axes(axs, axis='x'):
    """Synchronize the given axis (x or y) for the given list of `pg.PlotWidget` widgets."""
    # Use the first plot widget as master
    
    master = np.array(axs).flat[0]
    for pw in np.array(axs).flat:
        if pw != master:
            if axis == 'x':
                pw.getViewBox().setXLink(master.getViewBox())
            elif axis == 'y':
                pw.getViewBox().setYLink(master.getViewBox())

    # Connect the master's view change signal to the sync function
    # master.getViewBox().sigRangeChanged.connect(sync_views)


def output_figure_and_axes(func):
    def wrapper(*args, **kwargs) -> Tuple[Figure, AxesWidget]:
        fig, axs = func(*args, **kwargs)
        return fig, axs
    return wrapper

@output_figure_and_axes
def subplots(nrows=1, ncols=1, sharex=False, sharey=False, figsize=None, axwidget=AxesWidget, parent=None):
    """Create a figure with a set of subplots (wrapper function for calling the `Subplots` class)

    This utility wrapper makes it convenient to create common layouts of
    subplots, including the enclosing figure object, in a single call.

    Parameters
    ----------
    nrows, ncols : int
        Number of rows/columns of the subplot grid.
    sharex, sharey : bool, default: False
    figsize: tuple of (width, height) in inches, default: None
    axwidget : Widget to use, default: AxesWidget (the base class for all axes widgets)
    
    Returns
    -------
    fig : Figure
        The instance of the Figure object to which the subplots belong.
    axs : array of Axes
    """
    _subplots = Subplots(nrows, ncols, sharex=sharex,
                         sharey=sharey, figsize=figsize, axwidget=axwidget, parent=parent)
    fig, axs = _subplots.get_fig_and_axs()
    return fig, axs
    

if __name__ == "__main__":
    app=0           # Somehow prevents the kernel from crashing when closing the window
    app = QtWidgets.QApplication([])
    # window = QtWidgets.QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    
    import pyqtplotlib as qtplt
    fig, axs = qtplt.subplots(2, 3, sharex=True, sharey=True, figsize=(7,5))
    
    axs[0,0].plot([1, 2, 3], [1, 2, 3])
    axs[0, 2].plot([1, 2, 3], [1, 2, 3])
    axs[1,0].set_title('Test')
    

    fig.show()
    app.exec_()

