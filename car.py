# coding: utf-8
import thread
from math import sin, cos, pi, pow, sqrt
import pygame
import time
import random
from random import randint
import socket
from pprint import pformat
import argparse
from settings import *
import settings
from serial import Serial

COM_PORT = "/dev/ttyACM0"
COM = Serial(COM_PORT, 115200)
#COM = open("temp.txt", "w")

UDP_SERVER_IP = "127.0.0.1"
UDP_SERVER_PORT = 5000

"""
Car parameters
"""


class Car(object):
    def __init__(self, start_point = (50,200), 
                 start_angle = 0, 
                 end_point = (100, 300),
                 end_angle = 0,
                 speed = 0,
                 listening_port = 0,
                 car_ind = 8):
        self.set_location(start_point, start_angle, speed)
        self.listening_port = listening_port
        self.sock = socket.socket(socket.AF_INET, # Internet
                             socket.SOCK_DGRAM) # UDP
        self.turning = 0
        self.throttle = 0
        self.prev_t = None
        self.end_pos = end_point
        self.end_angle = end_angle
        self.car_ind = car_ind
        self.com = COM
        self.UP = car_ind
        self.LEFT = car_ind+1
        self.RIGHT = car_ind+2
        for i in xrange(3):
            self.com.write(chr(0x10 | (car_ind+i)))
        #self.com.write("\x08\x09\x0a")

    def set_location(self, pos, angle, speed):
        self.pos = pos
        self.angle = angle
        self.speed = speed

    def make_step(self):
        t = time.time()
        if self.prev_t is not None:
            delta_t = t-self.prev_t

            self.speed += (self.throttle*(ACCELERATION+DECELERATION))*delta_t
            if self.speed > 0:
                sign = 1
            else:
                sign = -1
            
            if (self.speed*sign)<DECELERATION*delta_t:
                self.speed = 0
            else:
                self.speed-=sign*DECELERATION*delta_t
            
            
            
            if self.speed > MAX_SPEED:
                self.speed = MAX_SPEED
            if self.speed < -MAX_SPEED:
                self.speed = -MAX_SPEED

            self.angle += self.turning*self.speed*delta_t/TURNING_RADIUS
            self.angle = self.angle % (2*pi)

            x = (self.speed * cos(self.angle)) * delta_t + self.pos[0]
            y = (self.speed * sin(self.angle)) * delta_t + self.pos[1]

            self.pos = (x,y)

        self.prev_t = t
    
    def right(self):
        self.turning = 1
        self.com.write(chr(self.LEFT | 0x10) + chr(self.RIGHT))
        #self.com.write("\x19\x0a")

    def left(self):
        self.turning = -1
        #self.com.write("\x09\x1a")
        self.com.write(chr(self.RIGHT | 0x10) + chr(self.LEFT))

    def straight(self):
        self.turning = 0
        #self.com.write("\x09\x0a")
        self.com.write(chr(self.LEFT | 0x10) + chr(self.RIGHT | 0x10))

    def up(self):
        self.throttle = 1
        #self.com.write("\x08")
        self.com.write(chr(self.UP))

    def down(self):
        self.throttle = -1

    def stop(self):
        self.throttle = 0
        #self.com.write("\x18")
        self.com.write(chr(self.UP | 0x10))

    def __repr__(self):
        temp = pformat((self.listening_port, self.pos, self.angle, time.time()+1, self.end_pos, self.end_angle)) + "\n"
        return temp

    def send_car_data(self):
        self.sock.sendto(repr(self), (UDP_SERVER_IP, UDP_SERVER_PORT))

def main_loop(start_point, start_angle, end_point, end_angle): 
    listening_port = randint(10000,30000)
    sock_input = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock_input.bind((UDP_SERVER_IP, listening_port))
    sock_input.setblocking(False)

    c = Car(speed = 1.0,
            start_point = start_point, #(randint(100,500), randint(100,400)),
            start_angle = start_angle,
            end_point = end_point,
            end_angle = end_angle,
            listening_port = listening_port)
    while True:
        #TODO: Make this code pretty
        c.make_step()
        #c.angle -= ((0.5 - random.random()) / 10)*c.speed/100
        c.send_car_data()
        try:
            data, addr = sock_input.recvfrom(1024) # buffer size is 1024
            if data != "":
                cmds = {
                    "right": c.right,
                    "left": c.left,
                    "straight": c.straight,
                    "up": c.up,
                    "down": c.down,
                    "stop": c.stop
                }
                for cmd, op in cmds.items():
                    if cmd in data:
                        op()
        except socket.error:
            pass
        time.sleep(0.03)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-p','--proc_num', type=int, default = 1,
                       help='Number of car processes to start')
    parser.add_argument('-x','--x', type=float, default = START_POINT[0],
                       help='X coord')
    parser.add_argument('-y','--y', type=float, default = START_POINT[1],
                       help='Y coord')
    parser.add_argument('-a','--angle', type=float, default = START_ANGLE,
                       help='Angle')

    args = parser.parse_args()
    for i in xrange(args.proc_num):
        thread.start_new_thread(main_loop, ((args.x, args.y), args.angle, settings.END_POINT, settings.END_ANGLE))

    while True:
        time.sleep(10000)

if __name__ == "__main__":
    main()
