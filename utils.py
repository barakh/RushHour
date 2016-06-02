from math import pow, sqrt

def sub_vecs(v1, v2):
    return (v1[0]-v2[0], v1[1]-v2[1])

def norm(v):
    return sqrt(v[0]*v[0] + v[1]*v[1])