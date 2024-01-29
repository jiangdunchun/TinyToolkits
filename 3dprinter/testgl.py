from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image
import numpy as np
# from stl import mesh
# from pywavefront import Wavefront
#from pyassimp import *

# scene = load('cow.obj')
# mesh = scene.meshes[0]
# print(mesh.vertices[0])
# release(scene)

stencil_arr = bytearray(400 * 400)


vertices = []
indices = []
f = open("cow.obj")
line = f.readline()
while line:
    vs = line.split()
    if len(vs) == 4 and vs[0] == 'v':
        vertices.append([float(vs[1]),float(vs[2]),float(vs[3])])
    if len(vs) == 4 and vs[0] == 'f':
        indices.append([int(vs[1]),int(vs[2]),int(vs[3])])

    # if line.startswith('f'):
    line = f.readline()
f.close()

vertices = np.array(vertices)
indices = np.array(indices)

# obj = Wavefront('cow.obj')
# #mesh = mesh.Mesh.from_file("test.STEP")

aabb_min = np.array([np.finfo(np.float32).max, np.finfo(np.float32).max, np.finfo(np.float32).max])
aabb_max = np.array([np.finfo(np.float32).min, np.finfo(np.float32).min, np.finfo(np.float32).min])

for v in vertices:
    aabb_min[0] = min(aabb_min[0], v[0])
    aabb_min[1] = min(aabb_min[1], v[1])
    aabb_min[2] = min(aabb_min[2], v[2])
    aabb_max[0] = max(aabb_max[0], v[0])
    aabb_max[1] = max(aabb_max[1], v[1])
    aabb_max[2] = max(aabb_max[2], v[2])

sum = 100
index = 0

p_b = (aabb_min + aabb_max) / 2
p_b[2] = aabb_min[2]
p_a = (aabb_min + aabb_max) / 2
p_a[2] = aabb_max[2]

dx = np.array([(aabb_max[0] - aabb_min[0])/2, 0.0,0.0])
dy = np.array([0.0, (aabb_max[1] - aabb_min[1])/2,0.0])


def display():
    global sum
    global index
    p_z = (p_b * float(sum - index) + p_a * float(index)) / float(sum)
    p_m = (p_z + p_a) / 2
    dz = p_a - p_m
    print(p_m, dz)

    glDisable(GL_CULL_FACE)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_STENCIL_TEST)
    glStencilMask(0xFF)
    glStencilFunc(GL_ALWAYS, 1, 0xFF)
    #glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    glStencilOp(GL_KEEP, GL_KEEP, GL_INVERT)
    #glStencilOp(GL_INVERT, GL_INVERT, GL_INVERT)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT|GL_STENCIL_BUFFER_BIT)

    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_TRIANGLES)
    for t in indices:
        for i in t:
            v = vertices[i-1]
            v = v - p_m
            #print(v)
            v = np.array([np.dot(v,dx)/np.sqrt((dx*dx).sum()), np.dot(v,dy)/np.sqrt((dy*dy).sum()),np.dot(v,dz)/np.sqrt((dz*dz).sum()) ])
            #print(v[0],",", v[1],",",v[2])
            glVertex3f(v[0],v[1],v[2])
            if v[2] < -1.0 or v[2] > 1.0:
                print(v)
    #     print(" ")

    # glVertex3f(0.891067 , 0.7144076067891121 , 0.0)
    # glVertex3f(0.912855 , 0.73187600471735 , 0.0)
    # glVertex3f(1.0 , 0.8017439842224121 , 0.0)
    # glVertex3f(0.912855 , 0.73187600471735 , 0.0)
    # glVertex3f(0.886712 , 0.7109160117378235 , 0.0)
    # glVertex3f(0.891067 , 0.7144076067891121 , 0.0)

    # f = (0.912855 - 0.886712) / (0.886712 - 0.891067)
    # e = (0.73187600471735 - 0.7109160117378235) / (0.7109160117378235 - 0.7144076067891121)

    # glVertex3f(-1.0, -1.0, -1.0)
    # glVertex3f(1.0, -1.0, -1.0)
    # glVertex3f(1.0, 1.0, -1.0)
    glEnd()

    # glColor3f(1.0, 0.0, 0.0)
    # glBegin(GL_TRIANGLES)
    # glVertex3f(-0.8, -0.8, 0.5)
    # glVertex3f(0.8, -0.8, 0.5)
    # glVertex3f(0.8, 0.8, 0.5)
    # glVertex3f(-0.8, 0.8, 0.5)
    # glEnd()

    # glColor3f(0.0, 1.0, 0.0)
    # glBegin(GL_QUADS)
    # glVertex3f(-0.4, -0.4, 0.0)
    # glVertex3f(0.4, -0.4, 0.0)
    # glVertex3f(0.4, 0.4, 0.0)
    # glVertex3f(-0.4, 0.4, 0.0)
    # glEnd()

    # glColor3f(1.0, 0.0, 0.0)
    # glBegin(GL_TRIANGLES)
    # glVertex3f(-0.8, -0.8, -0.8)
    # glVertex3f(0.8, -0.8, -0.8)
    # glVertex3f(0.8, 0.8, -0.8)
    # glVertex3f(0.4, -0.4, 1.0)
    # glVertex3f(0.4, 0.4, 1.0)
    # glVertex3f(-0.4, 0.4, 1.0)
    # glVertex3f(0.1, 0.0, -0.5)
    # glVertex3f(0.2, 0.1, -0.5)
    # glVertex3f(0.2, -0.1, -0.5)
    # glEnd()

    glFlush()

    glReadPixels(0,0,400,400,GL_STENCIL_INDEX,GL_UNSIGNED_BYTE, stencil_arr)
    np_arr = np.frombuffer(stencil_arr,dtype=np.ubyte).reshape(400, 400)
    im = Image.fromarray(np_arr)
    im.save("./out/" + str(index) + ".jpg")

    index += 1
    index %= sum
    #print(index)

if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowSize(400, 400)
    glutCreateWindow("eastmount")

    glutDisplayFunc(display)
    glutIdleFunc(display)
    glutMainLoop()