import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import OpenGL.GLU
import OpenGL.GLUT
import numpy as np
import pyrr
import math
from pyrr import matrix44
from ObjLoader import ObjLoader
import random
from TextureLoader import load_texture

vertex_src = """
# version 330

layout(location = 0) in vec3 a_position;
layout(location = 1) in vec2 a_texture;
layout(location = 2) in vec3 a_normal;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec2 v_texture;

void main()
{
    gl_Position = projection * view * model * vec4(a_position, 1.0);
    v_texture = a_texture;
}
"""

fragment_src = """
# version 330

in vec2 v_texture;

out vec4 out_color;

uniform sampler2D s_texture;

void main()
{
    out_color = texture(s_texture, v_texture);
    //out_color = vec4(1, 0, 0, 1)
}
"""


def processInput(window):
    if(glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS):
        glfw.set_window_should_close(window, glfw.TRUE)
    if(glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
        cam[0] = cam[0]-(math.pi/1500)
    if(glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
        cam[0] = cam[0]+(math.pi/1500)
    if(glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS):
        if (cam[1] <= (math.pi/3)):
            cam[1] = cam[1]+(math.pi/1500)
    if(glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS):
        if (cam[1] >= -(math.pi/3)):
            cam[1] = cam[1]-(math.pi/1500)
    if(glfw.get_key(window, glfw.KEY_W) == glfw.PRESS):
        if (cam[2] >= 5):
            cam[2] = cam[2]-0.01
    if(glfw.get_key(window, glfw.KEY_S) == glfw.PRESS):
        if (cam[2] <= 40):
            cam[2] = cam[2]+0.01
    if(glfw.get_key(window, glfw.KEY_ENTER) == glfw.PRESS):
        global generate_sphere
        generate_sphere = 50


def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(
        45, width / height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


generate_sphere = 0
extra_sphere_count = 0

# initializing glfw library
if not glfw.init():
    raise Exception("glfw can not be initialized!")

# creating the window
window = glfw.create_window(1920, 1080, "Molecule Visualiser", None, None)

# check if window was created
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

# set window's position
glfw.set_window_pos(window, 0, 0)

# set the callback function for window resize
glfw.set_window_size_callback(window, window_resize)

# make the context current
glfw.make_context_current(window)

lightPos = [25, 25, 25]

cam = [(math.pi/4), (math.pi/4), 20]

wSphereI, wSphereB = ObjLoader.load_model("sphere.obj")
print(wSphereB[0])
print(wSphereB[1])
print(wSphereB[2])
print(wSphereB[3])
print(wSphereB[4])
print(wSphereB[5])
print(wSphereB[6])
print(wSphereB[7])
print(wSphereB[8])
floorI, floorB = ObjLoader.load_model("floor.obj")

shader = compileProgram(compileShader(
    vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

# VAO and VBO
VAO = glGenVertexArrays(100)
VBO = glGenBuffers(100)
VIndex = 0

for i in range(10):
    # Sphere VAO
    glBindVertexArray(VAO[i])
    # Sphere Vertex Buffer Object
    glBindBuffer(GL_ARRAY_BUFFER, VBO[i])
    glBufferData(GL_ARRAY_BUFFER, wSphereB.nbytes,
                 wSphereB, GL_STATIC_DRAW)
    # Sphere vertices
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                          wSphereB.itemsize * 8, ctypes.c_void_p(0))
    # Sphere textures
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                          wSphereB.itemsize * 8, ctypes.c_void_p(12))
    # Sphere normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                          wSphereB.itemsize * 8, ctypes.c_void_p(20))
    glEnableVertexAttribArray(2)
    VIndex += 1

for i in range(94, 100):
    glBindVertexArray(VAO[i])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[i])
    glBufferData(GL_ARRAY_BUFFER, floorB.nbytes,
                 floorB, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                          floorB.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                          floorB.itemsize * 8, ctypes.c_void_p(12))
    # Sphere normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                          floorB.itemsize * 8, ctypes.c_void_p(20))
    glEnableVertexAttribArray(2)

textures = glGenTextures(5)
load_texture("Red.jpg", textures[0])
load_texture("White.jpg", textures[1])
load_texture("LGrey.jpg", textures[2])
load_texture("DGrey.jpg", textures[3])
load_texture("Grid2.png", textures[4])

glUseProgram(shader)
glClearColor(0.8, 0.8, 0.8, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

sphere_pos = []
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([0, 0, 0])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([-5, -5, -5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([-5, -5, 5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([-5, 5, -5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([-5, 5, 5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([5, -5, -5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([5, -5, 5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([5, 5, -5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([5, 5, 5])))
sphere_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([0, 0, 0])))

sphere_scale = []
for i in range(9):
    sphere_scale.append(pyrr.matrix44.create_from_scale(
        pyrr.Vector3([0.1, 0.1, 0.1])))
sphere_scale.append(pyrr.matrix44.create_from_scale(
    pyrr.Vector3([0.2, 0.2, 0.2])))

sphere_trans = []
for i in range(9):
    sphere_trans.append(pyrr.matrix44.create_identity)
sphere_trans.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001])))

# 7df2ff
# fa87c4
# ffffff
# fa87c4
# 7df2ff

side_pos = []
side_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([0, -5, 0])))
side_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([0, 5, 0])))
side_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([-5, 0, 0])))
side_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([5, 0, 0])))
side_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([0, 0, -5])))
side_pos.append(pyrr.matrix44.create_from_translation(
    pyrr.Vector3([0, 0, 5])))

