import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import random
# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Lifter import Lifter
from Bin import Bin
from Cubo import Cubo
from box import Box
import requests

screen_width = 800
screen_height = 800
#vc para el obser.
FOVY=60.0
ZNEAR=1.0
ZFAR=1000.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X=150.0
EYE_Y=60.0
EYE_Z=150.0
CENTER_X=75
CENTER_Y=0
CENTER_Z=60
UP_X=0
UP_Y=1
UP_Z=0
#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500
Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 200

bins = []
n_bins = 1
#lifters
lifters = []
nlifters = 5

# Variables para el control del observador
theta = 0.0
radius = 300

# Arreglo para el manejo de texturas
textures = []
filenames = ["img1.bmp","wheel.jpeg", "robot_body.jpg","pared_des.jpg","conteneder.jpg","piso.jpg","pared.jpg","transito..jpg","caja.jpg","load_zone.jpg","techo.jpg"]

robots = []
boxes = []
h_load_zone = 0

num_cam = 0   

URL_BASE = "http://192.168.1.85:8000"
r = requests.post(URL_BASE + "/simulations", allow_redirects=False)
datos = r.json()
LOCATION = datos["Location"]
robots_julia = datos["robots"]
boxes_julia = datos["boxes"]

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)

def Texturas(filepath):
    global textures
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image, "RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    
def Init():
    global robots, boxes, textures, h_load_zone
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: cubos")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    

    for i in filenames:
        Texturas(i)
        
    for robot_data in robots_julia:
        x_log,y_log,z_log = robot_data["position"]
        w_box = robot_data["box_width"]
        h_box = robot_data["box_height"]
        d_box = robot_data["box_depth"]
        robot = Lifter([x_log,y_log,z_log],[w_box,h_box,d_box], textures)
        robots.append(robot)
    
    for box_data in boxes_julia:
        x_log, y_log,z_log = box_data["position"]
        w_log,h_log,d_log = box_data["WHD"]
        h_load_zone += h_log
        box = Box([x_log,y_log,z_log],[w_log,h_log,d_log],1,textures)
        boxes.append(box)
    

    bin = Bin(textures, [40,0.1,19.5],[65,44.5,40.5])
    bins.append(bin)
        
def update_simulation():
    global robots_julia, boxes_julia
    r = requests.get(URL_BASE + LOCATION)
    datos = r.json()
    robots_julia = datos["robots"]
    boxes_julia = datos["boxes"]
    
def draw_ceiling():
    glPushMatrix()
    # activate textures
    glColor(1.0, 1.0, 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[10])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(DimBoard, 100, 0)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(DimBoard, 50, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-DimBoard, 50, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-DimBoard, 100, 0)
    glEnd()
    glPopMatrix()
        
    glPushMatrix()
    # activate textures
    glColor(1.0, 1.0, 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[10])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 100, 0)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 50, -DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 50, -DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 100, 0)
    glEnd()
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
        
def draw_buildings():
    
    glPushMatrix()
    # activate textures
    glColor(1.0, 1.0, 1.0)
    # glEnable(GL_TEXTURE_2D)
    # glBindTexture(GL_TEXTURE_2D, textures[5])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-130, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, 0, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40,   0, -DimBoard)
    glEnd()
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, 0, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40,   0, -DimBoard)
    glEnd()
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, 0, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40,   0, -DimBoard)
    glEnd()
    glPopMatrix()
    
    # glDisable(GL_TEXTURE_2D)
            
def planoText():
    glPushMatrix()
    # activate textures
    glColor(1.0, 1.0, 1.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[5])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, 0, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40,   0, -DimBoard)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, 0, 60)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, 0, 200)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(200, 0, 200)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(200, 0, 60)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, 0, -20)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, 0, 20)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(100, 0, 20)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(100, 0, -20)
    glEnd()
    glPopMatrix()

    
    glDisable(GL_TEXTURE_2D)
    
    
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[3])  # Use the first texture
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, 0, 20)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, -20, 20)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(100, -20, 20)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(100, 0, 20)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, 0, 60)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, -20, 60)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, -20, 20)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40, 0, 20)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(200, 0, 60)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(200, -20, 60)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, -20, 60)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40, 0, 60)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(100, 0, 20)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(100, -20, 20)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(100, -20, -20)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(100, 0, -20)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(100, 0, -20)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(100, -20, -20)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, -20, -20)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40, 0, -20)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, 0, 20)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, -20, 20)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, -20, -DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(40, 0, -DimBoard)
    glEnd()
    glPopMatrix()
    
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, 0, -DimBoard)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, -20, -DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, -20, -DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    glPopMatrix()
    
    glDisable(GL_TEXTURE_2D)
    
    
    glEnable(GL_TEXTURE_2D)
    
    glBindTexture(GL_TEXTURE_2D, textures[7])  # Use the first texture
    glPushMatrix()
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(40, -20, -200)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, -20, 60)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(200, -20, 60)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(200, -20, -200)
    glEnd()
    glPopMatrix()
    
    
    
    glDisable(GL_TEXTURE_2D)
    
    
