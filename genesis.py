#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module that host several useful functions linked to the simulation code Genesis

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "06 juin 2011"
__version__ = "$Revision: 1.41 $"
__credits__ = """Thanks to Bastien for his help when I was learning Python and his useful tutorial"""

from math import pi

class planetcom(object):
    """class that define and write a parameter file 'planet.com' in order to run a Genesis simulation.

    Parameters :
    (each parameter, if defined, MUST BE a list with one element for
    each planet. The length of each list in parameter must be the same !)
    m : list of mass for each planet regardless to the central mass
        (i.e the mass of the planet is exprimed in unit of the mass of the central body)
    a : list of semi-major axis for each planet in numerical units
    e : list of eccentricities for each planet
    I : list of inclinaison (in degrees) for each planet
    is_I_damping='default' : By default there is inclinaison damping only if I is different from 0. If you want, you can set this parameter to a boolean, and it will
                        be the same for all the planets. Or you can define a list. Thus, each element will have to
                        be a boolean for each planet.
    pfd='default' : Set if each planet feel or not the disk (boolean : True or False or 1 or 0) if not defined, the
                    list will be created and each planet will feel the disk
    pfo='default' : Set if each planet feel or not the others planets (boolean : True or False or 1 or 0) if not defined, the
                    list will be created and each planet will feel each other
    accretion='default' : (boolean : True or False or 1 or 0) Set if the planet will accrete gas. By default, they won't
    accretion_parameter='default' : Don't know what it is. Has an effect on the accretion rate I think
    maximum_mass='default' : Maximum mass of the planet through accretion. By default, it's around a Jovian mass.
    smoothing='default' : This is the epsilon (smoothing = epsilon * (H/R) * R_p) for the smoothing length of the gravitationnal potential of the planets. By default, everything is set to '0.4', following the prescription by Paardekooper et al. 2011.
    region_excluded='default' : "Region excluded from torque calculation". By default set to '0.d0'. This is set to exclude a
                                certain amount of gas around a planet. The value is a number of Hill radius to define
                                an exclusion sphere around the planet.

    Return :
    Nothing
    You can write the file in the current working directory by using the write() method
    """

    SEPARATOR = "  "

    #Hereafter the default values for several parameters.
    # We exclude by default a sphere of 1 hill radius around each planet.
    REGION_EXCLUDED = 1.e0
    # Normally, the correct value for smoothing is 0.6*H/R
    SMOOTHING = 0.4 # prescription by Paardekooper et al. 2011
    ACCRETION = False
    PLANET_FEEL_DISK = True
    PLANET_FEEL_OTHERS = True
    ACCRETION_PARAMETER = 1.66e0
    MAXIMUM_MASS = 1.e-3

    def __init__(self, m, a, e, I, is_I_damping='default', pfd='default', 
                pfo='default', accretion='default', accretion_parameter='default',
                 maximum_mass='default', smoothing='default', region_excluded='default'):
        # we define a temporary variable that will exist only in the
        # method and help us define defaults values for several parameters.
        nb_planets = len(m)

        self.m = m
        self.a = a
        self.e = e
        self.I = I

        # By default, there is damping in inclinaison. If is_I_damping is a boolean, then the same value is applied for each planet.
        if (is_I_damping == 'default'):
            is_I_damping = False
            for Ii in self.I:
                if (Ii != 0e0):
                    is_I_damping = True
                    break
        
        if (type(is_I_damping) == bool):
            self.is_I_damping = []
            for i in range(nb_planets):
                self.is_I_damping.append(1 * is_I_damping)
        else:
            self.is_I_damping = [i * 1 for i in is_I_damping]

        # If pfd is not set, we define defaults values
        if (pfo == 'default'):
            self.pfo = []
            for i in range(nb_planets):
                self.pfo.append(1 * planetcom.PLANET_FEEL_OTHERS)
        else:
            self.pfo = [i * 1 for i in pfo]

        # If pfo is not set, we define defaults values
        if (pfd == 'default'):
            self.pfd = []
            for i in range(nb_planets):
                self.pfd.append(1 * planetcom.PLANET_FEEL_DISK)
        else:
            for i in range(nb_planets):
                self.pfd = [i * 1 for i in pfd]

        # If accretion is not set, we define defaults values
        if (accretion == 'default'):
            self.accretion = []
            for i in range(nb_planets):
                self.accretion.append(1 * planetcom.ACCRETION)
        else:
            self.accretion = [i * 1 for i in accretion]

        # If accretion_parameter is not set, we define defaults values
        if (accretion_parameter == 'default'):
            self.accretion_parameter = []
            for i in range(nb_planets):
                self.accretion_parameter.append(planetcom.ACCRETION_PARAMETER)
        else:
            self.accretion_parameter = accretion_parameter

        # If maximum_mass is not set, we define defaults values
        if (maximum_mass == 'default'):
            self.maximum_mass = []
            for i in range(nb_planets):
                self.maximum_mass.append(planetcom.MAXIMUM_MASS)
        else:
            self.maximum_mass = maximum_mass

        # If smoothing is not set, we define defaults values
        if (smoothing == 'default'):
            self.smoothing = []
            for i in range(nb_planets):
                self.smoothing.append(planetcom.SMOOTHING)
        elif (type(smoothing) in [list, tuple]):
            self.smoothing = smoothing
        else:
            self.smoothing = []
            for i in range(nb_planets):
                self.smoothing.append(smoothing)
        
        
        # If region_excluded is not set, we define defaults values
        if (region_excluded == 'default'):
            self.region_excluded = []
            for i in range(nb_planets):
                self.region_excluded.append(planetcom.REGION_EXCLUDED)
        elif (type(region_excluded) in [list, tuple]):
            self.region_excluded = region_excluded
        else:
            self.region_excluded = []
            for i in range(nb_planets):
                self.region_excluded.append(region_excluded)
        
        # We automatically write the file when we initialize the object
        #self.write()

    def write(self):
        """method that write the file 'planet.com' in the current working directory"""

        planetcomfile = open("planet.com", 'w')

        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.m))+" : Mass of the planets (in mstar)\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.a))+" : Semi-major axes\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.e))+" : Eccentricities\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.I))+" : Inclinaison (deg)\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.is_I_damping))+" : is Inclinaison damping?\n")
        #"1 * " is here to allow the following parameters to be set undifferently to 0, 1, False or True (Indeed, 1 * True = 1 and 1 * False = 0)
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.pfd))+" : planets feel Disk ?\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.pfo))+" : planets feel others ?\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.accretion))+" : Accretion onto planets ?\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.accretion_parameter))+" : Accretion parameter\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.maximum_mass))+" : Maximum mass of the planet\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.smoothing))+" : Smoothing\n")
        planetcomfile.write(planetcom.SEPARATOR.join(map(str, self.region_excluded))+" : Region excluded from torque calculation\n")

        planetcomfile.close()

