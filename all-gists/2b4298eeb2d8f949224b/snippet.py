#!/usr/bin/env python
"""
Consumer example to use the shared object created in Rust.
Ref: http://blog.skylight.io/bending-the-curve-writing-safe-fast-native-gems-with-rust/
Rust program: points.rs

    use std::num::pow;

    pub struct Point { x: int, y: int }
    struct Line  { p1: Point, p2: Point }

    impl Line {
      pub fn length(&self) -> f64 {
        let xdiff = self.p1.x - self.p2.x;
        let ydiff = self.p1.y - self.p2.y;
        ((pow(xdiff, 2) + pow(ydiff, 2)) as f64).sqrt()
      }
    }

    #[no_mangle]
    pub extern "C" fn make_point(x: int, y: int) -> Box<Point> {
        box Point { x: x, y: y }
    }


    #[no_mangle]
    pub extern "C" fn get_distance(p1: &Point, p2: &Point) -> f64 {
        Line { p1: *p1, p2: *p2 }.length()
    }

"""
from ctypes import CDLL, Structure, c_int, c_void_p
from ctypes import c_double, CFUNCTYPE

RUST_SO_PATH = "/home/aravinda/sandbox/exp/rust/libpoints.so"


class Point (Structure):
    _fields_ = [
        ("x", c_int),
        ("y", c_int)
    ]

api = CDLL(RUST_SO_PATH)

make_point = CFUNCTYPE(c_void_p, c_int, c_int)(('make_point', api))
get_distance = CFUNCTYPE(c_double, c_void_p, c_void_p)(('get_distance', api))

p1 = make_point(10, 10)
p2 = make_point(20, 20)

print get_distance(p1, p2)
