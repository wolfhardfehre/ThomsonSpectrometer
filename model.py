#!/usr/local/bin/python
# coding: utf-8

import numpy as np


class MyModel(object):

    def __init__(self, view, length_start, length_step):
        '''
        Parameters
        ------------------------------
        q  ... charge in [C]
        m  ... mass of proton in [kg]
        e0 ... electrical field in [V/m]
        b  ... magnetic field in [T]
        d  ... is length of magnet in [m]
        l  ... is drift of spectrometer in [m]
        a  ... is mass number in [Integers]
        z  ... is ionization degree (number of charge) in [Integers]
        s  ... is image calculation in [m/px]
        '''

        self.length_start = length_start
        self.length_step = length_step
        self.view = view
        self.q = 1.602E-19
        self.m = 1.673E-27
        self.length = 0.0106
        self.e = 4.75E3
        self.e0 = self.e / self.length
        self.b = 0.28
        self.d = 0.05
        self.l = 0.533
        self.a = 1
        self.z = 1
        self.s = 1.08E-4

    def calcTheoryModel(self, x0, y0, xList, y_img_size):
        self.updateTxt()
        if xList[0] > xList[1]:
            from_x, to_x = x0 - xList
        else:
            to_x, from_x = x0 - xList
        x_arr = np.arange(from_x, to_x, 1)
        factor = ((self.q * self.z * self.b**2 * self.l * self.d)
                  / (self.e0 * self.a * self.m))**-1 * self.s
        yres = []
        xres = []
        for x in x_arr:
            y = factor * x**2 + y0
            if y > y_img_size or y < 0:
                break
            xres.append(x0 - x)
            yres.append(y)
        return np.array(xres), np.array(yres)

    def updateTxt(self):
        edits = self.view.getEditTxts()
        self.b = float(edits[0])
        self.l = float(edits[1])
        self.d = float(edits[2])
        self.e = float(edits[3])
        self.z = float(edits[4])
        self.a = float(edits[5])
        self.s = float(edits[6])
        self.length = self.length_start + self.length_step * float(edits[7])
        self.e0 = self.e / self.length

    def setParams(self, edits):
        self.b = float(edits["b"])
        self.l = float(edits["l"])
        self.d = float(edits["d"])
        self.e = float(edits["e"])
        self.z = float(edits["z"])
        self.a = float(edits["a"])
        self.s = float(edits["s"])

    def displayEkin(self, x):
        if x > 0.0:
            res = str(self.calculateEkin(x))
        else:
            res = "out of bounds"
        self.view.stat.showMessage('Ekin: %s' % res)

    def getZ(self):
        return self.z

    def getA(self):
        return self.a

    def calculateEkin(self, x):
        # Ekin= 0.5*a*m*10E-6*(q*z*l*d*b)**2/(q*m*a*x*s)**2
        self.updateTxt()
        fac1 = 0.5 * self.a * self.m * 1E-6
        fac2 = (self.q * self.z * self.l * self.d * self.b)**2
        denom = self.q * (self.m * self.a * x * self.s)**2
        return fac1 * fac2 / denom
