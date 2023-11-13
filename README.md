# pyqtplotlib

Pyqtplotlib is a Python library designed to simplify the development of GUI applications for scientific purposes. It offers a user-friendly interface for creating interactive GUIs and plots, leveraging the power of PyQt5 and PyQtGraph while providing a syntax similar to Matplotlib's pyplot.

## Features

- **Easy-to-use Syntax**: Familiar matplotlib-like syntax for quick adaptation.
- **Powerful Backend**: Built on PyQt5/PyQtGraph for robust and interactive GUIs.
- **Customizable**: Easy to customize and extend for various scientific applications.
<!-- - **Cross-platform**: Compatible with Windows, macOS, and Linux. -->

## Installation

To install pyqtplotlib, run the following command:

```bash
pip install --user .
```

## Usage

```python
# Example code
import pyqtplotlib as qtplt
from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])
fig, ax = qtplt.subplots()
ax.plot([1, 2, 3], [1, 2, 3], color='r', linestyle='--', label='example 1')
fig.show()
app.exec_()
```
For more examples, see the [examples](examples) folder.

## TODO's:

The 'Axes' class misses the following functionalities:
- [ ] `ax.grid()`
- [ ] `ax.set_aspect()`
- [ ] Diverse format options passed to the `ax.plot()` function are not yet implemented.
- [ ] ...

The 'Figure' class misses the following functionalities:
- [ ] pass `figsize` to `Figure` constructor
- [ ] ...

## Acknowledgments

Thanks to the PyQt5 and PyQtGraph communities for providing the frameworks, as well as the Matplotlib community for the inspiration.

