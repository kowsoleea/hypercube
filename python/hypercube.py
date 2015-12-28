#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0111
#
#  hypercube.py
#
#  Copyright 2015 ivan <ivan@ivan-X55A>
#
#


#a hypercube is a collection of lines, wich are point pairs.
#each point is a n-list.
#this functions returns the hypercube as a list
def make_hypercube(dimension):
    #make a hypercube with dimension - 1
    if dimension == 1:
        return [[[0],[1]]]
    else:
        lower_hycube = make_hypercube(dimension - 1)
        newlines = []
        for line in lower_hycube:
            p1low = list(line[0])
            p1high = list(line[0])
            p2low = list(line[1])
            p2high = list(line[1])
            p1low.append(0)
            p2low.append(0)
            p1high.append(1)
            p2high.append(1)
            newlines.append([p1low, p1high])
            newlines.append([p2low, p2high])
            newlines.append([p1low, p2low])
            newlines.append([p1high, p2high])
        return newlines
            
                
def dotproduct(v1, v2):
    sum = 0
    for i in range(len(v1)):
        sum = sum + v1[i] * v2[i]
    return sum

def addvectors(v1, v2):
    result = []
    for i in  range(len(v1)):
        result.append(v1[i] + v2[i])
    return result

def minusvector(v1):
    result = []
    for i in range(len(v1)):
        result.append(-v1[i])
    return result
    
def scalarmult(s, v):
    result = []
    for i in range(len(v)):
        result.append(s * v[i])
    return result


#a projection is a list of vectors with length 1 perpendicular to
#each other (e1, e2, e3), combined with a view_vector (v)
#like this [v, e1, e2, e3, ...]
#each vector has dimension n.
#the result of the projection of point p will result in a point pp
#with dimension n-1
def project(projection, p):
    v = scalarmult(1.0,projection[0])
    p_v = addvectors(p, minusvector(v))
    l = dotproduct(v, v) / dotproduct(v, p_v)
    pp = addvectors(v, minusvector(scalarmult(l, p_v)))
    evectors = projection[1:]
    newpp = []
    for ev in evectors:
        newpp.append(dotproduct(pp, ev))
    return newpp


def on_paper(point):
    origin_x = 250
    origin_y = 400
    scale_x = 400
    scale_y = 400
    px = origin_x + scale_x * point[0]
    py = origin_y - scale_y * point[1]
    return [px, py]

#<line x1="0" y1="0" x2="90" y2="20" style="stroke:rgb(0,0,0);stroke-width:1" />
def drawline(line):
    svg_string = ""
    outfile.write(svg_string)


def main():
    print project([[8, 0, 0], [0,1,0], [0,0,1]],[1,1,1])
    return 0


if __name__ == '__main__':
    main()



