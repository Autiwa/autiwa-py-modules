#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Librairies contenant des constantes utiles
# Version 0.18
# pour importer les variables, faire "from constants import *", 
# sinon, les variables s'appeleront constants.nom_variable
import math

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "15 novembre 2010"
__version__ = "$Revision: 0.18 $"
__credits__ = """Script that define several constants"""

######################
# Définition des constantes
######################
ms = 1.9891e30# kg masse du soleil
mj = 1.8986e27# kg masse de jupiter
mt = 5.9736e24# kg masse de la terre
msat = 5.6846e26# kg masse de saturne

dj = 1.326 #g/cm³ densité moyenne d'une planète géante (ici, densité moyenne de jupiter)
dt = 5.515 #g/cm³ densité moyenne d'une planète de type terrestre (ici, densité moyenne de la terre)

# en mètre valeur d'une unité astronomique
ua = 1.495979e11

# nombre de jours dans un an, c'est plus simple ensuite pour calculer T
yr = 365.25

# nombre de secondes dans une journée
day = 86400

# Constante de gravitation universelle en unité SI
G = 6.6726e-11

# Constante de la gravitation avec distance en ua, 
# temp en jours, et masse en masse solaire
G0 = 2.959122082855911e-4#G * jour**2 * ms / ua**3 

######################
# Facteurs de conversion
######################
degtorad = math.pi/180
radtodeg = 180/math.pi


#[]
#{}
#\{}
