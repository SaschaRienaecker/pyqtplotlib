# %%

import unittest
import numpy as np
from PyQt5.QtCore import QTimer

import sys
import unittest
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv) if QApplication.instance() is None else QApplication.instance()

from pyqtplotlib.pltwrapper import AxesWidget


class TestAxesWidget(unittest.TestCase):
    
    # def __init__(self, *args, **kwargs):
    #     self.test_CustomPlotWidget()
    
    # def test_CustomPlotWidget(self, timeout=3000):
        
    def setUp(self):
        # Setup runs before each test method
        self.ax = AxesWidget()
    
    def test_plot(self):
        
        x = [0, 1, 2, 3, 4]
        y = [0, 1, 4, 9, 16]
        line = self.ax.plot(x, y, color='r', linestyle='--', marker='o', label='data')
        self.ax.set_xlim(left=-1)
        self.ax.set_ylim(-1, top=20)
        
       
        # Set up the timer to call the self.close_application method
        # QTimer.singleShot(timeout, window.close)
        # window.show()
        
        
        # # Clean up and exit the application properly when the window is closed.
        # app.aboutToQuit.connect(app.deleteLater)
        # sys.exit(app.exec_())

    def test_imshow(self):
        
        data = np.random.rand(10,10)
        im = self.ax.imshow(data, extent=(-10,5,-3,3), cmap='plasma')


    
    def tearDown(self):
        # Cleanup runs after each test method
        self.ax.close()
if __name__ == '__main__':
    unittest.main()
    
# %%
