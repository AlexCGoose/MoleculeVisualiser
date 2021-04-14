from io import BufferedRandom
import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import OpenGL.GLU
import OpenGL.GLUT
import numpy as np
import pyrr
import math
from ObjLoader import ObjLoader
import random
from TextureLoader import load_texture
import Object

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
    global generate_sphere
    global atom_to_make
    global make_a_molecule
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


def window_resize(window, width, height):
    glViewport(0, 0, width, height)
    projection = pyrr.matrix44.create_perspective_projection_matrix(
        45, width / height, 0.1, 100)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)


def key_callback(window, key, scancode, action, mods):
    global atom_to_make, make_a_molecule
    if(glfw.get_key(window, glfw.KEY_H) == glfw.PRESS):
        atom_to_make = 0
    if(glfw.get_key(window, glfw.KEY_O) == glfw.PRESS):
        atom_to_make = 1
    if(glfw.get_key(window, glfw.KEY_M) == glfw.PRESS):
        make_a_molecule = 1


def bindArrays(buffer):
    global VAO, VBO, VIndex
    glBindVertexArray(VAO[VIndex])
    glBindBuffer(GL_ARRAY_BUFFER, VBO[VIndex])
    glBufferData(GL_ARRAY_BUFFER, buffer.nbytes,
                 buffer, GL_STATIC_DRAW)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                          buffer.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                          buffer.itemsize * 8, ctypes.c_void_p(12))
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                          buffer.itemsize * 8, ctypes.c_void_p(20))
    glEnableVertexAttribArray(2)
    VIndex += 1
    return VIndex-1


def drawObject(indexNo, texture, model, faceNo):
    global VAO, model_loc
    glBindVertexArray(VAO[indexNo])
    glBindTexture(GL_TEXTURE_2D, texture)
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
    glDrawArrays(GL_TRIANGLES, 0, faceNo)


generate_sphere = 0
atom_to_make = -1
make_a_molecule = 0

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

glfw.set_key_callback(window, key_callback)

textures = glGenTextures(6)
load_texture("White.jpg", textures[0])
load_texture("Red.jpg", textures[1])
load_texture("LGrey.jpg", textures[2])
load_texture("DGrey.jpg", textures[3])
load_texture("Grid2.png", textures[4])
load_texture("Black.jpg", textures[5])

sphereI, sphereB = ObjLoader.load_model("sphere.obj")
floorI, floorB = ObjLoader.load_model("floor.obj")
barI, barB = ObjLoader.load_model("cube.obj")

shader = compileProgram(compileShader(
    vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))

glUseProgram(shader)
glClearColor(0.8, 0.8, 0.8, 1)
glEnable(GL_DEPTH_TEST)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

objectList = []

lightPos = [25, 25, 25]

cam = [(math.pi/4), (math.pi/4), 20]

# VAO and VBO
VAO = glGenVertexArrays(100)
VBO = glGenBuffers(100)
VIndex = 0

side_pos = []
side_pos.append([0, -5, 0])
side_pos.append([0, 5, 0])
side_pos.append([-5, 0, 0])
side_pos.append([5, 0, 0])
side_pos.append([0, 0, -5])
side_pos.append([0, 0, 5])

side_rotate = []
side_rotate.append([0, 0, 0])
side_rotate.append([np.pi, 0, 0])
side_rotate.append([0, 0, np.pi/2])
side_rotate.append([0, 0, (np.pi/2)*3])
side_rotate.append([np.pi/2, 0, 0])
side_rotate.append([(np.pi/2)*3, 0, 0])

side_scale = [0.2, 0.2, 0.2]

for i in range(6):
    objectList.append(Object.Object(bindArrays(floorB), len(floorI), "Floor", i,
                      side_pos[i], side_rotate[i], side_scale, [0, 0, 0], 4, True))

marker_pos = []
marker_pos.append([-5, -5, -5])
marker_pos.append([-5, -5, 5])
marker_pos.append([-5, 5, -5])
marker_pos.append([-5, 5, 5])
marker_pos.append([5, -5, -5])
marker_pos.append([5, -5, 5])
marker_pos.append([5, 5, -5])
marker_pos.append([5, 5, 5])

marker_scale = [0.1, 0.1, 0.1]

