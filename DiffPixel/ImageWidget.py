from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
import cv2

debug_print = False

vert_src = '''
#version 330 core

layout (location = 0) in vec2 position;
layout (location = 1) in vec2 texCoord;

out vec2 TexCoord;

void main()
{
    gl_Position = vec4(position, 0.0, 1.0);
    TexCoord = texCoord;
}
'''
frag_null_src = '''
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D NUllTexture;

void main()
{
    FragColor = texture(NUllTexture, TexCoord);
}
'''
frag_bg_src = '''
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

void main()
{
    float uv_x = (TexCoord.x - int(TexCoord.x)) - 0.5;
    float uv_y = (TexCoord.y - int(TexCoord.y)) - 0.5;

    if (uv_x * uv_y <= 0.0)
        FragColor = vec4(0.25,0.25,0.25,1.0);
    else
        FragColor = vec4(0.75,0.75,0.75,1.0);

}
'''
frag_img_src = '''
#version 330 core

in vec2 TexCoord;
out vec4 FragColor;

uniform sampler2D ImgTexture;
uniform bool IsDiff;
uniform float DiffMax;
uniform float DiffMin;

void main()
{
    if (!IsDiff) 
    {
        FragColor = texture(ImgTexture, TexCoord);
    }
    else
    {
        float diff = texture(ImgTexture, TexCoord).r;
        diff = (diff - DiffMin) / (DiffMax - DiffMin);
        diff = clamp(diff, 0.0, 1.0);

        FragColor = diff * vec4(1.0,0.0,0.0,1.0) + (1.0 - diff) * vec4(1.0,1.0,1.0,1.0);
    }
}
'''
null_texture_path = './asset/null.png'
full_screen_position = np.array([[-1.0,1.0],[-1.0,-1.0],[1.0,-1.0],[1.0,1.0]],dtype=float)
full_texture_texCoord = np.array([[0.0,0.0],[0.0,1.0],[1.0,1.0],[1.0,0.0]],dtype=float)

