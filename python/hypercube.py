#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0111, C0103
#
#  hypercube.py
#
#  Copyright 2015 ivan <ivan@ivan-X55A>
#
#

import math
import ConfigParser

INIFILE = "hypercube.ini"
IMAGEFILE = "hypercube.svg"


#a hypercube is a collection of lines, wich are point pairs.
#each point is a n-list.
#this functions returns the hypercube as a list
def make_hypercube(dimension):
    #make a hypercube with dimension
    if dimension == 1:
        return [[[-1], [1]]]
    else:
        lower_hycube = make_hypercube(dimension - 1)
        newlines = []
        for line in lower_hycube:
            p1low = list(line[0])
            p1high = list(line[0])
            p2low = list(line[1])
            p2high = list(line[1])
            p1low.append(-1)
            p2low.append(-1)
            p1high.append(1)
            p2high.append(1)
            newlines.append([p1low, p1high])
            newlines.append([p2low, p2high])
            newlines.append([p1low, p2low])
            newlines.append([p1high, p2high])
        return newlines



hypercrosslength = 2
hypercrosscross = 0.5
def make_hypercross(dimension):
    if dimension == 1:
        return [[0], [hypercrosslength]]
    else:
        lines = []
        zero = [0 for _ in range(dimension)]
        for i in range(dimension):
            s = [0 for _ in range(dimension)]
            s[i] = hypercrosslength
            c = [s[k] for k in range(dimension)]
            j = i + 1
            j = j if j < dimension else 0
            c[j] = hypercrosscross
            lines.append([zero, s])
            lines.append([s, c])
    return lines

def dotproduct(v1, v2):
    vsum = 0
    for i in range(len(v1)):
        vsum = vsum + v1[i] * v2[i]
    return vsum

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
#each vector has dimension n.
#the result of the projection of point p will result in a point pp
#with dimension n-1

class Projection(object):
    dimension = 2 #projects from 3 onto 2 dimensions
    distance = 10 #default
    view_vector = []
    unit_vectors = []

    def __init__(self, dimension=2, distance=10):
        self.dimension = dimension
        self.distance = distance
        self.view_vector = [0 for _ in range(self.dimension + 1)]
        self.view_vector[self.dimension] = self.distance
        self.unit_vectors = []
        self.rotmatrix = []
        for i in range(self.dimension):
            e = [0 for _ in range(self.dimension + 1)]
            e[i] = 1
            self.unit_vectors.append(e)

    def set_distance(self, d):
        v = self.view_vector
        scalar = d / math.sqrt(dotproduct(v, v))
        v = scalarmult(scalar, v)
        self.view_vector = v
        self.distance = d

    def project_point(self, p):
        v = scalarmult(1.0, self.view_vector)
        p_v = addvectors(p, minusvector(v))
        l = dotproduct(v, v) / dotproduct(v, p_v)
        pp = addvectors(v, minusvector(scalarmult(l, p_v)))
        pp_coords = []
        for uv in self.unit_vectors:
            pp_coords.append(dotproduct(pp, uv))
        return pp_coords

    def project_line(self, l):
        result_line = []
        result_line.append(self.project_point(l[0]))
        result_line.append(self.project_point(l[1]))
        return result_line

    def project_all_lines(self, lines):
        result_lines = []
        for l in lines:
            result_lines.append(self.project_line(l))
        return result_lines

    def make_rotate_matrix(self, axis1, axis2, angle):
        '''angle in degrees; axis1, axis2: 0..n index
        of coordinates that should be affected by rotation'''
        a_rad = (angle * math.pi) / 180.0
        #a matrix is a list of vectors (more or less)
        self.rotmatrix = []
        for i in range(self.dimension + 1):
            vec = [0 for _ in range(self.dimension + 1)]
            vec[i] = 1
            self.rotmatrix.append(vec)
        #now we have the unity matrix
        sin_a = math.sin(a_rad)
        cos_a = math.cos(a_rad)
        self.rotmatrix[axis1][axis1] = cos_a
        self.rotmatrix[axis2][axis1] = sin_a
        self.rotmatrix[axis1][axis2] = - sin_a
        self.rotmatrix[axis2][axis2] = cos_a

    def rotate_point(self, p):
        pr = [0 for _ in range(self.dimension + 1)]
        for i in range(self.dimension + 1):
            for j in range(self.dimension + 1):
                pr[i] += self.rotmatrix[i][j] * p[j]
        return pr

    def rotate(self, axis1, axis2, angle):
        self.make_rotate_matrix(axis1, axis2, angle)
        self.view_vector = self.rotate_point(self.view_vector)
        for i in range(self.dimension):
            self.unit_vectors[i] = self.rotate_point(self.unit_vectors[i])



