# -*- coding: utf-8 -*-
"""
GUI stub for BigWorld Engine / World of Tanks
"""

class Simple(object):
    def __init__(self, textureName=''):
        self.textureName = textureName
        self.position = (0.0, 0.0, 0.0)
        self.size = (0.0, 0.0)
        self.visible = True
        self.colour = (255, 255, 255, 255)
    def addChild(self, component): pass
    def delChild(self, component): pass

class Text(Simple):
    def __init__(self, text=''):
        super(Text, self).__init__()
        self.text = text
        self.font = 'default_small.font'

def screenResolution():
    return (1920, 1080)

def addRoot(component): pass
def delRoot(component): pass
def roots(): return []