class ImageWidget(QOpenGLWidget):
    RenderAreaChangedSignal = pyqtSignal(list)
    PixelSelectedSignal = pyqtSignal(list)
    ImgLoadedSignal = pyqtSignal()

    def __init__(self, parent=None, enable_null=True):
        super(ImageWidget, self).__init__(parent)
        self.enable_null = enable_null
        self.null_texture_size = np.array([0,0])
        self.null_texture = None
        self.null_pass_shader = None
        self.null_pass_texCoord = full_texture_texCoord

        if self.enable_null:
            self.setAcceptDrops(True)

        self.bg_size = 64
        self.bg_pass_shader = None
        self.bg_pass_texCoord = full_texture_texCoord

        self.has_img = False
        self.is_diff = False
        self.diff_max = 1.0
        self.diff_min = 0.0
        self.img_texture_data = np.empty([0,0,3],dtype='uint8')
        self.img_texture = None
        self.img_pass_shader = None
        self.img_pass_position = full_screen_position

    def initializeGL(self):
        self.null_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.null_texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        null_texture = cv2.imread(null_texture_path)
        null_texture = cv2.cvtColor(null_texture, cv2.COLOR_BGR2RGB)
        self.null_texture_size = np.array([null_texture.shape[1], null_texture.shape[0]])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.null_texture_size[0], self.null_texture_size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, null_texture)

        vert_null_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_null_shader = compileShader(frag_null_src, GL_FRAGMENT_SHADER)
        self.null_pass_shader = compileProgram(vert_null_shader, frag_null_shader)


        vert_bg_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_bg_shader = compileShader(frag_bg_src, GL_FRAGMENT_SHADER)
        self.bg_pass_shader = compileProgram(vert_bg_shader, frag_bg_shader)


        self.img_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.img_texture)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        vert_img_shader = compileShader(vert_src, GL_VERTEX_SHADER)
        frag_img_shader = compileShader(frag_img_src, GL_FRAGMENT_SHADER)
        self.img_pass_shader = compileProgram(vert_img_shader, frag_img_shader)

    def resizeGL(self, canvas_width, canvas_height):
        glViewport(0, 0, canvas_width, canvas_height)

        canvas_size = np.array([canvas_width, canvas_height],dtype=float)

        self.null_pass_texCoord = (canvas_size / canvas_size.min()) * (full_texture_texCoord - 0.5) + 0.5

        self.bg_pass_texCoord = (canvas_size / self.bg_size) * full_texture_texCoord

        if self.has_img:
            self.initImgPassPosition()

    def drawNull(self):
        glUseProgram(self.null_pass_shader)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.null_texture)
        glUniform1i(glGetUniformLocation(self.null_pass_shader, 'NUllTexture'), 0)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, full_screen_position)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, self.null_pass_texCoord)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def drawBg(self):
        glUseProgram(self.bg_pass_shader)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, full_screen_position)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, self.bg_pass_texCoord)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def drawImg(self):
        glUseProgram(self.img_pass_shader)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.img_texture)
        glUniform1i(glGetUniformLocation(self.img_pass_shader, 'ImgTexture'), 0)
        glUniform1i(glGetUniformLocation(self.img_pass_shader, 'IsDiff'), self.is_diff)
        glUniform1f(glGetUniformLocation(self.img_pass_shader, 'DiffMax'), self.diff_max)
        glUniform1f(glGetUniformLocation(self.img_pass_shader, 'DiffMin'), self.diff_min)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8, self.img_pass_position)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8, full_texture_texCoord)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glDisable(GL_DEPTH_TEST)
        
        if self.enable_null and not self.has_img:
            self.drawNull()
        else:
            self.drawBg()

        if self.has_img:
            self.drawImg()

    def loadFile(self, path):
        if not self.enable_null:
            return True
        
        img_texture = cv2.imread(path)
        if img_texture is None:
            msg_box = QMessageBox(QMessageBox.Warning, 'Error', 'Not a image file!')
            msg_box.exec_()
            return False
        
        img_texture = cv2.cvtColor(img_texture, cv2.COLOR_BGR2RGB)
        self.SetImgData(img_texture)
        if debug_print:
            print('ImgLoadedSignal:')
        self.ImgLoadedSignal.emit()
        
        return True

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        if not self.has_img:
            return
        
        ratio = 1.1 if delta > 0 else 1 / 1.1
        canvas_size = np.array([self.size().width(), self.size().height()],dtype=float)
        press_pixel = np.array([event.x(), canvas_size[1]-event.y()],dtype=float)
        
        press_uv = 2 * press_pixel / canvas_size - 1
        new_position = ratio * (self.img_pass_position - press_uv) + press_uv
        if new_position[:,0].max() - new_position[:,0].min() < 1.0 and new_position[:,1].max() - new_position[:,1].min() < 1.0:
            return 
        self.img_pass_position = new_position

        if debug_print:
            print('RenderAreaChangedSignal: ',self.img_pass_position.tolist())
        self.RenderAreaChangedSignal.emit(self.img_pass_position.tolist())
        self.repaint()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        path_list = event.mimeData().text()
        path = path_list.split('\n')[0]
        path = path.replace('file:///', '', 1)
        self.loadFile(path)

    def mousePressEvent(self, event: QMouseEvent):
        self.button = event.button()
        self.last_press_pixel = np.array([event.x(), event.y()],dtype=float)

        if not self.has_img:
            if self.enable_null and self.button == Qt.MouseButton.LeftButton:
                path,_ = QFileDialog.getOpenFileName(self, 'Open File', './', 'Image Files(*.jpg *.png)')
                self.loadFile(path)
            return
        
        if self.button == Qt.MouseButton.RightButton:
            canvas_size = np.array([self.size().width(), self.size().height()],dtype=float)
            press_pos = 2 * self.last_press_pixel / canvas_size - 1
            press_pos[1] = -press_pos[1]
            selected_uv = (press_pos - self.img_pass_position[0]) / (self.img_pass_position[2] - self.img_pass_position[0])
            selected_uv[1] = selected_uv[1]
            if selected_uv[0] >= 0.0 and selected_uv[0] <= 1.0 and selected_uv[1] >= 0.0 and selected_uv[1] <= 1.0:
                img_size = np.array([self.img_texture_data.shape[1], self.img_texture_data.shape[0]],dtype=float)
                press_tex = selected_uv * img_size
                press_tex = press_tex.astype(int)

                if debug_print:
                    print('PixelSelectedSignal: ', press_tex.tolist(), ',pixel color:', self.GetPixelData(press_tex[0], press_tex[1]))
                self.PixelSelectedSignal.emit(press_tex.tolist())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.button = Qt.MouseButton.NoButton
        self.last_press_pixel = np.array([-1,-1],dtype=float)        
        
    def mouseMoveEvent(self, event: QMouseEvent):
        now_press_pixel = np.array([event.x(), event.y()],dtype=float)
        pixel_move = now_press_pixel - self.last_press_pixel
        self.last_press_pixel = now_press_pixel

        if not self.has_img:
            return

        if self.button == Qt.MouseButton.LeftButton:
            pixel_move[1] = -1 * pixel_move[1]
            canvas_size = np.array([self.size().width(), self.size().height()],dtype=float)
            uv_move = 2 * pixel_move / canvas_size
            new_position = self.img_pass_position + uv_move
            # if new_position[:,0].max() * new_position[:,0].min() > 0.0 or new_position[:,1].max() * new_position[:,1].min() > 0.0:
            #     return 
            self.img_pass_position = new_position

            if debug_print:
                print('RenderAreaChangedSignal: ',self.img_pass_position.tolist())
            self.RenderAreaChangedSignal.emit(self.img_pass_position.tolist())
            self.repaint()
    
    def initImgPassPosition(self):
        img_size = np.array([self.img_texture_data.shape[1], self.img_texture_data.shape[0]],dtype=float)
        canvas_size = np.array([self.size().width(), self.size().height()],dtype=float)

        ratio = img_size / canvas_size
        ratio = ratio / ratio.max()

        self.img_pass_position = ratio * full_screen_position

        if debug_print:
                print('RenderAreaChangedSignal: ',self.img_pass_position.tolist())
        self.RenderAreaChangedSignal.emit(self.img_pass_position.tolist())
        self.repaint()

    # shape=[width,height,3],dtype='uint8' for img, shape=[width,height],dtype='float' for diff
    def SetImgData(self, img_data=np.empty([0,0,3],dtype='uint8')):
        self.img_texture_data = img_data
        img_size = np.array([self.img_texture_data.shape[1], self.img_texture_data.shape[0]])

        self.has_img = True
        if img_size[0] == 0 or img_size[1] == 0:
            self.has_img = False
            return

        self.is_diff = False
        if len(self.img_texture_data.shape) == 2:
            self.is_diff = True

        glBindTexture(GL_TEXTURE_2D, self.img_texture)
        if self.is_diff:
            self.diff_max = 1.0
            self.diff_min = 0.0
            diff_max = self.img_texture_data.max()
            diff_min = self.img_texture_data.min()
            normalized_texture_data = (self.img_texture_data - diff_min) / (diff_max - diff_min)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, img_size[0], img_size[1], 0, GL_RED, GL_FLOAT, normalized_texture_data)
        else:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img_size[0], img_size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, self.img_texture_data)

        self.initImgPassPosition()
        self.repaint()

    def SetDiffDataRange(self, lower, upper):
        if self.has_img and self.is_diff:
            diff_max = self.img_texture_data.max()
            diff_min = self.img_texture_data.min()
            self.diff_max = (upper - diff_min) / (diff_max - diff_min)
            self.diff_min = (lower - diff_min) / (diff_max - diff_min)
            self.repaint()

    def SetRenderArea(self, render_area):
        if not self.has_img:
            return
        
        self.img_pass_position = render_area
        self.repaint()

    def HasImg(self):
        return self.has_img

    def GetImgData(self):
        return self.img_texture_data
    
    def GetPixelData(self, x, y):
        return self.img_texture_data[y][x]

import sys
import cv2

if __name__ == '__main__':
    debug_print = True

    app = QApplication(sys.argv)

    widget = ImageWidget(None, True)

    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
