from pprint import pprint
import socket
import dubins
from random import randint
from settings import *
import time
import math
from utils import *
from math import atan2, pi

"""
Helper functions
"""

def send_command(car, command):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    sock.sendto(command, ("127.0.0.1", int(car)))
    sock.close()

def move_car(car, left=False, right=False, up=False, down=False):
    cmd = ""
    if left:
        cmd += "left "
    elif right:
        cmd += "right "
    else:
        cmd += "straight "
    if up:
        cmd += "up "
    elif down:
        cmd += "down "
    else:
        cmd += "stop "
    #print cmd
    send_command(car, cmd)

def left(car):
    send_command(car, "left")
    
def right(car):
    send_command(car, "right")

def speed_up(car):
    send_command(car, "up")

def slow_down(car):
    send_command(car, "down")

class CarState(object):
    def __init__(self, point, angle, t):
        self.point = point
        self.angle = angle
        self.t = t

    def get_xy_angle(self):
        return (self.point[0],
                self.point[1],
                self.angle)

class CarMovementDubins(object):
    PATH_LENGTH_TOLERANCE = 50

    def __init__(self, end_state):
        self._end_state = end_state
        self._prev_state = None
        self._prev_time = None
        self._prev_path_length = WIDTH*HEIGHT
        self.stop_dubins = False
        self.remaining_path_length = 0

    def _get_speed(self, curr_state):
        if self._prev_state is None:
            self._prev_state = curr_state
            return 0
        else:
            delta_t = curr_state.t - self._prev_state.t
        if delta_t == 0:
            return 0

        v = sub_vecs(curr_state.point, self._prev_state.point)
        speed = norm(v)/delta_t

        self._prev_state = curr_state

        return speed

    def do_next_step(self, curr_state, car):
        #move_car(car, False, True, True, False)
        #return

        curr = curr_state.get_xy_angle()
        end = self._end_state.get_xy_angle()

        speed = self._get_speed(curr_state)

        right = False
        left = False

        next_move = dubins.next_move(curr, end, TURNING_RADIUS, 0.0001)
        d = norm(sub_vecs(curr,end))
        if self.stop_dubins:            
            self.remaining_path_length = TURNING_RADIUS*2*math.asin(d/(2*TURNING_RADIUS))
        else:
            self.remaining_path_length = dubins.path_length(curr, end, TURNING_RADIUS)
        
        vec_to_end_point = sub_vecs(end_state.point, curr_state.point)
        dist_to_end_point = norm(vec_to_end_point)
        if ((self.remaining_path_length - self._prev_path_length) > CarMovementDubins.PATH_LENGTH_TOLERANCE) or (self.stop_dubins):
            # Dubins missed
            #print "Dubins missed, dist to point:", dist_to_end_point
            
            angle_to_end_point = atan2(vec_to_end_point[1], vec_to_end_point[0])
            #print "Angle to end point:", angle_to_end_point
            
            if (angle_to_end_point-curr_state.angle)%(2*pi) < pi:
                right = True
            else:
                left = True       
            #if left:
            #    print "Turning left"
            #else:
            #    print "Turning right"
            self.stop_dubins = True
            
                
        else:
            left = (next_move == dubins.RIGHT)
            right = (next_move == dubins.LEFT)
            self._prev_path_length = self.remaining_path_length
            
        
        forward = True
        if( self.remaining_path_length<(speed*speed/(2*DECELERATION*0.9)) or self.remaining_path_length<50):
            forward = False            
        
        move_car(car, left, right, forward, False)

#        if dist_to_end_point < 10:
 #           print curr_state.angle
        
        
class CarMovementFollowPath(object):
    NEAR_FINISH_WINDOW_SIZE = 10
    STRAIGHT_ANGLE_TOL = 0.3

    def __init__(self, path, delta_sample):
        self._prev_state = None
        self._path = path
        self._delta_sample = delta_sample;
        self._total_length = (len(path)-1)*delta_sample
        self._total_visited_length = 0
        self._stopping = False
        self._stopping_final = False
        self._min_remaining_length = 10e8

    def _get_speed_delta_t(self, curr_state):
        if self._prev_state is None:
            self._prev_state = curr_state
            return 0, 0
        else:
            delta_t = curr_state.t - self._prev_state.t
        if delta_t == 0:
            return 0, 0

        v = sub_vecs(curr_state.point, self._prev_state.point)
        speed = norm(v)/delta_t

        self._prev_state = curr_state

        return speed, delta_t

    def do_next_step(self, curr_state, car, rabbit_db, rabbit_db_lock):
        curr = curr_state.get_xy_angle()
        
        speed, delta_t = self._get_speed_delta_t(curr_state)
        self._total_visited_length += speed * delta_t
        
        curr_ind = int(self._total_visited_length/self._delta_sample)+100
        if curr_ind >= len(self._path) - CarMovementFollowPath.NEAR_FINISH_WINDOW_SIZE:
            curr_ind = len(self._path) - 1
        
        next_point = self._path[curr_ind]
        
        with rabbit_db_lock:
            rabbit_db[car] = next_point

        right = False
        left = False

        d = norm(sub_vecs(curr, next_point))
        
        remaining_path_length = self._total_length - self._total_visited_length
        
        vec_to_end_point = sub_vecs(next_point, curr_state.point)
        dist_to_end_point = norm(vec_to_end_point)
                      
        angle_to_end_point = atan2(vec_to_end_point[1], vec_to_end_point[0])        
        
        delta_angle = (angle_to_end_point-curr_state.angle)%(2*pi) - pi
        if abs(delta_angle) > CarMovementFollowPath.STRAIGHT_ANGLE_TOL:
            if delta_angle < 0:
                right = True
            else:
                left = True                                       
            
        forward = True
         

        remaining_path_length_ext = max(remaining_path_length,dist_to_end_point)
            
        if remaining_path_length_ext<(speed*speed/(2*DECELERATION)):
            forward = False
            self._stopping = True
        
        if (self._stopping) and (self._min_remaining_length < remaining_path_length_ext-10):
            forward = False
            self._stopping_final = True
        
        if self._min_remaining_length < 10:
            self._stopping_final = True            
        
        if self._stopping_final:
            forward = False
            
        self._min_remaining_length = min(self._min_remaining_length, remaining_path_length_ext)
                
        move_car(car, left, right, forward, False)        



end_state = CarState(END_POINT,
                     END_ANGLE,
                     0)
#car_movement = CarMovementDubins(end_state)
car_movement = {}

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
def car_control(db, rabbit_db, rabbit_db_lock, e_state = None):
    global car_movement
    global end_state
         
    for car in db:
        curr_car = db[car]
        curr_state = CarState((float(curr_car['x']),
                               float(curr_car['y'])),
                              float(curr_car['angle']),
                              float(curr_car['time']))
        
        if end_state != e_state:
        #if car not in car_movement:
            """end_state = CarState((float(curr_car['end_x']),
                               float(curr_car['end_y'])),
                              float(curr_car['end_angle']),
                              float(curr_car['time']))"""
            end_state = e_state
            DELTA_SAMPLE = 0.1
            path, time = dubins.path_sample(curr_state.get_xy_angle(), end_state.get_xy_angle(), TURNING_RADIUS, DELTA_SAMPLE)                
            car_movement[car] = CarMovementFollowPath(path, DELTA_SAMPLE)
        
        car_movement[car].do_next_step(curr_state, car, rabbit_db, rabbit_db_lock)

