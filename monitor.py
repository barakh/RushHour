# coding: utf-8
from math import sin, cos, pi
import pygame
import time
import random
import socket
import re
import thread
from pprint import pprint
from pprint import pformat
from threading import Lock
from car_control import car_control, CarState
import dubins

from settings import *

DEBUG = True
UDP_IP = "127.0.0.1"
UDP_PORT = 5000
RE = re.compile("\((?P<listening_port>[-\d\.]*), \((?P<x>[-\d\.]*), (?P<y>[-\d.]*)\), (?P<angle>[-\d.]*), (?P<time>[-\d.]*), \((?P<end_x>[-\d\.]*), (?P<end_y>[-\d.]*)\), (?P<end_angle>[-\d.]*)")

class Car(object):
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle

class Surface(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.car_size = 10

    def draw_car(self, pos, angle, color = (255, 0, 0)):
        start_x = int(pos[0] - (self.car_size * cos(angle)))
        end_x   = int(pos[0] + (self.car_size * cos(angle)))
        start_y = int(pos[1] - (self.car_size * sin(angle)))
        end_y   = int(pos[1] + (self.car_size * sin(angle)))
        pygame.draw.line(self.screen, color, (start_x, start_y), (end_x,
        end_y))
        #                 end_y), 5)
        #self.draw_dest(pos, color)

    def draw_dest(self, dest, color = (255, 0, 0)):
        pygame.draw.circle(self.screen, color, (int(dest[0]),int(dest[1])), 5, 5)

    def draw_path(self, path, color = (0, 255, 0)):
        for p in path:
            pygame.draw.circle(self.screen, color, (int(p[0]),int(p[1])), 1, 1)

    def delete_car(self, pos, angle, color = (0, 0, 0)):
        """
        The color parameter is ignored.
        """
        self.draw_car(pos, angle, color = (0, 0, 0))

    def update(self):
        pygame.display.update()
        time.sleep(0.5)

def updater(db, db_lock):
    """
    This is the only function that update the DB
    """
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    #sock.settimeout(0.1)
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024
        data = data.replace("\n","")
        if DEBUG:
            print data
        parsed = RE.match(data).groupdict()
        with db_lock:
            db[parsed['listening_port']] = parsed

curr_end_state = CarState(END_POINT,
                        END_ANGLE,
                            0)

def control(db, db_lock, rabbit_db, rabbit_db_lock):
    while True:
        time.sleep(0.1)
        with db_lock:
            car_control(db, rabbit_db, rabbit_db_lock, curr_end_state)

def get_mouse():
    global curr_end_state
    x = y = 0
    running = 1
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    while running:
        pygame.event.clear()
        time.sleep(0.05)
        event = pygame.event.poll()
        if event.type == pygame.MOUSEMOTION:
            curr_end_state = CarState(event.pos,
                    END_ANGLE,
                    0)
            #data = pformat((255, event.pos, 0)) + "\n"
            #sock.sendto(data, (UDP_IP, UDP_PORT))
            #data = pformat((254, event.pos, pi / 2)) + "\n"
            #sock.sendto(data, (UDP_IP, UDP_PORT))

def monitor(db, db_lock, rabbit_db, rabbit_db_lock):
    surface = Surface()
    path, t = dubins.path_sample((START_POINT[0], START_POINT[1], START_ANGLE),
                       (END_POINT[0], END_POINT[1], END_ANGLE),
                       TURNING_RADIUS, 0.1)
    surface.draw_path(path)
    thread.start_new_thread(get_mouse, ())
    while True:
        #The temp db is used because the actual db may change during the
        #operation
        with db_lock:
            temp_db = []
            temp_db_end_pts = []
            for car in db:
                x = float(db[car]["x"])
                y = float(db[car]["y"])
                angle = float(db[car]["angle"])
                                             
                #temp_db.append(((x,y), angle, int(car, 16)))
                temp_db.append(((x,y), angle, 0xff))                                
                
                end_x = float(db[car]["end_x"])
                end_y = float(db[car]["end_y"])
                end_angle = float(db[car]["end_angle"])
                temp_db_end_pts.append((end_x, end_y))                                

        with rabbit_db_lock:
            temp_rabbit_db = []
            for car in rabbit_db:                                            
                temp_rabbit_db.append(rabbit_db[car])    

        for car in temp_db:
            surface.draw_car(*car)
        
        for end_pt in temp_db_end_pts:
            surface.draw_dest(end_pt)
        
        for rabbit in temp_rabbit_db:
            surface.draw_dest(rabbit, (255, 255, 255))

        surface.update()
        for car in temp_db:
            surface.delete_car(*car)
        for rabbit in temp_rabbit_db:
            surface.draw_dest(rabbit, (0, 0, 0))
    
def main():
    db = {}
    db_lock = Lock()
    rabbit_db = {}
    rabbit_db_lock = Lock()

    thread.start_new_thread(updater, (db, db_lock,))
    thread.start_new_thread(control, (db, db_lock, rabbit_db, rabbit_db_lock,))
    thread.start_new_thread(monitor, (db, db_lock, rabbit_db, rabbit_db_lock,))
    while True:
        time.sleep(1000)

if __name__ == "__main__":
    main()
