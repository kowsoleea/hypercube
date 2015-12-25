/*jslint browser: true, devel: true, sloppy: true*/
/*globals $*/

var canvas;
var ctx;
//screen
var scale = 180;
var origin = {x: 600, y: 300};
//viewpoint 3D
var vp3 = {x: 0, y: 0, z: 10};
var e31 = {x: 1, y: 0, z: 0};
var e32 = {x: 0, y: 1, z: 0};
//viewpoint 4D
var vp4 = {w: 0, x: 0, y: 0, z: 10};
var e41 = {w: 1, x: 0, y: 0, z: 0};
var e42 = {w: 0, x: 1, y: 0, z: 0};
var e43 = {w: 0, x: 0, y: 1, z: 0};

//object constructors
function Point(x, y) {
    this.x = x;
    this.y = y;
    this.absval = function () {
        return Math.sqrt(this.x * this.x + this.y * this.y);
    };
    this.plus = function (p) {
        return new Point(this.x + p.x, this.y + p.y);
    };
    this.minus = function (p) {
        return new Point(this.x - p.x, this.y - p.y);
    };
    this.dotproduct = function (p) {
        return this.x * p.x + this.y * p.y;
    };
    this.scalproduct = function (a) {
        return new Point(a * this.x, a * this.y);
    };
}

function Point3D(x, y, z) {
    this.x = x;
    this.y = y;
    this.z = z;
    this.absval = function () {
        return Math.sqrt(this.x * this.x + this.y * this.y + this.z * this.z);
    };
    this.plus = function (p) {
        return new Point3D(this.x + p.x, this.y + p.y, this.z + p.z);
    };
    this.minus = function (p) {
        return new Point3D(this.x - p.x, this.y - p.y, this.z - p.z);
    };
    this.dotproduct = function (p) {
        return this.x * p.x + this.y * p.y + this.z * p.z;
    };
    this.scalproduct = function (a) {
        return new Point3D(a * this.x, a * this.y, a * this.z);
    };
}

function Point4D(w, x, y, z) {
    this.w = w;
    this.x = x;
    this.y = y;
    this.z = z;
    this.absval = function () {
        return Math.sqrt(this.w * this.w + this.x * this.x + this.y * this.y + this.z * this.z);
    };
    this.plus = function (p) {
        return new Point4D(this.w + p.w, this.x + p.x, this.y + p.y, this.z + p.z);
    };
    this.minus = function (p) {
        return new Point4D(this.w - p.w, this.x - p.x, this.y - p.y, this.z - p.z);
    };
    this.dotproduct = function (p) {
        return this.w * p.w + this.x * p.x + this.y * p.y + this.z * p.z;
    };
    this.scalproduct = function (a) {
        return new Point4D(a * this.w, a * this.x, a * this.y, a * this.z);
    };
}

function rotate3d(p, alpha) {
    var cos = Math.cos(alpha),
        sin = Math.sin(alpha),
        //pp = new Point3D(p.x, p.y * cos  + p.z * sin, p.z * cos - p.y * sin); // x invariant
        pp = new Point3D(p.x * cos + p.z * sin, p.y, p.z * cos - p.x * sin); // y invariant
    return pp;
}


function rotate4d(p, alpha) {
    var cos = Math.cos(alpha),
        sin = Math.sin(alpha),
        pp = new Point4D(p.w, p.x, p.y * cos + p.z * sin, p.z * cos - p.y * sin); // w, x invariant*
        //pp = new Point4D(p.w, p.x * cos + p.z * sin, p.y, p.z * cos - p.x * sin); // w, y invariant
        //pp = new Point4D(p.w, p.x * cos + p.y * sin, p.y * cos - p.x * sin, p.z); // w, z invariant
        //pp = new Point4D(p.w * cos + p.z * sin, p.x, p.y, p.z * cos - p.w * sin); // x, y invariant
        //pp = new Point4D(p.w * cos + p.y * sin, p.x, p.y * cos - p.w * sin, p.z); // x, z invariant
        //pp = new Point4D(p.w * cos + p.x * sin, p.x * cos - p.w * sin, p.y, p.z); // y, z invariant
    return pp;
}



//define viewpoints
var viewpoint3D = {
    v: new Point3D(vp3.x, vp3.y, vp3.z),
    e1: new Point3D(e31.x, e31.y, e31.z),
    e2: new Point3D(e32.x, e32.y, e32.z),
    rotate: function (alpha) {
        this.v = rotate3d(this.v, alpha);
        this.e1 = rotate3d(this.e1, alpha);
        this.e2 = rotate3d(this.e2, alpha);
    }
};
    
var viewpoint4D = {
    v: new Point4D(vp4.w, vp4.x, vp4.y, vp4.z),
    e1: new Point4D(e41.w, e41.x, e41.y, e41.z),
    e2: new Point4D(e42.w, e42.x, e42.y, e42.z),
    e3: new Point4D(e43.w, e43.x, e43.y, e43.z),
    rotate: function (alpha) {
        this.v = rotate4d(this.v, alpha);
        this.e1 = rotate4d(this.e1, alpha);
        this.e2 = rotate4d(this.e2, alpha);
        this.e3 = rotate4d(this.e3, alpha);
    }
};

