#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script that generate parameter files for genesis simulation code.
# In particuliar, it helps generate random planetary systems.
from __future__ import print_function

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "24 août 2011"
__version__ = "$Revision: 0.2 $"
__credits__ = """Module that contains functions to help generate simulations, no matter the code. Function to generate random parameters
function to round values with significative round and so on."""

from random import uniform, gauss
from constants import *
from math import *
import pdb
import subprocess

def setExecutionRight(doc_name):
	"""function that set the right for the file to be executed. This file must be in the current working directory

	Parameters
	doc_name = the name of the file

	Return : the return code of the chmod command. If 0, then everything went good.
	"""

	import subprocess

	command = "chmod u+x "+doc_name

	process = subprocess.Popen(command, shell=True)
	returncode = process.poll()

	return returncode

def str2bool(value):
	"""function that convert a string into a boolean given various ways to say 'True'. 
	The normal behaviour in python is to set to 
	True when the string is not empty, which is not what I want.
	
	Return : True (boolean) if value is 'True', 'yes', 1 or '.true.' 
	(no matter the case, i.e True, TRUE, true or tRuE will work)"""
	return value.lower() in ("yes", "true", "1", '.true.')
	
def str2str(value):
	"""function that convert a string into a string. That might be weird to say, 
	but this function aim to suppress any '"' or "'" in string
	
	Return a string without extremal quotes that might exist
	"""
	
	# We suppress extremal white spaces
	value = value.strip()
	
	value = value.strip('"').strip("'")
	
	return value


def writeRunjob(command, queue, nb_proc=1):
	"""function that creates a script named 'runjob' that
	will run a job on a queue. If the number of processor exceed 1, then
	 the function will try to launch the job on every queue. If not, it
	 will launch the job on all the parallel queues.

	Parameters
	nb_proc=1 : (integer) number of processor we want to use. By default, it will be 1
	queue : the queue you want to use to launch your job. You can use the various syntaxes allowed by the job scheduler. 
	command : The command you want the job to launch. 
	
	Example : 
	writeRunjob("./mercury", "arguin1.q,arguin2.q")
	will create a "runjob" script that will look like : 
	qsub -q arguin1.q,arguin2.q ./mercury

	Return : Nothing
	"""

	NAME_SCRIPT = "runjob"

	
	
	if (queue == ""):
		queue_append = ""
	else:
		queue_append = " -q "+queue
	
	script = open(NAME_SCRIPT, 'w')
	if (nb_proc > 1):
		script.write("qsub -pe mpi "+str(nb_proc)+queue_append+" "+command)
	else:
		script.write("qsub"+queue_append+" "+command)

	script.close()

	setExecutionRight(NAME_SCRIPT)

def setParameter(parameter, nb_planets):
	"""This function will generate the parameters list given a tuple a values.. 
	
	Parameter : 
	parameter : If parameter is a number, then it will be assumed that all the planets have the same value
				If parameter is a list or a tuple, then so far, it must have 3 elements. The third element must be either 'uniform' or 'gauss'.
				If it's 'uniform', then the first two elements will be assumed to be min and max for uniform random generation. 
				If it's 'gauss' then the first will be the mean value and the second the standard deviation.
				!!! IF IT'S A LIST OR A TUPLE, IT MUST HAVE 3 VALUES
	
	Exemple : 
	(if nb_planets=3)
	>>> a = setParameter(2.0, 3)
	>>> print(a)
	[2.0, 2.0, 2.0]
	
	>>> a = setParameter(2, 3)
	>>> print(a)
	[2, 2, 2]
	
	>>> a = setParameter((1, 2, 'uniform'), 3)
	>>> print(a)
	[1.0422813370661363, 1.5658739594149007, 1.3426454303851822]
	
	>>> a = setParameter((0.05, 0.01, 'gaussian'), 3)
	>>> print(a)
	[0.061185035654398909, 0.049134828792707953, 0.034602504519382703]
	
	
	return : the list of planet parameters.
	"""
	# Significative numbers for the figures
	SIGNIFICATIVE_NUMBERS = 4
	
	if (type(parameter) in (int, float)):
		output_parameters = [significativeRound(parameter,SIGNIFICATIVE_NUMBERS) for i in range(nb_planets)]
		return output_parameters
	elif (type(parameter) in [tuple, list] and parameter[2] == 'uniform'):
		output_parameters = [significativeRound(uniform(parameter[0], parameter[1]),SIGNIFICATIVE_NUMBERS) for i in range(nb_planets)]
		return output_parameters
	elif (type(parameter) in [tuple, list] and parameter[2] == 'gaussian'):
		output_parameters = [significativeRound(gauss(parameter[0], parameter[1]),SIGNIFICATIVE_NUMBERS) for i in range(nb_planets)]
		return output_parameters
	else:
		raise ValueError("The way you're trying to set the parameter doesn't seems to be implemented so far")

