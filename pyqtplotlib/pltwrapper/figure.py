#%%
# %gui qt
from PyQt5 import QtWidgets
from pyqtplotlib.pltwrapper.axes import AxesWidget

class Figure(QtWidgets.QWidget):
    def __init__(self, parent=None, title="", figsize=(600, 400)):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self.resize(*figsize)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        # self.plots = []

    def add_subplot(self, *args, **kwargs):
        ax = AxesWidget(*args, **kwargs)
        self.layout.addWidget(ax)
        # self.plots.append(ax)
        ax.figure = self
        return ax
    

    def savefig(self, filename, format=None):
        """Not working yet
        """
        
        from PyQt5 import QtGui
        if format is None:
            format = filename.split('.')[-1]

        if format.lower() in ['png', 'jpg', 'jpeg', 'bmp']:
            # Raster image formats
            pixmap = QtGui.QPixmap(self.size())
            self.render(pixmap)
            pixmap.save(filename, format.upper())
        elif format.lower() in ['pdf', 'svg']:
            # Vector image formats
            printer = QtGui.QPrinter() if format.lower() == 'pdf' else QtGui.QSvgGenerator()
            printer.setOutputFormat(QtGui.QPrinter.PdfFormat if format.lower() == 'pdf' else QtGui.QSvgGenerator.SvgFormat)
            printer.setOutputFileName(filename)
            printer.setPaperSize(self.size(), QtGui.QPrinter.DevicePixel)
            printer.setFullPage(True)

            painter = QtGui.QPainter(printer)
            self.render(painter)
            painter.end()
        else:
            raise ValueError(f"Unsupported file format: '{format}'")
    
if __name__ == '__main__':
    
    import sys
    # Create a simple application window
    app = QtWidgets.QApplication([])
    figure = Figure(title="My Plot")

    plot1 = figure.add_subplot()
    plot1.plot([1, 2, 3, 4, 5], [5, 6, 9, 10, 7])

    plot2 = figure.add_subplot()
    plot2.plot([0, 1, 2, 3, 4], [1, 2, 3, 2, 1])

    figure.show()
    
    # figure.savefig('test.png') # not working yet (should not be placed in the event loop)
    
    app.exec_()
# %%
