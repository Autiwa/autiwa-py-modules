#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "30 septembre 2011"
__version__ = "$Revision: 0.3 $"
__credits__ = """Based on the work of Pierre gay, in particuliar his get_module function."""

"""The aim of this module is to provide a simple way to compile complex fortran programs with various dependencies. 

All you have to do is to define wich sourcefile is the main sourcefile. The module will get binaries only for theses sources (there can be severals)
"""
import os
import string
import subprocess # To launch various process, get outputs et errors, returnCode and so on.
import pdb # To debug
from svg import *
import autiwa

class SubroutineSource(object):
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
	
	## We define a dictionnary where we store, for each name of a subroutine,
	# the link toward the object file where it is defined
	findSubroutine = {}

	# A dictionary that contains in keys the names of 'external' Subroutine
	# and in values() the object subroutine where they are.
	findExternal = {}
	
	
	def __init__(self, name, source):
		"""Will check everything that is included in the source code
		and initialize the object"""
		
		self.name = name
		
		(self.used, self.external, self.arguments) = self.__getCalls(source)

		self.source = source

		SubroutineSource.findSubroutine[name] = self
		
	
	@classmethod
	def setColors(cls):
		"""class function that gives a dictionnary of colors for each sourceFile defined so far
		"""
		
		cls.subroutine_colors = dict(zip(cls.findSubroutine.keys(), autiwa.colorList(len(cls.findSubroutine))))
		
		#~ pdb.set_trace()
		return 0
	
	def __getCalls(self, lines):
		"""returns a tuple containing the list of defined subroutines and 
		the list of used subroutines of a fortran source file

		WARNING : lines must not have a "\n". They MUST begin with the
			"subroutine name (args)"
		and end with
			"end subroutine name"
		
		Return 
		defined : a list of subroutine defined in the fortran source code
		used : a list of subroutine that are used by the code
		included : a list of things included in the code
		"""

		used = []

		# For each external we store the position in the list of arguments
		# in order to retrieve the real name of the subroutine used in the call
		external = {}

		# We want all the args
		entete = lines[0]
		del(lines[0])
		temp = entete.replace(' ','') # We delete spaces
		if (temp.count('(') != 0):
			temp = temp.split("(")[1] # We suppress what is before '(', that is "subroutine name" normally
			temp = temp.split(")")[0] # We suppress what is after ')'
			arguments = temp.split(",") # We split to get each arg separately in a list
		else:
			arguments = []
		
		
		for lsave in lines:
			l=string.expandtabs(string.lower(lsave),1)
			l = l.split('!')[0]
			words=string.split(string.lstrip(l))
			if len(words) > 0:
				if words[0] == "external":
					temp = "".join(words[1:])
					names = temp.split(',')
					for name in names:
						SubroutineSource.findExternal[self.name+"."+name.upper()] = self
				for i in range(len(words)-1):
					if words[i] == 'call':
						name = string.split(words[i+1],'(')[0]
						if not(name in external):
							used.append(name)

# We delete all dependencies that are present several number of times.
		used = list(set(used))

		return (used, external, arguments)

	def addUsed(self, *used):
		"""method that add dependancies of a program manually. This has been
		made to add "external" meta-subroutine (that will contain all possible
		subroutine that are effectively used by the current subroutine
		through the external name)"""
		for dep in used:
			self.used.append(dep)
		return 0
 
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
		for subroutine in excluded:
			try:
				used.remove(subroutine)
			except:
				pass

		# For each modules, we search the defined object in the base of sourcefiles
		for subroutine in used:
			try:
				dependencies.append(SubroutineSource.findSubroutine[subroutine])
			except:

				key = self.name+"."+subroutine
				SubroutineSource.findExternal[key] = self
				#print("Warning: '"+subroutine+"' might be an external subroutine from a module")

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

		# Theses lines are here only for the case where several routines
		# have the same name pour one subroutine given in parameter (the name of the 'external'). 
		try:
			name = self.name.split(".")[1]
		except:
			name = self.name
		architecture.append(TextBox(name, parent_x-width/2., parent_y-height/2., color=SubroutineSource.subroutine_colors[self.name]))

		return (architecture, parent_x, parent_y, tree_width)

class FunctionSource(object):
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
	
	## We define a dictionnary where we store, for each name of a subroutine,
	# the link toward the object file where it is defined
	findFunction = {}

	
	
	def __init__(self, name, source):
		"""Will check everything that is included in the source code
		and initialize the object"""
		
		self.name = name
		
		self.used = self.__getCalls(source)
		
		self.source = source

		FunctionSource.findFunction[name] = self
		
	
	def __getCalls(self, lines):
		"""returns a tuple containing the list of defined subroutines and 
		the list of used subroutines of a fortran source file
		
		Return 
		defined : a list of subroutine defined in the fortran source code
		used : a list of subroutine that are used by the code
		included : a list of things included in the code
		"""

		used = []

		for lsave in lines:
			l=string.expandtabs(string.lower(lsave)[:-1],1)
			words=string.split(string.lstrip(l))
			if len(words) > 0:
				if (words[0][0] == '!'):
					continue
				for i in range(len(words)-1):
					if words[i] == 'call':
						used.append(string.split(words[i+1],',')[0])

