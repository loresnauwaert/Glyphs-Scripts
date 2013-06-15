#MenuTitle: Delete guidelines
# -*- coding: utf-8 -*-
"""Delete all local guidelines in selected glyphs."""

import GlyphsApp

selectedLayers = Glyphs.currentDocument.selectedLayers()

def process( thisLayer ):
	thisLayer.setGuideLines_([])

Font.disableUpdateInterface()

for thisLayer in selectedLayers:
	print "Processing", thisLayer.parent.name
	thisLayer.undoManager().beginUndoGrouping()
	process( thisLayer )
	thisLayer.undoManager().endUndoGrouping()

Font.enableUpdateInterface()
