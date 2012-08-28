#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""module that allow us to simplify object definition. In other words, it offer us some usefull functions to define a 
planetary system with user friendly commands. """

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "2011-09-21"
__version__ = "1.1"

import mercury
from random import uniform 
import simulations_utilities
import autiwa
import subprocess

# Dictionnary that store, for each server, the location of the binaries for mercury (in this folder, there are mercury, element and close
BINARY_FOLDER = {'arguin.obs.u-bordeaux1.fr':"/home/cossou/bin/mercury", 
								 'avakas-frontend2':"/home/ccossou/bin/mercury",
								 'avakas-frontend1':"/home/ccossou/bin/mercury"}

def prepareSubmission(hostname):
  """This function will generate files usefull to launch the simulation, 
  especially if the simulation has moved from a server to another. 
  'runjob' and 'simulation.sh' will be generated. 'runjob' is the file that must be executed to launch the simulation. 
  In fact, 'runjob' will submit to the queue scheduler the script 'simulation.sh' that contains all the 
  binaries that must be launched by the simulation.
  
  Indeed, the scripts used to launch the simulation will be adapted in function of the hostname"""
  
  command = BINARY_FOLDER[hostname]+"/mercury\n" + \
            BINARY_FOLDER[hostname]+"/element\n" + \
            "echo `date '+%d-%m-%Y at %H:%M:%S'` `pwd` ': Done'>>~/qsub.log\n"
            
  # We define a bash script to launch the simulation in a queue
  if ('arguin' in hostname):
    script = simulations_utilities.SimpleJob(command) # For arguin
    simulations_utilities.writeRunjobSGE("simulation.sh") # For arguin
  elif('avakas' in hostname):
    script = simulations_utilities.Job_PBS(command, walltime=48) # For avakas
    simulations_utilities.writeRunjobPBS("simulation.sh") # For avakas
  else:
    raise NameError("The hostname %s is not recognized by the script" % hostname)
  script.write()
  
  simulations_utilities.setExecutionRight("simulation.sh")

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
	g = simulations_utilities.setParameter((0, 360, 'uniform'), nb_planets)
	n = simulations_utilities.setParameter((0, 360, 'uniform'), nb_planets)
	M = simulations_utilities.setParameter((0, 360, 'uniform'), nb_planets)

	#~ g = [uniform(0, 360) for i in range(nb_planets)]
	#~ n = [uniform(0, 360) for i in range(nb_planets)]
	#~ M = [uniform(0, 360) for i in range(nb_planets)]
	
	bodies = []
	index = 1
	for (mi, ai, ei, Ii, gi, ni, Mi) in zip(m, a, e, I, g, n, M):
		bodies.append(mercury.BodyAst("big", m=mi, a=ai, e=ei, I=Ii, 
g=gi, n=ni, M=Mi, ep=epoch))
		index += 1
	
	return mercury.PlanetarySystem(bodies=bodies, m_star=m_star, epoch=epoch)
	
def get_aei_files():
	"""function that return the list of *.aei files of the current folder"""
	(process_stdout, process_stderr, return_code) = autiwa.lancer_commande("ls *.aei")
	if (return_code != 0):
		print("the command return an error "+str(return_code))
		print(process_stderr)
		exit()
		
	liste_aei = process_stdout.split("\n")
	liste_aei.remove('') # we remove an extra element that doesn't mean anything
	return liste_aei

def mercury_restart():
	"""function that will restart a simulation. That means cleaning the existing file, 
	and launch the simulation again, from the start
	"""
	
	# For each folder were there is a problem (NaN in the output in other words) we clean and relaunch the simulation
	command = "rm *.out *.dmp *.tmp *.sh.* *.aei *.clo"
	print("\tCleaning the simulation files : %s" % command)
	(stdout, stderr, returnCode) = autiwa.lancer_commande(command)
	
	command = "./runjob"
	print("\tContinuing the simulation to allow it to finish properly : %s" % command)
	job = subprocess.Popen(command, shell=True)
	returnCode = job.wait()

def mercury_continue():
	"""function that will continue an existing simulation that did not have time to finish
	"""
	command = "rm *.aei *.clo"
	print("\tCleaning the simulation files : %s" % command)
	(stdout, stderr, returnCode) = autiwa.lancer_commande(command)

	command = "./runjob"
	print("\tStarting the simulation again : %s" % command)
	job = subprocess.Popen(command, shell=True)
	returnCode = job.wait()
	