#%%
import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore, QtWidgets
from pyqtplotlib.pltwrapper import AxesWidget


class ROIAxesWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None
        self.scatter = None
        self.mask = None

        # Create an ROI object
        self.roi = pg.RectROI([0, 0], [1, 1], movable=True, sideScalers=True)
        self.roi.setPen('r')
        self.addItem(self.roi)

        # Hide ROI until Ctrl is pressed
        self.roi.hide()
        # self.ctrlPressed = False
        self.ePressed = False
        self.shiftPressed = False
        self.roiStart = None
        
        # Connect ROI event with additional argument using lambda
        self.roi.sigRegionChangeFinished.connect(lambda: self.onROIChanged(inverted=False))

    def set_data(self, x, y, **plot_kwargs):
        self.data = (np.array(x), np.array(y))
        if self.scatter is None:
            self.scatter = self.plot(x, y, **plot_kwargs)
        else:
            self.scatter.setData(x, y)
        return self.scatter
    
    

    def onROIChanged(self, inverted=False):
        """Override to add custom functionality.This method is called when the ROI is changed.
        The `inverted` argument is used to invert the logic of the ROI, when holding Shift.
        """
        pass        
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.ePressed = True
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                # Connect with inverted logic
                self.roi.sigRegionChangeFinished.disconnect()
                self.roi.sigRegionChangeFinished.connect(lambda: self.onROIChanged(inverted=True))
            else:
                # Connect with normal logic
                self.roi.sigRegionChangeFinished.disconnect()
                self.roi.sigRegionChangeFinished.connect(lambda: self.onROIChanged(inverted=False))
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.ePressed = False
            # Revert to default connection
            self.roi.sigRegionChangeFinished.disconnect()
            self.roi.sigRegionChangeFinished.connect(lambda: self.onROIChanged(inverted=False))
        super().keyReleaseEvent(event)
    
    def mousePressEvent(self, event):
        if self.ePressed:
            self.roi.show()
            self.roiStart = self.plotItem.vb.mapSceneToView(event.pos())
            self.roi.setPos(self.roiStart, update=False)
            self.roi.setSize([0, 0], update=False)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.ePressed and self.roiStart is not None:
            currentPos = self.plotItem.vb.mapSceneToView(event.pos())
            self.roi.setSize(currentPos - self.roiStart)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.ePressed:
            self.roi.hide()
            self.roiStart = None
        else:
            super().mouseReleaseEvent(event)
        

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
    def __init__(self, parent=None):
        """Plot widget with an ROI that can be used to exclude data points from the plot.
        """
        super().__init__(parent=parent)
                    
        self.mask = None
        self.roi_data = self.plot([], [], color='r', marker='o', label='ROI')
        self.set_title('Select a region to exclude by holding "e" and dragging the mouse.\nDrag with "Shift+e" to invert the selection.')
            
    def onROIChanged(self, inverted=False):
        
        bounds = self.roi.parentBounds()
        x1, y1, x2, y2 = bounds.left(), bounds.top(), bounds.right(), bounds.bottom()
        
        x, y = self.data    
        mask = (x>x1) & (x<x2) & (y>y1) & (y<y2)
        self.update_mask(mask, inverted=inverted)
    
    def update_mask(self, mask, inverted=False):
        
        x, y = self.data
        
        if self.mask is None:
            self.mask = np.zeros_like(x, dtype=bool)
        else:
            
            if not inverted: # append to existing mask
                self.mask[mask] = True
                # self.mask = np.hstack([self.mask, mask])
            else: # remove from existing mask
                self.mask[mask] = False
                
        # self.set_data(x[~mask], y[~mask])
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
