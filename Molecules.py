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
import Atom

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
        atom_to_make = "H"
    if(glfw.get_key(window, glfw.KEY_HOME) == glfw.PRESS):
        atom_to_make = "He"
    if(glfw.get_key(window, glfw.KEY_L) == glfw.PRESS):
        atom_to_make = "Li"
    if(glfw.get_key(window, glfw.KEY_RIGHT_BRACKET) == glfw.PRESS):
        atom_to_make = "Be"
    if(glfw.get_key(window, glfw.KEY_B) == glfw.PRESS):
        atom_to_make = "B"
    if(glfw.get_key(window, glfw.KEY_C) == glfw.PRESS):
        atom_to_make = "C"
    if(glfw.get_key(window, glfw.KEY_N) == glfw.PRESS):
        atom_to_make = "N"
    if(glfw.get_key(window, glfw.KEY_O) == glfw.PRESS):
        atom_to_make = "O"
    if(glfw.get_key(window, glfw.KEY_1) == glfw.PRESS):
        make_a_molecule = "O2"
    if(glfw.get_key(window, glfw.KEY_2) == glfw.PRESS):
        make_a_molecule = "H2O"
    if(glfw.get_key(window, glfw.KEY_3) == glfw.PRESS):
        make_a_molecule = "C2H6"


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


def addAtom(atom, position, move):
    global periodic_table, atom_list, sphereB, sphereI, objectList
    objectCount = len(objectList)
    atom_list.append(atom)
    objectList.append(Object.Object(bindArrays(sphereB), len(sphereI), "Atom", len(atom_list)-1,
                                    position, [0, 0, 0], [atom.size, atom.size, atom.size], move, atom.texture, True))
    atom_list[len(atom_list)-1].setObjectNo(objectCount)


def addRandAtom(label):
    global periodic_table, atom_list, sphereB, sphereI, objectList
    for atom in periodic_table:
        if atom.label == label:
            position = [
                random.randrange(-5000, 5000)*0.001, random.randrange(-5000, 5000)*0.001, random.randrange(-5000, 5000)*0.001]
            move = [random.randrange(-1000, 1000)*0.001*0.005,
                    random.randrange(-1000, 1000)*0.001*0.005, random.randrange(-1000, 1000)*0.001*0.005]
            addAtom(atom, position, move)


def addBar(start, end):
    global barB, barI
    centre = (pyrr.Vector3(start) + pyrr.Vector3(end))/pyrr.Vector3([2, 2, 2])
    centre = centre + pyrr.Vector3([0, 0.1, 0])
    vector = pyrr.Vector3(end) - pyrr.Vector3(start)
    up = pyrr.Vector3([0, 1, 0])
    if vector.y != 0 and vector.z != 0:
        angleX = np.arctan(vector.z/vector.y)
        print("x:", angleX)
    elif vector.y == 0:
        angleX = (np.pi/2)
    elif vector.z == 0:
        angleX = 0

    if vector.x != 0 and vector.y != 0:
        angleZ = np.arctan(vector.x/vector.y)
    elif vector.y == 0:
        angleZ = 0
    elif vector.x == 0:
        angleZ = 0

    rotate = [-angleX, 0, angleZ]
    scale = [0.15, 0.75, 0.15]
    objectList.append(Object.Object(bindArrays(barB), len(barI), "Bar", len(bar_list),
                                    centre, rotate, scale, [0, 0, 0], 13, True))


def addMolecule(moleculeName):
    gap = 0.75
    if moleculeName == "O2":
        addAtom(periodic_table[7], [0, 0, -gap], [0, 0, 0])
        addAtom(periodic_table[7], [0, 0, gap], [0, 0, 0])
        addBar([0, 0, -gap], [0, 0, gap])
    if moleculeName == "H2O":
        addAtom(periodic_table[0], [0, np.sqrt(3)-1, 1], [0, 0, 0])
        addAtom(periodic_table[7], [0, 1-np.sqrt(3), 0], [0, 0, 0])
        addBar([0, np.sqrt(3)-1, 1], [0, 1-np.sqrt(3), 0])
        addAtom(periodic_table[0], [0, np.sqrt(3)-1, -1], [0, 0, 0])
        addBar([0, np.sqrt(3)-1, -1], [0, 1-np.sqrt(3), 0])
    if moleculeName == "C2H6":
        addAtom(periodic_table[5], [0, 0, -gap], [0, 0, 0])
        addAtom(periodic_table[5], [0, 0, gap], [0, 0, 0])
        addBar([0, 0, -gap], [0, 0, gap])
        addAtom(periodic_table[0], [0, gap*np.sqrt(4.5), gap*2.5], [0, 0, 0])
        addBar([0, 0, gap], [0, gap*np.sqrt(4.5), gap*2.5])
        addAtom(periodic_table[0], [gap*1.5, -gap*1.5, gap*2.5], [0, 0, 0])
        addBar([0, 0, gap], [gap*1.5, -gap*1.5, gap*2.5])
        addAtom(periodic_table[0], [-gap*1.5, -gap*1.5, gap*2.5], [0, 0, 0])
        addBar([0, 0, gap], [-gap*1.5, -gap*1.5, gap*2.5])

        addAtom(periodic_table[0], [0, gap*np.sqrt(4.5), -gap*2.5], [0, 0, 0])
        addBar([0, 0, -gap], [0, gap*np.sqrt(4.5), -gap*2.5])
        addAtom(periodic_table[0], [gap*1.5, -gap*1.5, -gap*2.5], [0, 0, 0])
        addBar([0, 0, -gap], [gap*1.5, -gap*1.5, -gap*2.5])
        addAtom(periodic_table[0], [-gap*1.5, -gap*1.5, -gap*2.5], [0, 0, 0])
        addBar([0, 0, -gap], [-gap*1.5, -gap*1.5, -gap*2.5])


