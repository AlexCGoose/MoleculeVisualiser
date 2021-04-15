import pyrr
import numpy as np
import random


class Object:
    def __init__(self, index, faceNo, type, typeNo, position, rotation, scale, move, texture, isDrawn):
        self.index = index
        self.type = type
        self.typeNo = typeNo
        self.faceNo = faceNo
        self.position = pyrr.matrix44.create_from_translation(position)
        self.rotation = pyrr.matrix44.multiply(pyrr.matrix44.create_from_z_rotation(rotation[2]), pyrr.matrix44.multiply(
            pyrr.matrix44.create_from_y_rotation(rotation[1]), pyrr.matrix44.create_from_x_rotation(rotation[0])))
        self.scale = pyrr.matrix44.create_from_scale(scale)
        self.model = pyrr.matrix44.multiply(
            self.position, pyrr.matrix44.multiply(self.rotation, self.scale))
        self.move = pyrr.matrix44.create_from_translation(move)
        self.texture = texture
        self.isDrawn = isDrawn

    def updatePos(self):
        self.position = pyrr.matrix44.multiply(self.move, self.position)
        self.model = pyrr.matrix44.multiply(
            self.scale, pyrr.matrix44.multiply(self.rotation, self.position))

    def randomTrans(self):
        self.move = pyrr.matrix44.create_from_translation([random.randrange(-1000, 1000)*0.001*0.005,
                                                           random.randrange(-1000, 1000)*0.001*0.005, random.randrange(-1000, 1000)*0.001*0.005])
