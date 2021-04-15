import pyrr
import numpy as np


class Atom:
    def __init__(self, label, name, size, texture, objectNo):
        self.label = label
        self.name = name
        self.size = size
        self.texture = texture
        self.objectNo = objectNo

    def setObjectNo(self, objectNo):
        self.objectNo = objectNo
