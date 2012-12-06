#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module to parse and create an ebook using the epub module. 
# * You will need a text file in utf-8 to generate the epub.
# * Some fashion can be done. For instance _text_ in 
#   the .txt file will display "text" in italic
# * By default, paragraph are separated by a blanck line. If more than 
#   one blanck line is used, then a bigskip will be displayed 
#   between the two paragraph

import epub
from genshi.template import TemplateLoader
import re
import codecs
import pdb
import os

__help__ = """
Module to parse and create an ebook using the epub module. 
* You will need a text file in utf-8 to generate the epub.
* Some fashion can be done. For instance _text_ in 
  the .txt file will display "text" in italic
* By default, paragraph are separated by a blanck line. If more than 
  one blanck line is used, then a bigskip will be displayed 
  between the two paragraph.
  
To generate an epub, here is an example : 
book = book_epub.Book(title='Lorem Ipsum', authors = ['test'], 
                      lang = 'fr-FR', cover = 'cover.jpg')
# the cover is facultative, like the others parameters, 
# even if title and authors are quite recommended

book.sections = book_epub.parseBook('lorem_ipsum.txt')
book.make('epub/%s' % book.title)

# Note that if you want to skip a preamble, you must specify 
# the line of the beginning of the first chapter
# book.sections = ez_epub.parseBook('lorem_ipsum.txt', startLineNum=start_line)

/!\ Warning
A sub folder 'templates' with the templates must exists
a sub folder 'epucheck' should exists if you want to check your epub after creating it.

"""

CHAPTER = "Chapitre"



modulePath = os.path.dirname(os.path.realpath(__file__)) # the folder in which the module is. 

TEMPLATE_DIR = os.path.join(modulePath, 'templates')
if not(os.path.isdir(TEMPLATE_DIR)):
	raise IOError("The template folder '%s' does not exists" % TEMPLATE_DIR)


EPUBCHECK = os.path.join(modulePath, 'epubcheck/epubcheck-3.0-RC-2.jar')
if not(os.path.isdir(EPUBCHECK)):
	print("Warning: 'epubcheck' is not found in the subdirectory of\
	 the 'book_epub' module. The .epub will not be checked.")

class Section:

	def __init__(self):
		"""
		
		variables : 
		text : an array constitued of the following 
		       element : ('paragraph', 'class'). The first element is the text of a 
		       given paragraph. The second element of the tuple is the 'class' 
		       associated with the paragraph. Each element will be a <p></p> 
		       html element, and, if different from '', the class will be the 
		       class of a <span></span> element, surrounding the paragraph.
		       'class' can be empty, if regular paragraph, or a sequence of class
		       separated by space
		       """
		
		self.title = ''
		self.subsections = []
		self.css = ''
		self.text = []
		self.templateFileName = 'ez-section.html'
		
