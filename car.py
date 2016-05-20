# coding: utf-8
import thread
from math import sin, cos
import pygame
import time
import random
from random import randint
import socket
from pprint import pformat
import argparse

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 5000

"""
Car parameters
"""
TURNING_ANGLE = 0.2
ACCELERATION = 0.2
DECELERATION = -0.5
MAX_SPEED = 2

class Car(object):
    def __init__(self, start_point = (50,200), 
                 start_angle = 0, 
                 speed = 0,
                 listening_port = 0):
        self.set_location(start_point, start_angle, speed)
        self.listening_port = listening_port
        self.sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP

    def set_location(self, pos, angle, speed):
        self.pos = pos
        self.angle = angle
        self.speed = speed

    def make_step(self):
        x = (self.speed * cos(self.angle)) + self.pos[0]
        y = (self.speed * sin(self.angle)) + self.pos[1]
        self.pos = (x,y)
    
    def right(self):
        self.angle += TURNING_ANGLE

    def left(self):
        self.angle -= TURNING_ANGLE

    def speed_up(self):
        self.speed += ACCELERATION
        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED
        
    def slow_down(self):
        self.speed += DECELERATION
        if self.speed < 0:
            self.speed = 0

    def __repr__(self):
        return pformat((self.listening_port, self.pos, self.angle)) + "\n"

    def send_car_data(self):
        self.sock.sendto(repr(self), (UDP_SERVER_IP, UDP_SERVER_PORT))

def main_loop(): 
    listening_port = randint(10000,30000)
    sock_input = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock_input.bind((UDP_SERVER_IP, listening_port))
    sock_input.setblocking(False)

    c = Car(speed = 1.0, 
            start_point = (randint(100,500), randint(100,400)),
            listening_port = listening_port)
    while True:
        #TODO: Make this code pretty
        c.make_step()
        c.angle -= (0.5 - random.random()) / 10
        c.send_car_data()
        try:
            data, addr = sock_input.recvfrom(1024) # buffer size is 1024
            if data != "":
                if "right" in data:
                    c.right()
                elif "left" in data:
                    c.left()
                elif "up" in data:
                    c.speed_up()
                elif "down" in data:
                    c.slow_down()
        except socket.error:
            pass
        time.sleep(0.03)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p','--proc_num', type=int, default = 1,
                       help='Number of car processes to start')

    args = parser.parse_args()
    for i in xrange(args.proc_num):
        thread.start_new_thread(main_loop, ())

    while True:
        time.sleep(10000)

if __name__ == "__main__":
    main()
