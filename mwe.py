import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

# Define the main window class
class SimpleApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set some main window's properties
        self.setWindowTitle('Simple PyQt5 App')
        self.setGeometry(100, 100, 280, 80)

        # Set a QLabel
        self.label = QLabel('Hello, PyQt5!', self)
        self.label.move(50, 30)

        # Show the application's GUI
        self.show()

# Create the application object
app = QApplication(sys.argv)

# Create an instance of your application's main window
window = SimpleApp()

# Run your application's event loop (or main loop)
sys.exit(app.exec_())
