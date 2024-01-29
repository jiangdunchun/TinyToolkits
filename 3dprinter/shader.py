import numpy as np
from OpenGL.GLUT import *
from OpenGL.GL import *
import ctypes
from PIL import Image
#顶点着色器部分
VERTEX_SHADER = """
#version 330

layout (location = 0) in vec3 Position;

uniform vec3 center;
uniform vec3 dx;
uniform vec3 dy;
uniform vec3 dz;

void main()
{
    gl_Position = vec4(0.5 * Position.x, 0.5 * Position.y, Position.z, 1.0);
    }
"""
#片段着色器部分,字符串类型
FRAGMENT_SHADER = """
#version 330
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
"""
def Create_Shader( ShaderProgram, Shader_Type , Source):  #创建并且添加着色器（相当于AddShader）Shader_Type为类型
    ShaderObj = glCreateShader( Shader_Type )  #创建Shader对象
    glShaderSource(ShaderObj , Source)
    glCompileShader(ShaderObj)  #进行编译
    glAttachShader(ShaderProgram, ShaderObj)  #将着色器对象关联到程序上


def Compile_Shader():  #编译着色器
    Shader_Program = glCreateProgram()  #创建空的着色器程序
    Create_Shader(Shader_Program , GL_VERTEX_SHADER , VERTEX_SHADER)
    Create_Shader(Shader_Program , GL_FRAGMENT_SHADER , FRAGMENT_SHADER)
    glLinkProgram(Shader_Program)
    glUseProgram(Shader_Program)

stencil_arr = bytearray(500 * 500)
sum = 100
index = 0

def Draw():
    global sum
    global index

    glDisable(GL_DEPTH_TEST)
    glEnable(GL_STENCIL_TEST)
    glStencilMask(0xFF)
    glStencilFunc(GL_ALWAYS, 1, 0xFF)
    glStencilOp(GL_KEEP, GL_KEEP, GL_INVERT)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)

    glBindVertexArray(VAO)
    glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, None)
    glutSwapBuffers()

    glReadPixels(0,0,500,500,GL_STENCIL_INDEX,GL_UNSIGNED_BYTE, stencil_arr)
    np_arr = np.frombuffer(stencil_arr,dtype=np.ubyte).reshape(500, 500)
    im = Image.fromarray(np_arr)
    im.save("./shadero/" + str(index) + ".jpg")

    index += 1
    index %= sum
    print(index)


vertices = np.array([[-1.0,-1.0,0.0],
                    [1.0,-1.0,0.0],
                    [0.0,1.0,0.0]],np.float32)

indices = np.array([0,1,2],np.int32)

def CreateBuffer():  #创建顶点缓存器
    global VBO, VAO, EBO
    VAO = glGenVertexArrays(1,)
    VBO = glGenBuffers(1)
    EBO = glGenBuffers(1)

    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0,None) 
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)


def main():
    glutInit([])
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)  # 显示模式 双缓存
    glutInitWindowPosition(100, 100)  # 窗口位置
    glutInitWindowSize(500, 500)  # 窗口大小
    glutCreateWindow("sanjiao")  # 创建窗口
    glutInitContextVersion(4,3)   #为了兼容
    glutInitContextProfile(GLUT_CORE_PROFILE)   #为了兼容
    glutDisplayFunc(Draw)  # 回调函数
    glClearColor(0.0, 0.0, 0.0, 0.0)
    CreateBuffer()
    Compile_Shader()
    glutMainLoop()

main()