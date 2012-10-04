#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module librement utilisable
"""module to retrieve information about a git repository and create a source code containing thoses informations."""
from __future__ import print_function

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "04 october 2012"
__version__ = "$Revision: 1.0 $"
__credits__ = """Thanks to Bastien for his help when I was learning Python and his usefull tutorial"""



import sys
import os
import time
import commands
import subprocess
import pdb

def run_command(commande):
		"""lance une commande qui sera typiquement soit une liste, soit une 
		commande seule. La fonction renvoit un tuple avec la sortie, 
		l'erreur et le code de retour"""
		if (type(commande)==list):
				process = subprocess.Popen(commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		elif (type(commande)==str):
				process = subprocess.Popen(commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		else:
				raise TypeError("La commande n'est ni une liste, ni une chaÃ®ne de caractÃ¨re.")
		(process_stdout, process_stderr) = process.communicate()
		returncode = process.poll()
		# there is .poll() or .wait() but I don't remember the difference. For some kind of things, one of the two was not working
		return (process_stdout, process_stderr, returncode)

def get_current_branch():
	"""function that return as a string the current branch of the git repository"""
	(stdout, stderr, returnCode) = run_command("git branch")
	
	if (returnCode != 0):
		return None
	
	lines = stdout.split("\n")
	for line in lines:
		if (line[0] == '*'):
			return line[2:]

def get_current_revision():
	"""function that return as a string the current revision of the git repository"""
	(stdout, stderr, returnCode) = run_command("git log|head -1")
	
	if (returnCode != 0):
		return None
	
	commit = stdout.split()[1]
	return commit

	