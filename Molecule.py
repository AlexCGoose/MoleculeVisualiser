import pyrr
import numpy as np


class Molecule:
    def __init__(self, name, startObject, endObject, atomList, atomPos, barList):
        self.name = name
        self.startObject = startObject
        self.endObject = endObject
        self.atomList = atomList
        self.atomPos = atomPos
        self.barList = barList
