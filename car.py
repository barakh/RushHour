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

class Car(object):
    def __init__(self, start_point = (50,200), 
                 start_angle = 0, 
                 speed = 0,
                 listening_port = 0):
        self.pos = start_point
        self.angle = float(start_angle)
        self.speed = speed
        self.listening_port = listening_port

    def make_step(self):
        x = (self.speed * cos(self.angle)) + self.pos[0]
        y = (self.speed * sin(self.angle)) + self.pos[1]
        self.pos = (x,y)

    def __repr__(self):
        return pformat((self.listening_port, self.pos, self.angle)) + "\n"

def main_loop(): 
    listening_port = randint(10000,30000)
    sock_input = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock_input.bind((UDP_SERVER_IP, listening_port))
    sock_input.setblocking(False)

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    c = Car(speed = 1.0, 
            start_point = (randint(100,500), randint(100,400)),
            listening_port = listening_port)
    while True:
        #TODO: Make this code pretty
        c.make_step()
        c.angle -= (0.5 - random.random()) / 10
        sock.sendto(repr(c), (UDP_SERVER_IP, UDP_SERVER_PORT))
        try:
            data, addr = sock_input.recvfrom(1024) # buffer size is 1024
            if data != "":
                if "right" in data:
                    c.angle += 0.2
                elif "left" in data:
                    c.angle -= 0.2
                elif "up" in data:
                    c.speed += 1
                elif "down" in data:
                    c.speed -= 1
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
