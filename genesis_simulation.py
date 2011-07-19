#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Script that generate parameter files for genesis simulation code.
# In particuliar, it helps generate random planetary systems.
from __future__ import print_function

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "17 mai 2011"
__version__ = "$Revision: 1.13 $"
__credits__ = """Module that contains functions to help generate parameter files."""

import subprocess
from random import uniform, gauss
from genesis import parcom, planetcom
from constants import *
from autiwa import significativeRound
from math import *
import os
import pdb

# PARAMETERS
# default path to the simulation program genesis
LOCATION_PRGM = "/home/cossou/bin/genesis/genesis"

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


def writeGenesisLauncher(nb_proc, location_program=LOCATION_PRGM):
    """function that creates a bash script named 'genesis.sh' that
    specify the number of processor we want to use.

    Parameters
    nb_proc : (integer) number of processor we want to use (maxi 8,
    determined by the configuration of the mpi environment of venus)

    Return : Nothing
    """

    BEGIN_SCRIPT = "#/bin/sh\n" + \
                   "#$ -V\n" + \
                   "#$ -cwd\n"

    NAME_SCRIPT = "genesis.sh"

    script = open(NAME_SCRIPT, 'w')
    script.write(BEGIN_SCRIPT)
    script.write("date=`date '+%d/%m/%Y %T'`\n")
    script.write('echo "[$date] launching a simulation on the folder $PWD">>~/qsub.log\n')
    script.write("mpiexec.gforker -np "+str(nb_proc)+" "+location_program+"\n")
    script.close()

    setExecutionRight(NAME_SCRIPT)

def writeParameters(M_TOT, DELTA, A_MIN, A_MAX, a, E, I, M_MIN, M_MAX, m, R_MIN, R_MAX):
    """function that writes all parameters, even random parameters,
    used for the generation of the planetary system and the gas disk in
    a file whose name is defined in the LOG_PARAMETERS constant
    """

    LOG_PARAMETERS = "random_parameters.log"

    log = open(LOG_PARAMETERS, 'w')
    log.write("the total mass contained in the protoplanets is :\n")
    log.write("m_tot = "+str(M_TOT)+" earth masses\n")
    if (type(DELTA) in (float, int)):
        log.write("the number of mutual hill radii between the planets is set to :\n")
        log.write("delta="+str(DELTA)+"\n")
    else:
        log.write("the number of mutual hill radii between the planets is randomly generated ("+DELTA[2]+") between :\n")
        log.write("delta_min="+str(DELTA[0])+" and delta_max="+str(DELTA[1]))

    if (A_MAX == A_MIN):
        log.write("the semi-major axis of the first proto-planet is set to :\n")
        log.write("a="+str(A_MAX)+" ua\n")
    else:
        log.write("the semi-major axis of the first proto-planet is randomly generated between :\n")
        log.write("a_min="+str(A_MIN)+" ua and a_max="+str(A_MAX)+" ua\n")

    if (type(E) in (float, int)):
        log.write("the eccentricities of the protoplanets are set to :\n")
        log.write("e="+str(E)+"\n")
    else:
        log.write("the eccentricities of the protoplanets are randomly generated ("+E[2]+") between :\n")
        if (E[2] == 'gaussian'):
            random = ["mean", "sigma"]
        elif (EI[2] == 'uniform'):
            random = ["min", "max"]
        log.write("e_"+random[0]+"="+str(E[0])+" and e_"+random[1]+"="+str(E[1])+"\n")

    if (type(I) in (float, int)):
        log.write("the inclinaisons of the protoplanets are set to :\n")
        log.write("I="+str(I)+" deg\n")
    else:
        log.write("the inclinaisons of the protoplanets are randomly generated ("+I[2]+") between :\n")
        if (I[2] == 'gaussian'):
            random = ["mean", "sigma"]
        elif (I[2] == 'uniform'):
            random = ["min", "max"]
        log.write("I_"+random[0]+"="+str(I[0])+" deg and I_"+random[1]+"="+str(I[1])+" deg\n")

    if (M_MAX == M_MIN):
        log.write("the masses of the protoplanets are set to :\n")
        log.write("m="+str(M_MAX)+" earth mass\n")
    else:
        log.write("the masses of the protoplanets are randomly generated between :\n")
        log.write("m_min="+str(M_MIN)+" earth mass and m_max="+str(M_MAX)+" earth mass\n")
        log.write("the masses in earth mass are :\n")
        log.write(str([round(mi*ms/mt, 2) for mi in m])+"\n")

    log.write("the edges of the gas disk are :\n")
    log.write("R_min="+str(R_MIN)+" N.u. and R_max="+str(R_MAX)+" N.u\n")
    log.write("(Note that the outer edge might be greater than that if a very far away planet exist)")
    log.close()


