#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""module that allow us to simplify object definition. In other words, it offer us some usefull functions to define a 
planetary system with user friendly commands. """

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "2011-08-24"
__version__ = "1.0"

import mercury
from random import uniform 
import simulations

def definePlanetarySystem(m, a, e, I, m_star=1.0, epoch=0):
	""" We will assume a certain number of parameters. For example, all bodies will be big bodies. 
	We will also assume that all the bodies will be set with the 'asteroidal' properties (that is to say (a, e, I, g, n, M)). Plus, 
	g, n, M ill be randomly generated (g the argument of pericentre (degrees), n the longitude of the ascending node (degrees), 
	M the mean anomaly (degrees) )
	
	CONSTANTS : 
	PREFIX_BIG : This is a name prefix, whose length must be 7. This will be used to set automatic name to the bodies
	
	Parameters : 
	m_star=1.0 : By default, the mass of the central object will be the mass of our sun.
	epoch=0 : By default, planetary systems are not real. Thus, we set the start time to 0 to be more convenient
	
	m, a, e, I: they must be lists of the same length, one element for each planet. 
	(m the mass (in solar mass), a the semi major axis (in AU), e the eccentricity, I the inclination (in degrees))
	
	
	Return : 
	An object PlanetarySystem defined with the given parameters
	"""
	
	PREFIX_BIG = "PLANETE"
	
	if (type(m) != list):
		raise TypeError("'m' must be a list")
	
	if (type(a) != list):
		raise TypeError("'a' must be a list")
	
	if (type(e) != list):
		raise TypeError("'e' must be a list")
	
	if (type(I) != list):
		raise TypeError("'I' must be a list")
	
	
	# We test if the lists are of the same length
	nb_planets = len(a)
	for param in [m, a, e, I]:
		if (len(param) != nb_planets):
			raise ValueError("(m, a, e, I) must be of the same length")
	
	
	# We generate randomly g, n, and M
	g = simulations.setParameter((0, 360, 'uniform'), nb_planets)
	n = simulations.setParameter((0, 360, 'uniform'), nb_planets)
	M = simulations.setParameter((0, 360, 'uniform'), nb_planets)

	#~ g = [uniform(0, 360) for i in range(nb_planets)]
	#~ n = [uniform(0, 360) for i in range(nb_planets)]
	#~ M = [uniform(0, 360) for i in range(nb_planets)]
	
	bodies = []
	index = 1
	for (mi, ai, ei, Ii, gi, ni, Mi) in zip(m, a, e, I, g, n, M):
		str_idx = str(index)
		name = PREFIX_BIG[0:8-len(str_idx)]+str_idx
		bodies.append(mercury.BodyAst("big", name=name, m=mi, a=ai, e=ei, I=Ii, 
g=gi, n=ni, M=Mi, ep=epoch))
		index += 1
	
	return mercury.PlanetarySystem(bodies=bodies, m_star=m_star, epoch=epoch)
	
