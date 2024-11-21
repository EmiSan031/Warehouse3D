
import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math


class Bin:
    def __init__(self, textures, position, WHD):
        # Se inicializa las coordenadas de los vertices del cubo

        self.Position = position #[0,0,0]
        self.WHD = WHD
        #Arreglo de texturas
        self.textures = textures


    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[4])
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        # Se dibuja el cubo
        # ...

        #glEnable(GL_TEXTURE_2D)
        #front face
        #glBindTexture(GL_TEXTURE_2D, self.textures[self.txtIndex])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(self.WHD[0], self.WHD[2], self.WHD[1])
        glTexCoord2f(0.0, 1.0)
        glVertex3d(self.WHD[0], self.WHD[2], 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(self.WHD[0], 0, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(self.WHD[0], 0, self.WHD[1])

        #2nd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(0, self.WHD[2], self.WHD[1])
        glTexCoord2f(0.0, 1.0)
        glVertex3d(self.WHD[0], self.WHD[2], self.WHD[1])
        glTexCoord2f(1.0, 1.0)
        glVertex3d(self.WHD[0], 0, self.WHD[1])
        glTexCoord2f(1.0, 0.0)
        glVertex3d(0, 0, self.WHD[1])

        # #3rd face
        # glTexCoord2f(0.0, 0.0)
        # glVertex3d(0, self.WHD[2], 0)
        # glTexCoord2f(0.0, 1.0)
        # glVertex3d(0, self.WHD[2], self.WHD[1])
        # glTexCoord2f(1.0, 1.0)
        # glVertex3d(0, 0, self.WHD[1])
        # glTexCoord2f(1.0, 0.0)
        # glVertex3d(0, 0, 0)

        #4th face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(self.WHD[0], self.WHD[2], 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(0, self.WHD[2], 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(0, 0, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(self.WHD[0], 0, 0)

        # #top
        # glTexCoord2f(0.0, 0.0)
        # glVertex3d(self.WHD[0], self.WHD[2], self.WHD[1])
        # glTexCoord2f(0.0, 1.0)
        # glVertex3d(0, self.WHD[2], self.WHD[1])
        # glTexCoord2f(1.0, 1.0)
        # glVertex3d(0, self.WHD[2], 0)
        # glTexCoord2f(1.0, 0.0)
        # glVertex3d(self.WHD[0], self.WHD[2], 0)
        
        #bottom
        glTexCoord2f(0.0, 0.0)
        glVertex3d(0, 0.1, self.WHD[1])
        glTexCoord2f(0.0, 1.0)
        glVertex3d(self.WHD[0], 0.1 ,self.WHD[1])
        glTexCoord2f(1.0, 1.0)
        glVertex3d(self.WHD[0], 0.1 ,0)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(0, 0.1 ,0)

        glEnd()

        glPopMatrix()
        glDisable(GL_TEXTURE_2D)