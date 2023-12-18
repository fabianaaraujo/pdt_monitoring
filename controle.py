# -*- coding: utf-8 -*-
"""
@author: Fabiana Toon de Araújo
@contact: fabianaaraujo@usp.br
"""

# imported modules and libraries 
import sys, os
from PyQt5 import QtWidgets, QtCore, uic, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtWidgets import QMessageBox, QApplication, QWidget, QVBoxLayout
from datetime import datetime
from threading import Thread
import cv2
import numpy as np
from matplotlib import pyplot as plt
from mplwidget import MplWidget
import pandas as pd
import time
import csv

# time counter thread
class TimeCounterThread(QtCore.QThread):
    writerow_signal = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.run_flag = True
    
    def run(self):
        y= 0
        # creates a csv file to store time data 
        while self.run_flag:
            start = time.time()
            time.sleep(5)
            end=time.time()
            x = end-start
            y = x + y
            with open('time_data.csv','a', newline='') as results:
                dados = csv.writer(results)
                dados.writerow(["{:.2f}".format(y)])
            self.writerow_signal.emit(y)
            if y>=60:
                self.run_flag = False
    def stop(self):
        self.run_flag = False
        self.wait()

# camera thread
class ThreadClass(QtCore.QThread): 
    change_pixmap_signal = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self):
        # set run flag to False and waits for thread to finish
        self._run_flag = False
        self.wait()

# main thread that handles the UI thread            
class App(QtWidgets.QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("Interface.ui", self)
        #connect actions to methods
        self.salvar.clicked.connect(self.criar_pasta)
        self.btnIniciar.clicked.connect(self.plotar_grafico)
        
        self.threadclass = ThreadClass()
        # connect its signal to the update_image slot
        self.threadclass.change_pixmap_signal.connect(self.update_image)
        
        self.timecounterthread = TimeCounterThread()
        self.timecounterthread.writerow_signal.connect(self.save_image)
        
        self.path2 = None
        self.paciente = None
        self.data = None
        self.label = 0
        self.cv_img = None
        
        self.MplWidget = MplWidget()
        self.mpl_container.layout().addWidget(self.MplWidget)
        
    # aquire user data to create folders
    def criar_pasta(self):
        self.paciente = self.pacienteinput.text()
        self.data = datetime.strftime(self.dateinput.date().toPyDate(),'%y-%m-%d')
        self.path = os.getcwd()
        default = "21-01-01"
        
        if not self.paciente:
            QMessageBox.warning(self,'Erro', 'Insira o nome do usuário para prosseguir.')
        elif self.data == default:
            QMessageBox.warning(self,'Erro', 'Insira a data de hoje para prosseguir.')
        else: 
            self.pacienteinput.setEnabled(False)
            self.dateinput.setEnabled(False)
            if not os.path.exists(self.path +'/'+ self.paciente):
               os.mkdir(self.path +'/'+ self.paciente)
               os.mkdir(self.path +'/'+ self.paciente + '/' + self.data)
               QMessageBox.information(self,'Aviso','Sua pasta foi criada, o tratamento pode ser iniciado.')
            else:
               os.mkdir(self.path +'/'+ self.paciente + '/' + self.data)
               QMessageBox.information(self,'Aviso','Sua pasta foi criada, o tratamento pode ser iniciado.')
        self.path2 = self.path +'/'+ self.paciente + '/' + self.data
        return self.path2
    
    # starts the camera and the time counter threads
    def plotar_grafico(self):
        self.threadclass.start()
        self.timecounterthread.start()
    
    # deal with the closing UI event and stop threads       
    def closeEvent(self, event):
        self.threadclass.stop()
        self.timecounterthread.stop()
        event.accept()
    
    # receive signals and show the frame images from the webcam on the screen
    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image.setPixmap(qt_img)
    
    # adjust image format
    def convert_cv_qt(self, cv_img):
        self.cv_img = cv_img
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        #p = convert_to_Qt_format.scaled(Qt.KeepAspectRatio)
        return QPixmap.fromImage(convert_to_Qt_format)    
 
    @pyqtSlot(float)
    def save_image(self):
        print(np.shape(self.cv_img))
        cv2.imwrite(self.path2 +'/'+ f'{self.label:04d}' +'.jpg', self.cv_img)
        self.label = self.label + 1
        # Calculates image pixel mean
        with open('img_data.csv','a', newline='') as data:
            dados_imagem = csv.writer(data)
            img_mean = np.mean(self.cv_img)
            dados_imagem.writerow(["{:.2f}".format(img_mean)])
        self.plot_graph()
    
    def plot_graph(self):
        dados_x = pd.read_csv('time_data.csv', header = None, names = ["Time"])
        dados_y = pd.read_csv('img_data.csv', header = None, names = ["Data"])
        dados_x = dados_x["Time"].tolist()
        dados_y = dados_y["Data"].tolist()
        self.MplWidget.update_data(dados_x, dados_y)
        
        
        
# main code         
if __name__ =='__main__':           #Running the file directly
    qt = QApplication(sys.argv)     #Instance of the QApplication Class
    window = App()                  #Instance of the App Class
    window.show()                   #Calling the method show() through the instance
    sys.exit(qt.exec_())            #Calling the method exec_()