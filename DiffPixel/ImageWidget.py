from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np

debug_print = False

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

frag_bg_src = """
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
    FragColor = texture(textureSampler, TexCoord);
}
"""

class ImageWidget(QOpenGLWidget):
    renderAreaChangedSignal = pyqtSignal(float, float, float, float)
    pixelSelectedSignal = pyqtSignal(int, int)

    def __init__(self, parent=None, img_data=np.array([[]])):
        super(ImageWidget, self).__init__(parent)
        self.bg_enabled = True
        self.bg_size = 64
        self.bg_pass_shader = None
        self.bg_pass_position = np.array([[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]])
        self.bg_pass_texCoord = np.array([[0.0,0.0],[1.0,0.0],[1.0,1.0],[0.0,1.0]])

        self.img_data = img_data
        self.img_pass_shader = None
        self.img_texture = None
        self.img_pass_position = np.array([[-1.0,-1.0],[1.0,-1.0],[1.0,1.0],[-1.0,1.0]])
        self.img_pass_texCoord = np.array([[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]])
        
    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)

        vert_bg_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_bg_shader = compileShader(frag_bg_src, GL_FRAGMENT_SHADER)
        self.bg_pass_shader = compileProgram(vert_bg_shader, frag_bg_shader)

        vert_img_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_img_shader = compileShader(frag_img_src, GL_FRAGMENT_SHADER)
        self.img_pass_shader = compileProgram(vert_img_shader, frag_img_shader)

        self.img_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.img_texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        img_width = self.img_data.shape[1]
        img_height = self.img_data.shape[0]
        if img_width == 0 or img_height == 0:
            return
        if len(self.img_data.shape) == 3:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_width, img_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.img_data)
        if len(self.img_data.shape) == 2:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, img_width, img_height, 0, GL_RED, GL_FLOAT, self.img_data)

    def resizeGL(self, canvas_width, canvas_height):
        img_width = self.img_data.shape[1]
        img_height = self.img_data.shape[0]

        ratio = max(float(img_width) / canvas_width, float(img_height) / canvas_height)

        w = float(img_width) / (canvas_width * ratio)
        h = float(img_height) / (canvas_height * ratio)

        self.img_pass_position = np.array([[-w,-h],[w,-h],[w,h],[-w,h]])

        glViewport(0, 0, canvas_width, canvas_height)

    def drawbg(self):
        canvas_width = self.size().width()
        canvas_height = self.size().height()

        w = canvas_width / self.bg_size
        h = canvas_height / self.bg_size

        self.bg_pass_texCoord[1][0] = w
        self.bg_pass_texCoord[2][0] = w
        self.bg_pass_texCoord[2][1] = h
        self.bg_pass_texCoord[3][1] = h

        glUseProgram(self.bg_pass_shader)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, self.bg_pass_position)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, self.bg_pass_texCoord)
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
        
        if self.bg_enabled:
            self.drawbg()

        self.drawIamge()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        mouse_x = event.x()
        mouse_y = event.y()
        canvas_width = self.size().width()
        canvas_height = self.size().height()
        
        ratio = 1.1 if delta > 0 else 1 / 1.1

        press_pixel = np.array([mouse_x, canvas_height-mouse_y],dtype=float)
        canvas_size = np.array([canvas_width, canvas_height],dtype=float)
        press_uv = 2 * press_pixel / canvas_size + np.array([-1,-1],dtype=float)
        img_pass_position = ratio * (self.img_pass_position - press_uv) + press_uv

        if debug_print:
            print("renderAreaChangedSignal: ",img_pass_position[0][0], img_pass_position[0][1], img_pass_position[2][0], img_pass_position[2][1])
        self.renderAreaChangedSignal.emit(img_pass_position[0][0], img_pass_position[0][1], img_pass_position[2][0], img_pass_position[2][1])
        self.renderAreaChanged(img_pass_position[0][0], img_pass_position[0][1], img_pass_position[2][0], img_pass_position[2][1])

    def mousePressEvent(self, event: QMouseEvent):
        mouse_x = event.x()
        mouse_y = event.y()

        self.button = event.button()
        self.last_press_pixel = np.array([mouse_x, mouse_y],dtype=float)

        if self.button == Qt.MouseButton.RightButton:
            canvas_size = np.array([self.size().width(), self.size().height()],dtype=float)
            press_pos = 2 * self.last_press_pixel / canvas_size - np.array([1,1],dtype=float)
            press_pos[1] = -press_pos[1]
            selected_uv = (press_pos - self.img_pass_position[0]) / (self.img_pass_position[2] - self.img_pass_position[0])
            selected_uv[1] = 1.0 - selected_uv[1]
            if selected_uv[0] >= 0.0 and selected_uv[0] <= 1.0 and selected_uv[1] >= 0.0 and selected_uv[1] <= 1.0:
                width = self.img_data.shape[1]
                height = self.img_data.shape[0]
                img_size = np.array([width,height],dtype=float)
                press_tex = selected_uv * img_size

                if debug_print:
                    print("pixelSelectedSignal:", int(press_tex[1]), int(press_tex[0]))
                self.pixelSelectedSignal.emit(int(press_tex[1]), int(press_tex[0]))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.button = Qt.MouseButton.NoButton
        self.last_press_pixel = np.array([-1,-1],dtype=float)

    def mouseMoveEvent(self, event: QMouseEvent):
        mouse_x = event.x()
        mouse_y = event.y()
    
        now_press_pixel = np.array([mouse_x, mouse_y],dtype=float)
        pixel_move = now_press_pixel - self.last_press_pixel
        self.last_press_pixel = now_press_pixel

        if self.button == Qt.MouseButton.LeftButton:
            pixel_move[1] = -1 * pixel_move[1]
            canvas_size = np.array([self.size().width(), self.size().height()],dtype=float)
            uv_move = 2 * pixel_move / canvas_size
            img_pass_position = self.img_pass_position + uv_move

            if debug_print:
                print("renderAreaChangedSignal:",img_pass_position[0][0], img_pass_position[0][1], img_pass_position[2][0], img_pass_position[2][1])
            self.renderAreaChangedSignal.emit(img_pass_position[0][0], img_pass_position[0][1], img_pass_position[2][0], img_pass_position[2][1])
            self.renderAreaChanged(img_pass_position[0][0], img_pass_position[0][1], img_pass_position[2][0], img_pass_position[2][1])
    
    def renderAreaChanged(self, x0, y0, x1, y1):
        self.img_pass_position = np.array([[x0,y0],[x1,y0],[x1,y1],[x0,y1]])
        self.repaint()

    # shape=[width,height,3],dtype='uint8'
    def SetImgData(self, img_data=np.empty([0,0,3],dtype='uint8')):
        self.img_data = img_data
        self.has_img_data = True
        if img_data.shape[0] == 0 or img_data.shape[1] == 0:
            self.has_img_data = False
        self.repaint()

    # shape=[width,height],dtype='float'
    def SetDiffData(self, diff_data=np.empty([0,0],dtype='float')):
        self.img_data = diff_data
        self.has_diff_data = True
        if diff_data.shape[0] == 0 or diff_data.shape[1] == 0:
            self.has_diff_data = False
        self.repaint()
    
    def SetDiffDataRange(self, lower, upper):
        self.diff_data_range = np.array([0,1],dtype='float')
        if self.has_diff_data:
            self.repaint()

    def SetRenderArea(self, x0, y0, x1, y1):
        self.img_pass_position = np.array([[x0,y0],[x1,y0],[x1,y1],[x0,y1]])
        self.repaint()

import sys
import cv2

if __name__ == '__main__':
    debug_print = True

    app = QApplication(sys.argv)

    image = cv2.imread("./test/original/1.png")
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    widget = ImageWidget(None, image_rgb)

    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
