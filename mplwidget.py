# -*- coding: utf-8 -*-
"""
@author: Fabiana Toon de Araújo
@contact: fabianaaraujo@usp.br
"""
#from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

class MplWidget(QWidget):
    
    def __init__(self, parent = None):

        QWidget.__init__(self, parent)
        self.figure = Figure()
        self.grafico = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.grafico)
        self.setLayout(layout)
        self.grafico.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        
        
    def update_data(self, x, y):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('Image Pixels Mean')
        ax.plot(x, y)
        self.grafico.draw()
        
        
