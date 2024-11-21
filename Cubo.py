
import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math


class Cubo:
    def __init__(self,position,WHD):
        # Se inicializa las coordenadas de los vertices del cubo

        self.Position = position
        self.WHD = WHD

        #Arreglo de texturas
        self.textures = textures



    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        # Se dibuja el cubo
        # ...

        #glEnable(GL_TEXTURE_2D)
        #front face
        #glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, 1)

        #2nd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, -1, 1)

        #3rd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-1, -1, -1)

        #4th face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, -1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -1, -1)

        #top
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-1, 1, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-1, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 1, -1)

        glEnd()
        #glDisable(GL_TEXTURE_2D)
        #glEnableClientState(GL_VERTEX_ARRAY)
        #glEnableClientState(GL_COLOR_ARRAY)
        #glVertexPointer(3, GL_FLOAT, 0, self.vertexCoords)
        #glColorPointer(3, GL_FLOAT, 0, self.vertexColors)
        #glDrawElements(GL_QUADS, 24, GL_UNSIGNED_INT, self.elementArray)
        #glDisableClientState(GL_VERTEX_ARRAY)
        #glDisableClientState(GL_COLOR_ARRAY)

        glPopMatrix()