#%%
import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore, QtWidgets, QtGui
from pyqtplotlib.pltwrapper import AxesWidget

class ROIAxesWidget(pg.PlotWidget):
    def __init__(self, parent=None, roi_type='rect'):
        super().__init__(parent)

        self.data = None
        self.scatter = None
        self.mask = None
        self.roi_type = roi_type
        
        pen = pg.mkPen(color=(255, 0, 0), width=2) # red contour for the ROI
        fillbrush = pg.mkBrush(color=(0, 0, 0, 20)) # transparent black fill for the ROI

        if self.roi_type == 'rect':
            # Create a Rectangular ROI object
            self.roi = pg.RectROI([0, 0], [1, 1], movable=True, sideScalers=True, pen=pen)
            # self.roi.setPen(pen)
        elif self.roi_type == 'linear':
            # Create a Linear Region ROI object
            self.roi = pg.LinearRegionItem(values=[0, 1], movable=True, pen=pen, brush=fillbrush)
            # self.roi.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
        else:
            raise ValueError("Unsupported ROI type. Use 'rect' or 'linear'.")

        self.addItem(self.roi)

        # Hide ROI until Ctrl is pressed
        self.roi.hide()
        self.ePressed = False
        self.roiStart = None

        # Connect ROI event with additional argument using lambda
        self.roi.sigRegionChangeFinished.connect(lambda: self.onROIChanged())

    def set_data(self, x, y, **plot_kwargs):
        self.data = (np.array(x), np.array(y))
        if self.scatter is None:
            self.scatter = self.plot(x, y, **plot_kwargs)
        else:
            self.scatter.setData(x, y)
        return self.scatter

    def onROIChanged(self):
        """Override to add custom functionality. This method is called when the ROI is changed."""
        pass

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.ePressed = True

        if event.key() == QtCore.Qt.Key_Shift:
            self.shiftPressed = True

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.ePressed = False

        if event.key() == QtCore.Qt.Key_Shift:
            self.shiftPressed = False

        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):
        if self.ePressed and event.button() == QtCore.Qt.LeftButton:
            self.roi.show()
            self.roiStart = self.plotItem.vb.mapSceneToView(event.pos())
            if self.roi_type == 'rect':
                self.roi.setPos(self.roiStart, update=False)
                self.roi.setSize([0, 0], update=False)
            elif self.roi_type == 'linear':
                self.roi.setRegion([self.roiStart.x(), self.roiStart.x()])
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.roiStart is not None:
            currentPos = self.plotItem.vb.mapSceneToView(event.pos())
            if self.roi_type == 'rect':
                self.roi.setSize(currentPos - self.roiStart)
            elif self.roi_type == 'linear':
                self.roi.setRegion([self.roiStart.x(), currentPos.x()])
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.roi.hide()
            self.roiStart = None
        super().mouseReleaseEvent(event)

# Example usage
if __name__ == "__main__":
    
    from PyQt5.QtWidgets import QApplication, QMainWindow
    import sys
    app=0
    app = QApplication(sys.argv)
    window = QMainWindow()

    # Initialize the ROIAxesWidget with desired ROI type ('rect' or 'linear')
    ax = ROIAxesWidget(roi_type='linear')  

    # Add the plot widget to the main window
    window.setCentralWidget(ax)
    window.setGeometry(100, 100, 1000, 600)

    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    curve = ax.set_data(x, y, color='b', linestyle='--', marker='x', label='data')

    window.show()
    sys.exit(app.exec_())
    
    
# %%
"""
The idea is to combine the functionality of the two classes into one class, as illustrated below:
class Mixin1:
    def __init__(self):
        super().__init__()
        # Initialization code for Mixin1

class Mixin2:
    def __init__(self):
        super().__init__()
        # Initialization code for Mixin2

class BaseClass:
    def __init__(self):
        # Base class initialization

class CombinedClass(BaseClass, Mixin1, Mixin2):
    def __init__(self):
        super().__init__()
        # CombinedClass specific initialization
        
This will allow the base class (here: AxesWidget) to be enhanced with additional functionality, depending on the use case.
"""

class ExcludeSelectionPlot(AxesWidget, ROIAxesWidget):
    def __init__(self, parent=None, roi_type='rect'):
        """Plot widget with an ROI that can be used to exclude data points from the plot."""
        super().__init__(parent=parent, roi_type=roi_type)

        self.mask = None
        self.roi_data = self.plot([], [], color='r', marker='o', label='ROI')
        self.set_title('Select a region to exclude by holding "e" and dragging the mouse.\nDrag with "Shift+e" to invert the selection.')
            
    def onROIChanged(self, inverted=False):
        x, y = self.data
        if self.roi_type == 'rect':
            bounds = self.roi.parentBounds()
            x1, y1, x2, y2 = bounds.left(), bounds.top(), bounds.right(), bounds.bottom()
            mask = (x > x1) & (x < x2) & (y > y1) & (y < y2)
        elif self.roi_type == 'linear':
            x1, x2 = self.roi.getRegion()
            mask = (x > x1) & (x < x2)
        self.update_mask(mask, inverted=inverted)

    def update_mask(self, mask, inverted=False):
        x, y = self.data

        if self.mask is None:
            self.mask = np.zeros_like(x, dtype=bool)
        if not inverted:
            self.mask[mask] = True
        else:
            self.mask[mask] = False

        self.roi_data.setData(x[self.mask], y[self.mask])
        
if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = 0
    app = QApplication(sys.argv)
    window = QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    
    ax = ExcludeSelectionPlot()  

    # Add the plot widget to the main window
    window.setCentralWidget(ax)
    window.setGeometry(100, 100, 1000, 600)
    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    curve = ax.set_data(x, y, color='b', linestyle='--', marker='x', label='data')

    
    window.show()
    sys.exit(app.exec_())
# %%
