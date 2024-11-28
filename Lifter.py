import pygame
from pygame.locals import *
from Cubo import Cubo

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import math

from box import Box


class Lifter:
    def __init__(self, position, box_dims ,textures):
        # Se inicializa una posicion aleatoria en el tablero
        # self.Position = [random.randint(-dim, dim), 6, random.randint(-dim, dim)]
        self.Position = position
        # Inicializar las coordenadas (x,y,z) del cubo en el tablero
        # almacenandolas en el vector Position
        self.box_width = box_dims[0]
        self.box_height= box_dims[1]
        self.box_depth= box_dims[2]
        # Se inicializa un vector de direccion aleatorio
        dirX = random.randint(-10, 10) or 1
        dirZ = random.randint(-1, 1) or 1
        magnitude = math.sqrt(dirX**2 + dirZ**2)
        self.Direction = [(dirX / magnitude), 0, (dirZ / magnitude)]
        self.angle = 0
        # El vector aleatorio debe de estar sobre el plano XZ (la altura en Y debe ser fija)
        # Se normaliza el vector de direccion

        # Arreglo de texturas
        self.textures = textures

        self.theta = 0.0
        self.delta_theta = 0.0
        self.newdeg = lambda deg, inc_deg: (deg + inc_deg) % 360
        self.turn_LR = 0  # == 0: no girando, != 0: girando
        # Control variables for platform movement
        self.platformHeight = -1.9
        self.platformUp = False
        self.platformDown = False

        #Control variable for collisions
        self.radiusCol = 5

        #Control variables for animations
        self.status = 0
        self.trashID = -1
        #0 = searching
        #1 = lifting
        #2 = delivering
        #3 = dropping
        #4 = returning
    def setTurnLR(self, turn):
        if self.turn_LR == 0:
            if turn == "R":
                self.turn_LR = 90  # Grados a rotar
                self.delta_theta = -15.0  # Incremento negativo para girar a la izquierda
            elif turn == "L":
                self.turn_LR = 90
                self.delta_theta = 15.0
            elif turn == "B":
                self.turn_LR = 180
                self.delta_theta = 15.0# Incremento positivo para girar a la derecha
    def update_carrying_box(self,w_box,h_box,d_box):
        self.box_width = w_box
        self.box_height = h_box
        self.box_depth = d_box
    

    def up(self,new_pos):
        if self.turn_LR == 0:
            self.Position = new_pos   # Mover hacia adelante

    def update(self):
        if self.turn_LR != 0:
            self.turn_LR -= abs(self.delta_theta)
            self.theta = self.newdeg(self.theta, self.delta_theta)
            if self.turn_LR <= 0:
                self.turn_LR = 0
                self.delta_theta = 0
        # if self.status == 1:
        #     delta = 0.01
        #     if self.platformHeight >= 0:
        #         self.targetCenter()
        #         self.status = 2
        #     else:
        #         self.platformHeight += delta
        # elif self.status == 2:
        #     if (self.Position[0] <= 10 and self.Position[0] >= -10) and (self.Position[2] <= 10 and self.Position[2] >= -10):
        #         self.status = 3
        #     else:
        #         newX = self.Position[0] + self.Direction[0] * self.vel
        #         newZ = self.Position[2] + self.Direction[2] * self.vel
        #         if newX - 10 < -self.dim or newX + 10 > self.dim:
        #             self.Direction[0] *= -1
        #         else:
        #             self.Position[0] = newX
        #         if newZ - 10 < -self.dim or newZ + 10 > self.dim:
        #             self.Direction[2] *= -1
        #         else:
        #             self.Position[2] = newZ
        #         self.angle = math.acos(self.Direction[0]) * 180 / math.pi
        #         if self.Direction[2] > 0:
        #             self.angle = 360 - self.angle
        # elif self.status == 3:
        #     delta = 0.01
        #     if self.platformHeight <= -1.5:
        #         self.status = 4
        #         #print("Estatus 4")
        #     else:
        #         self.platformHeight -= delta
        # elif self.status == 4:
        #     if (self.Position[0] <= 20 and self.Position[0] >= -20) and (self.Position[2] <= 20 and self.Position[2] >= -20):
        #         self.Position[0] -= (self.Direction[0] * (self.vel/4))
        #         self.Position[2] -= (self.Direction[2] * (self.vel/4))
        #     else:
        #         self.search()
        #         self.status = 0
        # else:
        #     # Update position
        #     if random.randint(1,1000) == 69:
        #         self.search()
        #     newX = self.Position[0] + self.Direction[0] * self.vel
        #     newZ = self.Position[2] + self.Direction[2] * self.vel
        #     if newX - 10 < -self.dim or newX + 10 > self.dim:
        #         self.Direction[0] *= -1
        #     else:
        #         self.Position[0] = newX
        #     if newZ - 10 < -self.dim or newZ + 10 > self.dim:
        #         self.Direction[2] *= -1
        #     else:
        #         self.Position[2] = newZ
        #     self.angle = math.acos(self.Direction[0]) * 180 / math.pi
        #     if self.Direction[2] > 0:
        #         self.angle = 360 - self.angle

        #     # Move platform
        #     delta = 0.01
        #     if self.platformUp:
        #         if self.platformHeight >= 0:
        #             self.platformUp = False
        #         else:
        #             self.platformHeight += delta
        #     elif self.platformDown:
        #         if self.platformHeight <= -1.5:
        #             self.platformUp = True
        #         else:
        #             self.platformHeight -= delta

    def draw(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1]+5, self.Position[2])
        if self.theta != 0:
            glRotatef(self.theta, 0, 1, 0)
        glScaled(5, 5, 5)
        glColor3f(1.0, 1.0, 1.0)
        # front face
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[2])
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 0.5, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 0.5, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -0.5, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -0.5, 1)

        # 2nd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-2, 0.5, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 0.5, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(1, -0.5, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-2, -0.5, 1)

        # 3rd face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-2, 0.5, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 0.5, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, -0.5, 1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-2, -0.5, -1)

        # 4th face
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 0.5, -1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 0.5, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, -0.5, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, -0.5, -1)

        # top
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 0.5, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-2, 0.5, 1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-2, 0.5, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(1, 0.5, -1)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        


        # Wheels
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.textures[1])
        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(-1.2, -0.8, 1)
        glScaled(0.3, 0.3, 0.3)
        
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -0.8, 1)
        glScaled(0.3, 0.3, 0.3)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.5, -0.8, -1)
        glScaled(0.3, 0.3, 0.3)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-1.2, -0.8, -1)
        glScaled(0.3, 0.3, 0.3)
        wheel = Cubo(self.textures, 0)
        wheel.draw()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

        # Lifter
        glPushMatrix()
        glColor3f(0.0, 0.0, 0.0)
        glTranslatef(0, self.platformHeight, 0)  # Up and down
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(1, 1, 1)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(1, 1, -1)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(4, 1, -1)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(4, 1, 1)
        glEnd()
        glPopMatrix()
        
        #Dibujar columnas
        glPushMatrix()
        glColor3f(0.0, 0.0, 0.0)
        glTranslate(1.5,-1.5,-1)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(0, 0, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(0, 0, 0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(0, 4, 0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(0, 4, 0)
        glEnd()
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-0.5, 0, 0.5)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(0, 0, 0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(0, 4, 0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-0.5, 4, 0)
        glEnd()
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(-0.5, 0, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-0.5, 0, 0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-0.5, 4, 0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-0.5, 4, 0)
        glEnd()
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(0, 0, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(-0.5, 0, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-0.5, 4, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(0, 4, 0)
        glEnd()
        
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3d(0, 4, 0)
        glTexCoord2f(0.0, 1.0)
        glVertex3d(0, 4, 0.5)
        glTexCoord2f(1.0, 1.0)
        glVertex3d(-0.5, 4, 0.5)
        glTexCoord2f(1.0, 0.0)
        glVertex3d(-0.5, 4, 0)
        glEnd()
        
           
        glPopMatrix()
        
        glPopMatrix()

    def draw_box(self):
        glPushMatrix()
        glTranslatef(self.Position[0], self.Position[1], self.Position[2])
        if self.theta != 0:
            glRotatef(self.theta, 0, 1, 0)
        glColor3f(1.0, 1.0, 1.0)
        box = Box([13.5,self.platformHeight+self.box_depth/2 + 2,0],[self.box_width,self.box_height,self.box_depth],1,self.textures)
        box.draw()
        glPopMatrix()
        