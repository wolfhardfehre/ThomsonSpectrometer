#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import sys
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from view import View


PROGRAM_NAME = u'<< LaSeR | pOw pOw >>'
VERSION = u'0.1.1'

ABOUT_TEXT = u"""LASER
Copyright 2014 Julia and Wolle

This program analyzes ...

It may be used and modified with no restriction, raw copies as well as
modified versions may be distributed without limitation."""


class Controller(View):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setupUi(self)
        self.getCMaps()

        self.buttonCol.clicked.connect(self.setColor)
        self.buttonBin.clicked.connect(self.calculateBins)
        # self.buttonFLR.clicked.connect(self.canvas.flipLR)
        # self.buttonFUD.clicked.connect(self.canvas.flipUD)
        self.buttonZro.clicked.connect(self.canvas.setPointFlag)
        self.buttonMkr.clicked.connect(self.canvas.setBoarderFlag)
        self.buttonMdl.clicked.connect(self.setThModel)
        self.spinboxRot.valueChanged.connect(self.rotateElements)
        self.spinboxWidth.valueChanged.connect(self.binWidthChanged)
        self.lengthSlider.valueChanged.connect(self.sliderChanged)
        self.lineEditB.returnPressed.connect(self.valueChanged)
        self.lineEditL.returnPressed.connect(self.valueChanged)
        self.lineEditD.returnPressed.connect(self.valueChanged)
        self.lineEditE.returnPressed.connect(self.valueChanged)
        self.lineEditZ.returnPressed.connect(self.valueChanged)
        self.lineEditA.returnPressed.connect(self.valueChanged)
        self.lineEditS.returnPressed.connect(self.valueChanged)

        self.askImageFile()

    def calculateBins(self):
        xs, self.binn = self.canvas.calculateBins()
        self.ekin = self.model.calculateEkin(xs)

    def rotateElements(self):
        self.canvas.rotate(self.spinboxRot.value())

    def binWidthChanged(self):
        self.binRange = self.spinboxWidth.value()
        self.canvas.binWidthChanged(self.binRange)

    def setThModel(self):
        self.canvas.setCurveFlag()
        self.valueChanged()

    def sliderChanged(self):
        length = self.length_start + self.length_step * float(self.lengthSlider.value())
        self.labelLength.setText("Length: %.4f" % length)
        self.valueChanged()

    def valueChanged(self):
        self.canvas.setThModel()

    def setColor(self):
        self.canvas.setColor(cname=self.cname)
        self.ccount += 1
        self.cname = self.cmaps[self.ccount % 70]
        self.buttonCol.setText('Set Color To %s' % self.cname)

    def getCMaps(self):
        self.ccount = 0
        self.cmaps = [m for m in plt.cm.datad if not m.endswith("_r")]
        self.cmaps.sort()
        self.cname = self.cmaps[0]
        self.buttonCol.setText('Set Color To %s' % self.cname)

    def askOpenFile(self, format):
        #  tiff with intel based integers from imagej
        # filename = 'data/20140312_004ionsnew.tif'
        filename = str(QtGui.QFileDialog.getOpenFileName(self, 'Open File', format))
        return filename

    def askImageFile(self):
        self.image_filename = self.askOpenFile('*.tif')
        self.canvas.setImage(self.image_filename)

    def askParamsFile(self):
        filename = self.askOpenFile('*.txt')
        edits = {}
        with open(filename, 'r') as f:
            for line in f.readlines():
                key, value = line.split(";")
                edits[key] = value
        f.closed

        self.setEditTxts(edits)
        self.model.setParams(edits)

    def askSaveFile(self, format):
        filename = str(QtGui.QFileDialog.getSaveFileName(self, "Export Bins", "",
                                                 'Text File (*.txt)'))

        return filename

    def saveBinsFile(self):
        if hasattr(self, "binn"):
            filename = self.askSaveFile('Text File (*.txt)')
            z = self.model.getZ()
            a = self.model.getA()
            with open(filename, 'wb') as f:
                f.writelines('# %s | Z=%s | A=%s | binRange=(+-)%s\n' % (self.image_filename, z, a, self.binRange))
                for e, b in zip(self.ekin, self.binn):
                    f.writelines("{}\t{}\n".format(e, b))
            f.close()
        else:
            print "Sorry no BINs calculated"

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtGui.QMessageBox.about(self, u"About", ABOUT_TEXT)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = Controller()
    main.setWindowTitle("%s %s" % (PROGRAM_NAME, VERSION))
    main.show()
    sys.exit(app.exec_())
