# -*- coding: utf-8 -*-
"""
ResMgr stub for BigWorld Engine / World of Tanks
"""

class DataSection(object):
    def __init__(self, name=''):
        self.name = name
    def readString(self, tag, default=''): return default
    def readInt(self, tag, default=0): return default
    def readFloat(self, tag, default=0.0): return default
    def readBool(self, tag, default=False): return default
    def readVector2(self, tag, default=(0.0, 0.0)): return default
    def readVector3(self, tag, default=(0.0, 0.0, 0.0)): return default
    def readVector4(self, tag, default=(0.0, 0.0, 0.0, 0.0)): return default
    def writeString(self, tag, val): pass
    def writeInt(self, tag, val): pass
    def writeFloat(self, tag, val): pass
    def writeBool(self, tag, val): pass
    def save(self): pass
    def values(self): return []
    def keys(self): return []
    def items(self): return []
    def has_key(self, key): return False
    def __getitem__(self, key): return DataSection(key)

def openSection(path, createIfMissing=False):
    return DataSection(path)

def root():
    return DataSection('root')

def appDirectory():
    return 'F:/Tanki'

def resolveToAbsolutePath(path):
    return path
