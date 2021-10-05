import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#F0F0F0')
        self.axes = fig.add_subplot(211)
        super(MplCanvas, self).__init__(fig)
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

        self._plot_x_label = 'Counts'
        self._plot_y_label = 'Y ax[a.u.]'
        self._plot_title = 'Plot title'

    def plot(self, data_x: list, data_y: list):
        self.axes.cla()
        if data_x is None and data_y:
            self.axes.plot(data_y, 'go--')
        elif data_x and data_y:
            self.axes.plot(data_x, data_y, 'go--')
        else:
            pass

        self.axes.set_title(self._plot_title)
        self.axes.set_ylabel(self._plot_y_label)
        self.axes.set_xlabel(self._plot_x_label)
        self.axes.grid()
        self.draw()

    @property
    def plot_x_label(self):
        return self._plot_x_label

    @property
    def plot_y_label(self):
        return self._plot_y_label

    @property
    def plot_title(self):
        return self._plot_title

    @plot_x_label.setter
    def plot_x_label(self, value: str = 'Counts'):
        self._plot_x_label = value

    @plot_y_label.setter
    def plot_y_label(self, value: str = "Y label"):
        self._plot_y_label = value

    @plot_title.setter
    def plot_title(self, value: str = 'title'):
        self._plot_title = value

