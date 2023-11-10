#%%
from pyqtplotlib.pltwrapper import AxesWidget
from PyQt5 import QtCore, QtWidgets
import numpy as np

from pyqtplotlib.pltwrapper.figure import Figure
from pyqtplotlib.pltwrapper.axes import AxesWidget

class Subplots(Figure):
    
    def __init__(self, nrows=1, ncols=1, sharex=False, sharey=False, parent=None, **figure_kwargs):
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
                ax = AxesWidget()
                ax.figure = self
                row_splitter.addWidget(ax)
                self.axs[i, j] = ax

        # Synchronize axes if necessary
        if sharex:
            self._sync_axes('x')
        if sharey:
            self._sync_axes('y')


    def _sync_axes(self, axis):
        """Synchronize the given axis (x or y) for all plot widgets."""
        # Use the first plot widget as master
        master = self.axs[0, 0]
        for pw in self.axs.flat:
            if pw != master:
                if axis == 'x':
                    pw.getViewBox().setXLink(master.getViewBox())
                elif axis == 'y':
                    pw.getViewBox().setYLink(master.getViewBox())

        # Connect the master's view change signal to the sync function
        # master.getViewBox().sigRangeChanged.connect(sync_views)

    def get_axs(self):
        """Return the 2D numpy array of Axes unless there is only one axis."""
        if self.axs.shape==(1,1):
            return self.axs[0,0]
        else:
            return self.axs


    
def subplots(nrows, ncols, sharex=False, sharey=False, parent=None):
    """Create a figure with a set of subplots already made.

    This utility wrapper makes it convenient to create common layouts of
    subplots, including the enclosing figure object, in a single call.

    Parameters
    ----------
    nrows, ncols : int
        Number of rows/columns of the subplot grid.
    sharex, sharey : bool, default: False
    
    Returns
    -------
    fig : Figure
        The instance of the Figure object to which the subplots belong.
    axs : array of Axes
    """
    _subplots = Subplots(nrows, ncols, sharex=sharex, sharey=sharey, parent=parent)
    axs = _subplots.get_axs()
    fig = axs[0, 0].get_figure()
    return fig, axs
    

if __name__ == "__main__":
    app=0           # Somehow prevents the kernel from crashing when closing the window
    app = QtWidgets.QApplication([])
    # window = QtWidgets.QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    
    import pyqtplotlib as qtplt
    fig, axs = qtplt.subplots(2, 3, sharex=True, sharey=True)
    
    axs[0,0].plot([1, 2, 3], [1, 2, 3])
    axs[0, 2].plot([1, 2, 3], [1, 2, 3])
    axs[1,0].set_title('Test')
    
    fig.setGeometry(100, 100, 1500, 600)

    fig.show()
    app.exec_()

# %%
