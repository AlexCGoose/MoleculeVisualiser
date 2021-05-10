import pyrr
import numpy as np


class Molecule:
    def __init__(self, name, startObject, atomList, atomPos, barList, barCount):
        self.name = name
        self.startObject = startObject
        self.atomList = atomList
        self.atomPos = atomPos
        self.barList = barList
        self.barCount = barCount
