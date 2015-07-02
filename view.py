#!/usr/local/bin/python
# coding: utf-8

# from matplotlib.path import Path
from PyQt4 import QtGui, QtCore
from model import MyModel
from canvas_controller import MplImageCanvas


class View(QtGui.QMainWindow):

    def setupUi(self, dialog):

        self.length_start = 0.0056
        self.length_step = 0.00005
        self.binRange = 1
        slider_max = 200
        slider_pos = int(slider_max * 0.5)

        self.setMinimumSize(800, 600)

        # MENU
        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit',
                                 self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        
        self.file_menu.addAction('&Load Image', self.askImageFile)
        self.file_menu.addAction('&Load Params', self.askParamsFile)
        self.file_menu.addAction('&Save Bins', self.saveBinsFile)
        
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)
        self.help_menu.addAction('&About', self.about)

        # SET MAIN WIDGET AND LAYOUTS
        self.main_widget = QtGui.QWidget(dialog)
        main_layout = QtGui.QVBoxLayout(self.main_widget)
        h1_layout = QtGui.QHBoxLayout()
        v1_layout = QtGui.QVBoxLayout()
        h21_layout = QtGui.QHBoxLayout()
        h22_layout = QtGui.QHBoxLayout()
        h23_layout = QtGui.QHBoxLayout()

        # BUTTONS CREATION
        self.buttonCol = QtGui.QPushButton()
        self.buttonFLR = QtGui.QPushButton(u'Flip L- R')
        self.buttonFUD = QtGui.QPushButton(u'Flip U- D')
        self.buttonZro = QtGui.QPushButton(u'Set Zero')
        self.buttonMkr = QtGui.QPushButton(u'Set Borders')
        self.buttonMdl = QtGui.QPushButton(u'Theo. Model')
        self.buttonBin = QtGui.QPushButton(u'Calculate Bins')

        # SPINBOXES
        self.spinboxRot = QtGui.QSpinBox()
        self.spinboxRot.setMinimum(-180)
        self.spinboxRot.setMaximum(180)
        self.spinboxWidth = QtGui.QSpinBox()
        self.spinboxWidth.setMinimum(1)
        self.spinboxWidth.setValue(self.binRange)
        self.spinboxWidth.setMaximum(200)

        # TEXT LABELS
        self.labelB = QtGui.QLabel("B = ")
        self.labelL = QtGui.QLabel("L = ")
        self.labelD = QtGui.QLabel("D = ")
        self.labelE = QtGui.QLabel("E = ")
        self.labelZ = QtGui.QLabel("Z = ")
        self.labelA = QtGui.QLabel("A = ")
        self.labelS = QtGui.QLabel("S = ")
        self.labelRotate = QtGui.QLabel("Rotation")
        self.labelWidth = QtGui.QLabel("Trace width")

        length = self.length_start + self.length_step * slider_pos
        self.labelLength = QtGui.QLabel("Length: %.4f" % length)

        # Slider
        self.lengthSlider = QtGui.QSlider()
        self.lengthSlider.setMaximum(slider_max)
        self.lengthSlider.setSingleStep(1)
        self.lengthSlider.setSliderPosition(slider_pos)
        self.lengthSlider.setOrientation(QtCore.Qt.Horizontal)
        self.lengthSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.lengthSlider.setTickInterval(10)

        # LINE EDITS
        self.model = MyModel(self, self.length_start, self.length_step)
        self.canvas = MplImageCanvas(self.model, self.binRange)

        self.lineEditB = QtGui.QLineEdit(str(self.model.b))
        self.lineEditL = QtGui.QLineEdit(str(self.model.l))
        self.lineEditD = QtGui.QLineEdit(str(self.model.d))
        self.lineEditE = QtGui.QLineEdit(str(self.model.e))
        self.lineEditZ = QtGui.QLineEdit(str(self.model.z))
        self.lineEditA = QtGui.QLineEdit(str(self.model.a))
        self.lineEditS = QtGui.QLineEdit(str(self.model.s))

        # SET BUTTONS AND CANVAS TO LAYOUTS
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(h1_layout)
        main_layout.addLayout(v1_layout)
        h1_layout.addWidget(self.buttonCol)
        h1_layout.addWidget(self.labelRotate)
        h1_layout.addWidget(self.spinboxRot)
        h1_layout.addWidget(self.buttonFLR)
        h1_layout.addWidget(self.buttonFUD)
        h1_layout.addWidget(self.buttonZro)
        h1_layout.addWidget(self.buttonMkr)
        h1_layout.addWidget(self.buttonMdl)

        # SET TEXT LABELS AND LINE EDITS TO LAYOUTS
        v1_layout.addLayout(h21_layout)
        v1_layout.addLayout(h22_layout)
        v1_layout.addLayout(h23_layout)
        h21_layout.addWidget(self.labelB)
        h21_layout.addWidget(self.lineEditB)
        h21_layout.addWidget(self.labelL)
        h21_layout.addWidget(self.lineEditL)
        h21_layout.addWidget(self.labelD)
        h21_layout.addWidget(self.lineEditD)
        h21_layout.addWidget(self.labelE)
        h21_layout.addWidget(self.lineEditE)
        h22_layout.addWidget(self.labelZ)
        h22_layout.addWidget(self.lineEditZ)
        h22_layout.addWidget(self.labelA)
        h22_layout.addWidget(self.lineEditA)
        h22_layout.addWidget(self.labelS)
        h22_layout.addWidget(self.lineEditS)
        h22_layout.addWidget(self.labelWidth)
        h22_layout.addWidget(self.spinboxWidth)
        h23_layout.addWidget(self.labelLength)
        h23_layout.addWidget(self.lengthSlider)
        h23_layout.addWidget(self.buttonBin)

        # FOCUS
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.stat = self.statusBar()

    def getEditTxts(self):
        edits = []
        edits.append(self.lineEditB.text())
        edits.append(self.lineEditL.text())
        edits.append(self.lineEditD.text())
        edits.append(self.lineEditE.text())
        edits.append(self.lineEditZ.text())
        edits.append(self.lineEditA.text())
        edits.append(self.lineEditS.text())
        edits.append(self.lengthSlider.value())
        return edits

    def setEditTxts(self, edits):
        self.lineEditB.setText(edits["b"])
        self.lineEditL.setText(edits["l"])
        self.lineEditD.setText(edits["d"])
        self.lineEditE.setText(edits["e"])
        self.lineEditZ.setText(edits["z"])
        self.lineEditA.setText(edits["a"])
        self.lineEditS.setText(edits["s"])
