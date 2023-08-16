from PyQt5.QtWidgets import QApplication, QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from PyQt5.QtGui import QWheelEvent, QMouseEvent
from PyQt5.QtCore import Qt

vert_src = """
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

frag_background_src = """
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

void main()
{
    float uv_x = (TexCoord.x - int(TexCoord.x)) - 0.5;
    float uv_y = (TexCoord.y - int(TexCoord.y)) - 0.5;

    if (uv_x * uv_y <= 0.0)
        FragColor = vec4(0.5,0.5,0.5,1.0);
    else
        FragColor = vec4(1.0,1.0,1.0,1.0);

}
"""

frag_img_src = """
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D textureSampler;

void main()
{
    if (TexCoord.x < 0.0 || TexCoord.x > 1.0 || TexCoord.y < 0.0 || TexCoord.y > 1.0)
        discard;
    FragColor = texture(textureSampler, TexCoord);
}
"""

class ImageWidget(QOpenGLWidget):
    def __init__(self, parent=None, img_data=[[]]):
        super(ImageWidget, self).__init__(parent)
        self.background_enabled = True
        self.background_size = 64
        self.background_pass_shader = None
        self.background_pass_position = np.array([[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]])
        self.background_pass_texCoord = np.array([[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0]])

        self.img_data = img_data
        self.img_pass_shader = None
        self.img_texture = None
        self.img_pass_position = np.array([[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]])
        self.img_pass_texCoord = np.array([[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]])
        
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)

        vert_background_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_background_shader = compileShader(frag_background_src, GL_FRAGMENT_SHADER)
        self.background_pass_shader = compileProgram(vert_background_shader, frag_background_shader)

        vert_img_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_img_shader = compileShader(frag_img_src, GL_FRAGMENT_SHADER)
        self.img_pass_shader = compileProgram(vert_img_shader, frag_img_shader)

        self.img_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.img_texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        width = self.img_data.shape[1]
        height = self.img_data.shape[0]
        if width == 0 or height == 0:
            return
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.img_data)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)

        img_width = self.img_data.shape[1]
        img_height = self.img_data.shape[0]

        pixel_size = max(float(img_width) / width, float(img_height) / height)

        width_len = float(img_width) / (width * pixel_size)
        height_len = float(img_height) / (height * pixel_size)

        self.img_pass_position = np.array([[-width_len,-height_len],[width_len,-height_len],[width_len,height_len],[-width_len,height_len]])

    def drawBackground(self):
        uv_x_max = self.size().width() / self.background_size
        uv_y_max = self.size().height() / self.background_size

        self.background_pass_texCoord[1][0] = uv_x_max
        self.background_pass_texCoord[2][0] = uv_x_max
        self.background_pass_texCoord[2][1] = uv_y_max
        self.background_pass_texCoord[3][1] = uv_y_max

        glUseProgram(self.background_pass_shader)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, self.background_pass_position)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, self.background_pass_texCoord)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def drawIamge(self):
        glUseProgram(self.img_pass_shader)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.img_texture)
        glUniform1i(glGetUniformLocation(self.img_pass_shader, "textureSampler"), 0)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, self.img_pass_position)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, self.img_pass_texCoord)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)

        glDisable(GL_DEPTH_TEST)
        
        if self.background_enabled:
            self.drawBackground()

        self.drawIamge()

    def wheelEvent(self, event: QWheelEvent):
        ratio = 1.1 if event.angleDelta().y() > 0 else 1 / 1.1

        press_pixel_lb = np.array([event.x(), self.size().height()-event.y()],dtype=float)
        screen_size = np.array([self.size().width(), self.size().height()],dtype=float)
        press_uv = 2 * press_pixel_lb / screen_size + np.array([-1,-1],dtype=float)
        for i in range(0, 4):
            self.img_pass_position[i] = ratio * (self.img_pass_position[i] - press_uv) + press_uv

        self.repaint()

    def mousePressEvent(self, event: QMouseEvent):
        self.button = event.button()
        self.last_press_pixel = np.array([event.x(), event.y()],dtype=float)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        self.button = Qt.MouseButton.NoButton
        self.last_press_pixel = np.array([-1,-1],dtype=float)

    def mouseMoveEvent(self, event: QMouseEvent):
        now_press_pixel = np.array([event.x(), event.y()],dtype=float)
        pixel_move = now_press_pixel - self.last_press_pixel
        self.last_press_pixel = now_press_pixel

        if self.button == Qt.MouseButton.LeftButton:
            pixel_move[1] = -1 * pixel_move[1]
            screen_size = np.array([self.size().width(), self.size().height()],dtype=float)
            uv_move = 2 * pixel_move / screen_size
            self.img_pass_position = self.img_pass_position + uv_move

        self.repaint()
        
import sys
import cv2
import numpy as np
from PyQt5 import QtGui

if __name__ == '__main__':
    app = QApplication(sys.argv)

    image = cv2.imread("D:/jdc/life/photos/sony_a7/_DSC0763.JPG")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    widget = ImageWidget(None, image_rgb)

    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
