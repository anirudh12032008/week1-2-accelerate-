import threading
import time
import math
import random
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template

running = True
resetf = False

app = Flask(__name__)

class Pendulum:
    def __init__(self, origin_x=0, origin_y=0,
                 length_rod_1=1, length_rod_2=1,
                 mass_bob_1=1, mass_bob_2=1, g=9.81,
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
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.update()

    def update(self):
        self.x1 = self.origin_x + self.length_rod_1* math.sin(self.theta_1)
        self.y1 = self.origin_y + self.length_rod_1 * math.cos(self.theta_1)
        self.x2 = self.x1 + self.length_rod_2 * math.sin(self.theta_2)
        self.y2 = self.y1 + self.length_rod_2 * math.cos(self.theta_2)
        # print(f"b1: ({self.x1}, {self.y1}) | b2: ({self.x2}, {self.y2})")

    def derivate(self, theta_1, theta_2, omega_1, omega_2):
        # im just going to derivate here but not actually implement the way to solve the differential equations I'll do that later so I just don't mess things up
        m1, m2, l1, l2, g = self.mass_bob_1, self.mass_bob_2, self.length_rod_1, self.length_rod_2, self.g
        delta = theta_2 - theta_1
        # **2 is not working :(
        den1 = (m1 + m2) * l1 - m2 * l1 * math.cos(delta) * math.cos(delta) 
        den2 = (l2 / l1) * den1         

        a1 = (m2 * l1 * omega_1 * omega_1 * math.sin(delta) * math.cos(delta) +
              m2 * g * math.sin(theta_2) * math.cos(delta) +
              m2 * l2 * omega_2 * omega_2 * math.sin(delta) -
              (m1 + m2) * g * math.sin(theta_1)) / den1
        a2 = (-m2 * l2 * omega_2 * omega_2 * math.sin(delta) * math.cos(delta) +
              (m1 + m2) * g * math.sin(theta_1) * math.cos(delta) -
              (m1 + m2) * l1 * omega_1 * omega_1    * math.sin(delta) -
              (m1 + m2) * g * math.sin(theta_2)) / den2
        return a1, a2
    
    def compute(self, dt=0.02):
        # integrating right now Range's method but i can change it later from here
        def k(s):
            t1, w1, t2, w2 = s
            a1, a2 = self.derivate(t1, t2, w1, w2)
            return [w1, a1, w2, a2]
        s = [self.theta_1, self.omega_1, self.theta_2, self.omega_2]
        k1 = k(s)
        k2 = k([v + 0.5 * dt * ki for v, ki in zip(s, k1)])
        k3 = k([v + 0.5 * dt * ki for v, ki in zip(s, k2)])
        k4 = k([v + dt * ki for v, ki in zip(s, k3)])

        for i in range(4):
            s[i] += (dt / 6.0) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])

        self.theta_1, self.omega_1, self.theta_2, self.omega_2 = s
        self.update()

pendulum = Pendulum()


# flasky things
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_params', methods=['POST'])
def set_params():
    data = request.json
    pendulum.length_rod_1 = data.get('length_rod_1', pendulum.length_rod_1)
    pendulum.length_rod_2 = data.get('length_rod_2', pendulum.length_rod_2)
    pendulum.mass_bob_1 = data.get('mass_bob_1', pendulum.mass_bob_1)
    pendulum.mass_bob_2 = data.get('mass_bob_2', pendulum.mass_bob_2)
    pendulum.g = data.get('g', pendulum.g)
    pendulum.theta_1 = data.get('theta_1', pendulum.theta_1)
    pendulum.theta_2 = data.get('theta_2', pendulum.theta_2)
    pendulum.omega_1 = pendulum.omega_2 = 0
    pendulum.update()
    return jsonify({
        'status': 'OK',
        'params': {
            'length_rod_1': pendulum.length_rod_1,
            'length_rod_2': pendulum.length_rod_2,
            'mass_bob_1': pendulum.mass_bob_1,
            'mass_bob_2': pendulum.mass_bob_2,
            'g': pendulum.g,
            'theta_1': pendulum.theta_1,
            'theta_2': pendulum.theta_2
        }
    })


@app.route('/coords')
def coords():
    global running, resetf
    dt = 0.02
    if running:
        pendulum.compute(dt)

    if resetf:
        pendulum.length_rod_1 = 1
        pendulum.length_rod_2 = 1
        pendulum.mass_bob_1 = 1
        pendulum.mass_bob_2 = 1
        pendulum.g = 9.81
        pendulum.theta_1 = math.pi/2
        pendulum.theta_2 = math.pi/2
        pendulum.omega_1 = pendulum.omega_2 = 0
        pendulum.update()
        resetf = False

    return jsonify({
        'x1': pendulum.x1,
        'y1': pendulum.y1,
        'x2': pendulum.x2,
        'y2': pendulum.y2,
        'theta_1': pendulum.theta_1,
        'theta_2': pendulum.theta_2,
        'omega_1': pendulum.omega_1,
        'omega_2': pendulum.omega_2,
        'kinetic': 0.5 * pendulum.mass_bob_1 * (pendulum.length_rod_1 * pendulum.omega_1) ** 2 +
                     0.5 * pendulum.mass_bob_2 * ((pendulum.length_rod_1 * pendulum.omega_1) ** 2 +
                                                     (pendulum.length_rod_2 * pendulum.omega_2) ** 2 +
                                                     2 * pendulum.length_rod_1 * pendulum.length_rod_2 * pendulum.omega_1 * pendulum.omega_2 *
                                                     math.cos(pendulum.theta_1 - pendulum.theta_2)),    
        'potential': (pendulum.mass_bob_1 * pendulum.g * (pendulum.length_rod_1 * (1 - math.cos(pendulum.theta_1))) +
                      pendulum.mass_bob_2 * pendulum.g * (pendulum.length_rod_1 * (1 - math.cos(pendulum.theta_1)) +
                                                          pendulum.length_rod_2 * (1 - math.cos(pendulum.theta_2)))),
        # total energy
        'energy': ( 0.5 * pendulum.mass_bob_1 * (pendulum.length_rod_1 * pendulum.omega_1) ** 2 +
                     0.5 * pendulum.mass_bob_2 * ((pendulum.length_rod_1 * pendulum.omega_1) ** 2 +
                                                     (pendulum.length_rod_2 * pendulum.omega_2) ** 2 +
                                                     2 * pendulum.length_rod_1 * pendulum.length_rod_2 * pendulum.omega_1 * pendulum.omega_2 *
                                                     math.cos(pendulum.theta_1 - pendulum.theta_2)) + (pendulum.mass_bob_1 * pendulum.g * (pendulum.length_rod_1 * (1 - math.cos(pendulum.theta_1))) +
                      pendulum.mass_bob_2 * pendulum.g * (pendulum.length_rod_1 * (1 - math.cos(pendulum.theta_1)) +
                                                          pendulum.length_rod_2 * (1 - math.cos(pendulum.theta_2)))) )

    })

@app.route('/pause', methods=['POST'])
def pause():
    global running
    running = False
    return jsonify({'status': 'paused'})

@app.route('/resume', methods=['POST'])
def resume():
    global running
    running = True
    return jsonify({'status': 'resumed'})

@app.route('/reset', methods=['POST'])
def reset():
    global resetf
    resetf = True
    return jsonify({'status': 'resetting'})


if __name__ == '__main__':
    CORS(app)
    app.run(host='0.0.0.0', debug=True) 