# We delete all dependencies that are present several number of times.
		used = list(set(used))

		return used
 
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
		used = list(self.used.keys()) # list() is here to avoid virtual link

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
		
				
		architecture.append(TextBox(self.name, parent_x-width/2., parent_y-height/2., color=sourceFile.subroutine_colors[self.name]))

		return (architecture, parent_x, parent_y, tree_width)

class ProgramSource(object):
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
	
	## We define a dictionnary where we store, for each name of a subroutine,
	# the link toward the object file where it is defined
	findProgram = {}

	
	
	def __init__(self, name, source):
		"""Will check everything that is included in the source code
		and initialize the object"""
		
		self.name = name
		
		self.used = self.__getCalls(source)

		self.source = source

		ProgramSource.findProgram[name] = self
		
	

	def __getCalls(self, lines):
		"""returns a tuple containing the list of defined subroutines and 
		the list of used subroutines of a fortran source file
		
		Return 
		defined : a list of subroutine defined in the fortran source code
		used : a list of subroutine that are used by the code
		included : a list of things included in the code
		"""

		used = []

		for lsave in lines:
			l=string.expandtabs(string.lower(lsave)[:-1],1)
			words=string.split(string.lstrip(l))
			if len(words) > 0:
				if (words[0][0] == '!'):
					continue
				for i in range(len(words)-1):
					if words[i] == 'call':
						name = string.split(words[i+1],'(')[0]

						used.append(name)

# We delete all dependencies that are present several number of times.
		used = list(set(used))

		return used

	def addUsed(self, *used):
		"""method that add dependancies of a program manually. This has been
		made to add "external" meta-subroutine (that will contain all possible
		subroutine that are effectively used by the current subroutine
		through the external name)"""

		pdb.set_trace()
		for dep in used:
			self.used.append(dep)

		return 0

	def writeTree(self,filename,excluded=[], direction="leftright"):
		"""write the architecture in a .svg file"""
		
		if (direction == "topbottom"):
			constructArch = self.__getArchitectureTopBottom
		elif (direction == "leftright"):
				constructArch = self.__getArchitectureLeftRight
		else:
				raise ValueError("the 'direction' you typed do not exist. You must choose between: \n_ 'topbottom'\n_ 'leftright'")
		
		# We define the dictionary of colors for each source file defined.
		SubroutineSource.setColors()
		
		architecture = []
		(architecture, x, y, total_width) = constructArch(architecture=architecture,excluded=excluded)
		
		createSVG(filename, *architecture)
 
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
			try:
				dependencies.append(SubroutineSource.findSubroutine[mod])
			except:
				pdb.set_trace()

		nb_dep = len(dependencies)
		
		# We search for children and print lines to join them to the present
		# box if there are any dependencies (except thoses excluded)
		if (nb_dep != 0):
			
			tree_width = 0
			x_cursor = x + width + width_space
			y_cursor = y
			child_coord = []
			for dep in dependencies:
				#~ pdb.set_trace()
				(architecture, x_cursor, y_cursor, childchild_width) = dep._SubroutineSource__getArchitectureLeftRight(architecture, excluded=excluded, x=x_cursor, y=y_cursor)
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
		
				
		architecture.append(TextBox(self.name, parent_x-width/2., parent_y-height/2., color='ffffff'))

		return (architecture, parent_x, parent_y, tree_width)