side_rotate = []
side_rotate.append(pyrr.matrix44.create_identity())
side_rotate.append(pyrr.matrix44.create_from_x_rotation(np.pi))
side_rotate.append(pyrr.matrix44.create_from_z_rotation(np.pi/2))
side_rotate.append(pyrr.matrix44.create_from_z_rotation((np.pi/2)*3))
side_rotate.append(pyrr.matrix44.create_from_x_rotation(np.pi/2))
side_rotate.append(pyrr.matrix44.create_from_x_rotation((np.pi/2)*3))

side_scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([0.2, 0.2, 0.2]))

projection = pyrr.matrix44.create_perspective_projection_matrix(
    45, 1920/1080, 0.1, 100)
view = pyrr.matrix44.create_look_at(pyrr.Vector3(
    [0, 10, 0]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)


# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    processInput(window)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camPos2D = [math.sin(cam[0]) * cam[2], math.cos(cam[0]) * cam[2]]
    camPosY = math.sin(cam[1]) * cam[2]
    camPosX = camPos2D[0]*math.cos(cam[1])
    camPosZ = camPos2D[1]*math.cos(cam[1])

    view = pyrr.matrix44.create_look_at(pyrr.Vector3([camPosX, camPosY, camPosZ]), pyrr.Vector3([0.0, 0.0, 0.0]),
                                        pyrr.Vector3([0.0, 1.0, 0.0]))

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    if generate_sphere > 1:
        generate_sphere -= 1
        if generate_sphere == 1:
            # generate_sphere()
            # Sphere VAO
            glBindVertexArray(VAO[VIndex])
            # Sphere Vertex Buffer Object
            glBindBuffer(GL_ARRAY_BUFFER, VBO[VIndex])
            glBufferData(GL_ARRAY_BUFFER, wSphereB.nbytes,
                         wSphereB, GL_STATIC_DRAW)
            # Sphere vertices
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                                  wSphereB.itemsize * 8, ctypes.c_void_p(0))
            # Sphere textures
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                                  wSphereB.itemsize * 8, ctypes.c_void_p(12))
            # Sphere normals
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                                  wSphereB.itemsize * 8, ctypes.c_void_p(20))
            glEnableVertexAttribArray(2)
            VIndex += 1
            sphere_pos.append(pyrr.matrix44.create_from_translation(
                pyrr.Vector3([0, 0, 0])))
            sphere_scale.append(pyrr.matrix44.create_from_scale(
                pyrr.Vector3([0.2, 0.2, 0.2])))
            sphere_trans.append(pyrr.matrix44.create_from_translation(
                pyrr.Vector3([random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001])))
            generate_sphere -= 1

    for i in range(len(sphere_pos)):
        model = pyrr.matrix44.multiply(sphere_scale[i], sphere_pos[i])
        glBindVertexArray(VAO[i])
        glBindTexture(GL_TEXTURE_2D, textures[0])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glDrawArrays(GL_TRIANGLES, 0, len(wSphereI))

    indexNo = 94
    if camPosY < 0:
        indexNo += 1

    temp = pyrr.matrix44.multiply(side_scale, side_rotate[indexNo-94])
    model = pyrr.matrix44.multiply(temp, side_pos[indexNo-94])
    glBindVertexArray(VAO[indexNo])
    glBindTexture(GL_TEXTURE_2D, textures[4])
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, len(floorI))

    indexNo = 96
    if camPosX < 0:
        indexNo += 1

    temp = pyrr.matrix44.multiply(side_scale, side_rotate[indexNo-94])
    model = pyrr.matrix44.multiply(temp, side_pos[indexNo-94])
    glBindVertexArray(VAO[indexNo])
    glBindTexture(GL_TEXTURE_2D, textures[4])
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, len(floorI))

    indexNo = 98
    if camPosZ < 0:
        indexNo += 1

    temp = pyrr.matrix44.multiply(side_scale, side_rotate[indexNo-94])
    model = pyrr.matrix44.multiply(temp, side_pos[indexNo-94])
    glBindVertexArray(VAO[indexNo])
    glBindTexture(GL_TEXTURE_2D, textures[4])
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, len(floorI))

    for i in range(9, len(sphere_pos)):
        sphere_pos[i] = pyrr.matrix44.multiply(sphere_trans[i], sphere_pos[i])
        for j in range(3):
            if sphere_pos[i][3][j] >= 5:
                sphere_pos[i][3][j] = 5
                sphere_trans[i] = pyrr.matrix44.create_from_translation(
                    pyrr.Vector3([random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001]))
            if sphere_pos[i][3][j] <= -5:
                sphere_pos[i][3][j] = -5
                sphere_trans[i] = pyrr.matrix44.create_from_translation(
                    pyrr.Vector3([random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001]))

    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()