class SVG_file(object):
    width = 1000
    height = 1000
    scale = 300
    output_file = ''

    def __init__(self, width=1000, height=1000, scale=300, outfile=IMAGEFILE):
        self.width = width
        self.height = height
        self.origin_x = int(width / 2.0)
        self.origin_y = int(height / 2.0)
        self.scale_x = scale
        self.scale_y = scale
        self.output_file = outfile

    def set_scale(self, scale):
        self.scale_x = scale
        self.scale_y = scale

    def set_width(self, width):
        self.width = width
        self.origin_x = int(width / 2.0)

    def set_height(self, height):
        self.height = height
        self.origin_y = int(height / 2.0)

    def make_point(self, point):
        px = int(self.origin_x + self.scale * point[0])
        py = int(self.origin_y - self.scale * point[1])
        return [px, py]

    #<line x1="0" y1="0" x2="90" y2="20"
    #style="stroke:rgb(0,0,0);stroke-width:1" />
    def make_line(self, line):
        p1 = self.make_point(line[0])
        p2 = self.make_point(line[1])
        svg_string = '     <line x1="{0}" y1="{1}" x2="{2}" y2="{3}" \
        style="stroke:rgb(0,0,0);stroke-width:1" />'.format(p1[0],
                                                            p1[1],
                                                            p2[0],
                                                            p2[1])
        return svg_string

    def make_svg(self, lines):
        of = open(self.output_file, 'w')
        of.write('<?xml version="1.0" encoding="utf-8"?>\n')
        of.write('<svg xmlns="http://www.w3.org/2000/svg"\n')
        of.write('     xmlns:xlink="http://www.w3.org/1999/xlink"\n')
        of.write('     width="{0}" height="{1}">\n'.format(self.width,
                                                           self.height))
        for l in lines:
            of.write(self.make_line(l) + '\n')
        of.write('</svg>\n')
        of.close()

def read_inifile(p3, p2, svg):
    config = ConfigParser.SafeConfigParser()
    config.read(INIFILE)
    p3options = config.items('project4to3')
    for option in p3options:
        name, value = option
        if name == 'distance':
            p3.set_distance(float(value))
        if name.startswith('rot'):
            rotlist = value.split(',')
            p3.rotate(int(rotlist[0]), int(rotlist[1]), int(rotlist[2]))
    p2options = config.items('project3to2')
    for option in p2options:
        name, value = option
        if name == 'distance':
            p2.set_distance(float(value))
        if name.startswith('rot'):
            rotlist = value.split(',')
            p2.rotate(int(rotlist[0]), int(rotlist[1]), int(rotlist[2]))
    svgoptions = config.items('svg')
    for option in svgoptions:
        name, value = option
        if name == 'width':
            svg.set_width(int(value, 10))
        elif name == 'height':
            svg.set_height(int(value, 10))
        elif name == 'scale':
            svg.set_scale(int(value, 10))
        elif name == 'outfile':
            svg.output_file = value
    return p3, p2, svg

def main():
    # p2 = Projection(2)
    # p3 = Projection(3)
    # svg = SVG_file()
    # p3, p2, svg = read_inifile(p3, p2, svg)
    #now do the work
    # hc = make_hypercube(4)
    # hc3 = p3.project_all_lines(hc)
    # hc2 = p2.project_all_lines(hc3)
    # svg.make_svg(hc2)
    p2 = Projection(2)
    p3 = Projection(3)
    svg = SVG_file()
    p3, p2, svg = read_inifile(p3, p2, svg)
    #now do the work
##    hc = make_hypercube(4)
##    hc3 = p3.project_all_lines(hc)
##    hc2 = p2.project_all_lines(hc3)
##    svg.make_svg(hc2)
    hc = make_hypercross(4)
    hc_3 = p3.project_all_lines(hc)
    hc_2 = p2.project_all_lines(hc_3)
    svg.make_svg(hc_2)
    return 0


if __name__ == '__main__':
    main()
