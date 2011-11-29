#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "14 novembre 2011"
__version__ = "$Revision: 1.7.1 $"
__credits__ = """Based on the work of Pierre gay, in particuliar his get_module function."""

"""The aim of this module is to provide a simple way to compile complex fortran programs with various dependencies. 

All you have to do is to define wich sourcefile is the main sourcefile. The module will get binaries only for theses sources (there can be severals)
"""
import os, sys
import string
import subprocess # To launch various process, get outputs et errors, returnCode and so on.
import difflib # To compare two strings
import pdb # To debug
from svg import *


def make_binaries(sources_filename, mains, debug=False, gdb=False, profiling=False):
  """function that will compile every needed sourceFile and get a 
  binary for the defined source files
  
  Parameters : 
  sources_filename : a list of source filenames that must be present in the current working directory for which we will define an object 'sourceFile'
  mains : either a list of filename or a dictionnary for which keys are filename and values are the name of the binary file we want.
   i.e we define a list of filename if we want that the binary has the same name (without extension) as the source file, 
   or a dictionnary to make the correspondance between the two.
  debug=False : (boolean) Whether we want or not debug options for compilation. There is no debug by default
  gdb=False : If set to True, will add a compilation option to run the program under the GNU debugger gdb. 
  profiling=False : If set to True, will change compilation options to profile the binary files (using gprof). 
                    As a consequence, this will deactivate all optimization options. 
  
  Examples : 
  make_binaries(sources_filename, {"mercury6_2.for":"mercury", "element6.for":"element", "close6.for":"close"})
  or
  make_binaries(sources_filename, ["mercury.f90", "element.f90", "close.f90"])
  where 'sources_filename' is a list of all the sources file with the extension '*.for' and '*.f90' respectively.
  
  """
  
  # We define the objects for each source file.
  sources = []
  for filename in sources_filename:
    source = sourceFile(filename)
    sources.append(source)
  
  # If source filename and name of the binary is the same (except the extension) we can define only the list of names, but else 
  # we can set a dictionnary to define the correspondance between the source filename (as keys() ) and the name of the binary (as values() )
  if (type(mains) == dict):
    main_list = mains.keys()
    for source in sources:
      source.name = mains[source.filename]
  elif (type(mains) == list):
    main_list = mains
    
  # For the source files which are programs, we set the flag.
  for main in main_list:
    sourceFile.findSource[main].setProgram(True)
  
  sourceFile.setDebug(debug)
  sourceFile.setGDB(gdb)
  sourceFile.setProfiling(profiling)
  
  # We compile the programs (dependencies are automatically compiled if needed.
  for source in sources:
    if (not(source.isCompiled) and source.isProgram):
      print source.compile()

def run(command):
  """run a command that will be a string.
  The function return a tuple with the output, 
  the stderr and the return code. 
  It is fitted to run only command placed in the parent directory (of type "../command")"""

  process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  
  (process_stdout, process_stderr) = process.communicate()
  returnCode = process.poll()
  
  if (returnCode == 0):
    #print(command+" was runned successfully\n")
    
    # We delete the last \n introduced by subprocess and that corrupt the diff managed to see differences between outputs.
    return (process_stdout[0:-1], process_stderr[0:-1])
  else:
    print(command+" has terminated with an error code: "+str(returnCode))
    
    #temp = command.lstrip("../")
    temp = command.split("/")[-1]
    errlogname = temp+".err"
    print("Writing the error of the compilation in '"+errlogname+"'")
    f = open(errlogname,'w')
    f.write(process_stderr)
    f.close()
    
    outlogname = temp+".out"
    print("Writing the output of the compilation in '"+outlogname+"'")
    f = open(outlogname,'w')
    f.write(process_stdout)
    f.close()
    
    return (process_stdout, process_stderr)

def compare(original, new):
  """function that compare and print differences between to strings that are compared line by line."""
  
  modified = ["+ ", "- ", "? "]
  
  # We want lists, because difflib.Differ only accept list of lines.
  original = original.split("\n")
  new = new.split("\n")
  
  d = difflib.Differ()

  result = list(d.compare(original, new))
  
  differences = []
  line_number_original = 0
  line_number_new = 0
  for line in result:
    if (line[0:2] == "  "):
      line_number_original += 1
      line_number_new += 1
    elif (line[0:2] == "- "):
      line_number_original += 1
      differences.append("[ori] l"+str(line_number_original)+" :"+line[2:])
    elif (line[0:2] == "+ "):
      line_number_new += 1
      differences.append("[new] l"+str(line_number_new)+" :"+line[2:])
    elif (line[0:2] == "? "):
      differences.append("      l"+str(max(line_number_new, line_number_original))+" :"+line[2:])

  # We print separately because it is more convenient if we want to store in a file instead.
  if (differences != []):
    return "\n".join(differences)
  else:
    return None

