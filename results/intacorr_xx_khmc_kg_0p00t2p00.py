#!/usr/bin/env python
import numpy as np

from common import intac
from hmc.potentials import Klein_Gordon as KG
from correlations.corr import twoPoint
from theory.operators import phi2_1df
from theory.autocorrelations import M2_Fix as AC_Theory

file_name = __file__
pot = KG()

n, dim = 20, 1
x0 = np.random.random((n,)*dim)
spacing    = 1.
step_size  = .1
n_steps    = 1
points     = 50
tau        = n_steps*step_size

n_samples, n_burn_in = 100000, 20
h_res = np.linspace(-0.15, 0.15, 100, True)
l_res = np.linspace(0.151, 0.85, points, True)
angle_fracs = np.concatenate([h_res,l_res,h_res+1,l_res+1,h_res+2])

opFn = lambda samples: twoPoint(samples, separation=0)
op_name = r'$\hat{O}_{pq} = \phi_0^2$'

# theoretical calculations
op_theory   = phi2_1df(mu=pot.m, n=x0.size, a=spacing, sep=0)
pacc_theory = acceptance(dtau=step_size, tau=tau, n=x0.size, m=pot.m, t=tau*n_samples)
acth = AC_Theory(tau=n_steps*step_size, m=pot.m)
iTauTheory  = acth.integrated

if '__main__' == __name__:
    intac.main(x0, pot, file_name, 
        n_samples = n_samples, n_burn_in = n_burn_in, spacing = spacing,
        step_size = step_size, n_steps = n_steps,
        opFn = opFn, op_name=op_name,
        angle_fracs = angle_fracs,
        iTauTheory = iTauTheory, pacc_theory = pacc_theory, op_theory = op_theory,
        save = True)
