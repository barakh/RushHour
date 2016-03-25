from pprint import pprint
import socket

"""
Helper functions
"""

def send_command(car, command):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    sock.sendto(command, ("127.0.0.1", int(car)))
    sock.close()

def left(car):
    send_command(car, "left")
    
def right(car):
    send_command(car, "right")

def speed_up(car):
    send_command(car, "up")

def slow_down(car):
    send_command(car, "down")

"""
car_control
===========

This function runs every 100 miliseconds.

example input:
db = 
{
'10806': {'angle': '-0.25142812439204276',
           'listening_port': '10806',
           'x': '494.9052745360873',
           'y': '322.09201232436624'},
 '12588': {'angle': '0.29452586428448524',
           'listening_port': '12588',
           'x': '158.9297468979414',
           'y': '276.7557723004153'}
}
* listening_port is also the car ID
* The cars with the ID of 255/254 are actually the current location of the
* mouse pointer.
"""
count = 0
def car_control(db):
    global count
    count += 1
    if count == 2:
        for car in db:
            left(car)
        count = 0
        
