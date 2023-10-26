from gui.plot_widget import CustomPlotWidget
from PyQt5 import QtCore, QtWidgets
import numpy as np


# class Subplots(QtWidgets.QWidget):
#     def __init__(self, nrows, ncols, sharex=False, sharey=False, parent=None):
#         super().__init__(parent=parent)
#         layout = QtWidgets.QGridLayout()
#         self.setLayout(layout)

#         # Splitter config
#         splitter_width = 10

#         self.plot_widgets = np.empty((nrows, ncols), dtype=object)
#         # Store all created splitters for further axis synchronization
#         self.row_splitters = []
#         self.col_splitters = []

#         # Create splitters and plot_widgets
#         for i in range(nrows):
#             v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
#             v_splitter.setHandleWidth(splitter_width)
#             self.row_splitters.append(v_splitter)

#             for j in range(ncols):
#                 h_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
#                 h_splitter.setHandleWidth(splitter_width)
#                 self.col_splitters.append(h_splitter)

#                 plot_widget = CustomPlotWidget()
#                 h_splitter.addWidget(plot_widget)
#                 self.plot_widgets[i, j] = plot_widget

#                 if j == 0:
#                     v_splitter.addWidget(h_splitter)
#                 else:
#                     v_splitter.insertWidget(j, h_splitter)

#             layout.addWidget(v_splitter, i, 0)

class Subplots(QtWidgets.QWidget):
    def __init__(self, nrows, ncols, sharex=False, sharey=False, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()  # Main layout
        self.setLayout(layout)

        self.plot_widgets = np.empty((nrows, ncols), dtype=object)

        main_splitter = QtWidgets.QSplitter(
            QtCore.Qt.Vertical)  # Main splitter to hold rows
        layout.addWidget(main_splitter)

        for i in range(nrows):
            row_splitter = QtWidgets.QSplitter(
                QtCore.Qt.Horizontal)  # Splitter for each row
            main_splitter.addWidget(row_splitter)
            for j in range(ncols):
                plot_widget = CustomPlotWidget()
                row_splitter.addWidget(plot_widget)
                self.plot_widgets[i, j] = plot_widget

        # Synchronize axes if necessary
        if sharex:
            self._sync_axes('x')
        if sharey:
            self._sync_axes('y')


    def _sync_axes(self, axis):
        """Synchronize the given axis (x or y) for all plot widgets."""
        # Use the first plot widget as master
        master = self.plot_widgets[0, 0]
        for pw in self.plot_widgets.flat:
            if pw != master:
                if axis == 'x':
                    pw.getViewBox().setXLink(master.getViewBox())
                elif axis == 'y':
                    pw.getViewBox().setYLink(master.getViewBox())

        # Connect the master's view change signal to the sync function
        # master.getViewBox().sigRangeChanged.connect(sync_views)

    def get_plot_widgets(self):
        """Return the 2D numpy array of plot widgets."""
        return self.plot_widgets

if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create a central widget for the main window
    central_widget = QtWidgets.QWidget()
    window.setCentralWidget(central_widget)

    # Set layout for the central widget
    layout = QtWidgets.QVBoxLayout()
    central_widget.setLayout(layout)

    subplots = Subplots(2, 3, sharex=True, sharey=True)
    layout.addWidget(subplots)

    axs = subplots.get_plot_widgets()
    axs[0, 0].plot([1, 2, 3], [1, 2, 3])
    axs[0, 2].plot([1, 2, 3], [1, 2, 3])
    axs[1,0].set_title('Test')

    window.show()
    app.exec_()
