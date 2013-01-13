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
import xml.etree.ElementTree as ET

__help__ = """
Module to parse and create an ebook using the epub module. 
* You will need a text file in utf-8 to generate the epub.

Allow us to create an object that we will try to convert into en epub. We must create the objet, then parse a xml file to fill in the properties of the book. 

Basic example : 
> book = book_epub.Book(title='Le Passeur', authors=['Lois Lowry'], lang='fr-FR', cover='le_passeur.jpg')
> 
> # the text file must be in utf-8
> book.parseBook('le_passeur.xml')
> book.make('epub/%s' % book.title)

The XML must have the following properties : 
_ The book and all its properties must be in a "<book></book>".
_ Each paragraph is <par</par>
_ each section start with <section>the section title</section>
_ the paragraph can have one or more of the following options : 
  * poem : italic style for poem and songs
  * bigskip : ahead of the current paragraph, there will be an extra space
  
  To define the options : <par option="poem bigskip"> or <par option="poem">
_ for italic text, braket the text with "<i></i>
_ to define footnotes, use where you want the mark : "<footnote>the text of the footnote</footnote>". The footnote texts will appear at the end of the book.

Basic Example of XML book : 
<book>
<section>Chapter 1</section>
<par>Lorem ipsum blabla bla.</par>

<par> Paragraph 2, <i>blabla</i>. But trhoi<footnote>Does not mean 
anything though.</footnote>
</par>
</book>
  

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
if not(os.path.isfile(EPUBCHECK)):
  print("Warning: 'epubcheck' is not found in the subdirectory of\
   the 'book_epub' module. The .epub will not be checked.")
  pdb.set_trace()

class Section:
  
  section_id = 0 # usefull for the default filename of the object

  def __init__(self, title='', filename="default"):
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
    
    Section.section_id += 1
    
    self.title = title
    
    if (filename == "default"):
      self.filename = "section_%d" % Section.section_id # without the extension
    else:
      self.filename = filename
    self.subsections = []
    self.css = ''
    self.text = []
    
class Book:
  """
  Allow us to create an object that we will try to convert into en epub. We must create the objet, then parse a xml file to fill in the properties of the book. 
  
  Basic example : 
  > book = book_epub.Book(title='Le Passeur', authors=['Lois Lowry'], lang='fr-FR', cover='le_passeur.jpg')
  > 
  > # the text file must be in utf-8
  > book.parseBook('le_passeur.xml')
  > book.make('epub/%s' % book.title)
  
  The XML must have the following properties : 
  _ The book and all its properties must be in a "<book></book>".
  _ Each paragraph is <par</par>
  _ each section start with <section>the section title</section>
  _ the paragraph can have one or more of the following options : 
    * poem : italic style for poem and songs
    * bigskip : ahead of the current paragraph, there will be an extra space
    
    To define the options : <par option="poem bigskip"> or <par option="poem">
  _ for italic text, braket the text with "<i></i>
  _ to define footnotes, use where you want the mark : "<footnote>the text of the footnote</footnote>". The footnote texts will appear at the end of the book.
  
  Basic Example of XML book : 
  <book>
  <section>Chapter 1</section>
  <par>Lorem ipsum blabla bla.</par>
  
  <par> Paragraph 2, <i>blabla</i>. But trhoi<footnote>Does not mean 
  anything though.</footnote>
  </par>
  </book>
  """
  
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
    
  def __addSection(self, section, depth):
    if depth > 0:
      html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n' + \
             '<html xmlns="http://www.w3.org/1999/xhtml">\n' + \
             '<head>\n' + \
             '  <title>%s</title>\n' % section.title + \
             '  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n' + \
             '  <link href="../Styles/stylesheet.css" rel="stylesheet" type="text/css" />\n' + \
             '  <style type="text/css">\n' + \
             '%s\n' % section.css + \
             '  </style>\n' + \
             '</head>\n' + \
             '<body>\n' + \
             '  <h1>%s</h1>\n' % section.title
      for paragraph in section.text:
        html += '  %s\n\n' % paragraph
      
      html += '</body>\n</html>'
      html = html.encode('utf-8')
      #~ stream = self.templateLoader.load(section.templateFileName).generate(section = section)
      #~ try:
        #~ html = stream.render('xhtml', doctype = 'xhtml11', drop_xml_decl = False)
      #~ except:
        #~ pdb.set_trace()
      
      item = self.epub.addHtml('', '%s.html' % section.filename, html)
      self.epub.addSpineItem(item)
      self.epub.addTocMapNode(item.destPath, section.title, depth)

    if len(section.subsections) > 0:
      for (i, subsection) in enumerate(section.subsections):
        self.__addSection(subsection, depth + 1)
  
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
    """
    
    tree = ET.parse(path)
    root = tree.getroot()
    
    footnote = [] # The list of footnote text, we will write them at the end of the book
    footnote_ref = [] # the corresponing ref for each footnote

    sections = []
    for child in root:
      tag = child.tag
      
      if (tag == 'section'):
        section = Section()
        section.title = child.text
        sections.append(section)
      elif (tag == 'par'):
        id_tail = 0
        texts = [text for text in child.itertext()]
        
        for grandchild in child._children:
          if (grandchild.text != None):
            id_text = texts.index(grandchild.text)
          
          
          if (grandchild.tag == 'i'):
            texts[id_text] = '<span class="italic">%s</span>' % texts[id_text]
          elif (grandchild.tag == 'footnote'):
            footnote.append(texts[id_text])
            nb_footnote = len(footnote)
            footnote_ref_tmp = "%s.html#footnotebackref_%d" % (section.filename, nb_footnote)
            footnote_ref.append(footnote_ref_tmp)
            texts[id_text] = '<a id="footnotebackref_%d"></a><a href="footnote.html#footnote_%d">[%d]</a>' % (nb_footnote, nb_footnote, nb_footnote)
          elif (grandchild.tag == 'br'):
            try:
              # In some cases, for short tail texts, several occurences can appear in the list. The following line is here to prevent such misplacements of "<br />"
              id_tail = id_tail + texts[id_tail:].index(grandchild.tail)
              texts.insert(id_tail, '<br />')
            except:
              print("Warning: Apparently two tag seems to be one next to each other, this make the parser bug.")
              pdb.set_trace()
        
        tmp = '<p>'
        styles = []
        if child.attrib.has_key('option'):
          options = child.attrib['option'].split()
          
          for option in options:
            if (option == 'bigskip'):
              styles.append('bigskip')
            elif (option == 'poem'):
              styles.append('poem')
          
          if styles:
            tmp = '<p class="%s">' % " ".join(styles)
            
        tmp += "%s</p>\n" % " ".join(texts)
        section.text.append(tmp)
    
    if (len(footnote) != 0):
      section = Section()
      section.title = "Notes"
      section.filename = "footnote"
      sections.append(section)
      tmp = ''
      for nb in range(len(footnote)):
        footnote_text = footnote[nb]
        ref = footnote_ref[nb]
        tmp += '\n\n<br /><br /><a id="footnote_%d"></a><a href="%s">[%d]</a> %s' % (nb+1, ref, nb+1, footnote_text)
      tmp = "<p>%s</p>\n" % tmp
      section.text.append(tmp)

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
    self.__addSection(root, 0)
    self.epub.createBook(outputDir)
    self.epub.createArchive(outputDir, outputFile)
    if os.path.isfile(EPUBCHECK):
      self.epub.checkEpub(EPUBCHECK, outputFile)
    else:
      print("Unable to find Epubcheck, .epub not checked")