def writeRunjob(nb_proc):
    """function that creates a script named 'runjob' that
    will run a job on a queue. If the number of processor exceed 1, then
     the function will try to launch the job on every queue. If not, it
     will launch the job on all the parallel queues.

    Parameters
    nb_proc : (integer) number of processor we want to use (maxi 8,
    determined by the configuration of the mpi environment of venus)

    Return : Nothin
    """

    NAME_SCRIPT = "runjob"

    script = open(NAME_SCRIPT, 'w')
    if (nb_proc > 1):
        script.write("qsub -pe mpi "+str(nb_proc)+" -q arguin-mpi.q  ./genesis.sh")
    else:
        script.write("qsub ./genesis.sh")

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

def setBoolean(parameter, nb_planets=None):
    """This function will generate the parameters list given a tuple a values.. 
    
    Parameter : 
    parameter : If parameter is a boolean, then it will be assumed that all the planets have the same value
                If parameter is a list or a tuple, then so far, it must have 3 elements. The third element must be either 'uniform' or 'gauss'.
                If it's 'uniform', then the first two elements will be assumed to be min and max for uniform random generation. 
                If it's 'gauss' then the first will be the mean value and the second the standard deviation.
                !!! IF IT'S A LIST OR A TUPLE, IT MUST HAVE 3 VALUES
    nb_planets=None : You must set nb_planets if you give a non list/tuple value
    
    Exemple : 
    (if nb_planets=3)
    >>> a = setParameter(True, 3)
    >>> print(a)
    [True, True, True]
    
    >>> a = setParameter(1, 3)
    >>> print(a)
    [True, True, True]
    
    >>> a = setParameter([True, False, True])
    >>> print(a)
    [True, False, True]
    
    
    return : the list of planet parameters.
    """
    
    if (type(parameter) in (bool, int, float)):
        output_parameters = [bool(parameter) for i in range(nb_planets)]
        return output_parameters
    elif (type(parameter) in [tuple, list]):
        output_parameters = parameter
        return output_parameters
    else:
        raise ValueError("The way you're trying to set the parameter doesn't seems to be implemented so far")

def readPlanetCom():
    """function that read a 'planet.com' file and return a planetcom object
    """

    try:
        planetcomfile = open('planet.com','r')
    except IOError:
        print("Warning: The file 'planet.com' does not exist")
        return -1
    lines = planetcomfile.readlines()
# En fortran on peut aussi noter les puissances de 10 via un "d", ce qui n'est pas accepté en python.
    lines = [line.split(':')[0].replace('d','e') for line in lines]
    planetcomfile.close()
    

    m = map(float,lines[0].split())
    a = map(float,lines[1].split())
    e = map(float,lines[2].split())
    I = map(float,lines[3].split())
    is_I_damping = map(bool,map(int,lines[4].split()))
    pfd = map(bool,map(int,lines[5].split()))
    pfo = map(bool,map(int,lines[6].split()))
    accretion = map(bool,map(int,lines[7].split()))
    accretion_parameter = map(float,lines[8].split())
    maximum_mass = map(float,lines[9].split())
    smoothing = map(float,lines[10].split())
    region_excluded = map(float,lines[11].split())

    planetcomobject = planetcom(m=m, a=a, e=e, I=I, is_I_damping=is_I_damping, pfd=pfd, pfo=pfo, accretion=accretion, accretion_parameter=accretion_parameter, maximum_mass=maximum_mass, smoothing=smoothing, region_excluded=region_excluded)

    return planetcomobject

def readParCom():
    """function that read a 'par.com' file and return a parcom object
    """
    
    try:
        parcomfile = open('par.com','r')
    except IOError:
        print("Warning: The file 'par.com' does not exist")
        return -1
    lines = parcomfile.readlines()
    parcomfile.close()

