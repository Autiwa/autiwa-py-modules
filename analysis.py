#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""module that contains generic functions that help analyse simulations of planetary dynamic."""

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "2011-09-21"
__version__ = "1.1"

import numpy as np

def get_x_s(mass):
	"""with the mass of the planet in solar mass, 
	and for planets around 3AU in my disk (for the fixed value of 'h')"""
	mstar = 1.0 # the stellar mass in solar mass
	b_over_h = 0.4
	h = 0.045
	q = mass / mstar
	adiabatic_index = 1.4
	
	x_s = (1.1 * (0.4 / b_over_h)**0.25 / adiabatic_index**0.25) * np.sqrt(q / h)
	
	return x_s