periodic_table = []
periodic_table.append(Atom.Atom("H", "Hydrogen", 0.15, 0, None))
periodic_table.append(Atom.Atom("He", "Helium", 0.15, 7, None))
periodic_table.append(Atom.Atom("Li", "Lithium", 0.2, 11, None))
periodic_table.append(Atom.Atom("Be", "Beryllium", 0.2, 12, None))
periodic_table.append(Atom.Atom("B", "Boron", 0.2, 10, None))
periodic_table.append(Atom.Atom("C", "Carbon", 0.25, 1, None))
periodic_table.append(Atom.Atom("N", "Nitrogen", 0.25, 2, None))
periodic_table.append(Atom.Atom("O", "Oxygen", 0.25, 3, None))
atom_list = []
bar_list = []

atom_to_make = None
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

textures = glGenTextures(17)
load_texture("textures/White.jpg", textures[0])
load_texture("textures/Black.jpg", textures[1])
load_texture("textures/Blue.jpg", textures[2])
load_texture("textures/Red.jpg", textures[3])
load_texture("textures/Green.jpg", textures[4])
load_texture("textures/DRed.jpg", textures[5])
load_texture("textures/DViolet.jpg", textures[6])
load_texture("textures/Cyan.jpg", textures[7])
load_texture("textures/Orange.jpg", textures[8])
load_texture("textures/Yellow.jpg", textures[9])
load_texture("textures/Beige.jpg", textures[10])
load_texture("textures/Violet.jpg", textures[11])
load_texture("textures/DGreen.jpg", textures[12])
load_texture("textures/LGrey.jpg", textures[13])
load_texture("textures/DOrange.jpg", textures[14])
load_texture("textures/Pink.jpg", textures[15])
load_texture("textures/Grid.png", textures[16])

sphereI, sphereB = ObjLoader.load_model("models/sphere.obj")
floorI, floorB = ObjLoader.load_model("models/floor.obj")
barI, barB = ObjLoader.load_model("models/cube.obj")

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
                      side_pos[i], side_rotate[i], side_scale, [0, 0, 0], 16, True))

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
                                    marker_pos[i], [0, 0, 0], marker_scale, [0, 0, 0], 1, True))

projection = pyrr.matrix44.create_perspective_projection_matrix(
    45, 1920/1080, 0.1, 100)
view = pyrr.matrix44.create_look_at(pyrr.Vector3(
    [0, 10, 0]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

model_loc = glGetUniformLocation(shader, "model")
proj_loc = glGetUniformLocation(shader, "projection")
view_loc = glGetUniformLocation(shader, "view")

glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

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

    if camPosY < 0:
        objectList[0].isDrawn = False
        objectList[1].isDrawn = True
    elif camPosY >= 0:
        objectList[0].isDrawn = True
        objectList[1].isDrawn = False

    if camPosX < 0:
        objectList[2].isDrawn = False
        objectList[3].isDrawn = True
    elif camPosX >= 0:
        objectList[2].isDrawn = True
        objectList[3].isDrawn = False

    if camPosZ < 0:
        objectList[4].isDrawn = False
        objectList[5].isDrawn = True
    elif camPosZ >= 0:
        objectList[4].isDrawn = True
        objectList[5].isDrawn = False

    if make_a_molecule != None:
        addMolecule(make_a_molecule)
        make_a_molecule = None

    if atom_to_make != None:
        addRandAtom(atom_to_make)
        atom_to_make = None

    for object in objectList:
        if object.type == "Atom":
            for i in range(3):
                if object.position[3][i] >= 5:
                    object.position[3][i] = 5
                    object.randomTrans()
                if object.position[3][i] <= -5:
                    object.position[3][i] = -5
                    object.randomTrans()
        object.updatePos()
        if object.isDrawn == True:
            drawObject(
                object.index, textures[object.texture], object.model, object.faceNo)
    glfw.swap_buffers(window)

# terminate glfw, free up allocated resources
glfw.terminate()
