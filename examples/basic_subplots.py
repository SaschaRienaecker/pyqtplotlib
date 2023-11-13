
# This example shows how to create a figure with multiple subplots, in a fashion similar to matplotlib's subplots() function.
import pyqtplotlib as qtplt
from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])
fig, axs = qtplt.subplots(1, 2, sharex=True, sharey=False)
axs[0, 0].plot([1, 2, 3], [1, 2, 3], color='r', label='example 1')
axs[0, 1].set_title('Test')
axs[0, 1].plot([1, 2, 3], [3, 2, 1], color='b', label='example 1')
axs[0, 1].legend()

for ax in axs.flatten():
    ax.set_xlabel('x')
    ax.set_ylabel('y')
ax.set_xlim(0, 4)
ax.set_ylim(0, 4)

fig.setGeometry(100, 100, 1500, 600)
fig.show()
app.exec_()