for i in range(8):
    objectList.append(Object.Object(bindArrays(sphereB), len(sphereI), "Marker", i,
                                    marker_pos[i], [0, 0, 0], marker_scale, [0, 0, 0], 4, True))

periodic_table = []
hydrogen = ["H", "Hydrogen", pyrr.matrix44.create_from_scale(
    pyrr.Vector3([0.2, 0.2, 0.2])), 0]
oxygen = ["O", "Oxygen", pyrr.matrix44.create_from_scale(
    pyrr.Vector3([0.25, 0.25, 0.25])), 1]
periodic_table.append(hydrogen)
periodic_table.append(oxygen)

projection = pyrr.matrix44.create_perspective_projection_matrix(
    45, 1920/1080, 0.1, 100)
view = pyrr.matrix44.create_look_at(pyrr.Vector3(
    [0, 10, 0]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)


h1 = -1
h2 = -1
o1 = -1
molecule1 = False
molecule2 = False
molecule3 = False
lastTime = glfw.get_time()
nbFrames = 0

# the main application loop
while not glfw.window_should_close(window):
    glfw.poll_events()

    currentTime = glfw.get_time()
    nbFrames += 1
    if currentTime-lastTime >= 1.0:
        print(1000/nbFrames, "ms/frame")
        nbFrames = 0
        lastTime += 1.0

    processInput(window)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camPos2D = [math.sin(cam[0]) * cam[2], math.cos(cam[0]) * cam[2]]
    camPosY = math.sin(cam[1]) * cam[2]
    camPosX = camPos2D[0]*math.cos(cam[1])
    camPosZ = camPos2D[1]*math.cos(cam[1])

    view = pyrr.matrix44.create_look_at(pyrr.Vector3([camPosX, camPosY, camPosZ]), pyrr.Vector3([0.0, 0.0, 0.0]),
                                        pyrr.Vector3([0.0, 1.0, 0.0]))

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

    for object in objectList:
        drawObject(
            object.index, textures[object.texture], object.model, object.faceNo)

    # indexNo = 0
    # if camPosY < 0:
    #    indexNo += 1

    # temp = pyrr.matrix44.multiply(side_scale, side_rotate[indexNo])
    # model = pyrr.matrix44.multiply(temp, side_pos[indexNo])
    # drawObject(indexNo, textures[4], model, len(floorI))

    # indexNo = 2
    # if camPosX < 0:
    #    indexNo += 1

    # temp = pyrr.matrix44.multiply(side_scale, side_rotate[indexNo])
    # model = pyrr.matrix44.multiply(temp, side_pos[indexNo])
    # drawObject(indexNo, textures[4], model, len(floorI))

    # indexNo = 4
    # if camPosZ < 0:
    #    indexNo += 1

    # temp = pyrr.matrix44.multiply(side_scale, side_rotate[indexNo])
    # model = pyrr.matrix44.multiply(temp, side_pos[indexNo])
    # drawObject(indexNo, textures[4], model, len(floorI))

    # indexNo = 6

    # for i in range(len(test_pos)):
    #    temp = pyrr.matrix44.multiply(test_scale[i], test_rotate[i])
    #    model = pyrr.matrix44.multiply(temp, test_pos[i])
    #    if i <= 3:
    #        drawObject(indexNo, textures[test_tex[i]], model, len(sphereI))
    #    elif i >= 4:
    #        drawObject(indexNo, textures[test_tex[i]], model, len(barI))
    #    indexNo += 1

    # for i in range(len(marker_pos)):
    #    model = pyrr.matrix44.multiply(marker_scale, marker_pos[i])
    #    drawObject(indexNo, textures[5], model, len(sphereI))
    #    indexNo += 1

    # for i in range(len(atom_list)):
    #    model = pyrr.matrix44.multiply(atom_scale[i], atom_pos[i])
    #    drawObject(
    #        indexNo, textures[periodic_table[atom_list[i]][2]], model, len(sphereI))
    #    indexNo += 1

    # if molecule1 == False:
    #    for i in range(len(atom_list)):
    #        if atom_list[i] == 0:
    #            if h1 == -1:
    #                h1 = i
    #            elif h2 == -1:
    #                if h1 != i:
    #                    h2 = i
    #        elif atom_list[i] == 1:
    #            o1 = i
    #    if h1 != -1 & h2 != -1 & o1 != -1:
    #        molecule1 = True
    #        molecule2 = True
    #        molecule3 = True

    # if molecule2 == True:
    #    print(atom_pos[h1])
    #    average = [(atom_pos[h1][3][0]+atom_pos[h2][3][0]+atom_pos[o1][3][0])/3, (
    #        atom_pos[h1][3][1]+atom_pos[h2][3][1]+atom_pos[o1][3][1])/3, (atom_pos[h1][3][2]+atom_pos[h2][3][2]+atom_pos[o1][3][2])/3]
    #    atom_trans[h1] = pyrr.matrix44.create_from_translation(
    #        pyrr.Vector3([(0-atom_pos[h1][3][0])*-0.002, (0.5-atom_pos[h1][3][1])*-0.002, (1.2-atom_pos[h1][3][2])*-0.002]))
    #    atom_trans[h2] = pyrr.matrix44.create_from_translation(
    #        pyrr.Vector3([(0-atom_pos[h2][3][0])*-0.002, (0.5-atom_pos[h2][3][1])*-0.002, (-1.2-atom_pos[h2][3][2])*-0.002]))
    #    atom_trans[o1] = pyrr.matrix44.create_from_translation(
    #        pyrr.Vector3([(0-atom_pos[o1][3][0])*-0.002, (-0.5-atom_pos[o1][3][1])*-0.002, (0-atom_pos[o1][3][2])*-0.002]))
    #    molecule2 = False

    # if molecule3 == True:
    #    if pyrr.Matrix44(atom_pos[h1]) == pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0.5, 1.2])):
    #        print("AWOOGA")

    #    print("AWOooOGA")
    #    print(pyrr.Matrix44(atom_pos[h1]))
    #    print(pyrr.matrix44.create_from_translation(
    #        pyrr.Vector3([0, 0.5, 1.2])))

    #    if atom_pos[h1][3][0] == 0:
    #        atom_trans[h1][0] = 0
    #    if atom_pos[h1][3][1] == 0.5:
    #        atom_trans[h1][1] = 0
    #    if atom_pos[h1][3][2] == 1.2:
    #        atom_trans[h1][0] = 0
    #    if atom_pos[h2][3][0] == 0:
    #        atom_trans[h2][0] = 0
    #    if atom_pos[h2][3][1] == 0.5:
    #        atom_trans[h2][1] = 0
    #    if atom_pos[h2][3][2] == -1.2:
    #        atom_trans[h2][0] = 0
    #    if atom_pos[o1][3][0] == 0:
    #        atom_trans[o1][0] = 0
    #    if atom_pos[o1][3][1] == -0.5:
    #        atom_trans[o1][1] = 0
    #    if atom_pos[o1][3][2] == 0:
    #        atom_trans[o1][0] = 0

    # for i in range(len(test_pos)):
    #    test_pos[i] = pyrr.matrix44.multiply(test_trans, test_pos[i])
    #    for j in range(3):
    #        if test_pos[i][3][j] >= 5:
    #            test_pos[i][3][j] = 5
    #            test_trans = pyrr.matrix44.create_from_translation(
    #                pyrr.Vector3([random.randrange(-20, 20)*0.00005, random.randrange(-20, 20)*0.00005, random.randrange(-20, 20)*0.00005]))
    #        if test_pos[i][3][j] <= -5:
    #            test_pos[i][3][j] = -5
    #            test_trans = pyrr.matrix44.create_from_translation(
    #                pyrr.Vector3([random.randrange(-20, 20)*0.00005, random.randrange(-20, 20)*0.00005, random.randrange(-20, 20)*0.00005]))

    # for i in range(len(atom_pos)):
    #    atom_pos[i] = pyrr.matrix44.multiply(atom_trans[i], atom_pos[i])
    #    for j in range(3):
    #        if atom_pos[i][3][j] >= 5:
    #            atom_pos[i][3][j] = 5
    #            atom_trans[i] = pyrr.matrix44.create_from_translation(
    #                pyrr.Vector3([random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001]))
    #        if atom_pos[i][3][j] <= -5:
    #            atom_pos[i][3][j] = -5
    #            atom_trans[i] = pyrr.matrix44.create_from_translation(
    #                pyrr.Vector3([random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001, random.randrange(-20, 20)*0.0001]))

    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()
