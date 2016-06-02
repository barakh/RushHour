import munkres
import toposort
import math
import dubins
import settings
from utils import *
import thread
import time

from car import main_loop

def main():
    CARS = 10
    START_PTS = []
    END_PTS = []
    for i in xrange(CARS):
        START_PTS += [(100+i*30, 500, -math.pi/2)]
        START_PTS += [(100+i*30, 400, -math.pi/2)]
        END_PTS += [(370-i*30, 100, -math.pi/2)]
        END_PTS += [(370-i*30, 200, -math.pi/2)]
    
    dist_matrix = []
    for start_pt in START_PTS:
        dist_vec = []
        for end_pt in END_PTS:
            dist_vec.append(dubins.path_length(start_pt, end_pt, settings.TURNING_RADIUS))
        print dist_vec
        dist_matrix.append(dist_vec)        
    
    m = munkres.Munkres()
    indices = m.compute(dist_matrix)
    
    d_pt_match = {}
    for start_pt_ind, end_pt_ind in indices:
        d_pt_match[start_pt_ind] = end_pt_ind
    
    cars = []
    for i in xrange(CARS):
        cars.append((START_PTS[i], END_PTS[d_pt_match[i]]))
        print cars[-1]    
    
    COLLISION_DIST = 5
    d_collisions = {}    
    for i, (start_pt, end_pt) in enumerate(cars):
        d_collisions[i] = set()
        path, t = dubins.path_sample(start_pt, end_pt, settings.TURNING_RADIUS, 0.1)
        for j, (temp_start_pt, temp_end_pt) in enumerate(cars):
            if j == i:
                continue
            for pt in path:
                if norm(sub_vecs(pt, temp_end_pt)) < COLLISION_DIST:
                    d_collisions[i].add(j)

    print d_collisions
    cars_order = list(toposort.toposort(d_collisions))
            
    for car_set in cars_order[::-1]:
        print "Creating cars", car_set
        for car_ind in car_set:
            thread.start_new_thread(main_loop, ((cars[car_ind][0][0], cars[car_ind][0][1]), cars[car_ind][0][2],
                                                (cars[car_ind][1][0], cars[car_ind][1][1]), cars[car_ind][1][2]))
        time.sleep(10)

if __name__ == "__main__":
    main()