class FortranSource(object):
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
	
	
	# We define a list of all the 'program' objects
	findSource = {}
	
	def __init__(self, filename):
		"""Will check everything that is included in the source code
		and initialize the object"""
		self.filename = filename
		
		(self.program, self.subroutine, self.function) = self.__readSource()

		FortranSource.findSource['self.filename'] = self

	def __getWords(self,line):
		"""method that return a list of words from a line of code
		"""

		l=string.expandtabs(string.lower(line),1)
		words=string.split(string.lstrip(l))
		
		return words

	def __readSource(self):
		"""returns a tuple containing the list of defined subroutines and 
		the list of used subroutines of a fortran source file
		
		Return 
		defined : a list of subroutine defined in the fortran source code
		used : a list of subroutine that are used by the code
		included : a list of things included in the code
		"""

		f=open(self.filename,'r')
		lines_raw = f.readlines()
		f.close()

		program=[]
		subroutine=[]
		function=[]

		# We merge all the lines that are in fact continuated lines with the '&' symbol
		line = lines_raw[0][:-1]
		lines = [line]
		i = 1
		while (i < len(lines_raw)):
			previous_line = line
			line = lines_raw[i].replace('\n', '') # We delete the '\n' character

			# If the previous line was empty, no need to check for continuating line.
			if (previous_line == ""):
				lines.append(line)
				i += 1
				continue
			
			if (previous_line[-1] == '&'):
				lines[-1] = lines[-1][:-1] + line # We suppress the "&" symbol and merge the two lines
			else:
				lines.append(line)
			i += 1
			

		line_index = 0
		nb_lines = len(lines)
		while line_index < nb_lines:
			lsave = lines[line_index]

			words = self.__getWords(lsave)
			
			if len(words) > 1:
				if words[0] == 'program':
					name_program = string.split(words[1],',')[0]

					program_source = [lsave]
					
					# We extract the code of the entire program
					isInsideProgram = True
					while isInsideProgram:
						line_index += 1
						try:
							lsave = lines[line_index]
						except:
							pdb.set_trace()
						words = self.__getWords(lsave)
						program_source.append(lsave)
						
						if ((len(words) >= 1) and (words[0] == "contains")):
							isInsideProgram = False
						elif ((len(words) > 2) and (words[0] == "end" and words[1] == "program" and words[2] == name_program)):
							isInsideProgram = False
						else:
							isInsideProgram = True

					#~ if (name_program == "mercury"):
						#~ pdb.set_trace()	

					program.append(ProgramSource(name=name_program, source=program_source))
					
					
				if (words[0] == 'subroutine'):
					name_subroutine = string.split(words[1],'(')[0]

					# We extract the source code of the subroutine
					subroutine_source = [lsave]
					isInsideSubroutine = True
					while ((line_index < nb_lines-1) and ((len(words) <= 2) or (words[0] != "end" and words[1] != "subroutine" and words[2] != name_subroutine))):
						line_index += 1
						lsave = lines[line_index]
						words = self.__getWords(lsave)
						subroutine_source.append(lsave)

						if ((len(words) > 2) and (words[0] == "end" and words[1] == "subroutine" and words[2] == name_subroutine)):
							isInsideSubroutine = False
						else:
							isInsideSubroutine = True

					subroutine.append(SubroutineSource(name=name_subroutine, source=subroutine_source))

				if (words[0] == 'function'):
					name_function = string.split(words[1],',')[0]
					
					function_source = [lsave]
					isInsideFunction = True
					while ((len(words) <= 2) or (words[0] != "end" and words[1] != "function" and words[2] != name_function)):
						line_index += 1
						lsave = lines[line_index]
						words = self.__getWords(lsave)
						function_source.append(lsave)

						if ((len(words) > 2) and (words[0] == "end" and words[1] == "function" and words[2] == name_function)):
							isInsideFunction = False
						else:
							isInsideFunction = True

					function.append(FunctionSource(name=name_function, source=function_source))
					
			line_index += 1

		return (program, subroutine, function)

def lister(scheme):
	"""list all the files corresponding to the given expression (might 
	be regular, in fact the same rules that goes for bash).	The function
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

def setExternals(externals):
	"""
	function that set externals with a dictionary in parameter.
	The dictionary must be of the following form:
	externals = {"parent_name.external" :	[list_of_possible_values_of_external]}
	where 'parent_name is the name as a string of the subroutine where the 'external' is used
	'external' is the name of the external

	Example :
	externals = {'mdt_hkce.force':["mfo_hkce"],
			'mal_hcon.coord':["mco_h2mvs", "mco_iden", "mco_h2dh"],
			'mal_hcon.bcoord':["mco_mvs2h", "mco_iden", "mco_dh2h"],
			'mal_hcon.onestep':["mdt_mvs", "mdt_hy"],
			'mal_hvar.onestep':["mdt_bs1", "mdt_bs2", "mdt_ra15"],
			'mdt_bs1.force':["mfo_all"],
			'mdt_bs2.force':["mfo_all"],
			'mdt_ra15.force':["mfo_all"]
			}
	"""
	
	object_ext = []
	for (external, dep) in externals.items():
		(parent, name) = external.split(".")

		# We search for the parent procedure
		try:
			parent_object = ProgramSource.findProgram[parent]
		except:
			pass
		try:
			parent_object = SubroutineSource.findSubroutine[parent]
		except:
			pass

		if not('parent_object' in locals()):
			pdb.set_trace()
			print("Failed to locate the parent procedure")

		parent_object.addUsed(parent+"."+name.upper()) # Name of externals will be in upper case
		temp = SubroutineSource(name=parent+"."+name.upper(), source=["subroutine "+name.upper()+"()", "end subroutine "+name.upper()])
		temp.addUsed(*dep)
		object_ext.append(temp)

	return object_ext
