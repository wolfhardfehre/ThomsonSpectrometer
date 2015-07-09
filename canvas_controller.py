#!/usr/local/bin/python
# coding: utf-8

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigCanvas
from elements_view import *
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


class AbstractMplCanvas(FigCanvas):
    elementList = []

    def __init__(self):
        self.fig = plt.figure()
        FigCanvas.__init__(self, self.fig)
        self.setAxes()

    def setAxes(self):
        self.ax = plt.Axes(plt.gcf(),
                           [0, 0, 1, 1],
                           yticks=[],
                           xticks=[],
                           frame_on=False)
        plt.gcf().delaxes(plt.gca())
        plt.gcf().add_axes(self.ax)
        plt.axis('off')

    def activateMovement(self, ax):
        Zoomable(self, ax).setUp()
        Pannable(self, ax).setUp()


class MplImageCanvas(AbstractMplCanvas):

    def __init__(self, model, binRange):
        AbstractMplCanvas.__init__(self)
        self.model = model
        self.moveFlag = False
        self.pointFlag = False
        self.boarderFlag = False
        self.curveFlag = False
        self.element = None
        self.binRange = binRange

        self.mpl_connect('motion_notify_event', self.onMotion)
        self.mpl_connect('pick_event', self.onPick)
        self.mpl_connect('button_press_event', self.onPress)
        self.mpl_connect('button_release_event', self.onRelease)

        self.activateMousePosition()

    def binWidthChanged(self, binRange):
        self.binRange = binRange

    def rotate(self, degree=45):
        if hasattr(self, "img"):
            self.img.rotate(degree)
            center = self.img.center
            if hasattr(self, "point"):
                self.point.rotate(center, degree)
            self.updateCanvas()
        else:
            print "No image loaded yet!"

    def updateCanvas(self):
        if not self.setThModel():
            self.draw()

    def onMotion(self, event):
        if event.inaxes is None:
            return
        if event.button == 1 and self.moveFlag:
            x, y = event.xdata, event.ydata
            length = len(self.element.get_xdata())
            if length == 1:
                self.element.set_data([x], [y])
            if length == 2:
                y1, y2 = self.ax.get_ylim()
                self.element.set_data([x, x], [y1, y2])
            self.updateCanvas()

    def onPick(self, event):
        self.element = event.artist
        self.moveFlag = True

    def onPress(self, event):
        if event.inaxes is None:
            return
        if event.button == 1 and not self.moveFlag:
            if self.pointFlag:
                self.setZeroPoint(event)
            if self.boarderFlag:
                self.setBoarders(event)

    def onRelease(self, event):
        self.moveFlag = False

    def setZeroPoint(self, event):
        self.point = MplZeroPoint(self.ax)
        if self.point.setElement(event):
            AbstractMplCanvas.elementList.append(self.point)
        self.draw()

    def setBoarders(self, event):
        self.boarder = MplBoarder(self.ax)
        if self.boarder.setElement(event):
            AbstractMplCanvas.elementList.append(self.boarder)
        self.draw()

    def setImage(self, fname):
        if hasattr(self, "img"):
            self.img.remove()
        self.img = MplImage(self.ax, Image.open(fname))
        self.activateMovement(self.ax)
        AbstractMplCanvas.elementList.append(self.img)

    def setThModel(self):
        if self.isModel():
            if hasattr(self, "curve"):
                self.curve.remove()
                self.upper.remove()
                self.lower.remove()
            x0, y0 = self.point.getCoords()
            xList = self.boarder.getCoords()

            x, y = self.model.calcTheoryModel(x0, y0, xList, self.img.y_size)
            y1, y2 = self.calculateBinExtrema(y)
            self.curve = MplCurveTheory(self.ax)
            self.curve.setElement(x, y)
            self.upper = MplCurveTheory(self.ax)
            self.upper.setElement(x[1:], y1)
            self.lower = MplCurveTheory(self.ax)
            self.lower.setElement(x[1:], y2)
            self.draw()

            return True

        return False

    def calculateBinExtrema(self, y_arr):
        y_old = -1
        lower = np.zeros(len(y_arr))
        upper = np.zeros(len(y_arr))
        y_max = self.img.mtrx.shape[0]

        for i, y in enumerate(y_arr):
            y = int(y)
            if y_old != -1:
                upper[i] = y_old - self.binRange
                lower[i] = y + self.binRange + 1
            y_old = y

        lower[lower > y_max] = y_max
        return upper[1:], lower[1:]

    def calculateBins(self):
        if hasattr(self, "curve"):
            x_array, y_array = self.curve.par.get_data()
            mtx = self.img.mtrx
            y_max = self.img.mtrx.shape[0]
            y_old = -1
            binn = []
            for x, y in zip(x_array, y_array):
                y = int(y)
                if y_old != -1:
                    up = y_old - self.binRange
                    low = y + self.binRange + 1
                    if low > y_max:
                        low = y_max
                    '''
                    summary = 0
                    for i in range(up, low):
                        summary += mtx[i, x]
                    binn.append(summary)
                    -->
                    '''
                    binn.append(sum([mtx[i, x] for i in range(up, low)]))
                y_old = y
            xs = x_array[1:] + 0.5

            return xs, binn

    def activateMousePosition(self):
        def onMotion(event):
            if event.inaxes is None:
                return
            if hasattr(self, "point"):
                if self.point.isSet():
                    x = self.point.element.get_xdata()[0] - event.xdata
                    self.model.displayEkin(x)
        self.mpl_connect('motion_notify_event', onMotion)
        return onMotion

    def isModel(self):
        if hasattr(self, "point") and\
           hasattr(self, "boarder") and\
           hasattr(self, "img") and\
           self.curveFlag:
            return self.point.isSet() and self.boarder.isBoarder()

    def setColor(self, cname):
        if hasattr(self, "img"):
            self.img.setColor(cname)
        self.draw()

    def setPointFlag(self):
        self.boarderFlag = False
        self.pointFlag = True

    def setCurveFlag(self):
        self.curveFlag = True

    def setBoarderFlag(self):
        self.pointFlag = False
        self.boarderFlag = True


