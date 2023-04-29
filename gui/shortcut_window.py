from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


class ShortcutWindow(QMainWindow):
    def __init__(self, shortcuts):
        super().__init__()
        """Display a list of available shortcuts in a window"""
        import pandas as pd
        from PyQt5.QtGui import QStandardItemModel, QStandardItem
        from PyQt5.QtWidgets import QTableView, QVBoxLayout

        self.setWindowTitle("Keyboard Shortcuts")

        # Set the default window size
        self.setGeometry(100, 100, 800, 600)
    
        df = pd.DataFrame([(shortcut.key().toString(), shortcut.property("Description")) for shortcut in shortcuts], columns=["Shortcut", "Description"])
        model = QStandardItemModel(df.shape[0], df.shape[1], self)
        model.setHorizontalHeaderLabels(df.columns)
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QStandardItem(str(df.iat[row, col]))
                model.setItem(row, col, item)
        view = QTableView()
        view.setModel(model)
        view.resizeColumnsToContents()
        layout = QVBoxLayout()
        layout.addWidget(view)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(widget.size())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 128); color: white; font-size: 16px;")

if __name__=='__main__':
    import sys
    from PyQt5.QtWidgets import QShortcut
    from PyQt5.QtGui import QKeySequence
    from gui.main_window import MainWindow

    app = QApplication(sys.argv)

    window = MainWindow()
    # adding a shortcut test
    def my_slot():
        """Description of the shortcut goes here."""
        print("Shortcut triggered!")
    window.add_shortcut("Ctrl+Shift+T", my_slot)

    # press "Esc" to display shortcuts
    window.show()
    sys.exit(app.exec_())
