#!/usr/bin/env python
import numpy as np

from common import dynamics_constEn_1d
from hmc.potentials import Quantum_Harmonic_Oscillator as QHO

file_name = __file__
pot = QHO()

n, dim = 100, 1
x0 = np.random.random((n,)*dim)



if '__main__' == __name__:
    dynamics_constEn_1d.main(x0, pot, file_name, all_lines = False, 
    step_size=.17, n_steps=100,
    save = False)