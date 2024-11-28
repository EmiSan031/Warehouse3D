
import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math


class Box:
    def __init__(self, position,WHD,color,textures):
        # Se inicializa las coordenadas de los vertices del cubo
        self.Position = position
        self.WHD = WHD
        self.color = color
        self.textures = textures

    def up(self,new_pos):
        self.Position = new_pos   # Mover hacia adelante
    def up_WHD(self,WHD):
        self.WHD = WHD 
        
    def draw(self):
        # Calcular las mitades de las dimensiones para simplificar las coordenadas
        half_width = self.WHD[0] / 2
        half_height = self.WHD[1] / 2
        half_depth = self.WHD[2] / 2

        # Coordenadas de los vértices relativos al centro
        vertices = [
            [ half_width,  half_height,  half_depth],  # Frente-arriba-derecha
            [ half_width,  half_height, -half_depth],  # Frente-arriba-izquierda
            [ half_width, -half_height, -half_depth],  # Frente-abajo-izquierda
            [ half_width, -half_height,  half_depth],  # Frente-abajo-derecha
            [-half_width,  half_height,  half_depth],  # Atrás-arriba-derecha
            [-half_width,  half_height, -half_depth],  # Atrás-arriba-izquierda
            [-half_width, -half_height, -half_depth],  # Atrás-abajo-izquierda
            [-half_width, -half_height,  half_depth],  # Atrás-abajo-derecha
        ]

        # Índices para dibujar las caras del cubo
        faces = [
            [0, 1, 2, 3],  # Frente
            [4, 5, 6, 7],  # Atrás
            [0, 4, 7, 3],  # Derecha
            [1, 5, 6, 2],  # Izquierda
            [0, 1, 5, 4],  # Arriba
            [3, 2, 6, 7],  # Abajo
        ]

        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        glScalef(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[8])
        glColor3f(1.0, 1.0, 1.0)

        # Dibujar las caras del cubo
        glBegin(GL_QUADS)
        for face in faces:
            glTexCoord2f(0.0, 0.0)
            glVertex3fv(vertices[face[0]])
            glTexCoord2f(0.0, 1.0)
            glVertex3fv(vertices[face[1]])
            glTexCoord2f(1.0, 1.0)
            glVertex3fv(vertices[face[2]])
            glTexCoord2f(1.0, 0.0)
            glVertex3fv(vertices[face[3]])
        glEnd()

        glDisable(GL_TEXTURE_2D)
        glPopMatrix()