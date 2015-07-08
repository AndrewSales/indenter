import getopt
import xml.sax
import sys
import io
import codecs


class Indenter( xml.sax.handler.ContentHandler, xml.sax.handler.ErrorHandler ):

	EVT_CHARS = 1
	EVT_START_ELEM = 2
	EVT_END_ELEM = 3
	EVT_START_DOC = 4
	EVT_PI = 5
	
	SHORT_OPTS = 'ac:i:p'
	LONG_OPTS = ''

	def __init__( self, args ):
		self.indent = 0
		self.indentIncr = 2
		self.indentChar = ' '
		self.attsOnNewLine = 0
		self.pIsOnNewLine = 0
		self.buf = io.StringIO()
		self.lastEvent = 0
		self.input = None
		self.parseCommandLine( args )
		xml.sax.parse(self.input, self, self)

	def startDocument( self ):
		sys.stdout.write('<?xml version=\'1.0\'?>' )
		self.lastEvent = self.EVT_START_DOC

	def startElement( self, name, attrs ):
		self.flushBuffer()
		indent = self.indentChar * self.indent
		attIndent = (len(name) + 2 + self.indent) * self.indentChar
		if self.lastEvent == self.EVT_START_ELEM:
			sys.stdout.write( '>' )
		sys.stdout.write( '\n%s<%s' % (indent,name) )

		atts = attrs.keys()
		first = 1
		for att in atts:
			if first:
				sys.stdout.write( ' %s=%s' % (att,xml.sax.saxutils.quoteattr(attrs[att]) ) )
				first = 0
			else:
				if self.attsOnNewLine:
					sys.stdout.write( '\n%s%s=%s' % (attIndent,att,xml.sax.saxutils.quoteattr(attrs[att])) )
				else:
					sys.stdout.write( ' %s=%s' % (att,xml.sax.saxutils.quoteattr(attrs[att])) )

		self.indent += self.indentIncr
		self.lastEvent = self.EVT_START_ELEM

	def endElement( self, name ):
		self.flushBuffer()
		if self.lastEvent == self.EVT_START_ELEM:
			sys.stdout.write( '/>' )
		elif self.lastEvent == self.EVT_CHARS:
			sys.stdout.write( '</%s>' % name )
		elif self.lastEvent == self.EVT_PI:
			sys.stdout.write( '</%s>' % name )			
		elif self.lastEvent == self.EVT_END_ELEM:
			sys.stdout.write( '\n%s</%s>' % (self.indentChar * (self.indent-self.indentIncr),name) )
		self.indent -= self.indentIncr		

		self.lastEvent = self.EVT_END_ELEM

	def characters( self, s ):
		if self.lastEvent == self.EVT_START_ELEM:
			sys.stdout.write( '>' )		
		self.buf.write( s )
		self.lastEvent = self.EVT_CHARS

	def processingInstruction( self, target, data ):
		if self.lastEvent == self.EVT_START_ELEM:
			sys.stdout.write( '>' )	
		newline = ''
		if self.pIsOnNewLine:
			newline = '\n%s' % (self.indent * self.indentChar)
		sys.stdout.write( '%s<?%s %s?>' % (newline,target,data) )
		self.lastEvent = self.EVT_PI

	def flushBuffer( self ):
		sys.stdout.write( ( xml.sax.saxutils.escape( self.buf.getvalue() ).encode('ascii', 'xmlcharrefreplace').decode() ) )
		self.buf = io.StringIO()

	def fatalError( self, e ):
		sys.stderr.write( 'FATAL error:%s\n' % e )
		#sys.exit(-1)

	def error( self, e ):
		sys.stderr.write( 'error:%s\n' % e )		
		
	def usage( self ):
		sys.stderr.write('indenter: XML indentation tool\nindenter.py file-to-indent [options]\n  options:\n\
	-a         new line for each attribute (default is keep inline)\n\
	-c[char]   specifies indent character (default is space; tab is \'\\t\')\n\
	-i[digit]  specifies indent increment (default is 2)\n\
	-p         processing instructions on new line (default is keep inline)')
		sys.exit(-1)	
		
	def parseCommandLine( self, argv ):
		if len( argv ) < 2:
			self.usage()
		else:
			self.input = argv[1]
			try:
				opts, args = getopt.getopt( argv[2:], self.SHORT_OPTS, self.LONG_OPTS )
			except getopt.GetoptError:
				self.error( sys.exc_info()[1].msg )	#see getopt module docs
				self.usage()
		
		for o, a in opts:
			if o == '-a':
				self.attsOnNewLine = 1
			if o == '-c':
				if a == '\\t':	#tab
					self.indentChar = '	'
				else:
					self.indentChar = a
			if o == '-i':
				try:
					self.indentIncr = int(a)
				except ValueError:
					self.error( str(sys.exc_info()[1]) + '; indent increment defaulting to 2' )
					self.indentIncr = 2
			if o == '-p':
				self.pIsOnNewLine = 1					
		
#main	

x = Indenter( sys.argv )