def robotTransitZone():
    # Activa el uso de texturas y define el color
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[7])  # Usa la textura del piso (cambia si deseas otra textura)
    
    # Dibuja la zona de tránsito
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-5, 0.5, 110)  # Inferior izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(6, 0.5, 110)  # Inferior derecha
    glTexCoord2f(1.0, 1.0)
    glVertex3d(6, 0.5, 20)  # Superior derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-5, 0.5, 20)  # Superior izquierda
    glEnd()
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(200, 0.5, 110)  # Inferior izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(200, 0.5, 100)  # Inferior derecha
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-5, 0.5, 100)  # Superior derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-5, 0.5, 110)  # Superior izquierda
    glEnd()
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(200, 0.5, 85)  # Inferior izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(200, 0.5, 75)  # Inferior derecha
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-5, 0.5, 75)  # Superior derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-5, 0.5,85)  # Superior izquierda
    glEnd()
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(25, 0.5, 75)  # Inferior izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(35, 0.5, 75)  # Inferior derecha
    glTexCoord2f(1.0, 1.0)
    glVertex3d(35, 0.5, 20)  # Superior derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(25, 0.5,20)  # Superior izquierda
    glEnd()
    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-5, 0.5, 45)  # Inferior izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(40, 0.5, 45)  # Inferior derecha
    glTexCoord2f(1.0, 1.0)
    glVertex3d(40, 0.5, 35)  # Superior derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-5, 0.5,35)  # Superior izquierda
    glEnd()
    glPopMatrix()
    #Deshabilita texturas después de dibujar
    glDisable(GL_TEXTURE_2D)
    
def robotLoadZone():
    global h_load_zone
    # Activa el uso de texturas y define el color
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[9])  # Usa la textura del piso (cambia si deseas otra textura)
    
    # Dibuja la zona de tránsito
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(3, 0.2, 140)  # Inferior izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(h_load_zone + 5, 0.2, 140)  # Inferior derecha
    glTexCoord2f(1.0, 1.0)
    glVertex3d(h_load_zone + 5, 0.2, 115)  # Superior derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(3, 0.2, 115)  # Superior izquierda
    glEnd()
    glPopMatrix()
    #Deshabilita texturas después de dibujar
    glDisable(GL_TEXTURE_2D)
    
    
def walls():
    glPushMatrix()
    wall_height = 200  # Altura de las paredes
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, textures[6]) 
# Dibujar la pared izquierda
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)  # Abajo izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, wall_height, -DimBoard)  # Arriba izquierda
    glTexCoord2f(1.0, 1.0)
    glVertex3d(-DimBoard, wall_height, DimBoard)  # Arriba derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(-DimBoard, 0, DimBoard)  # Abajo derecha
    glEnd()

    # Dibujar la pared derecha
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)  # Abajo izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(DimBoard, wall_height, -DimBoard)  # Arriba izquierda
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, DimBoard)  # Arriba derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, DimBoard)  # Abajo derecha
    glEnd()

    # Dibujar la pared frontal
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, DimBoard)  # Abajo izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, wall_height, DimBoard)  # Arriba izquierda
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, DimBoard)  # Arriba derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, DimBoard)  # Abajo derecha
    glEnd()

    # Dibujar la pared trasera
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)  # Abajo izquierda
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, wall_height, -DimBoard)  # Arriba izquierda
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, wall_height, -DimBoard)  # Arriba derecha
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)  # Abajo derecha
    glEnd()
    glPopMatrix()
    glDisable(GL_TEXTURE_2D)


