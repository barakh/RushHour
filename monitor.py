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
from car_control import car_control

UDP_IP = "127.0.0.1"
UDP_PORT = 5000
RE = re.compile("\((?P<listening_port>[-\d\.]*), \((?P<x>[-\d\.]*), (?P<y>[-\d.]*)\), (?P<angle>[-\d.]*)")

class Car(object):
    def __init__(self, pos, angle):
        self.pos = pos
        self.angle = angle

class Surface(object):
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640,480))
        self.car_size = 10

    def draw_car(self, pos, angle, color = (255, 0, 0)):
        start_x = int(pos[0] - (self.car_size * cos(angle)))
        end_x   = int(pos[0] + (self.car_size * cos(angle)))
        start_y = int(pos[1] - (self.car_size * sin(angle)))
        end_y   = int(pos[1] + (self.car_size * sin(angle)))
        pygame.draw.line(self.screen, color, (start_x, start_y), (end_x,
                         end_y), 5)

    def delete_car(self, pos, angle, color = (0, 0, 0)):
        """
        The color parameter is ignored.
        """
        self.draw_car(pos, angle, color = (0, 0, 0))

    def update(self):
        pygame.display.update()
        time.sleep(0.05)

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
        parsed = RE.match(data).groupdict()
        with db_lock:
            db[parsed['listening_port']] = parsed

def control(db, db_lock):
    while True:
        time.sleep(0.1)
        car_control(db)

def get_mouse():
    x = y = 0
    running = 1
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    while running:
        pygame.event.clear()
        time.sleep(0.05)
        event = pygame.event.poll()
        if event.type == pygame.MOUSEMOTION:
            data = pformat((255, event.pos, 0)) + "\n"
            sock.sendto(data, (UDP_IP, UDP_PORT))
            data = pformat((254, event.pos, pi / 2)) + "\n"
            sock.sendto(data, (UDP_IP, UDP_PORT))

def monitor(db, db_lock):
    surface = Surface()
    thread.start_new_thread(get_mouse, ())
    while True:
        #The temp db is used because the actual db may change during the
        #operation
        with db_lock:
            temp_db = []
            for car in db:
                x = float(db[car]["x"])
                y = float(db[car]["y"])
                angle = float(db[car]["angle"])
                temp_db.append(((x,y), angle, int(car, 16)))

        for car in temp_db:
            surface.draw_car(*car)
        surface.update()
        for car in temp_db:
            surface.delete_car(*car)
    
def main():
    db = {}
    db_lock = Lock()
    thread.start_new_thread(updater, (db, db_lock,))
    thread.start_new_thread(control, (db, db_lock,))
    thread.start_new_thread(monitor, (db, db_lock,))
    while True:
        time.sleep(1000)

if __name__ == "__main__":
    main()
