#!/usr/bin/env python
import numpy as np
from results.data.store import load
from common.intac import plot
from common.utils import saveOrDisplay

save = False
file_name = 'intacorr_xx_khmc_kg_0p00t0p50'

dest = 'results/data/other_objs/{}_allPlot.pkl'.format(file_name)
a = load(dest)

sites   = 20
n_steps = 1
dtau    = 0.1
tau     = n_steps*dtau
mass    = 1

a['subtitle'] = r"Lattice: " \
    + r"${}$; $a={:.1f}; \delta\tau={:.1f}; n={}; M=10^7$".format(
        (sites,), n_steps, dtau, n_steps)

# add integrated autocorrelation theory
# format :: {'lines':lines, 'x':angle_fracs, 'subtitle':subtitle, 'op_name':op_name}
# lines are [[y, err, label],..., [y, err, label]]
from theory.autocorrelations import M2_Fix, M2_Exp
from theory.acceptance import acceptance

x = a['x'] # fractions of pi
pacc = a['lines'][3][0][0] # 3rd key, 0th line, y-value

m = M2_Exp(tau=tau,m=1)
y = np.asarray([m.integrated(tau=tau, m=mass, pa=pa_i, theta=theta*np.pi) for theta, pa_i in zip(x, pacc)])
a['lines'][0].append([y, None, r'Theory'])

y = np.full(x.shape, acceptance(tau=tau, dtau=dtau, m=mass, n=sites))
a['lines'][3].append([y, None, r'Theory'])

plot(save = saveOrDisplay(save, file_name), **a)