PAN_STEP = 5.0    
def check_camera(keys):
    global EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z, theta, num_cam

    if keys[pygame.K_UP]:  # Cambiar entre cámaras
        num_cam = (num_cam + 1) % 4  # Cambia entre las cámaras (0 a 3)
        if num_cam == 0:
            EYE_X, EYE_Y, EYE_Z = -50, 10, 60
            CENTER_X, CENTER_Y, CENTER_Z = 50, 10, 60
        elif num_cam == 1:
            EYE_X, EYE_Y, EYE_Z = -40, 40, -40
            CENTER_X, CENTER_Y, CENTER_Z = 40, 10, 40
        elif num_cam == 2:
            EYE_X, EYE_Y, EYE_Z = 103.9, 39.9, 63.9
            CENTER_X, CENTER_Y, CENTER_Z = 75, 0, 40
        elif num_cam == 3:
            EYE_X, EYE_Y, EYE_Z = 150, 60, 150
            CENTER_X, CENTER_Y, CENTER_Z = 75, 0, 60

    elif keys[pygame.K_LEFT]:  # Paneo hacia la derecha
        # Mover el punto de mira hacia la derecha relativo a la dirección de la cámara
        dx = CENTER_X - EYE_X
        dz = CENTER_Z - EYE_Z
        norm = (dx ** 2 + dz ** 2) ** 0.5
        # Desplazamiento ortogonal a la dirección de la cámara
        CENTER_X += PAN_STEP * dz / norm
        CENTER_Z -= PAN_STEP * dx / norm

    elif keys[pygame.K_RIGHT]:  # Paneo hacia la izquierda
        # Mover el punto de mira hacia la izquierda relativo a la dirección de la cámara
        dx = CENTER_X - EYE_X
        dz = CENTER_Z - EYE_Z
        norm = (dx ** 2 + dz ** 2) ** 0.5
        # Desplazamiento ortogonal a la dirección de la cámara
        CENTER_X -= PAN_STEP * dz / norm
        CENTER_Z += PAN_STEP * dx / norm
    # Actualizar la vista con la nueva configuración
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)


def display():
    global robots_julia, boxes_julia, boxes,robots,h_load_zone
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)      
    for robot_data in robots_julia:
        x_log,y_log,z_log = robot_data["position"]
        robot = robots[robot_data["id"] - 30]
        
        if robot_data["rotating"] == 0:
            robot.up([x_log,y_log,z_log])
        else:
            if robot_data["one_time_rotation"] == 1:
                if robot_data["previous_direction"] == "DOWN":
                    if robot_data["direction"] == "RIGHT":
                        robot.setTurnLR('L')
                    elif robot_data["direction"] == "LEFT":
                        robot.setTurnLR('R')
                    else:
                        robot.setTurnLR('B')
                elif robot_data["previous_direction"] == "RIGHT":
                    if robot_data["direction"] == "UP":
                        robot.setTurnLR('L')
                    elif robot_data["direction"] == "DOWN":
                        robot.setTurnLR('R')
                    else:
                        robot.setTurnLR('B')
                elif robot_data["previous_direction"] == "LEFT":
                    if robot_data["direction"] == "DOWN":
                        robot.setTurnLR('L')
                    elif robot_data["direction"] == "UP":
                        robot.setTurnLR('R')
                    else:
                        robot.setTurnLR('B')
                elif robot_data["previous_direction"] == "UP":
                    if robot_data["direction"] == "LEFT":
                        robot.setTurnLR('L')
                    elif robot_data["direction"] == "RIGHT":
                        robot.setTurnLR('R')
                    else:
                        robot.setTurnLR('B')                 
        robot.draw()
        if robot_data["box_width"] != 0:
            robot.update_carrying_box(robot_data["box_width"],robot_data["box_height"],robot_data["box_depth"])
            robot.draw_box()
        robot.update()    

    
    #Axis()
  # Asegúrate de habilitar texturas
    # Dibuja el contenedor
    
    for obj in bins:
        obj.draw() 
    
    for box_data in boxes_julia:    
        x_log,y_log,z_log = box_data["position"]
        box = boxes[box_data["id"] - 1]
        box.up([x_log+0.1,y_log+0.1,z_log+0.1])
        box.up_WHD(box_data['WHD'])
        print(f"Box ID: {box_data['id']}, Position: ({x_log}, {y_log}, {z_log}), WHD: {box_data['WHD']}")
        if box_data["showing"] == 1:
            box.draw() 
    #Se dibuja el plano gris
    planoText()
    walls()
    robotTransitZone()  # Dibuja la zona de tránsito
    robotLoadZone()
    draw_ceiling()

    
    
    
def lookAt():
    global EYE_X, EYE_Y,EYE_Z
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)


done = False
Init()
while not done:
    keys = pygame.key.get_pressed()  # Checking pressed keys
    check_camera(keys)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        if event.type == pygame.QUIT:
            done = True
    update_simulation()
    display()
    pygame.display.flip()
    pygame.time.wait(10)
pygame.quit()