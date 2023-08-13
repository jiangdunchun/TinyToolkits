import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from qt_material import apply_stylesheet

from OpenGL.GL import *

import designer

class grahicOpenGL(QtWidgets.QOpenGLWidget):
    def __init__(self,parent = None,picFile=None):
        super().__init__(parent)
        self.resize(100, 100)
        self.img = None
        self.picFile = None
        if picFile:self.loadPicFile(picFile)

        self.img_data = None
        self.img_data_changed = False
        self.render_area = [0.0,0.0,1.0,1.0]
        self.render_area_changed = False
        self.rectangle_width = 1.0
        self.rectangle_color = [1.0,0.0,0.0]
        self.rectangle = [0.0,0.0,0.5,0.5]

    def loadPicFile(self,picFile):
        self.picFile = picFile
        self.img = QtGui.QImage()
        self.img.load(picFile)

    def drawRectangle(self):
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(self.rectangle_width)
        glColor3f(self.rectangle_color[0], self.rectangle_color[1], self.rectangle_color[2])
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINES)
        glVertex2f(self.rectangle[0], self.rectangle[1])
        glVertex2f(self.rectangle[0], self.rectangle[3])
        
        glVertex2f(self.rectangle[0], self.rectangle[3])
        glVertex2f(self.rectangle[2], self.rectangle[3])

        glVertex2f(self.rectangle[2], self.rectangle[3])
        glVertex2f(self.rectangle[2], self.rectangle[1])

        glVertex2f(self.rectangle[2], self.rectangle[1])
        glVertex2f(self.rectangle[0], self.rectangle[1])
        glEnd()

    def paintGL(self):
        if self.img:
            paint = QtGui.QPainter()
            paint.begin(self)
            paint.drawImage(QtCore.QPoint(0,0),self.img)
            paint.end()

        self.drawRectangle()

# create the application and the main window
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QMainWindow()

# widgt = designer.Ui_Form()
# widgt.setupUi(window)

openglw = grahicOpenGL(window, "D:/jdc/life/photos/sony_a7/_DSC0763.JPG")
window.setCentralWidget(openglw)

# setup stylesheet
apply_stylesheet(app, theme='dark_teal.xml')

# run
window.show()
app.exec_()