def compare2file(ori_files,new_files):
  """Function that will use compare to see differences between 'original' 
  that is thought to be a variable and 'new_file' that is the name of a 
  file to read then use as input
  """
  no_diff = []
  diff = []
  
  for (original, new) in zip(ori_files, new_files):
    f_old = open(original, 'r')
    old_lines = f_old.readlines()
    f_old.close()
    
    f_new = open(new, 'r')
    new_lines = f_new.readlines()
    f_new.close()
    
    
    difference = compare(''.join(old_lines), ''.join(new_lines))
    if (difference == None):
      no_diff.append(new)
    else:
      diff.append([new, difference])
  
  # Now we output results
  if (diff != []):
    for (file, comp) in diff:
      print("\nFor "+file)
      print(comp)
      
    if (no_diff != []):
      print "No differences seen on :",', '.join(no_diff)
  # We doesn't print anything if no file at all has differences
  
  return 0

def lister(scheme):
  """list all the files corresponding to the given expression (might 
  be regular, in fact the same rules that goes for bash).  The function
  return the list of files, or the return code if their was an error."""
  
  if (type(scheme) != str):
    print("The argument must be a string")
    return None
  
  commande = "ls "+scheme
  
  process = subprocess.Popen(commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

  (process_stdout, process_stderr) = process.communicate()
  returnCode = process.poll()
  
  # If returnCode is not 0, then there was a problem
  if (returnCode==0):
    files = process_stdout.split("\n")
    files.remove('')
    return files
  else:
    return returnCode
    
def clean(exts):
  """supprime les fichiers correspondant à l'expression donnée. La fonction renvoit la sortie si ça c'est bien 
  déroulée, sinon ne renvoit rien."""
  for ext in exts:
    
    commande = "rm *."+ext
    
    process = subprocess.Popen(commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    (process_stdout, process_stderr) = process.communicate()
    returnCode = process.poll()
  
  # If returnCode is not 0, then there was a problem (in fact, will only do something for the last one
  if (returnCode==0):
    return process_stdout
  else:
    return returnCode

class sourceFile(object):
  """Define an object linked to a fortran 90 source code that will
  store dependencies, including modules included, used or included
  
  Parameters : 
  filename : the name of an existing source code filename (for example "main.f90")
  name='default' : the name we want for a program (if it is a program, if not, there will be no use)
  isProgram=False : is this source file a main source for a binary we want, or just a module or sub-program?
  
  Attribute : 
  self.filename : the filename of the source code file.
  self.defined : a list of procedures defined in the fortran source code
  self.used : a list of modules that are used by the code
  self.included : a list of things included in the code
  self.isCompiled : a boolean to say if the source file has already been compiled.
  self.dependencies : a list of object (*.o) filenames we need to compile
  self.isProgram : a boolean to say if we want to have a binary, or if it's just a module or a subprogram
  self.name : the name we want for the binary file if it is a program. This name is by default the filename without the extension
  
  Methods :
  .compile() : Compile the current program and all the required dependencies
  .writeArchitecture(filename,excluded=[], direction="leftright") : To write a .svg file showing the tree of dependencies of the current sourceFile.
    filename : The filename of the .svg file, without the extension
    excluded : a list of names of the modules you don't want to print in the diagram
    direction="leftright" : How the diagram will be constructed
      leftright -> The main program will be on the left, and the dependencies will appear on the right, row by row for each 
        'generation' of children dependencies
      topbottom -> The main program will be on the top, and the dependencies will appear on the bottom, line by line for each 
        'generation' of children dependencies

  """
  
  ## We define a dictionnary where we store, for each name of a module,
  # the link toward the object file where it is defined
  findModule = {}
  
  # We define a dictionary to make the correspondance between a source filename and the object associated
  findSource = {}
  #~ COMPILATOR = "ifort"
  #~ OPTIONS = "-vec-report0 -i-dynamic -mcmodel=medium -shared-intel -L/usr/lib64/atlas -llapack"
  
  COMPILATOR = "gfortran"
  OPTIONS = "-O3 -march=native"
  DEBUG = "-fbounds-check -Wuninitialized -O -ftrapv -fimplicit-none -fno-automatic"
  GDB = "-g"
  
  
  
  #-Wextra : batterie supplémentaire de vérifications
  #-ffast-math : je l'ai enlevé car les résultats ne sont pas identiques, les derniers chiffres significatifs sont différents.
  #-march=native : permet d'optimiser pour le processeur de la machine sur laquelle on compile. 'native' permet d'aller chercher 
  #   cette information sur la machine au lieu de la spécifier à la main. Si l'option ne fonctionne pas, typiquement si 'native' ou 
  #   le type de processeur spécifié n'existe pas, une erreur est retournée.
  #-fimplicit-none : empêche les déclarations implicites à moins que le mot clé "implicit" ne soit explicitement utilisé.
  #-finit-real=zero : initialise tous les réels à 0
  # farfadet spatial m'a conseillé -O2 au lieu de -O3 mais je ne comprends pas encore pourquoi.

  # Boolean that say if we want to activate debug or not
  isDebug = False
  isGDB = False
  isProfiling = False
  
  def __init__(self, filename, name='default', isProgram=False):
    """Will check everything that is included in the source code
    and initialize the object"""
    self.filename = filename
    
    if (name == 'default'):
      self.name = self.filename.rstrip(".f90")
    else:
      self.name = str(name)
    
    self.isCompiled = False
    
    # By default, nothing is a program
    self.isProgram = isProgram
    
    
    (self.defined, self.used, self.included) = self.__getModules()
    
    for module in self.defined:
      sourceFile.findModule[module] = self
    
    sourceFile.findSource[self.filename] = self
  
  @classmethod
  def setDebug(cls, isDebug):
    """method that define cls.isDebug parameter to True or False.
    
    Parameter: isDebug (boolean)
    """
    
    cls.isDebug = isDebug

  @classmethod
  def setGDB(cls, isGDB):
    """method that define cls.isGDB parameter to True or False.
    
    Parameter: isGDB (boolean)
    """
    
    cls.isGDB = isGDB
  
  @classmethod
  def setProfiling(cls, isProfiling):
    """method that define cls.isProfiling parameter to True or False.
    
    Parameter: isProfiling (boolean)
    """
    
    cls.isProfiling = isProfiling
  
  @classmethod
  def setModColors(cls):
    """class function that gives a dictionnary of colors for each sourceFile defined so far
    """
    
    cls.mod_colors = dict(zip(cls.findSource.keys(), colorList(len(cls.findSource))))
    
    #~ pdb.set_trace()
    return 0
  
  @classmethod
  def setCompilingOptions(cls, options):
    """method that set the 'OPTIONS' value. 
    
    Parameter:
    options : a string with the compilation options for the binary construction
    """
    
    cls.OPTIONS = options
  
  @classmethod
  def setCompilator(cls, compilator):
    """method that set the 'COMPILATOR' value. 
    
    Parameter:
    options : a string with the compilator you want to use
    """
    
    cls.COMPILATOR = compilator
  
  def __getModules(self):
    """returns a tuple containing the list of defined modules and 
    the list of used modules of a fortran source file
    
    Return 
    defined : a list of procedures defined in the fortran source code
    used : a list of modules that are used by the code
    included : a list of things included in the code
    """

    f=open(self.filename,'r')
    lines = f.readlines()
    f.close()

    defined=[]
    used=[]
    included=[]

    for lsave in lines:
      l=string.expandtabs(string.lower(lsave)[:-1],1)
      words=string.split(string.lstrip(l))
      if len(words) > 0:
        if words[0] == 'use':
          used.append(string.split(words[1],',')[0])
        if words[0] == 'module':
          if len (words) == 2 or words[1] != "procedure":
            defined.append(words[1])
        if words[0] == 'include':
          newstring = string.replace(words[1],'\'','')
          newstring = string.replace(newstring,'\"','')
          included.append(newstring)
      l=string.expandtabs(lsave[:-1],1)
      words=string.split(string.lstrip(l))
      if len(words) > 0:
        if words[0] == '#include':
          newstring = string.replace(words[1],'\"','')
          included.append(newstring)

# We delete all dependencies that are present several number of times.
    used = list(set(used))

    return defined,used,included
  
  def __getFirstOrderDependence(self):
    """return a list of *.o files we need to compiled. They are 
    extracted from direct used files, that why we call them 
    "first order" dependance."""
    
    dependances = []
    for mod in self.used:
      try:
        source = sourceFile.findModule[mod]
      except:
        print("Error: Unable to locate the module '"+mod+"'")
      obj = string.replace(source.filename,'.f90','.o')
      dependances.append(obj)
    
    return dependances
  
  def setProgram(self, boolean):
    """method to defined the current object as a program, that is, if
    we want to have a binary from this source"""
    
    self.isProgram = boolean
  
  def writeArchitecture(self,filename,excluded=[], direction="leftright"):
    """write the architecture in a .svg file"""
    
    if (direction == "topbottom"):
      constructArch = self.__getArchitectureTopBottom
    elif (direction == "leftright"):
        constructArch = self.__getArchitectureLeftRight
    else:
        raise ValueError("the 'direction' you typed do not exist. You must choose between: \n_ 'topbottom'\n_ 'leftright'")
    
    # We define the dictionary of colors for each source file defined.
    self.setModColors()
    
    architecture = []
    (architecture, x, y, total_width) = constructArch(architecture=architecture,excluded=excluded)
    
    createSVG(filename, *architecture)

  def __getArchitectureTopBottom(self, architecture, excluded=[], x=0, y=0):
    """Retrieve the architecture of the program
    
    Parameter:
    x : The x position of the first box
    y : The y position of the parent box"""
    
    width = 150
    height = 30
    
    width_space = 10
    height_space = 50
    
    # we search for the dependencies of the current source file.
    dependencies = []
    used = list(self.used) # list() is here to avoid virtual link

    # We do not print excluded modules
    for mod in excluded:
      try:
        used.remove(mod)
      except:
        pass
    
    #~ for source in sourceFile.findSource.keys():
      # TODO là je mettais la ligne pour générer le dictionnaire des couleurs, mais il faut que ce soit un paramètre de classe
      # sinon il n'est pas connu des autres instances

    # For each modules, we search the defined object in the base of sourcefiles
    for mod in used:
      dependencies.append(sourceFile.findModule[mod])

    nb_dep = len(dependencies)
    
    # We search for children and print lines to join them to the present
    # box if there are any dependencies (except thoses excluded)
    if (nb_dep != 0):
      
      tree_width = 0
      x_cursor = x
      y_cursor = y + height + height_space# * len(dependencies) # may cause problems for close boxes that might overlap
      child_coord = []
      for dep in dependencies:
        (architecture, x_cursor, y_cursor, childchild_width) = dep.__getArchitectureTopBottom(architecture, excluded=excluded, x=x_cursor, y=y_cursor)
        child_coord.append((x_cursor, y_cursor))
        tree_width += childchild_width + width_space
        x_cursor += childchild_width/2. + width/2. + width_space
      
      # For the last element, we don't want the space between boxes
      tree_width = tree_width - width_space
      parent_y = y

      # We calculate the coords for the parent box
      parent_x = x + tree_width / 2. - width /2.
      
      # We write lines between the parent and each child
      for (child_x, child_y) in child_coord:
        temp = Path((parent_x, parent_y+height/2.), (child_x, child_y-height/2.))
        architecture.append(temp)
      
    else:
      tree_width = width
      
      parent_x = x
      parent_y = y
    
        
    architecture.append(TextBox(self.name, parent_x-width/2., parent_y-height/2., color=sourceFile.mod_colors[self.filename]))

    return (architecture, parent_x, parent_y, tree_width)

  def __getArchitectureLeftRight(self, architecture, excluded=[], x=0, y=0):
    """Retrieve the architecture of the program
    
    Parameter:
    x : The x position of the first box
    y : The y position of the parent box"""
    
    width = 150
    height = 30
    
    width_space = 50
    height_space = 10
    
    # we search for the dependencies of the current source file.
    dependencies = []
    used = list(self.used) # list() is here to avoid virtual link

    # We do not print excluded modules
    for mod in excluded:
      try:
        used.remove(mod)
      except:
        pass

    # For each modules, we search the defined object in the base of sourcefiles
    for mod in used:
      dependencies.append(sourceFile.findModule[mod])

    nb_dep = len(dependencies)
    
    # We search for children and print lines to join them to the present
    # box if there are any dependencies (except thoses excluded)
    if (nb_dep != 0):
      
      tree_width = 0
      x_cursor = x + width + width_space
      y_cursor = y
      child_coord = []
      for dep in dependencies:
        (architecture, x_cursor, y_cursor, childchild_width) = dep.__getArchitectureLeftRight(architecture, excluded=excluded, x=x_cursor, y=y_cursor)
        child_coord.append((x_cursor, y_cursor))
        tree_width += childchild_width + height_space
        y_cursor += childchild_width/2. + height/2. + height_space
      
      # For the last element, we don't want the space between boxes
      tree_width = tree_width - height_space
      parent_x = x

      # We calculate the coords for the parent box
      parent_y = y + tree_width / 2. - height /2.
      
      # We write lines between the parent and each child
      for (child_x, child_y) in child_coord:
        temp = Path((parent_x + width/2., parent_y), (child_x-width/2., child_y))
        architecture.append(temp)
      
    else:
      tree_width = height
      
      parent_x = x
      parent_y = y
    
        
    architecture.append(TextBox(self.name, parent_x-width/2., parent_y-height/2., color=sourceFile.mod_colors[self.filename]))

    return (architecture, parent_x, parent_y, tree_width)

  def compile(self):
    """method that check dependencies and try to compile
    
    Beware, there MUST NOT be inter dependant modules.
    """
    if not(self.isCompiled):
      # We only store, for the moment, the first order dependencies.
      self.dependencies = self.__getFirstOrderDependence()
      
      # We store links towards all the object sourceFile that defined the modules we are interested in.
      module_sources = []
      for module in self.used:
        module_sources.append(sourceFile.findModule[module])
      
      # For each object, we compile it if it's not already the case.
      for source in module_sources:
        if not(source.isCompiled):
          source.compile()
      
      # We complete the dependencies list now that all used modules
      # have been compiled, they must have a complete list of 
      # their own dependencies.
      for source in module_sources:
        for dep in source.dependencies:
          self.dependencies.append(dep)
              
      # We delete all dependencies that are present several number of times.
      self.dependencies = list(set(self.dependencies))
      
      # Now that all the dependencies have been compiled, we compile 
      # the current source file.
      options = sourceFile.OPTIONS
      if (sourceFile.isDebug):
        options += " "+sourceFile.DEBUG
      
      if (sourceFile.isGDB or sourceFile.isProfiling):
        options += " "+sourceFile.GDB
      
      if (sourceFile.isProfiling):
        # We deactivate all other options except GDB => not True anymore
        options += " "+" -pg"
        
      if not(self.isProgram):
        commande = sourceFile.COMPILATOR+" "+options+" -c "+self.filename
      else:
        commande = sourceFile.COMPILATOR+" "+options+" -o "+self.name+" "+self.filename+" "+" ".join(self.dependencies)
        print(commande)
      
      process = subprocess.Popen(commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

      (process_stdout, process_stderr) = process.communicate()
      
      print("Compiling "+self.filename+"...")
      returnCode = process.poll()
      
      self.isCompiled = True
      
      # If returnCode is not 0, then there was a problem
      if (returnCode==0):
        return process_stderr
      else:        
        logname = "compiling_"+self.filename+".log"

        # We write compilation errors in the following file.
        f = open(logname,'w')
        f.write(process_stderr)
        f.close()
        
        print("Compilation error, see '"+logname+"'")
        sys.exit(1)
      
  def __str__(self):
    """overload the str method. As a consequence, you can print the object via print name_instance

    return : a string that represent the properties of the object
    """

    texte = "filename: "+self.filename+"\n"
    
    texte += "defined: "+str(self.defined)+"\n"
    texte += "used: "+str(self.used)+"\n"
    texte += "included: "+str(self.included)+"\n"

    return texte

if __name__ == '__main__':
  
  print("""Warning: For the moment, I store the 'included' thing, but I
  don't know what to do with them, so the script is NOT adapted to 
  included procedure or whatever they are""")
  
  # We clean undesirable files. Indeed, we will compile everything everytime.
  clean(["o", "mod"])

  sources_filename = lister("*.f90")
  
  # We create the binaries
  make_binaries(["maintest.f90"])


# LOG
# Version 1.1 : Rajout de l'exportation dans un fichier des erreurs de compilation en cas de problème.
# Version 1.2 : Rajout d'un test (que j'avais oublié) pour que le module ne soit pas recompilé s'il l'a déjà été pour une autre fonction.
# Version 1.3 : rajout d'une liste qui épure la liste des dépendances pour qu'il n'y ait qu'une seule fois chaque dépendance 
#               (pose des problèmes de "multiple definition" sinon)
# Version 1.5.0 : Rajout de la couleur, implémentation sur une idée de marie pour rendre les graphes plus clairs.
# Version 1.5.2 : Rajout de la méthode setCompilator à la classe sourceFile
# Version 1.6.0 : Modification de compare() pour afficher de manière plus claire les différences entre les fichiers.
# Version 1.6.1 : L'option de profiling a été ajoutée à la classe sourceFile. Cette dernière désactive toutes les autres options.
# Version 1.7.0 : Si une erreur de compilation survient, le programme s'arrête et affiche un message d'erreur donnant le nom du fichier à regarder pour consulter les erreurs