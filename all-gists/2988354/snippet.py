#!/usr/bin/python
# -*- coding: UTF-8 -*-
""" Interactive study of an AR(2) auto-regressive filter/process.

AR(2) process definition : X_k = a_1 X_{k-1} + a_2 X_{k-2} + Z_k

Interactive choice :
  choose graphically the two coefficients (a1, a2) of the filter
  by clicking and dragging the red disc on the (a1, a2) plane.


While changing the coefficients, see the effect in real time on :
  1) the two roots of the polynomial P(z)=z^2 - a_1 z - a_2
    * is there any root outside the disc of stability (disc |z| < 1) ?
  2) the impulse response h(k)
    * is it stable ?
    * is it oscillating ?
  3) the frequency response 
    * is it monotously increasing/decreasing ?
    * is there a peak ?
    * how wide is the peak ?


Pierre Haessig — June 2012
This script is provided under BSD 3-Clause License


This script was inspired by the "looking glass" example
from Matplotlib documentation on event handling :
http://matplotlib.sourceforge.net/examples/event_handling/looking_glass.html
"""

import numpy as np
from numpy.polynomial import Polynomial
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.signal import lfilter

# Initial AR(2) coefficients choice
a1, a2 = 0.5, 0.0


### AR(2) coefficients plots ###################################################

### AR(2) coefficients : interactive selection
fig_coeff = plt.figure('AR(2) - coefficient choice', figsize=(6,9))
fig_coeff.clear()
ax_coeff = fig_coeff.add_subplot(211, title='Choose AR(2) coefficients: '
                                 '$(a_1, a_2)$=(%.2f, %.2f) \n'
                                 'process $X_k = a_1 X_{k-1} + a_2 X_{k-2} + Z_k$'\
                                  % (a1, a2),
                                 xlabel='coeff. $a_1$', ylabel='coeff. $a_2$')
ax_coeff.patch.set_facecolor('#CCCCDD') # Light blue background

ax_coeff.set_xlim(-2.5,2.5)
ax_coeff.set_ylim(-1.5,1.5)
ax_coeff.set_aspect('equal')
ax_coeff.fill([-2,0,2,-2],[-1,1,-1,-1], color='white', label='stability region')
# Delta = 0 boundary
a1_range = np.linspace(-2,2,50)
ax_coeff.plot(a1_range,-a1_range**2/4, '-', color='#555599',
              label=u'$\Delta=0$ boundary')
# x,y guide lines
coeff_line, = ax_coeff.plot([a1, a1, 0], [0,a2,a2], 'k--')
# x,y marking circle
circ = patches.Circle( (a1, a2), 0.1, alpha=0.8, fc='red')
ax_coeff.add_patch(circ)

ax_coeff.grid(True)

### Roots of z^2 - a1 z - a2  (related to stability of the filter)
ax_roots = fig_coeff.add_subplot(212, title='Roots of $P(z)=z^2 - a_1 z - a_2$',
                                     xlabel='Re(z)', ylabel='Im(z)')
ax_roots.patch.set_facecolor('#CCCCDD') # Light blue background
circ_roots = patches.Circle((0, 0), 1, fc='white', lw=0)
ax_roots.add_patch(circ_roots)
ax_roots.set_xlim(-1.5, 1.5)
ax_roots.set_ylim(-1.5, 1.5)
ax_roots.set_aspect('equal')

# Compute the roots numerically (the lazy way)
poly_ar2 = Polynomial([-a2, -a1, 1])
root1, root2 = poly_ar2.roots().astype(complex)
roots_line, = ax_roots.plot([root1.real, root2.real],
                            [root1.imag, root2.imag],
                            '*', color='red', ms=10)

fig_coeff.tight_layout()

### Response plots #############################################################
fig_res = plt.figure('AR(2) - responses')
fig_res.clear()

# 1) Impulse response plot
ax_ir = fig_res.add_subplot(211, title='Impulse Response $h(k)$',
                            xlabel='instant k')
K = 21 # How many instants
k = np.arange(0,K)
dirac = np.zeros(K)
dirac[0] = 1
h_ir = lfilter([1], [1, -a1, -a2], dirac)
# Plot the IR
ir_line, = ax_ir.plot(k, h_ir, 'b-o')
ax_ir.set_ylim(-1.5,1.5)
ax_ir.grid(True)

# 2) Frequency response plot
ax_spec = fig_res.add_subplot(212, title='Frequency Response $H(\omega)$',
                        xlabel='frequency $\omega / \pi$')

