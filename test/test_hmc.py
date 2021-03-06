import numpy as np
from scipy.stats import norm

import utils

from hmc.lattice import Periodic_Lattice
from hmc.potentials import Simple_Harmonic_Oscillator, Multivariate_Gaussian
from hmc.potentials import Quantum_Harmonic_Oscillator, Klein_Gordon
from hmc.hmc import *

class Test(object):
    """Tests for the HMC class
    
    Required Inputs
        rng :: np.random.RandomState :: random number generator
    """
    def __init__(self, rng):
        self.id  = 'HMC'
        self.rng = rng
        pass
    
    def hmcSho1d(self, n_samples = 1000, n_burn_in = 10, tol = 5e-2, print_out = True):
        """A test to sample the Simple Harmonic Oscillator
        
        Optional Inputs
            tol     ::  float   :: tolerance level allowed
            print_out   :: bool     :: print results to screen
            save    :: string   :: file to save plot. False or '' gives no plot
        """
        passed = True
        
        x0 = np.asarray([[1.]])
        dim = x0.shape[0] # dimension the column vector
        
        
        pot = Simple_Harmonic_Oscillator()
        
        lf = Leap_Frog(duE = pot.duE, step_size = 0.1, n_steps = 20)
        hmc = Hybrid_Monte_Carlo(x0, lf, pot, self.rng)
        
        p_samples, samples = hmc.sample(n_samples = n_samples, n_burn_in = n_burn_in,
            verbose = True)
        burn_in, samples = samples # return the shape: (n, dim, 1)
        
        # flatten last dimension to a shape of (n, dim)
        self.samples = np.asarray(samples).reshape(-1, dim)
        
        
        # is this right?
        w = (1 + .25) # w  = 1/(sigma)^2
        sigma = 1./np.sqrt(2.*w)
        
        mean = self.samples.ravel().mean()
        cov = np.var(self.samples)
        act_mean = 0.
        act_cov = sigma
        
        cov_tol = mean_tol = tol
        
        passed *= (np.abs(mean - act_mean) <= mean_tol).all()
        passed *= (np.abs(cov - act_cov) <= cov_tol).all()
        
        if print_out:
            utils.display("HMC: Simple Harmonic Oscillator", passed,
                details = {
                    'mean':[
                        'target:    {}'.format(     act_mean),
                        'empirical  {}'.format(     mean),
                        'tolerance  {}'.format(     mean_tol)
                        ],
                    'covariance':[
                        'target:    {}'.format(     act_cov ),
                        'empirical  {}'.format(     cov),
                        'tolerance  {}'.format(     cov_tol)
                        ]
                    })
        
        return passed
    
    def hmcGaus2d(self, n_samples = 1000, n_burn_in = 10, tol = 5e-2, print_out = True):
        """A test to sample the 2d Gaussian Distribution
        
        Optional Inputs
            tol     ::  float   :: tolerance level allowed
            print_out   :: bool     :: print results to screen
            save    :: string   :: file to save plot. False or '' gives no plot
        """
        passed = True
        
        x0 = np.asarray([[-3.5], [4.]])
        
        dim = x0.shape[0] # dimension the column vector
        pot = Multivariate_Gaussian()
        
        lf = Leap_Frog(duE = pot.duE, step_size = 0.1, n_steps = 20)
        hmc = Hybrid_Monte_Carlo(x0, lf, pot, self.rng)
        
        act_mean = hmc.potential.mean
        act_cov = hmc.potential.cov
        
        mean_tol = np.full(act_mean.shape, tol)
        cov_tol = np.full(act_cov.shape, tol)
        
        p_samples, samples = hmc.sample(n_samples = n_samples, n_burn_in=n_burn_in,
            verbose = True)
        burn_in, samples = samples # return the shape: (n, 2, 1)
        
        # flatten last dimension to a shape of (n, 2)
        self.samples = np.asarray(samples).T.reshape(dim, -1).T
        self.burn_in = np.asarray(burn_in).T.reshape(dim, -1).T
        self.p_samples = p_samples
        
        mean = self.samples.mean(axis=0)
        # covariance assumes observations in columns
        # we have observations in rows so specify rowvar=0
        cov = np.cov(self.samples, rowvar=0)
        
        passed *= (np.abs(mean - act_mean) <= mean_tol).all()
        passed *= (np.abs(cov - act_cov) <= cov_tol).all()
        
        if print_out:
            utils.display("HMC: Bivariate Gaussian", passed,
                details = {
                    'mean':[
                        'target:    {}'.format(     act_mean.reshape(np.prod(act_mean.shape))),
                        'empirical  {}'.format(     mean.reshape(np.prod(mean.shape))),
                        'tolerance  {}'.format(     mean_tol.reshape(np.prod(mean_tol.shape)))
                        ],
                    'covariance':[
                        'target:    {}'.format(     act_cov.reshape(np.prod(act_cov.shape))),
                        'empirical  {}'.format(     cov.reshape(np.prod(cov.shape))),
                        'tolerance  {}'.format(     cov_tol.reshape(np.prod(cov_tol.shape)))
                        ]
                    })
        
        return passed
    def hmcQho(self, n_samples = 100, n_burn_in = 10, tol = 5e-2, print_out = True):
        """A test to sample the Quantum Harmonic Oscillator
        
        Optional Inputs
            tol     ::  float   :: tolerance level allowed
            print_out   :: bool     :: print results to screen
            save    :: string   :: file to save plot. False or '' gives no plot
        """
        name = 'QHO'
        passed = True
        n = 100
        dim = 1
        spacing = 1.
        step_size = 0.1
        n_steps = 20
        mu = 1.
        
        x_nd = np.random.random((n,)*dim)
        p0 = np.random.random((n,)*dim)
        x0 = Periodic_Lattice(x_nd)
        
        pot = Quantum_Harmonic_Oscillator()
        
        lf = Leap_Frog(duE = pot.duE, 
            step_size = step_size, n_steps = n_steps, lattice = True)
        hmc = Hybrid_Monte_Carlo(x0, lf, pot, self.rng)
        
        p_samples, samples = hmc.sample(n_samples = n_samples, n_burn_in = n_burn_in,
            verbose = True)
        burn_in, samples = samples # return the shape: (n, dim, 1)
        
        # flatten last dimension to a shape of (n, 2)
        self.samples = np.asarray(samples)
        self.burn_in = np.asarray(burn_in)
        self.p_samples = p_samples
        
        s = np.asarray(self.samples).reshape(n_samples+1, n)
        fitted = norm.fit(s.ravel())
        
        w = mu**2*(1 + .25*(spacing*mu)**2) # w  = 1/(sigma)^2
        sigma = 1./np.sqrt(2.*w)
        
        passed *= (np.abs(fitted[0] - 0) <= tol)
        passed *= (np.abs(fitted[1] - sigma) <= tol)
        
        if print_out:
            utils.display("HMC: Quantum Harmonic Oscillator", passed,
                details = {
                    'mean':[
                        'target:    {}'.format(     0),
                        'empirical  {}'.format(     fitted[0]),
                        'tolerance  {}'.format(     tol)
                        ],
                    'standard deviation':[
                        'target:    {}'.format(     sigma),
                        'empirical  {}'.format(     fitted[1]),
                        'tolerance  {}'.format(     tol)
                        ]
                    })
        
        return passed
    
#
if __name__ == '__main__':
    rng = np.random.RandomState()
    utils.logging.root.setLevel(utils.logging.DEBUG)
    test = Test(rng)
    utils.newTest(test.id)
    test.hmcSho1d(n_samples = 10000, n_burn_in = 15, tol = 1e-2)
    # test.hmcGaus2d(n_samples = 100000, n_burn_in = 15, tol = 1e-1)
    test.hmcQho(n_samples = 1000, n_burn_in = 15, tol = 1e-1)
