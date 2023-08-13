# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSizePolicy

import image_widget
import cv2

class Ui_MainForm(object):
    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(1024, 728)
        self.widget = QtWidgets.QWidget(MainForm)
        self.widget.setGeometry(QtCore.QRect(10, 10, 1011, 391))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.OriginalWidget = QtWidgets.QWidget(self.widget)
        self.OriginalWidget.setMinimumSize(QtCore.QSize(200, 200))
        self.OriginalWidget.setObjectName("OriginalWidget")
        self.horizontalLayout.addWidget(self.OriginalWidget)
        self.ComparedWidget = QtWidgets.QWidget(self.widget)
        self.ComparedWidget.setMinimumSize(QtCore.QSize(200, 200))
        self.ComparedWidget.setObjectName("ComparedWidget")
        self.horizontalLayout.addWidget(self.ComparedWidget)
        self.ResultWidget = QtWidgets.QWidget(self.widget)
        self.ResultWidget.setMinimumSize(QtCore.QSize(200, 200))
        self.ResultWidget.setObjectName("ResultWidget")
        self.horizontalLayout.addWidget(self.ResultWidget)
        self.widget1 = QtWidgets.QWidget(MainForm)
        self.widget1.setGeometry(QtCore.QRect(20, 690, 987, 25))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget1)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.DifferentFunction = QtWidgets.QComboBox(self.widget1)
        self.DifferentFunction.setObjectName("DifferentFunction")
        self.horizontalLayout_2.addWidget(self.DifferentFunction)
        spacerItem = QtWidgets.QSpacerItem(748, 13, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.SaveAll = QtWidgets.QPushButton(self.widget1)
        self.SaveAll.setObjectName("SaveAll")
        self.horizontalLayout_2.addWidget(self.SaveAll)
        self.Save = QtWidgets.QPushButton(self.widget1)
        self.Save.setObjectName("Save")
        self.horizontalLayout_2.addWidget(self.Save)

        image = cv2.imread("D:/jdc/life/photos/sony_a7/_DSC0763.JPG")
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        self.OriginalImage = image_widget.ImageWidget(self.OriginalWidget)
        self.OriginalImage.setImageData(image_rgb)
        self.OriginalImage.setRenderArea(0.0,0.0,0.005,0.005)
        self.OriginalImage.setRectangle(0.0,0.0,0.5,0.5)
        self.OriginalImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        OriginalLayout = QVBoxLayout()
        OriginalLayout.addWidget(self.OriginalImage)
        self.OriginalWidget.setLayout(OriginalLayout)

        self.ComparedImage = image_widget.ImageWidget(self.ComparedWidget)
        self.ComparedImage.setImageData(image_rgb)
        self.ComparedImage.setRenderArea(0.0,0.0,0.005,0.005)
        self.ComparedImage.setRectangle(0.0,0.0,0.5,0.5)
        self.ComparedImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ComparedLayout = QVBoxLayout()
        ComparedLayout.addWidget(self.ComparedImage)
        self.ComparedWidget.setLayout(ComparedLayout)

        self.ResultImage = image_widget.ImageWidget(self.ResultWidget)
        self.ResultImage.setImageData(image_rgb)
        self.ResultImage.setRenderArea(0.0,0.0,0.005,0.005)
        self.ResultImage.setRectangle(0.0,0.0,0.5,0.5)
        self.ResultImage.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ResultLayout = QVBoxLayout()
        ResultLayout.addWidget(self.ResultImage)
        self.ResultWidget.setLayout(ResultLayout)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(_translate("MainForm", "Form"))
        self.SaveAll.setText(_translate("MainForm", "SaveAll"))
        self.Save.setText(_translate("MainForm", "Save"))


import sys
from qt_material import apply_stylesheet

# create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

widgt = Ui_MainForm()
widgt.setupUi(window)

# setup stylesheet
apply_stylesheet(app, theme='dark_teal.xml')

# run
window.show()
app.exec_()