# En fortran on peut aussi noter les puissances de 10 via un "d", ce qui n'est pas accepté en python.
    lines = [line.split(':')[0].replace('d','e') for line in lines]
    
    [rmin, rmax] = map(float,lines[0].split())
    [aspect_ratio, flaring_index] = map(float,lines[1].split())
    [density, density_exponent] = map(float,lines[2].split())
    [isIsothermal, adiabatic_index] = map(float,lines[3].split())
    mean_molecular_weight = float(lines[4])
    [viscosity_default, isViscosity, alpha] = map(float,lines[5].split())
    isHeatingCoolingTerms = int(lines[6])
    isRadiativeDiffusion = int(lines[7])
    omega_frame = float(lines[8])
    isFargo = int(lines[9])
    # We must eval each value of boundary condition, else, we'll have "'C'" wich will not be valid
    [BoundaryConditionInner, BoundaryConditionOuter] = map(eval,lines[10].split())
    [isWaveDamping, wd_rint, wd_rout] = map(float,lines[11].split())
    [isLinearViscosity, linear_vicosity] = map(float,lines[12].split())
    cfl_coeff = float(lines[13])
    [isRestart, n_restart] = map(int,lines[14].split())
    isRestartPlanets = float(lines[15])
    dtprint = float(lines[16])
    isTurbulence = int(lines[17])
    turbulence_forcing = float(lines[18])
    [mode_min, mode_max, mode_cut] = map(int,lines[19].split())
    mode_timelife = float(lines[20])
    [lengthUnit, massUnit] = map(float,lines[21].split())

    # I don't remember how to modify them in a loop (because all changes in the list booleans do nothing on each variables that he contains)
    booleans = (isIsothermal, isViscosity, isHeatingCoolingTerms, isRadiativeDiffusion, isFargo, isWaveDamping, isLinearViscosity, isRestart, isRestartPlanets, isTurbulence)
    (isIsothermal, isViscosity, isHeatingCoolingTerms, isRadiativeDiffusion, isFargo, isWaveDamping, isLinearViscosity, isRestart, isRestartPlanets, isTurbulence)=map(bool,booleans)

    if not(isViscosity):
        alpha = None

    if not(isLinearViscosity):
        linear_viscosity = None
    
    if not(isTurbulence):
        turbulence_forcing = None

    if not(isRestart):
        n_restart = None
        

    parcomobject = parcom(rmin=rmin, rmax=rmax, aspect_ratio=aspect_ratio, flaring_index=flaring_index, density=density, density_exponent=density_exponent, wd_rint=wd_rint, wd_rout=wd_rout, lengthUnit=lengthUnit, massUnit=massUnit, omega_frame=omega_frame, alpha=alpha, linear_viscosity=linear_viscosity, turbulence_forcing=turbulence_forcing, isIsothermal=isIsothermal, adiabatic_index=adiabatic_index, mean_molecular_weight=mean_molecular_weight, viscosity_default=viscosity_default, isHeatingCoolingTerms=isHeatingCoolingTerms, isRadiativeDiffusion=isRadiativeDiffusion, isFargo=isFargo, isWaveDamping=isWaveDamping, cfl_coeff=cfl_coeff, n_restart=n_restart, isRestartPlanets=isRestartPlanets, dtprint=dtprint, isTurbulence=isTurbulence, mode_min=mode_min, mode_max=mode_max, mode_cut=mode_cut, mode_timelife=mode_timelife, BoundaryConditionInner=BoundaryConditionInner, BoundaryConditionOuter=BoundaryConditionOuter)

    return parcomobject

def getResolution():
    """function that return the minimal resolution for a radiative 
    simulation in order to have the corotation region resolved (i.e at 
    least 4 cells in each part of the region) and an azimuthal resolution 
    sufficiant to have square cells at R=1 in numerical units

    Return :
    A list of tuple containing the mass of the planet and the resolution 
    needed for this planet to resolve the corotation region.
    """
    CELL_NUMBER = 4

    planetcom = readPlanetCom()
    parcom = readParCom()
    corot_region = []
    rad_res = []
    az_res = []
    for (mi,ai) in zip(planetcom.m, planetcom.a):
        x_s = sqrt(1.7 * (mi / parcom.massUnit) / parcom.aspect_ratio * ai**2)
        corot_region.append(x_s)
    
        # we round the value to the next positive integer.
        rad_res.append(int((parcom.rmax - parcom.rmin) / (x_s / CELL_NUMBER)) + 1)

        # We want to have square cells at the inner edge. It's not very important, 
        # but if we care about azimuthal res, square cells at inner edge is important
        az_res.append(int(2 * pi / ((parcom.rmax - parcom.rmin) / (parcom.rmin * rad_res[-1]))) + 1)
    

    return zip(planetcom.m, zip(rad_res,az_res))

if __name__=='__main__':
    parcom(rmin=0.6, rmax=2.5, aspect_ratio=0.05, flaring_index=0.e0, density=2.e-3, density_exponent=-0.5e0, wd_rint=0.75e0, wd_rout=2.3e0).write()

    test=readParCom()
    test.write()

    m = [2 * (i + 1) * 3e-6 for i in range(5)]
    a=[1 + i * 0.2 for i in range(5)]
    e=[0.01 for i in range(5)]
    I=[1. + 0.2*i for i in range(5)]

    planetcom(m, a, e, I).write()
    test = readPlanetCom()
    test.write()

    print(getResolution())

    


