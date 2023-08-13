from OpenGL.GL import *

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if status != GL_TRUE:
        error_message = glGetShaderInfoLog(shader)
        raise RuntimeError(f"Shader compilation failed: {error_message}")

    return shader

def create_shader_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    
    glLinkProgram(shader_program)
    
    # Check for linking errors
    status = glGetProgramiv(shader_program, GL_LINK_STATUS)
    if status != GL_TRUE:
        error_message = glGetProgramInfoLog(shader_program)
        raise RuntimeError(f"Shader program linking failed: {error_message}")
    
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return shader_program