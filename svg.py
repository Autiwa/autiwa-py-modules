#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Autiwa <autiwa@gmail.com>"
__date__ = "18 July 2011"
__version__ = "$Revision: 1.2 $"
__credits__ = """module to help writing svg files"""

import pdb

SVG_HEAD = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="210mm"
   height="297mm"
   id="svg2"
   version="1.1"
   inkscape:version="0.48.1 r9760"
   sodipodi:docname="test.svg">
  <defs
	 id="defs4" />
  <sodipodi:namedview
	 id="base"
	 pagecolor="#ffffff"
	 bordercolor="#666666"
	 borderopacity="1.0"
	 inkscape:pageopacity="0.0"
	 inkscape:pageshadow="2"
	 inkscape:zoom="1.4"
	 inkscape:cx="184.0203"
	 inkscape:cy="752.7937"
	 inkscape:document-units="px"
	 inkscape:current-layer="layer1"
	 showgrid="false" />
  <metadata
	 id="metadata7">
	<rdf:RDF>
	  <cc:Work
		 rdf:about="">
		<dc:format>image/svg+xml</dc:format>
		<dc:type
		   rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
		<dc:title />
	  </cc:Work>
	</rdf:RDF>
  </metadata>
  <g
	 inkscape:label="Calque 1"
	 inkscape:groupmode="layer"
	 id="layer1">"""
	 
SVG_FOOT = """  </g>
</svg>"""

def createSVG(filename,*boxs):
	"""function that create a SVG file that contains all the boxs created previously
	"""
	
	svgfile = open(filename, 'w')
	svgfile.write(SVG_HEAD)
	
	for box in boxs:
		svgfile.write(box.getSVGcode())
	
	svgfile.write(SVG_FOOT)
	svgfile.close()

def colorList(nb_colors):
	"""Function that return a list of colors given the number of different colors we want. 
	It is still a simple version of the function that may contain bugs, especially for large values of colors. 
	
	Parameter
	nb_colors : The number of different colors we want.
	
	Return 
	A list of colors, with the desired number of elements
	"""
	from math import ceil
	
	individual_colors = int(ceil(nb_colors**0.33))

	colors = [0, 255, 127]
	iteration = 0
	# We search for all individual values (for R, G, B) that we need to define at least the number of colors we want.
	while (len(colors) < individual_colors):
		step = 255 / (2**(iteration + 1))
		
		iteration += 1

		#For the current iteration, the number of subdivision will be a power of 2
		nb_el = 2**iteration

		# We start at half the step
		temp = step/2
		for i in range(nb_el):
			colors.append(temp)
			temp += step
	
	HEXcolors = []
	nb = 0
	for R in colors:
		for G in colors:
			for B in colors:
				colorTemp = hexColor(R)+hexColor(G)+hexColor(B)
				HEXcolors.append(colorTemp)
				nb += 1
				
				if (nb == nb_colors+1):
					HEXcolors.remove('000000')
					return HEXcolors

def hexColor(integer):
	"""given a number between 0 and 255, return the hexadecimal value as a two character string
	"""
	
	if (type(integer) != int):
		raise TypeError("The parameter must be an integer")
	
	if (integer <0 or integer > 255):
		raise ValueError("The parameter must be between 0 and 255")

	value = hex(integer)
	value = value.split("0x")[1]

	if (len(value) < 2):
		value = "0"+value

	return value

def contrastColor(ref_color):
	"""
	Return '000000' by default, but if 'color' is quite dark, then return 'ffffff'

	The principle is simple, we calculate the brightness of the color and regarding a tolerance parameter, 
	we put white or black in order to have a visible color on the given one.

	Example :
	contrastColor('ffffff') = '000000'
	contrastColor('000000') = 'ffffff'
	"""
	
	tolerance = 130

	R = int('0x'+ref_color[0:2],16)
	G = int('0x'+ref_color[2:4],16)
	B = int('0x'+ref_color[4:6],16)
	
	# We calculate the square of the brightness in order to avoid the use of sqrt.
	brightness_square = .241 * R**2 + .691 * G**2 + 0.068 * B**2 # source : http://alienryderflex.com/hsp.html
	

	if (brightness_square > tolerance**2):
		color = "000000"
	else:
		color = "ffffff"

	return color
	
class SVGobject(object):
	"""meta class that contains general behaviours for objects defining 
	svg objects like paths, line, circles, texts and so on
	"""
	
	def __init__(self):
		"""initialisation of the instance"""
		
		# For the moment, nothing is implemented. I wanted to define here 
		# the incrementation of id, that is, I would not have to define the 
		# variable and increment it in __init__ in each sub-class, but I 
		# don't know how to do it, so in order to save time, I skipped.
		

class TextBox(object):
	"""
	object that define various properties for a boxed text
	"""
		
	def __init__(self,text,x,y,color="ffffff"):
		"""We define the text and the position of the box
		"""
				
		self.text = text
		self.x = x
		self.y = y
		
		self.height = 30
		self.width = 150
		
		self.text_x = self.x + self.width/2.
		self.text_y = self.y + 18.
		
		self.rectangle = Rectangle(x=self.x, y=self.y, width=self.width, height=self.height)
		self.text = Text(x=self.text_x,y=self.text_y, text=self.text)
		
		self.rectangle.setColor(color)
		self.text.setColor(contrastColor(color))

		
	def getSVGcode(self):
		"""create a svg text that is thought to represent a text in a box
		"""
		
		text = Group(self.rectangle, self.text).getSVGcode()
		
		return text

class Group(SVGobject):
	"""object that define a group containing the given objets
	
	parameters:
	objects: a list of SVG object were a method 'getSVGcode' exist. 
	"""
	
	id = 0
	
	def __init__(self, *objects):
		SVGobject.__init__(self)
		Group.id += 1
		
		self.id = Group.id
		
		self.objects = objects
		
	def getSVGcode(self):
		"""create a svg text that is thought to represent a group and all that he contains
		"""
		
		text = "<g\n"
		text += '  id="g'+str(self.id)+'">\n'
		for obj in self.objects:
			text += obj.getSVGcode()
		text += '</g>\n'
		
		return text

class Text(SVGobject):
	"""
	object that define a text with the given coords
	
	Parameters:
	x : the horizontal position of the text
	y : the vertical position of the text
	text : the text as a string
	"""
	
	id = 0
	
	STYLE = {"font-size":"14px", "font-style":"normal", "font-variant":"normal", 
	"font-weight":"normal", "font-stretch":"normal", "text-align":"center", 
	"line-height":"125%", "letter-spacing":"0px", "word-spacing":"0px", 
	"writing-mode":"lr-tb", "text-anchor":"middle", "fill":"#000000", 
	"fill-opacity":"1", "stroke":"none", "font-family":"Sans", 
	"-inkscape-font-specification":"Sans"}
	
	
	def __init__(self, text, x, y):
		
		SVGobject.__init__(self)
		
		Text.id += 1
		
		self.id = Text.id
		
		self.x, self.y = x,y
		
		self.style = dict(Text.STYLE) # The "dict()" is here to make a copy and not a pointer link
		
		self.text = text

	def setColor(self,color):
		"""Let us change the color of the Text. 
		
		Parameter
		color : a string of 6 numbers in hexadecimal, for example "ff8800"
		"""
		
		self.style["fill"] = "#"+color
		
	def getSVGcode(self):
		"""create a svg text that is thought to represent a text in a box
		"""
	
		text = '<text\n'
		text += '  sodipodi:linespacing="125%"\n'
		text += '  id="text'+str(self.id)+'"\n'
		text += '  y="'+str(self.y)+'"\n'
		text += '  x="'+str(self.x)+'"\n'
		text += '  style="'
		
		list = map(str.__add__, [k+":" for k in self.style.keys()], self.style.values())
		text += ";".join(list)+'"\n'
		
		text += '  xml:space="preserve">'+self.text
		text += '</text>\n'
		
		return text
		

class Rectangle(SVGobject):
	"""
	object that define a rectangle with the given coord, width and height.
	The coordinate are those of the left top corner of the rectangle
	"""
	
	STYLE = {"fill":"#ffffff", "fill-opacity":"1", "fill-rule":"evenodd", 
	"stroke":"#000000", "stroke-width":"1", "stroke-miterlimit":"4", 
	"stroke-opacity":"1", "stroke-dasharray":"none", "stroke-dashoffset":"0"}
	
	id = 0
	
	def __init__(self,width,height,x,y):
		
		SVGobject.__init__(self)
		
		Rectangle.id += 1
		
		self.x = x
		self.y = y
		
		self.id = Rectangle.id
		self.style = dict(Rectangle.STYLE)
		
		self.height = height
		self.width = width
	
	def setColor(self,color):
		"""Let us change the color of the background of the rectangle. 
		
		Parameter
		color : a string of 6 numbers in hexadecimal, for example "ff8800"
		"""
		
		self.style["fill"] = "#"+color

	def getSVGcode(self):
		"""create a svg text that is thought to represent a rectangle
		"""
		
		text = '<rect\n'
		text += '  style="'
		
		list = map(str.__add__, [k+":" for k in self.style.keys()], self.style.values())
		text += ";".join(list)+'"\n'
		
		text += '  id="rect'+str(self.id)+'"\n'
		text += '  width="'+str(self.width)+'"\n'
		text += '  height="'+str(self.height)+'"\n'
		text += '  x="'+str(self.x)+'"\n'
		text += '  y="'+str(self.y)+'" />\n'
		
		return text

class Path(SVGobject):
	"""
	object that define a path with the given coords that will be of the form : 
	(x1, y1), (x2, y2), (x3, y3)
	"""
	
	PATH_STYLE = '	   style="fill:#ffffff;fill-opacity:1;fill-rule:evenodd;stroke:#000000;stroke-width:1;stroke-miterlimit:4;stroke-opacity:1;stroke-dasharray:none;stroke-dashoffset:0"'
	
	id = 0
	
	def __init__(self,*coords):
		"""We define the text and the position of the box
		"""
		
		SVGobject.__init__(self)
		
		Path.id += 1
		
		for coord in coords:
			if ((type(coord) != tuple) or (len(coord) != 2)):
				raise TypeError("Each element must be a tuple of 2 values that represents the coordinates")
		self.coords = coords
		
		self.id = Path.id
		
		self.height = 30
		self.width = 150
		
		
	def getSVGcode(self):
		"""create a svg text that is thought to represent a text in a box
		"""
		
		text = "	<path\n"
		text += Path.PATH_STYLE+"\n"
		text += '	   d="M'
		for (x,y) in self.coords:
			text += " "+str(x)+","+str(y)
		text += '"\n'
		text += '	   id="path'+str(self.id)+'"\n'
		text += '	   inkscape:connector-curvature="0" />\n'
		
		return text


if __name__ == '__main__':
	testbox = TextBox("test",2, 3,color="ff0000")
	testbox2 = TextBox("test2", 2, 40)
	testpath = Path((2, 3), (5, 40))
	testtext = Text("hey, how are you?", x=4, y=10)
	testgroup = Group(testpath)
	testbox3 = TextBox("COORD", 10, 10, color="000000")
	createSVG("test.svg",testbox, testbox2, testpath, testgroup, testbox3)
	

# RMQ : If you use objects in other objects, then there is a chance 
# you have different objects with the same ID. For exemple, if you 
# define a path that you print, and use this path in a group that you 
# print also, then you will have to objects Path with the same Path.id. 
# But I think the normal behaviour is to define an object an use 
# it only once, so I don't think it's a bug. 

# Version 1.1 : contrastColor has been added. Now the color of the text in TextBox change if the background color of the rectangle is too dark, regarding a 'tolerance' parameter than can be changed later easily
# Version 1.2 : contrastColor (need sqrt now) now use brightness of the color to check which color he must return.
