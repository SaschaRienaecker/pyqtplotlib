from PyQt5 import QtWidgets


class TabsWindow(QtWidgets.QMainWindow):
    def __init__(self, module_widgets=None, module_names=None, parent=None):
        super().__init__(parent)

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.tab_widget.removeTab)

        for i, widget in enumerate(module_widgets):
            name = module_names[i] if module_names is not None else f"Module {i+1}"
            self.tab_widget.addTab(widget, name)

        self.setCentralWidget(self.tab_widget)

        # Setting up shortcuts
        self.shortcut_next_tab = QtWidgets.QShortcut("Alt+Right", self)
        self.shortcut_next_tab.activated.connect(self.nextTab)
        self.shortcut_prev_tab = QtWidgets.QShortcut("Alt+Left", self)
        self.shortcut_prev_tab.activated.connect(self.prevTab)

    def nextTab(self):
        current_index = self.tab_widget.currentIndex()
        total_tabs = self.tab_widget.count()
        next_index = (current_index + 1) % total_tabs
        self.tab_widget.setCurrentIndex(next_index)

    def prevTab(self):
        current_index = self.tab_widget.currentIndex()
        total_tabs = self.tab_widget.count()
        prev_index = (current_index - 1) % total_tabs
        self.tab_widget.setCurrentIndex(prev_index)

    # Register the signal handler for keyboard interrupt (Ctrl+C)
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":

    class Module1(QtWidgets.QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QtWidgets.QVBoxLayout(self)
            layout.addWidget(QtWidgets.QLabel("This is Module 1"))


    class Module2(QtWidgets.QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QtWidgets.QVBoxLayout(self)
            layout.addWidget(QtWidgets.QLabel("This is Module 2"))

    app = QtWidgets.QApplication([])

    # Create instances of your module widgets and add them to the tab widget
    modules = [Module1(), Module2(), QtWidgets.QLabel("This is Module 3")]
    module_names = ["Module 1", "Module 2", "Module 3"]

    window = TabsWindow(modules, module_names=module_names)
    window.setGeometry(100, 100, 900, 100)
    window.show()
    app.exec_()
