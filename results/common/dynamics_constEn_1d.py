import numpy as np
import matplotlib.pyplot as plt

from models import Basic_HMC as Model
from utils import saveOrDisplay

from plotter import Pretty_Plotter, PLOT_LOC

def plot(y1, y2, subtitle, save, all_lines = False):
    """A plot of y1 and y2 as functions of the steps which
    are implicit from the length of the arrays
    
    Required Inputs
        y1 :: np.array :: conj kinetic energy array
        y2   :: np.array :: shape is either (n, 3) or (n,)
        subtitle :: string :: subtitle for the plot
        save :: bool :: True saves the plot, False prints to the screen
    
    Optional Inputs
        all_lines :: bool :: if True, plots hamiltonian as well as all its components
    """
    
    pp = Pretty_Plotter()
    pp._teXify() # LaTeX
    pp._updateRC()
    
    fig = plt.figure(figsize=(8, 8)) # make plot
    ax =[]
    ax.append(fig.add_subplot(111))
    
    # fig.suptitle(r"Change in Energy during Leap Frog integration",
    #     fontsize=pp.ttfont)
    
    ax[0].set_title(subtitle, fontsize=pp.ttfont)
    
    ax[0].set_xlabel(r'Number of Leap Frog Steps, $n$', fontsize=pp.axfont)
    ax[0].set_ylabel(r'Change in Energy, $\delta E_{n} = E_{n} - E_0$', fontsize=pp.axfont)
    
    steps = np.linspace(0, y1.size, y1.size, True)
    
    # check for multiple values in the potential
    multi_pot = (len(y2.shape) > 1)
    print multi_pot, y2.shape
    if multi_pot:
        action, k, u = zip(*y2)
        k = np.asarray(k)
        u = np.asarray(u)
    else:
        action = y2
        
    action = np.asarray(action)
    
    h = ax[0].plot(steps, y1+np.asarray(action), # Full Hamiltonian
        label=r"$\delta H_t = \delta T_n + \delta S_t$", color='blue',
        linewidth=5., linestyle = '-', alpha=1)
    
    if all_lines:
        t = ax[0].plot(steps, np.asarray(y1), # Kinetic Energy (conjugate)
            label=r'$\delta T_n$', color='darkred',
            linewidth=2., linestyle='-', alpha=1)
        
        if multi_pot:
            s = ax[0].plot(steps, np.asarray(action), # Potential Energy (Action)
                label=r'$\delta \delta S_n = \sum_{n} (\delta T^{(s)}_n + \delta V^{(s)}_n)$', color='darkgreen',
                linewidth=1., linestyle='-', alpha=1)
                
            t_s = ax[0].plot(steps, np.asarray(k),  # Kinetic Energy in Action
                label=r'$\sum_{n} \delta T^{(s)}_n$', color='red',
                linewidth=1., linestyle='--', alpha=2.)
            
            v_s = ax[0].plot(steps, np.asarray(u),  # Potential Energy in Action
                label=r'$\sum_{n} \delta V^{(s)}_n$', color='green',
                linewidth=1., linestyle='--', alpha=1.)
        else:
            s = ax[0].plot(steps, np.asarray(action), # Potential Energy (Action)
                label=r'$\delta S(x,t) = \frac{1}{2}\delta \phi_{n,x}^2$', color='darkgreen',
                linewidth=3., linestyle='-', alpha=1)
    
    # add legend
    ax[0].legend(loc='upper left', shadow=True, fontsize = pp.axfont)
    
    pp.save_or_show(save, PLOT_LOC)
    pass
#
def dynamicalEnergyChange(x0, pot, n_steps, step_size):
    """Iterates the dynamics for the steps and the step sizes
    returns the absolute change in the hamiltonian for each
    parameter configuration
    
    Required Inputs
        x0          :: dependent on the potential used
        pot         :: potential class - see hmc.potentials
        step_sample :: int   :: sample array of integrator step lengths
        step_sizes  :: float :: sample array of integrator step sizes
    """
    rng = np.random.RandomState()
    model = Model(x0, pot,
        n_steps   = n_steps, 
        step_size = step_size,
        rng=rng,
        save_path=True)
    # model.sampler.dynamics.save_path = True # saves the dynamics path
    
    # initial conditions - shoudn't matter much
    p0 = model.sampler.p0
    x0 = model.sampler.x0
    
    # calculate original hamiltonian and set starting vals
    h0    = model.sampler.potential.hamiltonian(p0, x0)
    kE0   = model.sampler.potential.kE(p0)
    uE0   = model.sampler.potential.uE(x0)
    print model.sampler.potential.debug
    # Setting debug = True returns a tuple
    # from the potential: (action, action_ke, action_ue)
    if len([uE0]) > 1: # list() as can be np.array or plain float
        check_uE0 = uE0[0] # if a debug then this is action
    else:
        check_uE0 = uE0    # if not debug then as normal
    
    # obtain new duynamics and resultant hamiltonian
    model.sampler.dynamics.newPaths()
    pf, xf = model.sampler.dynamics.integrate(p0.copy(), x0.copy(), verbose=True)
    
    kE_path = [model.sampler.potential.kE(i) for i in model.sampler.dynamics.p_ar]
    uE_path = [model.sampler.potential.uE(i) for i in model.sampler.dynamics.x_ar]
    
    kins = np.asarray([kE0] + kE_path) - kE0
    pots = np.asarray([uE0] + uE_path) - uE0
    return kins, pots 
#
def main(x0, pot, file_name, save = False, n_steps   = 100, step_size = .1, all_lines = True):
    """A wrapper function
    
    Required Inputs
        x0          :: np.array :: initial position input to the HMC algorithm
        pot         :: potential class :: defined in hmc.potentials
        file_name   :: string :: the final plot will be saved with a similar name if save=True
    
    Optional Inputs
        save :: bool :: True saves the plot, False prints to the screen
        n_steps :: list :: LF trajectory lengths
        step_size :: float :: Leap Frog step size
        all_lines :: bool :: if True, plots hamiltonian as well as all its components
    """
    print 'Running Model: {}'.format(file_name)
    kins, pots = dynamicalEnergyChange(x0, pot, n_steps, step_size)
    print 'Finished Running Model: {}'.format(file_name)
    
    plot(y1 = kins, y2 = pots, all_lines = all_lines,
        subtitle = r'Lattice: {}, '.format(x0.shape) + \
        r'$\delta\tau ='+'{}$'.format(step_size),
        save = saveOrDisplay(save, file_name)
        )
    pass
