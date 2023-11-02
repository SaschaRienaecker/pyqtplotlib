import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
import numpy as np
from pyqtgraph.Qt import QtCore


from gui.plot import CustomPlotWidget


class SelectivePlotWidget(CustomPlotWidget):
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
        # self.roi.hide()
        self.ctrlPressed = False

        # Connect ROI event
        self.roi.sigRegionChanged.connect(self.onROIChanged)

    def set_data(self, x, y, **plot_kwargs):
        self.data = (np.array(x), np.array(y))
        if self.scatter is None:
            self.scatter = self.plot(x, y, **plot_kwargs)
        else:
            self.scatter.setData(x, y)
        return self.scatter
    
    
    def _roi_mask(self):
        
        if self.data is None:
            return None
        
        X, Y = self.data
                
        # mask = np.array([self.roi.contains(pg.Point(x, y)) for x,y in zip(X,Y)])
        
        bounds = self.roi.parentBounds()
        x1, y1, x2, y2 = bounds.left(), bounds.top(), bounds.right(), bounds.bottom()
        
        mask = (X>x1) & (X<x2) & (Y>y1) & (Y<y2)
        
        return mask
        
    def onROIChanged(self):
        if self.scatter is None:
            return
        
        X, Y = self.data
        
        mask = self._roi_mask()
        if self.mask is None:
            self.mask = mask
        else: # append to existing mask
            self.mask = np.hstack([self.mask, mask])
        
        
        # alpha = [0.2 if m else 1 for m in mask]
        # colors = [pg.mkColor((0, 0, 255, 255 * a)) for a in alpha]
        # self.scatter.setBrush(colors)
        # Placeholder for fitting functionality. Only fit data outside the ROI.
        # self.apply_fit([x[i] for i, m in enumerate(mask) if not m],
                    #    [y[i] for i, m in enumerate(mask) if not m])

        self.set_data(X[~mask], Y[~mask])
        

    def apply_fit(self, x, y):
        # Placeholder for fit functionality
        pass

    # def keyPressEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Control:
    #         self.ctrlPressed = True
    #         self.roi.show()

    # def keyReleaseEvent(self, event):
    #     if event.key() == QtCore.Qt.Key_Control:
    #         self.ctrlPressed = False
    #         self.roi.hide()

    # def mousePressEvent(self, event):
    #     if self.ctrlPressed:
    #         self.roi.show()
    #         pos = self.plotItem.vb.mapSceneToView(event.pos())
    #         self.roi.setPos(pos.x(), pos.y(), update=True, finish=False)
    #         self.roi.setSize([0, 0])
    #     super().mousePressEvent(event)

    # def mouseMoveEvent(self, event):
    #     if self.ctrlPressed:
    #         pos = self.plotItem.vb.mapSceneToView(event.pos())
    #         self.roi.setSize([pos.x() - self.roi.pos().x(), pos.y() - self.roi.pos().y()])
    #     super().mouseMoveEvent(event)


if __name__ == "__main__":

    from PyQt5.QtWidgets import QApplication, QMainWindow
    import sys
    app = QApplication(sys.argv)
    window = QMainWindow()

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create a custom plot widget
    ax = SelectivePlotWidget()

    # Add the plot widget to the main window
    window.setCentralWidget(ax)
    window.setGeometry(100, 100, 800, 600)
    # Plot some data
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    curve = ax.set_data(x, y, color='r', linestyle='--', marker='o', label='data')


    window.show()
    sys.exit(app.exec_())