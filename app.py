from PyQt5 import QtWidgets,QtCore,QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType # loadUiType: Open File
from PyQt5.QtGui import QPixmap  # load image

import logging
from pathlib import Path  

from Image import Image  # import image class
import cv2

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.exporters

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import math

from scipy import signal
import scipy.io.wavfile as wavfile
import scipy
from scipy.fftpack import fft, fftfreq
import scipy.fftpack as fftpk
from scipy.fftpack import irfft

import os
from os import path ## os --> Operating system / path --> Ui File
import sys
import numpy as np

# logging setupUi
logging.basicConfig(filename="logging.log", 
                    format='%(asctime)s %(message)s', 
                    filemode='a',force= True) 


logger=logging.getLogger() 

logger.setLevel(logging.DEBUG) 

# Creat Variable that load .ui file from folder path 
FORM_CLASS,_= loadUiType(path.join(path.dirname(__file__),"Mixer.ui"))




# Class Take main window from Qt Designer and the file of the GUI (FORM_CLass)that take file path and name
class MainApp(QtWidgets.QMainWindow, FORM_CLASS):                #QmainWindow: refers to main window in Qt Designer
    def __init__(self,parent=None):
        super(MainApp,self).__init__(parent)
        QtWidgets.QMainWindow.__init__(self)
        pg.setConfigOption('background','w')
        self.setupUi(self)
        self.FT_ComboBox = [self.Imag1_comboBox, self.Imag2_comboBox]
        self.FTGraphicsView = [self.FT_Image1_graphicsView, self.FT_Image2_graphicsView, self.Output1_graphicsView, self.Output2_graphicsView]
        self.Image_Component_ComboBox = [self.Component1_comboBox, self.Component2_comboBox]
        self.Component_Slider = [self.Component1_Slider, self.Component2_Slider]
        self.FT_Component_comboBox = [self.FT_Component1_comboBox, self.FT_Component2_comboBox]
        self.FT_Component = [0,0]
        self.Slider_Ratio = [0,0]
        self.Component_Image = [0,0]
        self.Axis = ['bottom', 'left']
        self.Set_GraphicsView()
        self.Handel_Buttons()
        self.Output_Counter = 0

    def Handel_Buttons(self):
        self.Browse_Image1.clicked.connect(lambda: self.Upload_Image(1))
        self.Browse_Image2.clicked.connect(lambda: self.Upload_Image(2))

        self.Imag1_comboBox.currentIndexChanged.connect(lambda: self.FT_Combo_box_Handler(0))
        self.Imag2_comboBox.currentIndexChanged.connect(lambda: self.FT_Combo_box_Handler(1))

        self.Output_comboBox.currentIndexChanged.connect(self.Output_Combo_box_Handler)

        self.Component1_comboBox.currentIndexChanged.connect(lambda: self.Image_Component_Combo_box_Handler(0))
        self.Component2_comboBox.currentIndexChanged.connect(lambda: self.Image_Component_Combo_box_Handler(1))

        for x in self.Component_Slider:
            x.valueChanged.connect(self.Slider_value)

    def Upload_Image(self, image_no):
        logger.info("Uploading Images") 
        load_file = QtWidgets.QFileDialog.getOpenFileName()
        image_path, Format = load_file
        if os.path.isfile(image_path):
            self.Set_Draw_Function(image_path)
            if image_no == 1:  # first image place
                self.Image1 = Image(image_path)
                self.Image1_graphicsView.setScene(self.scene)
                self.FT_Image1_graphicsView.clear()
                self.Images = [self.Image1]
            elif image_no == 2:  # second image place
                self.Image2 = Image(image_path)
                if self.Image1.image.shape == self.Image2.image.shape:  # check size of 2 images
                    self.Image2_graphicsView.setScene(self.scene)
                    self.FT_Image2_graphicsView.clear()
                    self.Images = [self.Image1, self.Image2]
                else:
                    
                    QtWidgets.QMessageBox.question(self, 'Error message', "Picture does not has the same size of first one", QtWidgets.QMessageBox.Ok)
                    logger.warning("Warning: 2nd picture does not has the same size of first one") 
                  

    def Set_Draw_Function(self, image):
        self.scene = QtWidgets.QGraphicsScene(self)
        pixmap = QPixmap(image)
        pixmap=pixmap.scaled(QtCore.QSize(self.Image1_graphicsView.width(), self.Image1_graphicsView.height()))
        item = QtWidgets.QGraphicsPixmapItem(pixmap)
        self.scene.addItem(item)

    def Draw_FT(self, FT_Type, GraphicsView_No):
        self.img = pg.ImageItem(FT_Type)
        self.FTGraphicsView[GraphicsView_No].addItem(self.img)

    def FT_Combo_box_Handler(self, ComboBoxNo):
        self.FT = self.FT_ComboBox[ComboBoxNo].currentText()
        if self.FT == 'Mag':
            logger.info("Chose the magnitude component") 
            self.Draw_FT(self.Images[ComboBoxNo].FT_Magnitude, ComboBoxNo)
        elif self.FT == 'Phase':
            logger.info("Chose the phase component") 
            self.Draw_FT(self.Images[ComboBoxNo].FT_Phase, ComboBoxNo)
        elif self.FT == 'Real':
            logger.info("Chose the Real component") 
            self.Draw_FT(self.Images[ComboBoxNo].FT_Real, ComboBoxNo)
        elif self.FT == 'Imag':
            logger.info("Chose the imagnary component") 
            self.Draw_FT(self.Images[ComboBoxNo].FT_Imaginary, ComboBoxNo)

    def Image_Component_Combo_box_Handler(self, component_no):
        self.Image_Component = self.Image_Component_ComboBox[component_no].currentText()
        if self.Image_Component == 'Image1':
            self.Component_Image[component_no] = self.Image1
        elif self.Image_Component == 'Image2':
            self.Component_Image[component_no] = self.Image2

    def Output_Combo_box_Handler(self):
        self.Output = self.Output_comboBox.currentText()
        if self.Output == 'Output1' and self.Output_Counter == 1:
            logger.info("User choose first output space") 
            self.Draw_FT(self.Output_sig, 2)
            self.img.rotate(270)
        elif self.Output == 'Output2'and self.Output_Counter == 1:
            logger.info("User choose second output space")
            self.Draw_FT(self.Output_sig, 3)
            self.img.rotate(270)

    def Slider_value(self):
        logger.info("User change the sliders' value") 
        self.Slider_count = 0
        self.FT_component_no = 0

        for x in self.Component_Slider:
            self.Slider_Ratio[self.Slider_count] = (x.value())/100
            self.Slider_count += 1
           
        
        for y in self.FT_Component_comboBox:
            self.FT_Component[self.FT_component_no] = self.FT_Component_comboBox[self.FT_component_no].currentText()
            self.FT_component_no += 1
            

        self.Mixer()

    def Mixer(self):
        if (self.FT_Component[0] == 'Mag' and self.FT_Component[1] == 'Phase'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], self.Slider_Ratio[0], self.Slider_Ratio[1], 'Magnitude_Phase')
        elif (self.FT_Component[0] == 'Phase' and self.FT_Component[1] == 'Mag'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], self.Slider_Ratio[1], self.Slider_Ratio[0], 'Magnitude_Phase')
        elif (self.FT_Component[0] == 'Real' and self.FT_Component[1] == 'Imag'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], self.Slider_Ratio[0], self.Slider_Ratio[1], 'Real_Imaginary')
        elif (self.FT_Component[1] == 'Real' and self.FT_Component[0] == 'Imag'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], self.Slider_Ratio[0], self.Slider_Ratio[1], 'Real_Imaginary')
        elif (self.FT_Component[0] == 'Mag' and self.FT_Component[1] == 'UniPhase'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], self.Slider_Ratio[0], 100, 'Magnitude_UniformPhase')
        elif (self.FT_Component[0] == 'UniPhase' and self.FT_Component[1] == 'Mag'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], self.Slider_Ratio[1], 100, 'Magnitude_UniformPhase')
        elif (self.FT_Component[0] == 'UniMag' and self.FT_Component[1] == 'Phase'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], 100, self.Slider_Ratio[1], 'UniformMagnitude_Phase')
        elif (self.FT_Component[0] == 'Phase' and self.FT_Component[1] == 'UniMag'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], 100, self.Slider_Ratio[0],'UniformMagnitude_Phase')
        elif (self.FT_Component[0] == 'UniMag' and self.FT_Component[1] == 'UniPhase') or (self.FT_Component[0] == 'UniPhase' and self.FT_Component[1] == 'UniMag'):
            self.Output_sig = self.Component_Image[0].mix(self.Component_Image[1], 100, 100, 'UniformMagnitude_UniformPhase')
        else:
            QtWidgets.QMessageBox.question(self, 'Error message', "Component does not match ", QtWidgets.QMessageBox.Ok)
            logger.warning("Warning: Component does not match") 
            
        self.Output_Counter = 1
        self.Output_Combo_box_Handler()

    def Draw_Mixer(self, FT_Type, GraphicsView_No):
        image = pg.ImageItem(FT_Type)
        self.FTGraphicsView[GraphicsView_No].addItem(image)
    def Set_GraphicsView(self):
        for x in self.FTGraphicsView:
            for y in self.Axis:
                x.getPlotItem().hideAxis(y)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_() #infinite loop

if __name__=='__main__':
    main()
