import threading
import time
import math
import random
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template


app = Flask(__name__)

class Pendulum:
    def __init__(self, origin_x=300, origin_y=100,
                 length_rod_1=120, length_rod_2=120,
                 mass_bob_1=10, mass_bob_2=10, g=9.81,
                 theta_1=math.pi/2, theta_2=math.pi/2,
                 omega_1=0.0, omega_2=0.0):
        self.length_rod_1 = length_rod_1
        self.length_rod_2 = length_rod_2
        self.mass_bob_1 = mass_bob_1
        self.mass_bob_2 = mass_bob_2
        self.g = g
        self.theta_1 = theta_1
        self.theta_2 = theta_2
        self.omega_1 = omega_1
        self.omega_2 = omega_2
        self.update()

    def update(self):
        self.x1 = self.origin_x + self.length_rod_1* math.sin(self.theta_1)
        self.y1 = self.origin_y + self.length_rod_1 * math.cos(self.theta_1)
        self.x2 = self.x1 + self.length_rod_2 * math.sin(self.theta_2)
        self.y2 = self.y1 + self.length_rod_2 * math.cos(self.theta_2)

    def derivate(self, theta_1, theta_2, omega_1, omega_2):
        # im just going to derivate here but not actually implement the way to solve the differential equations I'll do that later so I just don't mess things up
        m1, m2, l1, l2, g = self.mass_bob_1, self.mass_bob_2, self.length_rod_1, self.length_rod_2, self.g
        delta = theta_2 - theta_1
        # **2 is not working :(
        den1 = (m1 + m2) * l1 - m2 * l1 * math.cos(delta) * math.cos(delta) 
        den2 = (l2 / l1) * den1         

    def step(self, dt):
        # Update the angles and angular velocities using the physics of the double pendulum
        pass