class Zoomable(object):

    def __init__(self, canvas, ax, base=1.1):
        self.xmin = ax.get_xlim()
        self.ymin = ax.get_ylim()
        self.base = base
        self.ax = ax
        self.canvas = canvas

    def setUp(self):

        def onScroll(event):
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            x = int(event.xdata)
            y = int(event.ydata)

            if event.button == 'down':
                self.scale = 1 / self.base
            elif event.button == 'up' and isFilled(xlim, ylim):
                self.scale = self.base
            else:
                self.scale = 1

            w = (xlim[1] - xlim[0]) * self.scale
            h = (ylim[1] - ylim[0]) * self.scale

            xrel = (xlim[1] - x) / (xlim[1] - xlim[0])
            yrel = (ylim[1] - y) / (ylim[1] - ylim[0])

            self.ax.set_xlim([x - w * (1 - xrel), x + w * xrel])
            self.ax.set_ylim([y - h * (1 - yrel), y + h * yrel])
            self.canvas.draw()

        def isFilled(xlim, ylim):
            return self.xmin[1] >= xlim[1] and self.ymin[1] <= ylim[1]

        self.canvas.mpl_connect('scroll_event', onScroll)


class Pannable(object):

    def __init__(self, canvas, ax):
        self.xmin = ax.get_xlim()
        self.ymin = ax.get_ylim()
        self.canvas = canvas
        self.ax = ax
        self.xpress = None

    def setUp(self):

        def onPress(event):
            if event.inaxes is None:
                return
            if event.inaxes != self.ax:
                return

            if event.button == 3:
                self.xpress = int(event.xdata)
                self.ypress = int(event.ydata)

        def onRelease(event):
            self.xpress = None

        def onMotion(event):
            if event.inaxes is None:
                return
            if self.xpress is None:
                return

            x = int(event.xdata)
            y = int(event.ydata)
            xlim = np.array(self.ax.get_xlim())
            ylim = np.array(self.ax.get_ylim())

            if event.button == 3:
                dx = x - self.xpress
                dy = y - self.ypress
                xlim -= dx
                ylim -= dy

                if isFilled(xlim, ylim):
                    self.ax.set_xlim(xlim)
                    self.ax.set_ylim(ylim)

            self.canvas.draw()

        def isFilled(xlim, ylim):
            xBool = xlim[0] > self.xmin[0] and xlim[1] < self.xmin[1]
            yBool = ylim[0] < self.ymin[0] and ylim[1] > self.ymin[1]

            return xBool and yBool

        self.canvas.mpl_connect('button_press_event', onPress)
        self.canvas.mpl_connect('button_release_event', onRelease)
        self.canvas.mpl_connect('motion_notify_event', onMotion)
