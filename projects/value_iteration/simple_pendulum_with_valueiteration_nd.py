# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 20:28:17 2018

@author: Alexandre
"""

import numpy as np
import cProfile as profile
import pstats

from pyro.dynamic  import pendulum
from pyro.planning import discretizer
from pyro.analysis import costfunction, stopwatch
from pyro.planning import valueiteration
from pyro.control  import controller

sys  = pendulum.SinglePendulum()

# Discrete world
grid_sys = discretizer.GridDynamicSystem( sys )

# Cost Function
qcf = sys.cost_function

qcf.xbar = np.array([ -3.14 , 0 ]) # target
qcf.INF  = 10000

# VI algo
vi = valueiteration.ValueIteration_ND(grid_sys, qcf, interpolation='scipy')

# Timer
timer = stopwatch.Stopwatch()

vi.initialize()
# vi.load_data('simple_pendulum_vi')

profile.run('vi.compute_steps(200, plot=True)', 'profile')
print('Profiling finished')
p = pstats.Stats('profile')
p.strip_dirs().sort_stats(-1).print_stats()
p.sort_stats('time', 'cumulative', 'ncalls').print_stats(.5, 'init')
p.print_callers(.5, 'init')

vi.assign_interpol_controller()
vi.plot_policy(0)
vi.plot_cost2go()
# vi.save_data('simple_pendulum_vi')

#asign controller
cl_sys = vi.ctl + sys

# Simulation and animation
cl_sys.x0   = np.array([0,0])
cl_sys.compute_trajectory(tf=20)
cl_sys.plot_trajectory('xu')
cl_sys.animate_simulation(11)