class parcom(object):
    """class that define and write a parameter file 'par.com' in order to run a Genesis simulation.

    Parameters :
    rmin : The radius from where the disk begin, in numerical units
    rmax : The radius where the disk end, in numerical units
    aspect_ratio : (H/R) of the disk
    flaring_index : the flaring index f is defined by : (H/R) = (H/R)_(R_0) * (R/R_0)^f
    density : density Sigma_0 of the disk in numerical units, at R=1
    density_exponent : exponent for the density formulae wich is of the form sigma = sigma_0 * R^exponent
    omega_frame : The omega angular speed of the frame
    wd_rint : Rint is radius at which the wave damping begin after the inner edge
    wd_rout : Rout is radius at which the wave damping end before the outer edge
    unityLength=5.0 : the equivalent for the length numerical unit in ua.
    unityMass=1.0 : the equivalent for the weight numerical unit in solar mass
    alpha=None : the parameter to set the density, wich is defined as nu = alpha * c_s * H (c_s being the sound speed and H the
                 thickness of the disk). If not set, then the value default_viscosity is used
    viscosity_default=0.e0 : The viscosity value used by genesis if alpha is not set
    linear_viscosity=None : the value of the linear viscosity
    turbulence_forcing=None : the value of the forcing of the turbulence
    isIsothermal=False : is the disk is isothermal (else, it will be adiabatic).
    adiabatic_index=1.4e0 : the adiabatic index gamma (p*V^gamma=constant)
    mean_molecular_weight=2.35e0 : the mean molecular weight (IN SOLAR MASS?)
    isViscousHeating=False : do we have viscous heating?
    isRadiativeTransfert=False : do we have radiative transfert?
    isFargo=True : do we use the FARGO algorithm to determine the timestep?
    isWaveDamping=True : do we have wave damping?
    cfl_coeff=0.5e0 : the CFL coeff. That is to say, it's a safe parameter to reduce the timestep in case of. For instance, the
                      code will determine a value of timestep, but the real timestep used will be multiplied by the CFL coeff.
    n_restart=None : if set, must be an integer that tells wich restart file we will use to restart the simulation.
                     The boolean isRestart is automatically set to the right value, given the value of n_restart
    dtprint=6.28318 : time between two outputs. time is set so that 2*pi equals one orbit. That is to say, with 6.28318, we
                      have an output for the planet position each orbit (i.e once a year roughly).
    isTurbulence=False : is there turbulence in the disk?
    mode_min=1 : the low index for the computation of turbulence
    mode_max=48 : the upper index for the computation of turbulence
    mode_cut=6 : a cut for the modes, but I don't understand it
    mode_timelife=0.1e0 : has something to do with the mode and the fact that they fade away with a certain characteristic time
    isHeatingCoolingTerms=True : determine wether or not we add heating and cooling terms
    isRadiativeDiffusion=True : is there radiative diffusion ?
    BoundaryConditionInner='C' : Boundary conditions ('C':closed,'V':viscous,'O':outflow)
    BoundaryConditionOuter='C' : Boundary conditions ('C':closed,'V':viscous,'O':outflow)
    isRestartPlanets=True : Do we read planet restart files? (if not, we read planet.com instead)

    Return :
    Nothing
    You can write the file in the current working directory by using the write() method
    """

    SEPARATOR = "  "

    def __init__(self, rmin, rmax, aspect_ratio, flaring_index, density,
                density_exponent, wd_rint, wd_rout,lengthUnit=5.0, massUnit=1.0, 
                omega_frame=0.e0, alpha=None, linear_viscosity=None, turbulence_forcing=None, 
                isIsothermal=False, adiabatic_index=1.4e0, mean_molecular_weight=2.35e0, 
                viscosity_default=0.e0, isHeatingCoolingTerms=False, isRadiativeDiffusion=False, 
                isFargo=True, isWaveDamping=True, cfl_coeff=0.5e0, n_restart=None, 
                isRestartPlanets=True, dtprint=6.28318, isTurbulence=False, 
                mode_min=1, mode_max=48, mode_cut=6, mode_timelife=0.1e0, 
                BoundaryConditionInner='C', BoundaryConditionOuter='C'):
        """method that set the instance of the class. """

        # isTurbulence, isViscosity and isLinearViscosity are automatically set to the right value in function of the parameters needed if they are set to True.

        #parameters that must be set
        self.rmin = rmin
        self.rmax = rmax
        self.aspect_ratio = aspect_ratio
        self.flaring_index = flaring_index
        self.density = density
        self.density_exponent = density_exponent
        self.omega_frame = omega_frame
        self.wd_rint = wd_rint
        self.wd_rout = wd_rout

        #parameters that have a default value
        self.lengthUnit = lengthUnit
        self.massUnit = massUnit
        self.cfl_coeff = cfl_coeff
        self.isIsothermal = isIsothermal
        self.adiabatic_index = adiabatic_index
        self.mean_molecular_weight = mean_molecular_weight
        self.viscosity_default = viscosity_default
        self.isHeatingCoolingTerms = isHeatingCoolingTerms
        self.isRadiativeDiffusion = isRadiativeDiffusion
        self.isFargo = isFargo
        self.isWaveDamping = isWaveDamping
        self.BoundaryConditionInner = BoundaryConditionInner
        self.BoundaryConditionOuter = BoundaryConditionOuter
        self.mode_min = mode_min
        self.mode_max = mode_max
        self.mode_cut = mode_cut
        self.mode_timelife = mode_timelife
        self.dtprint = dtprint

        if (alpha == None):
            self.isViscosity = False
            self.alpha = 2.e-3
        else:
            self.isViscosity = True
            self.alpha = alpha

        if (linear_viscosity == None):
            self.isLinearViscosity = False
            self.linear_viscosity = 0.45
        else:
            self.isLinearViscosity = True
            self.linear_viscosity = linear_viscosity

        if (turbulence_forcing == None):
            self.isTurbulence = False
            self.turbulence_forcing = 1.3e-4
        else:
            self.isTurbulence = True
            self.turbulence_forcing = turbulence_forcing

        # In case we do not want a restart, a default valid value for
        # nrestart is set. The value itself doesn't count, the only thing
        # important is to be valid compared to the program syntax
        if (n_restart == None):
            self.isRestart = False
            self.n_restart = 0
        else:
            self.isRestart = True
            self.n_restart = n_restart

        self.isRestartPlanets = isRestartPlanets
        
        #####
        # Tests of the coherence of the simulation
        # Test of boundary conditions
        if (self.BoundaryConditionInner not in ['C', 'V', 'O', 'c', 'v', 'o']):
            print("Warning: The Inner boundary condition is not valid.")
        
        if (self.BoundaryConditionOuter not in ['C', 'V', 'O', 'c', 'v', 'o']):
            print("Warning: The Outer boundary condition is not valid.")
        
        # We MUST NOT do wave damping if the inner and/or outer edges conditions of the disk are not 'C' (close) conditions
        if (self.isWaveDamping and ((self.BoundaryConditionInner not in ['C', 'c']) or (self.BoundaryConditionOuter not in ['C', 'c']))):
            print("Warning: We MUST not define Wave damping for an edge that has not a 'close' boundary condition")
            
            if ((self.BoundaryConditionInner not in ['C', 'c']) and self.wd_rint != 0e0):
                print("Warning: Inner wave damping radius or boundary condition must be changed")
            if ((self.BoundaryConditionOuter not in ['C', 'c']) and self.wd_rout != 0e0):
                print("Warning: Outer wave damping radius or boundary condition must be changed")
        
        # Wave damping, if present, must occur IN the disk
        if (self.isWaveDamping):
            if (self.wd_rint < rmin):
                print("Warning: The inner wave damping radius is not in the disk")
            if (self.wd_rout > rmax):
                print("Warning: The outer wave damping radius is not in the disk")


        # We automatically write the file when we initialize the object
        # self.write()

    def write(self):
        """method that write the file 'par.com' in the current working directory"""

        parcomfile = open("par.com", 'w')

        parcomfile.write(str(self.rmin)+parcom.SEPARATOR+str(self.rmax)+" : Rmin,Rmax\n")
        parcomfile.write(str(self.aspect_ratio)+parcom.SEPARATOR+str(self.flaring_index)+" : Aspect ratio, Flaring Index\n")
        parcomfile.write(str(self.density)+parcom.SEPARATOR+str(self.density_exponent)+" : Density, Exponent\n")
        parcomfile.write(str(1 * self.isIsothermal)+parcom.SEPARATOR+str(self.adiabatic_index)+" : is isothermal EOS? (adiabatic if not), Adiabatic index\n")
        parcomfile.write(str(self.mean_molecular_weight)+" : Mean Molecular Weight\n")
        # multiplying by 1 allow us to define the parameter to True or False. Indeed, in the parameter file, only 1 or 0 are allowed
        parcomfile.write(str(self.viscosity_default)+parcom.SEPARATOR+str(1 * self.isViscosity)+parcom.SEPARATOR+str(self.alpha)+" : default value 'nu' if no viscosity, is Viscosity?, alpha\n")
        parcomfile.write(str(1 * self.isHeatingCoolingTerms)+" : is Heating/cooling terms? (not important if isothermal)\n")
        parcomfile.write(str(1 * self.isRadiativeDiffusion)+" : is Radiative diffusion? (not important if isothermal)\n")
        parcomfile.write(str(self.omega_frame)+" : Omega frame\n")
        parcomfile.write(str(1 * self.isFargo)+" : is Fargo?\n")
        parcomfile.write("'"+str(self.BoundaryConditionInner)+"'"+parcom.SEPARATOR+"'"+str(self.BoundaryConditionOuter)+"'"+" : Boundary conditions ('C':closed,'V':viscous,'O':outflow) \n")
        parcomfile.write(str(1 * self.isWaveDamping)+parcom.SEPARATOR+str(self.wd_rint)+parcom.SEPARATOR+str(self.wd_rout)+" : is Wave damping?, Rint damping, Rout damping\n")
        parcomfile.write(str(1 * self.isLinearViscosity)+parcom.SEPARATOR+str(self.linear_viscosity)+" : is Linear viscosity?, radius (in N.u.) below the viscosity will be linear. (there must not be WD!)\n")
        parcomfile.write(str(self.cfl_coeff)+" : CFL coef.\n")
        parcomfile.write(str(1 * self.isRestart)+parcom.SEPARATOR+str(self.n_restart)+" : is Restart?, Nrestart\n")
        parcomfile.write(str(1 * self.isRestartPlanets)+" : Do we read planet restart files? (if not, we read planet.com instead)\n")
        parcomfile.write(str(self.dtprint)+" : dtprint\n")
        parcomfile.write(str(1 * self.isTurbulence)+" : is Turbulence?\n")
        parcomfile.write(str(self.turbulence_forcing)+" : turbulence forcing\n")
        parcomfile.write(str(self.mode_min)+parcom.SEPARATOR+str(self.mode_max)+parcom.SEPARATOR+str(self.mode_cut)+" : Mode min, Mode max, cut (for turbulences)\n")
        parcomfile.write(str(self.mode_timelife)+" : Timelife of modes\n")
        parcomfile.write(str(self.lengthUnit)+parcom.SEPARATOR+str(self.massUnit)+" : lengthUnit (in ua) and massUnit (in Ms) for numerical units\n")

        parcomfile.close()

