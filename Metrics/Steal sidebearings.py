#MenuTitle: Steal Sidebearings
# -*- coding: utf-8 -*-
__doc__="""
Copy sidebearings from one font to another.
"""

import vanilla, math
windowHeight = 185

class MetricsCopy( object ):
	"""GUI for copying glyph metrics from one font to another"""
	
	def __init__( self ):
		self.listOfMasters = []
		self.updateListOfMasters() 
		
		self.w = vanilla.FloatingWindow( (400, windowHeight), "Steal Sidebearings", minSize=(350, windowHeight), maxSize=(650, windowHeight), autosaveName="com.mekkablue.MetricsCopy.mainwindow" )
		
		self.w.text_anchor = vanilla.TextBox( (15, 12+2, 130, 17), "Copy metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton( (150, 12, -15, 17), self.listOfMasterNames(), sizeStyle='small', callback=self.buttonCheck)
		
		self.w.text_value = vanilla.TextBox( (15, 12+2+25, 130, 17), "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton( (150, 12+25, -15, 17), self.listOfMasterNames()[::-1], sizeStyle='small', callback=self.buttonCheck)
		
		self.w.lsb   = vanilla.CheckBox( ( 17, 12+50, 80, 20), "LSB", value=True, callback=self.buttonCheck, sizeStyle='small' )
		self.w.rsb   = vanilla.CheckBox( ( 97, 12+50, 80, 20), "RSB", value=True, callback=self.buttonCheck, sizeStyle='small' )
		self.w.width = vanilla.CheckBox( (177, 12+50, 80, 20), "Width", value=False, callback=self.buttonCheck, sizeStyle='small' )
		
		self.w.ignoreSuffixes  = vanilla.CheckBox( (15+2, 12+75, 110, 20), "Ignore dotsuffix:", value=False, sizeStyle='small', callback=self.buttonCheck )
		self.w.suffixToBeIgnored = vanilla.EditText( (150, 12+75, -15, 20), ".alt", sizeStyle = 'small')

		self.w.keepWindowOpen  = vanilla.CheckBox( (15+2, 12+100, 150, 20), "Keep this window open", value=False, sizeStyle='small' )
		
		self.w.copybutton = vanilla.Button((-80, -32, -15, 17), "Copy", sizeStyle='small', callback=self.copyMetrics)
		self.w.setDefaultButton( self.w.copybutton )
		
		if not self.LoadPreferences( ):
			self.outputError( "Could not load preferences at startup. Will resort to defaults." )
		
		self.w.open()
		self.w.makeKey()
		
		self.buttonCheck( None )
	
	def updateListOfMasters( self ):
		try:
			masterList = []
		
			for thisFont in Glyphs.fonts:
				for thisMaster in thisFont.masters:
					masterList.append( thisMaster )
			
			masterList.reverse() # so index accessing works as expected, and the default is: current font = target
			self.listOfMasters = masterList
		except:
			print traceback.format_exc()
	
	def listOfMasterNames( self ):
		try:
			myMasterNameList = [ 
				"%i: %s - %s" % ( 
					i+1,
					self.listOfMasters[i].font().familyName,
					self.listOfMasters[i].name 
				) for i in range(len( self.listOfMasters ))
			]
			return myMasterNameList
		except:
			print traceback.format_exc()
	
	def outputError( self, errMsg ):
		print "Steal Sidebearings Warning:", errMsg
	
	def buttonCheck( self, sender ):
		try:
			# check if both font selection point to the same font
			# and disable action button if they do:
			fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
			toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]
		
			if fromFont == toFont:
				self.w.copybutton.enable( onOff=False )
			else:
				self.w.copybutton.enable( onOff=True )
		
			# check if checkbox is enabled
			# and sync availability of text box
			suffixCheckBoxChecked = self.w.ignoreSuffixes.get()
			if suffixCheckBoxChecked:
				self.w.suffixToBeIgnored.enable( onOff=True )
			else:
				self.w.suffixToBeIgnored.enable( onOff=False )
			
			# All of LSB, RSB and Width must not be on at the same time:
			if self.w.rsb.get() and self.w.lsb.get() and self.w.width.get():
				if sender == self.w.rsb:
					self.w.width.set(False)
				else:
					self.w.rsb.set(False)
		
			if not self.SavePreferences( self ):
				self.outputError( "Could not save preferences." )
		except:
			print traceback.format_exc()
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] = self.w.ignoreSuffixes.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] = self.w.suffixToBeIgnored.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"] = self.w.rsb.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"] = self.w.lsb.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.width"] = self.w.width.get()
			return True
		except:
			return False

	def LoadPreferences( self ):
		try:
			self.w.ignoreSuffixes.set( Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] )
			self.w.suffixToBeIgnored.set( Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] )
			self.w.lsb.set( Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"] )
			self.w.rsb.set( Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"] )
			self.w.width.set( Glyphs.defaults["com.mekkablue.MetricsCopy.width"] )
			return True
		except:
			return False
	
	def transform(self, shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
		"""
		Returns an NSAffineTransform object for transforming layers.
		Apply an NSAffineTransform t object like this:
			Layer.transform_checkForSelection_doComponents_(t,False,True)
		Access its transformation matrix like this:
			tMatrix = t.transformStruct() # returns the 6-float tuple
		Apply the matrix tuple like this:
			Layer.applyTransform(tMatrix)
			Component.applyTransform(tMatrix)
			Path.applyTransform(tMatrix)
		Chain multiple NSAffineTransform objects t1, t2 like this:
			t1.appendTransform_(t2)
		"""
		myTransform = NSAffineTransform.transform()
		if rotate:
			myTransform.rotateByDegrees_(rotate)
		if scale != 1.0:
			myTransform.scaleBy_(scale)
		if not (shiftX == 0.0 and shiftY == 0.0):
			myTransform.translateXBy_yBy_(shiftX,shiftY)
		if skew:
			skewStruct = NSAffineTransformStruct()
			skewStruct.m11 = 1.0
			skewStruct.m22 = 1.0
			skewStruct.m21 = math.tan(math.radians(skew))
			skewTransform = NSAffineTransform.transform()
			skewTransform.setTransformStruct_(skewStruct)
			myTransform.appendTransform_(skewTransform)
		return myTransform
	
	
	def copyMetrics(self, sender):
		fromFontIndex  = self.w.from_font.get()
		toFontIndex    = self.w.to_font.get() * -1 - 1
		sourceMaster   = self.listOfMasters[ fromFontIndex ]
		targetMaster   = self.listOfMasters[ toFontIndex ]
		sourceMasterID = sourceMaster.id
		targetMasterID = targetMaster.id
		sourceFont     = sourceMaster.font()
		targetFont     = targetMaster.font()
		ignoreSuffixes = self.w.ignoreSuffixes.get()
		lsbIsSet = self.w.lsb.get()
		rsbIsSet = self.w.rsb.get()
		widthIsSet = self.w.width.get()
		suffixToBeIgnored = self.w.suffixToBeIgnored.get().strip(".")
		selectedLayers = targetFont.selectedLayers
		
		print "Copying %i glyph metrics from %s %s to %s %s:" % ( 
				len(selectedLayers),
				sourceFont.familyName, sourceMaster.name,
				targetFont.familyName, targetMaster.name
			)
		
		for thisLayer in [ targetFont.glyphs[l.parent.name].layers[targetMasterID] for l in selectedLayers ]:
			try:
				glyphName = thisLayer.parent.name
			
				if ignoreSuffixes:
					# replace suffix in the middle of the name:
					glyphName = glyphName.replace( ".%s." % suffixToBeIgnored, "." )
				
					# replace suffix at the end of the name:
					if glyphName.endswith( ".%s" % suffixToBeIgnored ):
						glyphName = glyphName[:-len(suffixToBeIgnored)-1]
					
				sourceLayer = sourceFont.glyphs[ glyphName ].layers[ sourceMasterID ]
			
				if lsbIsSet:
					thisLayer.setLSB_( sourceLayer.LSB )
				if widthIsSet:
					thisLayer.setWidth_( sourceLayer.width )
					if rsbIsSet:
						shift = thisLayer.RSB - sourceLayer.RSB
						shiftTransform = self.transform(shiftX=shift)
						thisLayer.transform_checkForSelection_doComponents_(shiftTransform,False,True)
				elif rsbIsSet:
					thisLayer.setRSB_( sourceLayer.RSB )

				print "     %i <- %s -> %i (w: %i)" % ( thisLayer.LSB, glyphName, thisLayer.RSB, thisLayer.width )
			except Exception, e:
				if "'objc.native_selector' object has no attribute 'name'" not in e: # CR in the selection string
					print "Error:", e
		
		if not self.w.keepWindowOpen.get():
			self.w.close()
		
MetricsCopy()
