# -*- coding: utf-8 -*-
"""
Math stub for BigWorld Engine / World of Tanks
"""

class Vector2(object):
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    def length(self): return 0.0
    def normalise(self): return self

class Vector3(object):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        if isinstance(x, (tuple, list)):
            self.x, self.y, self.z = map(float, x[:3])
        else:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
    def length(self): return 0.0
    def lengthSquared(self): return 0.0
    def normalise(self): return self
    def distTo(self, other): return 0.0
    def flatDistTo(self, other): return 0.0
    def dotProduct(self, other): return 0.0
    def crossProduct(self, other): return Vector3()
    def __add__(self, o): return Vector3()
    def __sub__(self, o): return Vector3()
    def __mul__(self, o): return Vector3()
    def __div__(self, o): return Vector3()

class Vector4(object):
    def __init__(self, x=0.0, y=0.0, z=0.0, w=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

class Matrix(object):
    def __init__(self):
        self.translation = Vector3()
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
    def set(self, other): pass
    def setIdentity(self): pass
    def setRotateYPR(self, ypr): pass
    def setTranslate(self, v): pass
    def setScale(self, v): pass
    def postMultiply(self, other): pass
    def preMultiply(self, other): pass
    def invert(self): pass
    def applyToAxis(self, axis): return Vector3()
    def applyToOrigin(self): return Vector3()
    def applyV4Point(self, v4): return Vector4()
    def applyPoint(self, v3): return Vector3()
    def applyVector(self, v3): return Vector3()

class Quaternion(object):
    def __init__(self): pass

def createTranslationMatrix(v): return Matrix()
def createRotationMatrix(ypr): return Matrix()