class mpidata(object):
    """class that define and write a parameter file 'MPI.DATA' in order to run a Genesis simulation.

    Parameters :
    nb_proc=1 : integer that represent the number of processors we will use azimutally to run the genesis simulation (i.e if we set one processor, then each ring in the grid will 'have' only one processor, but several processor can compute radially).

    Return :
    Nothing
    You can write the file in the current working directory by using the write() method
    """

    def __init__(self, nb_proc=1):
        """nb_proc must be an integer"""

        self.nb_proc = int(nb_proc)

        # We automatically write the file when we initialize the object
        #self.write()

    def write(self):
        """method that write the file 'MPI.DATA' in the current working directory"""

        mpidatafile = open("MPI.DATA", 'w')
        mpidatafile.write(str(self.nb_proc))
        mpidatafile.close()

if __name__=='__main__':
    parcom(rmin=0.6, rmax=2.5, aspect_ratio=0.05, flaring_index=0.e0, density=2.e-3, density_exponent=-0.5e0, wd_rint=0.75e0, wd_rout=2.3e0).write()

    mpidata().write()

    m = [2 * (i + 1) * 3e-6 for i in range(5)]
    a=[1 + i * 0.2 for i in range(5)]
    e=[0.01 for i in range(5)]
    I=[1. + 0.2*i for i in range(5)]

    planetcom(m, a, e, I).write()

    #testUnitairesparcom()

    #testUnitairesplanetcom()

    #testUnitairesmpidata()


#[]
#{}
#\{}

#CHANGELOG

#v1.27 : now, inclination must be defined in degrees. planetcom has been modified in consequence.