//project 3d point into 2d plane
function project3to2(p) {
    var v = viewpoint3D.v,
        pv = p.minus(v),
        lambda = -1 * v.dotproduct(v) / v.dotproduct(pv),
        pp = pv.scalproduct(lambda).plus(v),
        p1 = pp.dotproduct(viewpoint3D.e1),
        p2 = pp.dotproduct(viewpoint3D.e2);
    return new Point(p1, p2);
}


//project 4d point in 3d space
function project4to3(p) {
    var v = viewpoint4D.v,
        pv = p.minus(v),
        lambda = -1 * v.dotproduct(v) / v.dotproduct(pv),
        pp = pv.scalproduct(lambda).plus(v),
        p1 = pp.dotproduct(viewpoint4D.e1),
        p2 = pp.dotproduct(viewpoint4D.e2),
        p3 = pp.dotproduct(viewpoint4D.e3);
    return new Point3D(p1, p2, p3);
}

//calculate screen coordinates
function translate(p) {
    return new Point(Math.floor(origin.x + scale * p.x), Math.floor(origin.y - scale * p.y));
}


function draw_path3d(p) {
    var i, pp;
    ctx.beginPath();
    pp = translate(project3to2(p[0]));
    ctx.moveTo(pp.x, pp.y);
    for (i = 1; i < p.length; i = i + 1) {
        pp = translate(project3to2(p[i]));
        ctx.lineTo(pp.x, pp.y);
    }
    ctx.stroke();
}

function draw_path4d(p) {
    var i, pp;
    ctx.beginPath();
    pp = translate(project3to2(project4to3(p[0])));
    ctx.moveTo(pp.x, pp.y);
    for (i = 1; i < p.length; i = i + 1) {
        pp = translate(project3to2(project4to3(p[i])));
        ctx.lineTo(pp.x, pp.y);
    }
    ctx.stroke();
}



var cube = {
    p1: new Point3D(-1, -1, -1),
    p2: new Point3D(1, -1, -1),
    p3: new Point3D(1, -1, 1),
    p4: new Point3D(-1, -1, 1),
    q1: new Point3D(-1, 1, -1),
    q2: new Point3D(1, 1, -1),
    q3: new Point3D(1, 1, 1),
    q4: new Point3D(-1, 1, 1),
    draw: function () {
        draw_path3d([this.p1, this.p2, this.p3, this.p4, this.p1, this.q1, this.q2, this.q3, this.q4, this.q1]);
        draw_path3d([this.p2, this.q2]);
        draw_path3d([this.p3, this.q3]);
        draw_path3d([this.p4, this.q4]);
    }
};

function draw_cube() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    cube.draw();
    //rotate viewpoint
    viewpoint3D.rotate(Math.PI / 360);
    //request next animation frame
    window.requestAnimationFrame(draw_cube);
}

var hypercube = {
    p1: new Point4D(-1, -1, -1, -1),
    p2: new Point4D(1, -1, -1, -1),
    p3: new Point4D(1, -1, 1, -1),
    p4: new Point4D(-1, -1, 1, -1),
    q1: new Point4D(-1, 1, -1, -1),
    q2: new Point4D(1, 1, -1, -1),
    q3: new Point4D(1, 1, 1, -1),
    q4: new Point4D(-1, 1, 1, -1),
    r1: new Point4D(-1, -1, -1, 1),
    r2: new Point4D(1, -1, -1, 1),
    r3: new Point4D(1, -1, 1, 1),
    r4: new Point4D(-1, -1, 1, 1),
    s1: new Point4D(-1, 1, -1, 1),
    s2: new Point4D(1, 1, -1, 1),
    s3: new Point4D(1, 1, 1, 1),
    s4: new Point4D(-1, 1, 1, 1),
    draw: function () {
        draw_path4d([this.r1, this.p1, this.p2, this.p3, this.p4,
                     this.p1, this.q1, this.q2, this.q3, this.q4, this.q1]);
        draw_path4d([this.r1, this.r2, this.r3, this.r4, this.r1,
                     this.s1, this.s2, this.s3, this.s4, this.s1, this.q1]);
        draw_path4d([this.r2, this.p2, this.q2, this.s2, this.r2]);
        draw_path4d([this.r3, this.p3, this.q3, this.s3, this.r3]);
        draw_path4d([this.r4, this.p4, this.q4, this.s4, this.r4]);
    }
};

function draw_hypercube() {
    //clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    hypercube.draw();
    //rotate viewpoint
    //viewpoint4D.rotate(Math.PI / 180);
    viewpoint3D.rotate(Math.PI / (180 * 21));
    //request next animation frame
    window.requestAnimationFrame(draw_hypercube);
}

function start() {
    canvas = document.getElementById("hypercanvas");
    ctx = canvas.getContext("2d");
    window.requestAnimationFrame(draw_hypercube);
}

