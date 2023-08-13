from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QImage, QPixmap
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shader_program = None
        self.vbo = None
        self.vao = None
        self.texture = None

    def initializeGL(self):
        # Initialize OpenGL state and resources

        glClearColor(0.0, 0.0, 0.0, 1.0)  # Set the clear color to black

        # Create and compile the shaders
        vertex_shader = """
        #version 330
        layout (location = 0) in vec2 position;
        layout (location = 1) in vec2 texCoord;

        out vec2 fragTexCoord;

        void main()
        {
            gl_Position = vec4(position, 0.0, 1.0);
            fragTexCoord = texCoord;
        }
        """

        fragment_shader = """
        #version 330
        in vec2 fragTexCoord;

        uniform sampler2D textureSampler;

        void main()
        {
            gl_FragColor = texture(textureSampler, fragTexCoord);
        }
        """

        vertex_shader = compileShader(vertex_shader, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader, GL_FRAGMENT_SHADER)

        # Create the shader program and link the shaders
        self.shader_program = compileProgram(vertex_shader, fragment_shader)

        # Create a vertex buffer object (VBO) to store the vertex data
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        vertices = [-1.0, -1.0, 0.0, 0.0,
                    1.0, -1.0, 1.0, 0.0,
                    1.0, 1.0, 1.0, 1.0,
                    -1.0, 1.0, 0.0, 1.0]

        glBufferData(GL_ARRAY_BUFFER, 64, (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)

        # Create a vertex array object (VAO) to store the vertex attribute bindings
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Specify the vertex attribute layouts
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glEnableVertexAttribArray(1)

        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Load the texture
        self.load_texture()

    def load_texture(self):
        image = QImage("D:/jdc/life/photos/sony_a7/_DSC0763.JPG")
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, image.constBits())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

    def resizeGL(self, width, height):
        # Handle widget resize event

        glViewport(0, 0, width, height)

    def paintGL(self):
        # Render the scene

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Use the shader program
        glUseProgram(self.shader_program)

        # Bind the vertex array object (VAO)
        glBindVertexArray(self.vao)

        # Activate and bind the texture
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(glGetUniformLocation(self.shader_program, "textureSampler"), 0)

        # Draw the vertices
        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

        # Unbind the vertex array object (VAO), texture, and shader program
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

from PyQt5.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("OpenGL Shader Texture Example")
        
        # Create an instance of MyOpenGLWidget
        self.opengl_widget = MyOpenGLWidget(self)
        self.setCentralWidget(self.opengl_widget)


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()