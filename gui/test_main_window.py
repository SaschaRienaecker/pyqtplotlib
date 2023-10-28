import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QAction, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox, QSpinBox
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QPainter, QIcon, QKeySequence
from PyQt5.QtCore import Qt, QPointF, QRectF
from gui.plot.plot_widget import CustomPlotWidget
from gui.shortcut_window import ShortcutWindow
import signal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.shortcuts = [] # placeholder for adding shortcuts
        self.shortcut_window = None # placeholder for shortcut window

        # Register the signal handler for keyboard interrupt (Ctrl+C)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        self.setWindowTitle("")

        # Set the default window size
        self.setGeometry(100, 100, 800, 600)

        # Create a central widget for the window
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a layout for the central widget
        layout = QHBoxLayout()

        # Create a toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        
        # Create the "Fit Gaussian" action
        fit_gaussian_action = QAction(QIcon(
            '/home/sascha/Desktop/220_Free_Flat_Vector_Icons/PNG/64px/Flat Vector Icons 4.png'), 'Fit Gaussian', self)
        fit_gaussian_action.triggered.connect(self.fit_gaussian)
        toolbar.addAction(fit_gaussian_action)

        # Create the a plot
        self.plot_widget = CustomPlotWidget()
        
        # Create a parameter box
        parameter_box = self.get_parameter_box()


        # Add the parameter box to the layout
        layout.addWidget(self.plot_widget)
        layout.addWidget(parameter_box)

        # Set the layout for the central widget
        central_widget.setLayout(layout)

    def get_parameter_box(self):
        # Create a parameter box
        parameter_box = QGroupBox('Parameters')

        # Create a layout for the parameter box
        layout = QFormLayout()

        layout = QFormLayout()
        # Create spin boxes for the amplitude, mean, and stddev parameters
        amplitude_spinbox = QSpinBox()
        amplitude_spinbox.setRange(0, 100)
        amplitude_spinbox.setValue(1)

        mean_spinbox = QSpinBox()
        mean_spinbox.setRange(-10, 10)
        mean_spinbox.setValue(0)

        stddev_spinbox = QSpinBox()
        stddev_spinbox.setRange(0, 10)
        stddev_spinbox.setValue(1)

        layout.addRow("Amplitude:", amplitude_spinbox)
        layout.addRow("Mean:", mean_spinbox)
        layout.addRow("Std Dev:", stddev_spinbox)

        # Set the layout for the parameter box
        parameter_box.setLayout(layout)

        return parameter_box

    def fit_gaussian(self):
        # Fit a Gaussian curve to the data
        print('Fitting Gaussian curve...')
        from gui.utils.fit import fit_curve
        x_data, y_data = self.plot_widget.get_xy_data()
        curve_func, curve_params = fit_curve(x_data, y_data, 'gaussian')

        # create and plot fitted curve
        x = np.linspace(np.min(x_data), np.max(x_data), 100)
        y = curve_func(x, *curve_params)
        self.plot_widget.plot(x, y, pen='r', symbol='o', name='fit')

    def mousePressEvent(self, event):
        self.origin = event.pos()

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MiddleButton:
            # Do any cleanup necessary when the mouse is released
            pass

    def wheelEvent(self, event):
        pass

    def add_shortcut(self, key_sequence, slot):
        shortcut = QShortcut(QKeySequence(key_sequence), self)
        shortcut.activated.connect(slot)
        shortcut.setProperty("Description", slot.__doc__)
        self.shortcuts.append(shortcut)

    def display_shortcuts(self):
        # display list of available shortcuts
        # import pandas as pd
        # from PyQt5.QtGui import QStandardItemModel, QStandardItem
        # from PyQt5.QtWidgets import QTableView, QVBoxLayout
        # df = pd.DataFrame([(shortcut.key().toString(), shortcut.property(
        #     "Description")) for shortcut in self.shortcuts], columns=["Shortcut", "Description"])
        # model = QStandardItemModel(df.shape[0], df.shape[1], self)
        # model.setHorizontalHeaderLabels(df.columns)
        # for row in range(df.shape[0]):
        #     for col in range(df.shape[1]):
        #         item = QStandardItem(str(df.iat[row, col]))
        #         model.setItem(row, col, item)
        # view = QTableView(self)
        # view.setModel(model)
        # view.resizeColumnsToContents()
        # layout = QVBoxLayout()
        # layout.addWidget(view)
        # widget = QWidget()
        # widget.setLayout(layout)

        # self.shortcut_widget = widget
        # self.shortcut_widget.setVisible(True)
        # self.setCentralWidget(widget)
        if self.shortcut_window is None:
            self.shortcut_window = ShortcutWindow(self.shortcuts)
        self.shortcut_window.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.display_shortcuts()
        else:
            super().keyPressEvent(event)


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.shortcut_window is not None:
                self.shortcut_window.hide()
        else:
            super().keyReleaseEvent(event)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    x = [0, 1, 2, 3, 4]
    y = [0, 1, 4, 9, 16]
    window.plot_widget.plot(x, y, pen='r', symbol='o', name='data1')


    # adding a shortcut test
    def my_slot():
        """Prints out something."""
        print("Shortcut triggered!")
    window.add_shortcut("Ctrl+Shift+T", my_slot)


    window.show()
    sys.exit(app.exec_())
