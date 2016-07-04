import numpy as np
from hmc import checks

class Corellations_1d(object):
    """Runs a model and calculates the 1 dimensional correlation function
    
    Required Inputs
        model           :: class    :: a class that runs some sort of model - see models.py
        attr_samples    :: str      :: attr location of the x sampeles: model.attr_samples
        attr_run        :: str      :: attr points to fn to run the model: model.attr_run()
    
    Expectations
        model has an attribute that contains the MCMC samples following a run
        model has a function that runs the MCMC sampling
        the samples are stored as [sample index, sampled lattice configuration]
    """
    def __init__(self, model, attr_run, attr_samples, *args, **kwargs):
        self.model = model
        self.attr_run = attr_run
        self.attr_samples = attr_samples
        
        checks.tryAssertEqual(True, hasattr(self.model, self.attr_run),
            "The model has no attribute: self.model.{} ".format(self.attr_run))
        
        # set all kwargs and args
        for kwarg,val in kwargs.iteritems(): setattr(self, kwarg, val)
        for arg in args: setattr(self, arg, arg)
        
        # run the model
        self.runWrapper = getattr(self.model, self.attr_run)
        pass
    
    def runModel(self, *args, **kwargs):
        """Runs the model with any given *args and **kwargs"""
        self.result = self.runWrapper(*args, **kwargs)
        return self.result
    
    def twoPoint(self, separation):
        """Delivers the two point with a given separation
        
        Once the model is run then the samples can be passed through the correlation
        function in once move utilising the underlying optimisations of numpy in full
        
        Equivalent to evaluating for each sample[i] and averaging over them
        
        Required Inputs
            separation :: int :: the lattice spacing between the two point function
        """
        
        checks.tryAssertEqual(int, type(separation),
            "Separation must be integer: type is: {}".format(type(separation)))
        
        if not hasattr(self, 'samples'): self._getSamples()
        
        # here the sample index will be the first index
        # the remaning indices are the lattice indices
        self.samples = np.asarray(self.samples)
        
        # shift the array by the separation
        # need the axis=1 as this is the lattice index, 0 is the sample index
        shifted = np.roll(self.samples, separation, axis=1)
        
        # this actually works for any dim arrays as * op broadcasts
        self.two_point = (shifted*self.samples)
        
        # ravel() just flattens averything into one dimension
        # rather than averaging over each lattice sample and averaging over
        # all samples I jsut average the lot saving a calculation
        return self.two_point.ravel().mean()
        
    def _getSamples(self):
        """grabs the position samples from the model"""
        
        checks.tryAssertEqual(True, hasattr(self, 'result'),
            "The model has not been run yet!\n\tself.result not found")
        checks.tryAssertEqual(True, hasattr(self.model, self.attr_samples),
            "The model has no lattice attribute: self.model.{} ".format(self.attr_samples))
        
        samples = getattr(self.model, self.attr_samples) # pull out the lattice values
        
        # check that the lattice is indeed 1D as the size should be equal to
        # the largest dimension. Won't be true if more than 1 entry != (1,)
        checks.tryAssertEqual(samples[0].size, max(samples[0].shape),
            "The lattice is not 1-dimensional: self.model.{}.shape ={}".format(
            self.attr_samples, samples[0].shape))
        self.samples = samples[1:] # the last burn-in sample is the 1st entry
        pass