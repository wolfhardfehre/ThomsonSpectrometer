#!/usr/local/bin/python
# coding: utf-8
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
from PyQt4 import QtGui
from abc import ABCMeta
from abc import abstractmethod


class AbstractMplElements(object):
    __metaclass__ = ABCMeta

    def __init__(self, ax):
        self.ax = ax

    @abstractmethod
    def setElement(self, element):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def flipUD(self):
        pass

    @abstractmethod
    def flipLR(self):
        pass


class ConnectableMplElements(AbstractMplElements):
    __metaclass__ = ABCMeta

    def __init__(self, ax):
        AbstractMplElements.__init__(self, ax)

    def drawElement(self, x, y):
        self.element = self.ax.plot(x, y,
                                    self.sign,
                                    picker=5,
                                    color=self.col,
                                    mew=self.mew,
                                    ms=self.ms,
                                    alpha=self.alpha).pop(0)

    @abstractmethod
    def setElement(self, element):
        pass

    @abstractmethod
    def remove(self):
        pass

    @abstractmethod
    def flipUD(self):
        pass

    @abstractmethod
    def flipLR(self):
        pass


class MplZeroPoint(ConnectableMplElements):
    pointAmount = 1
    pointCount = 0

    def __init__(self, ax):
        ConnectableMplElements.__init__(self, ax)
        self.col = 'red'
        self.sign = '+'
        self.mew = 2
        self.ms = 20
        self.alpha = .5
        MplZeroPoint.pointCount += 1

    def setElement(self, event):
        if self.tooManyPoints():
            return False
        self.drawElement(int(event.xdata), int(event.ydata))
        self.origin = np.array([int(event.xdata), int(event.ydata)])
        return True

    def tooManyPoints(self):
        return MplZeroPoint.pointCount > MplZeroPoint.pointAmount

    def isSet(self):
        return hasattr(self, "element")

    def getCoords(self):
        if not hasattr(self, "element"):
            QtGui.QMessageBox.about(QtGui.QWidget(),
                                    "Zero Point Error",
                                    "Please Set A Zero Point\n\
                                    Before Calculate The Model")
        return self.element.get_xydata()[0]

    def rotate(self, center, angle=90):
        """
        Rotation of a point around a anchor
        Attributes:
            anchor: point object with x- and y-coordinate
            angle:  the rotation angle in degree or rad
                    default = 90
                    positive ... counter clockwise
                    negativ  ... clockwise
            unit:   unit specification of angle
                    default = "degree"
        """
        angle = angle * np.pi / 180.
        rot_marix = np.array([[np.cos(angle), -np.sin(angle)],
                              [np.sin(angle), np.cos(angle)]])
        rot_pt = np.dot(self.origin - center, rot_marix) + center
        self.element.set_data([rot_pt[0]], [rot_pt[1]])

    def remove(self):
        if hasattr(self, 'element'):
            self.element.remove()

    def flipUD(self):
        pass

    def flipLR(self):
        pass


class MplBoarder(ConnectableMplElements):
    boarderAmount = 2
    boarderCount = 0
    boarderList = []

    def __init__(self, ax):
        ConnectableMplElements.__init__(self, ax)
        self.col = 'yellow'
        self.sign = '-'
        self.mew = 2
        self.ms = 20
        self.alpha = .5
        MplBoarder.boarderCount += 1

    def setElement(self, event):
        if self.tooManyBoarders():
            return False
        x = int(event.xdata)
        self.drawElement([x, x], self.ax.get_ylim())
        MplBoarder.boarderList.append(self.element)
        return True

    def tooManyBoarders(self):
        return MplBoarder.boarderCount > MplBoarder.boarderAmount

    def getCoords(self):
        comp = len(MplBoarder.boarderList)
        if comp != MplBoarder.boarderAmount:
            QtGui.QMessageBox.about(QtGui.QWidget(),
                                    "Marker Error",
                                    "Please Set %i Boarder Marker Before\
                                     Calculating The Model"
                                    % MplBoarder.boarderAmount - comp)
            return
        return [b.get_xdata()[0] for b in MplBoarder.boarderList]

    def isBoarder(self):
        return MplBoarder.boarderCount == MplBoarder.boarderAmount

    def remove(self):
        if hasattr(self, 'element'):
            self.element.remove()

    def flipUD(self):
        pass

    def flipLR(self):
        pass


class MplImage(AbstractMplElements):

    def __init__(self, ax, image, cname='gray'):
        AbstractMplElements.__init__(self, ax)
        self.origin = np.array(image)
        self.mtrx = self.origin[...]
        size = self.mtrx.shape
        self.x_size = size[1]
        self.y_size = size[0]
        self.center = [self.x_size / 2, self.y_size / 2]
        self.cname = cname
        self.rotFactor = 1
        idy, idx = np.unravel_index(self.mtrx.argmax(), self.mtrx.shape)
        idyn, idxn = np.unravel_index(self.mtrx.argmin(), self.mtrx.shape)
        mx = np.max(self.mtrx)
        mn = np.min(self.mtrx)
        print "Maximum in image is %i at (x = %i, y = %i)" % (mx, idx, idy)
        print "Minimum in image is %i at (x = %i, y = %i)" % (mn, idxn, idyn)
        print "Height x Width is %i x %i" % size
        self.setElement()

    def setElement(self):
        self.image = plt.imshow(self.mtrx)
        self.setColor(self.cname)

    def remove(self):
        if hasattr(self, 'image'):
            self.image.remove()

    def rotate(self, degree):
        self.remove()
        self.mtrx = ndimage.rotate(self.origin, degree, reshape=False)
        self.setElement()
        self.setColor(self.cname)

    def flipUD(self):
        self.mtrx = np.flipud(self.mtrx)
        self.image.set_data(self.mtrx)
        self.setColor(self.cname)

    def flipLR(self):
        self.mtrx = np.fliplr(self.mtrx)
        self.image.set_data(self.mtrx)
        self.setColor(self.cname)

    def setColor(self, cname):
        self.cname = cname
        self.image.set_cmap(self.cname)


class MplCurveTheory(AbstractMplElements):

    def __init__(self, ax):
        AbstractMplElements.__init__(self, ax)
        self.par = None
        #self.upp = None
        #self.low = None
        self.col = "red"
        self.alpha = 0.7
        self.lw = 1

    def setElement(self, xArr, yArr):
        self.par = self.drawElement(xArr, yArr, "-")

    def drawElement(self, x, y, sign):
        element = self.ax.plot(x, y, sign,
                               color=self.col,
                               lw=self.lw,
                               alpha=self.alpha).pop(0)
        return element

    def remove(self):
        self.par.remove()

    def rotate(self):
        pass

    def flipUD(self):
        pass

    def flipLR(self):
        pass