def significativeRound(real,roundNumber):
	"""function that return a truncative floating number of the number 
	in parameter, given the roundNumber we want
	Version 2.0
	
	Parameters
	real : The floating point number we want to truncate
	roundNumber : the number of significative figures we want
	"""
	#print "Warning:pour test, ne fait rien!!"
	#return real
	import math
	
	if (roundNumber == 0):
		print("'roundNumber' is set to 0")
		exit
	elif (type(roundNumber) != int):
		print("'roundNumber' is not an integer")
		exit
	
	# If an integer, we'll have problem for divisions.
	if (type(real) != float):
		real = float(real)
	
	if (real == 0.):
		return 0.
	
	# in case we have negative number
	if (real < 0.):
		negative = True
		real = - real
	else:
		negative = False
	
	significativeNumbers = []
	
	# First we initialise various parameters for the loop. The principle
	# is to extract the integer part of the logarithm. This way, we 
	# retrieve the first significative number. By substracting this 
	# number to the original number, we can successively retrieve all 
	# the significative figures.
	
	# We first get the order of magnitude of the number to be able to 
	# retrieve all the significative numbers in the loop after that.
	logNumber = int(math.log10(real))

	significativeNumbers = [0] # we force the 'while' loop to do at least one turn
	# For numbers under 1, we search for the first significative number
	while (significativeNumbers[-1] == 0):
		ordMagn = 10**logNumber
		significativeNumbers = [int(real/ordMagn)]
		decimalPart = real/ordMagn - significativeNumbers[-1]
		logNumber = logNumber - 1 # if this is the last turn, this line will do nothing. This avoid to substract one in the first turn (if we had done it at the beginning)

	if (significativeNumbers[-1] == 0):
		ordMagn = ordMagn / 10
		try:
			significativeNumbers = [int(real/ordMagn)]
		except:
			print(real)
			pdb.set_trace()
		decimalPart = real/ordMagn - significativeNumbers[-1]
		
	for i in range(roundNumber-2):
		significativeNumbers.append(int(decimalPart * 10))
		decimalPart = decimalPart * 10 - significativeNumbers[-1]
	
	# For the last number we must round.
	significativeNumbers.append(int(round(decimalPart * 10 + 0.5)))
		
	numberWithoutMagn = 0.
	for (i, si) in enumerate(significativeNumbers):
		numberWithoutMagn += si * 10**(-i)
	
	truncatedNumber = ordMagn * numberWithoutMagn
	
	if not(negative):
		return truncatedNumber
	else:
		return -truncatedNumber

def number_fill(number, fill):
	"""function that create a string given a number in parameter and the length 
	of the final string we want. It is used, for instance, to generate name for 
	folders were a counter is used. We get the maximal length of the string with 
	the maximal number of folders, and with this, we will know how many "0" 
	we need to display the folders. 
	
	Parameters 
	number : the number we want to display
	fill : the total length of the string we want. Zero will be added on the left to get this length
	
	Return : A string that display the number. 
	
	RMQ : An error is returned if the length of the string is not sufficient to display the number.
	
	Example : 
	display = number_fill(18, 4) 
	print(display)
	0018
	"""
	
	number = str(number)
	
	if (len(number) > fill):
		raise ValueError("The desired length of the string is not sufficient to display the number")
	
	# tant qu'on n'a pas la bonne taille, on rajoute des "0" Ã  gauche.
	while (len(number) < fill):
		number = "0"+number
	
	return number


if __name__=='__main__':
  print("No tests are implemented so far.")