def Var_AR2(a1,a2):
    '''Variance of an AR(2) process
    X_k = a1 X_{k-1} + a2 X_{k-2} + Z_k
    with Z_k of unit variance
    '''
    return 1/(1-a2**2 - a1**2 * (1+a2)/(1-a2))

def spectrum_ar2(a1,a2,w, normed=True):
    '''spectrum of an AR(2) process with unit variance input
    http://en.wikipedia.org/wiki/Autoregressive_model#AR.282.29
    '''
    cosw = np.cos(w)
    f = 1/(1 + 2*a2 + a1**2 + a2**2 + 2*a1*(a2-1)*cosw - 4*a2*cosw**2)
    if normed:
        return f/Var_AR2(a1, a2)
    else:
        return f

omega_list = np.linspace(0, np.pi, 100)
spectrum_line, = ax_spec.plot(omega_list/np.pi,
                              spectrum_ar2(a1,a2,omega_list),
                              '-', color='#D15100')
ax_spec.set_ylim(0,5)
ax_spec.grid(True)

fig_res.tight_layout()


################################################################################
### Animation management

class AnimatedPlot:
    def __init__(self):
        # Connect the event handlers
        fig_coeff.canvas.mpl_connect('button_press_event', self.onpress)
        fig_coeff.canvas.mpl_connect('button_release_event', self.onrelease)
        fig_coeff.canvas.mpl_connect('motion_notify_event', self.onmove)
        self.pressevent = None # State of mouse press event tracking
        
        
        # Frequency response
        self.spec_poly = ax_spec.fill_between(omega_list/np.pi,
                                              spectrum_ar2(a1,a2,omega_list),
                                              color='#FFAA00', alpha=0.5, lw=0)
    
    ### Plot update functions
    def update_coeff(self, a1,a2):
        '''update the AR(2) coefficients choice
        and the roots of the AR polynomial'''
        # Update the title
        ax_coeff.set_title('Choose AR(2) coefficients: '
                           '$(a_1, a_2)$=(%.2f, %.2f) \n'
                           'process $X_k = a_1 X_{k-1} + a_2 X_{k-2} + Z_k$'\
                            % (a1, a2))
        # Move the circle
        circ.center = a1, a2
        # Move the guiding lines
        coeff_line.set_data([a1, a1, 0], [0,a2,a2])
        # Move the roots:
        poly_ar2 = Polynomial([-a2, -a1, 1])
        root1, root2 = poly_ar2.roots().astype(complex)
        roots_line.set_data([root1.real, root2.real],
                            [root1.imag, root2.imag])

    def update_response(self, a1,a2):
        '''update the plots of the filter responses
        (impulse and frequency)'''
        h_ir = lfilter([1], [1, -a1, -a2], dirac)
        ir_line.set_data(k, h_ir)
        spectrum_line.set_data(omega_list/np.pi, spectrum_ar2(a1,a2,omega_list))
        self.spec_poly.remove()
        self.spec_poly = ax_spec.fill_between(omega_list/np.pi,
                                              spectrum_ar2(a1,a2,omega_list),
                                              color='#FFAA00', alpha=0.5, lw=0)
    
    ### Event handlers
    def onpress(self, event):
        '''mouse press = move the circle + follow the mouse'''
        if event.inaxes!=ax_coeff:
         return
        self.update_coeff(a1=event.xdata, a2=event.ydata)
        self.update_response(a1=event.xdata, a2=event.ydata)
        fig_coeff.canvas.draw()
        fig_res.canvas.draw()
        self.pressevent = event

    def onrelease(self, event):
        '''mouse release = stop following the mouse'''
        if self.pressevent is None:
         return

        self.update_coeff(a1=event.xdata, a2=event.ydata)
        self.update_response(a1=event.xdata, a2=event.ydata)
        fig_coeff.canvas.draw()
        fig_res.canvas.draw()
        self.pressevent = None
        print('a1, a2 = (%.2f, %.2f)' % circ.center)


    def onmove(self, event):
        '''mouse move = move the circle'''
        if self.pressevent is None or event.inaxes!=self.pressevent.inaxes:
         return

        self.update_coeff(a1=event.xdata, a2=event.ydata)
        self.update_response(a1=event.xdata, a2=event.ydata)
        fig_coeff.canvas.draw()
        fig_res.canvas.draw()


animated_plot = AnimatedPlot()
plt.show()