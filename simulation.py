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
from Basura import Basura
from Bin import Bin
from Cubo import Cubo
from box import Box
import requests

screen_width = 500
screen_height = 500
#vc para el obser.
FOVY=60.0
ZNEAR=0.01
ZFAR=1800.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X=200.0
EYE_Y=150.0
EYE_Z=200.0
CENTER_X=0
CENTER_Y=0
CENTER_Z=0
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
filenames = ["img1.bmp","wheel.jpeg", "walle.jpeg","basura.bmp","conteneder.jpg"]

robots = []
boxes = []
URL_BASE = "http://192.168.1.203:8000"
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
    global robots, boxes
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
        box = Box([x_log,y_log,z_log],[w_log, h_log,d_log])
        boxes.append(box)
    
    # for bin_data in bins_julia:
    #     x_log,y_log,z_log = bin_data["position"]
    #     x_log,y_log,z_log = bin_data["position"]
    bin = Bin(textures, [40,0,20],[40,60,15])
    bins.append(bin)
        
def update_simulation():
    global robots_julia, boxes_julia
    r = requests.get(URL_BASE + LOCATION)
    datos = r.json()
    robots_julia = datos["robots"]
    boxes_julia = datos["boxes"]
            
def planoText():
    # activate textures
    glColor(1.0, 1.0, 1.0)
    #glEnable(GL_TEXTURE_2D)
    # front face
    #glBindTexture(GL_TEXTURE_2D, textures[0])  # Use the first texture
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(-DimBoard, 0, -DimBoard)
    
    glTexCoord2f(0.0, 1.0)
    glVertex3d(-DimBoard, 0, DimBoard)
    
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, -DimBoard)
    
    glEnd()
    # glDisable(GL_TEXTURE_2D)



def display():
    global robots_julia, boxes_julia
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
        
    for robot_data in robots_julia:
        x_log,y_log,z_log = robot_data["position"]
        robot = robots[robot_data["id"] - 1]
        
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
    for obj in bins:
        obj.draw()
    for box_data in boxes_julia:
        x_log,y_log,z_log = box_data["position"]
        box = boxes[box_data["id"] - 1]
        box.up([x_log,y_log,z_log])
        if box_data["showing"] == 1:
            box.draw()
        
    #Se dibuja el plano gris
    planoText()
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    
    # Draw the walls bounding the plane
    wall_height = 50.0  # Adjust the wall height as needed
    
    # glColor3f(0.8, 0.8, 0.8)  # Light gray color for walls
    
    # # Draw the left wall
    # glBegin(GL_QUADS)
    # glVertex3d(-DimBoard, 0, -DimBoard)
    # glVertex3d(-DimBoard, 0, DimBoard)
    # glVertex3d(-DimBoard, wall_height, DimBoard)
    # glVertex3d(-DimBoard, wall_height, -DimBoard)
    # glEnd()
    
    # # Draw the right wall
    # glBegin(GL_QUADS)
    # glVertex3d(DimBoard, 0, -DimBoard)
    # glVertex3d(DimBoard, 0, DimBoard)
    # glVertex3d(DimBoard, wall_height, DimBoard)
    # glVertex3d(DimBoard, wall_height, -DimBoard)
    # glEnd()
    
    # # Draw the front wall
    # glBegin(GL_QUADS)
    # glVertex3d(-DimBoard, 0, DimBoard)
    # glVertex3d(DimBoard, 0, DimBoard)
    # glVertex3d(DimBoard, wall_height, DimBoard)
    # glVertex3d(-DimBoard, wall_height, DimBoard)
    # glEnd()
    
    # # Draw the back wall
    # glBegin(GL_QUADS)
    # glVertex3d(-DimBoard, 0, -DimBoard)
    # glVertex3d(DimBoard, 0, -DimBoard)
    # glVertex3d(DimBoard, wall_height, -DimBoard)
    # glVertex3d(-DimBoard, wall_height, -DimBoard)
    # glEnd()

    
def lookAt():
    glLoadIdentity()
    rad = theta * math.pi / 180
    newX = EYE_X * math.cos(rad) + EYE_Z * math.sin(rad)
    newZ = -EYE_X * math.sin(rad) + EYE_Z * math.cos(rad)
    gluLookAt(newX,EYE_Y,newZ,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    
done = False
Init()
while not done:
    keys = pygame.key.get_pressed()  # Checking pressed keys
    if keys[pygame.K_RIGHT]:
        if theta > 359.0:
            theta = 0
        else:
            theta += 1.0
        lookAt()
    if keys[pygame.K_LEFT]:
        if theta < 1.0:
            theta = 360.0
        else:
            theta -= 1.0
        lookAt()

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