class Book:
	
	def __init__(self, title='', authors = [], cover='', lang='en-US'):
		"""
		To define a book. 
		
		Parameters :
		title='' : The title of the book, as a string
		authors=[] : The authors of the book, as string elements of an array
		cover='' : The path to the cover of the book, 'cover.jpg' for instance
		lang='en-US' :  the lang of the book
		"""
		
		self.epub = epub.EpubBook()
		self.title = title
		self.authors = authors
		self.cover = cover
		self.lang = lang
		self.sections = []
		self.templateLoader = TemplateLoader(TEMPLATE_DIR)
	  
	def __addSection(self, section, id, depth):
		if depth > 0:
			stream = self.templateLoader.load(section.templateFileName).generate(section = section)
			try:
			  html = stream.render('xhtml', doctype = 'xhtml11', drop_xml_decl = False)
			except:
			  pdb.set_trace()
			item = self.epub.addHtml('', '%s.html' % id, html)
			self.epub.addSpineItem(item)
			self.epub.addTocMapNode(item.destPath, section.title, depth)
			id += '.'
		if len(section.subsections) > 0:
			for (i, subsection) in enumerate(section.subsections):
				self.__addSection(subsection, id + str(i + 1), depth + 1)
	
	def setSections(self, sections):
		"""
		define the book.sections parameter
		
		Parameter 
		sections : an array of 'Section' objects"""
		
		
		self.sections = sections
	
	def parseBook(self, path, startLineNum=0, endLineNum=None):
		"""
		Function that will create an .epub using a text file. 
		
		Parameters : 
		path : the path to the text file. For instance "lorem_ipsum.txt"
		startLineNum=0 : (integer) the line at which we want to start the 
						 parser (usefull we we want to skip some preamble, 
						 but the specified line MUST BE after the preamble, 
						 right before the first chapter)
						 If not specified, the default value is 0
		endLineNum=None : (integer) the line at which we stop the parser. 
							If not specified, the file will be parsed up to 
							the end.
		"""
		
		PATTERN = re.compile(r'%s \d+$' % CHAPTER)
		sections = []
		
		# This section will contain everything before the first chapter. 
		# Only used when the starting line is 0. Else, we assume that 
		# the starting line is right before the first chapter
		if (startLineNum == 0):
			section = Section()
			section.title = "Infos"
			sections.append(section)
		
		paragraph = u''
		blanck_line_count = 0 # The number of blanck line after a paragraph
		fin = codecs.open(path, 'r', 'utf-8')
		lineNum = 0
		for line in fin:
			lineNum += 1
			if lineNum < startLineNum:
				continue
			if endLineNum > 0 and lineNum > endLineNum:
				break
			line = line.strip()
			if PATTERN.match(line):
				# If we match the regexp for the title of a chapter, we define a new chapter
				section = Section()
				section.css = """.em { font-style: italic; }"""
				section.title = line
				sections.append(section)
			elif line == u'':
				# If this is a blanck line, it means that : 
				# 1/ this is the end of a paragraph
				# 2/ we want a big space if this is not the first consecutive blanck lineinfo
							
				blanck_line_count += 1
				if (paragraph != u''):
					tmp = formatParagraph(paragraph)
					
					# If to end the paragraph there is several blanck line, 
					# we use the class 'bigskip' for this one. 
					# This does not apply to the first paragraph of a chapter
					if ((len(section.text) > 0) and (blanck_line_count > 1)):
						tmp = [(tmp[0][0], 'bigskip')]
					
					section.text.append(tmp)
					paragraph = u''
					blanck_line_count = 0

			else:
				# We add the current line at the current paragraph
				if paragraph != u'':
					paragraph += u' '
				paragraph += line
		
		# Special treatment for the last paragraph of the book
		if paragraph != u'':
			section.text.append(formatParagraph(paragraph))
		
		self.setSections(sections)

	
	def make(self, outputDir):
		
		if (self.sections == []):
			raise ValueError("self.sections is an empty array, cannot create an .epub")
		
		outputFile = outputDir + '.epub'
		
		self.epub.setTitle(self.title)
		self.epub.setLang(self.lang)
		for author in self.authors:
			self.epub.addCreator(author)
		if self.cover:
			self.epub.addCover(self.cover)
		self.epub.addTitlePage()
		self.epub.addTocPage()
		self.epub.addCss(os.path.join(TEMPLATE_DIR, "stylesheet.css"), "stylesheet.css")
		root = Section()
		root.subsections = self.sections
		self.__addSection(root, 's', 0)
		self.epub.createBook(outputDir)
		self.epub.createArchive(outputDir, outputFile)
		if os.path.isdir(EPUBCHECK):
			self.epub.checkEpub(EPUBCHECK, outputFile)
		else:
			print("Unable to find Epubcheck, .epub not checked")

def formatParagraph(paragraph):
	# We want utf8 encoding
	paragraph = paragraph.encode('utf-8')
	
	# Search and replace for given characters
	paragraph = paragraph.replace('--', '–')
	
	# Search for patterns. In xml, we define the name of the span class 
	# we want to invoke, span.em for instance, if <em>
	paragraph = re.sub(r' +', ' ', paragraph)
	paragraph = re.sub(r'_(.+?)_', r'<em>\1</em>', paragraph)
	return segmentParagraph(paragraph)

def segmentParagraph(paragraph):
	# Will search for xml environments such as <em> </em> and mark the 
	# given selection to be inside a span html environment with 
	# the specified class ('em' for the example)
	segments = []
	textStart = 0
	style = []
	for match in re.finditer(r'<(/?)([^>]+)>', paragraph):
		if match.start() > textStart:
			segments.append((paragraph[textStart : match.start()].decode('utf-8'), ' '.join(style)))
		if match.group(1) == '':
			style.append(match.group(2))
		else:
			style.remove(match.group(2))
		textStart = match.end()
	if textStart < len(paragraph):
		segments.append((paragraph[textStart :].decode('utf-8'), ' '.join(style)))
	return segments
	

