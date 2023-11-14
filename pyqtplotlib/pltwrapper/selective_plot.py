#%%
import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore, QtWidgets
from pyqtplotlib.pltwrapper import AxesWidget


class SelectivePlotWidget(AxesWidget):
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
    
    

    def onROIChanged(self):
        """This method is called when the ROI is changed. Override this method to add custom functionality."""
        pass        
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.ePressed = True
            
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_E:
            self.ePressed = False

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
        


if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication, QMainWindow
    import sys
    
    # crate a classs that inherits from SelectivePlotWidget
    # and add some functionality to the onROIChanged method;
    # Here, we exclude the data points that are inside the ROI:
    class ExcludeSelectionPlot(SelectivePlotWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            self.mask = None
            
        def onROIChanged(self):
            bounds = self.roi.parentBounds()
            x1, y1, x2, y2 = bounds.left(), bounds.top(), bounds.right(), bounds.bottom()
            
            x, y = self.data    
            mask = (x>x1) & (x<x2) & (y>y1) & (y<y2)
            self.update_mask(mask)
        
        def update_mask(self, mask):
            
            if self.mask is None:
                self.mask = mask
            else:
                self.mask = np.hstack([self.mask, mask]) # append to existing mask
            x, y = self.data
            self.set_data(x[~mask], y[~mask])
        
    
    app = 0
    app = QApplication(sys.argv)
    window = QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    
    ax = ExcludeSelectionPlot()  
    

    # Add the plot widget to the main window
    window.setCentralWidget(ax)
    window.setGeometry(100, 100, 800, 600)
    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    curve = ax.set_data(x, y, color='r', linestyle='--', marker='o', label='data')


    window.show()
    sys.exit(app.exec_())
# %%
