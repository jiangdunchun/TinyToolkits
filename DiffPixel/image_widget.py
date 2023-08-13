from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

vertex_src = """
#version 330 core

layout (location = 0) in vec2 position;
layout (location = 1) in vec2 texCoord;

out vec2 TexCoord;

void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    TexCoord = texCoord;
}
"""

fragment_src = """
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D textureSampler;

void main()
{
    FragColor = texture(textureSampler, TexCoord);
}
"""

class ImageWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.img_data = [[]]
        self.img_data_changed = False
        self.render_area = [0.0,0.0,1.0,1.0]
        self.render_area_changed = False
        self.rectangle_width = 1.0
        self.rectangle_color = [1.0,0.0,0.0]
        self.rectangle = [0.0,0.0,-1.0,-1.0]

    def updateVBO(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        vertices = [-1.0, -1.0, self.render_area[0], self.render_area[3],
                    1.0,  -1.0, self.render_area[2], self.render_area[3],
                    1.0,   1.0, self.render_area[2], self.render_area[1],
                    -1.0,  1.0, self.render_area[0], self.render_area[1]]
        glBufferData(GL_ARRAY_BUFFER, 64, (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)

        self.render_area_changed = False
    
    def updateTexture(self):
        width = self.img_data.shape[1]
        height = self.img_data.shape[0]
        if width == 0 or height == 0:
            return
        
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.img_data)

        self.img_data_changed = False

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)

        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_shader, fragment_shader)

        self.vbo = glGenBuffers(1)
        self.updateVBO()
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)

        self.texture = glGenTextures(1)
        self.updateTexture()
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

    def drawIamge(self):
        if self.render_area_changed:
            self.updateVBO()
    
        if self.img_data_changed:
            self.updateTexture()

        glUseProgram(self.shader_program)

        glBindVertexArray(self.vao)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(glGetUniformLocation(self.shader_program, "textureSampler"), 0)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def drawRectangle(self):
        if self.rectangle[2] < self.rectangle[0]:
            return
        
        glUseProgram(0)

        glEnable(GL_LINE_SMOOTH)
        glLineWidth(self.rectangle_width)
        glColor3f(self.rectangle_color[0], self.rectangle_color[1], self.rectangle_color[2])
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINES)
        glVertex2f(self.rectangle[0] * 2 - 1, self.rectangle[1] * 2 - 1)
        glVertex2f(self.rectangle[0] * 2 - 1, self.rectangle[3] * 2 - 1)
        
        glVertex2f(self.rectangle[0] * 2 - 1, self.rectangle[3] * 2 - 1)
        glVertex2f(self.rectangle[2] * 2 - 1, self.rectangle[3] * 2 - 1)

        glVertex2f(self.rectangle[2] * 2 - 1, self.rectangle[3] * 2 - 1)
        glVertex2f(self.rectangle[2] * 2 - 1, self.rectangle[1] * 2 - 1)

        glVertex2f(self.rectangle[2] * 2 - 1, self.rectangle[1] * 2 - 1)
        glVertex2f(self.rectangle[0] * 2 - 1, self.rectangle[1] * 2 - 1)
        glEnd()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        self.drawIamge()

        self.drawRectangle()

    def setImageData(self, img_data):
        self.img_data = img_data
        self.img_data_changed = True

    # left top - right bottom
    def setRenderArea(self, x0, y0, x1, y1):
        self.render_area = [x0, y0, x1, y1]
        self.render_area_changed = True

    # left bottom - right top
    def setRectangle(self, x0, y0, x1, y1, color_r=1.0, color_g=0.0, color_b=0.0, width=1.0):
        self.rectangle_width = width
        self.rectangle_color = [color_r, color_g, color_b]
        self.rectangle = [x0, y0, x1, y1]

# import sys
# import cv2
# import numpy as np
# from PyQt5 import QtGui

# if __name__ == '__main__':
#     app = QApplication(sys.argv)

#     widget = ImageWidget()

#     image = cv2.imread("D:/jdc/life/photos/sony_a7/_DSC0763.JPG")
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     widget.setImageData(image_rgb)
#     widget.setRenderArea(0.0,0.0,0.005,0.005)
#     widget.setRectangle(0.0,0.0,0.5,0.5)

#     widget.resize(800, 600)
#     widget.show()

#     sys.exit(app.exec_())
