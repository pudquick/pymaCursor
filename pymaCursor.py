import objc, time, os
import Quartz.CoreGraphics as qCG
from Quartz.CoreGraphics import CGEventPost,CGEventSetFlags, \
	CGEventSetIntegerValueField,CGPointMake,CGEventCreate, \
	CGEventGetLocation,CGEventCreateMouseEvent
from AppKit import NSEvent, NSScreen, NSPointInRect

global sourceRef
sourceRef = qCG.CGEventSourceCreate(qCG.kCGEventSourceStateHIDSystemState)

def getMouseLoc():
	mouseEvent = CGEventCreate(objc.NULL)
	mouseLoc = CGEventGetLocation(mouseEvent)
	# print mouseLoc
	return mouseLoc

def mouseEvent(eventVal, mouseLocation = False):
	global sourceRef
	if (mouseLocation == False):
		mouseLocation = getMouseLoc()
	# return CGEventCreateMouseEvent(objc.NULL, eventVal, mouseLocation, 0)
	return CGEventCreateMouseEvent(sourceRef, eventVal, mouseLocation, 0)

def doEvent(eventObj):
	CGEventPost(qCG.kCGHIDEventTap, eventObj)

# mouse clicks

def performLeftClick(modKeys = 0):
	mLoc = getMouseLoc()
	clickMouse = mouseEvent(qCG.kCGEventLeftMouseDown, mLoc)
	if (modKeys != 0):
		CGEventSetFlags(clickMouse, modKeys)
	doEvent(clickMouse)
	doEvent(mouseEvent(qCG.kCGEventLeftMouseUp, mLoc))
	return True

def performRightClick():
	mLoc = getMouseLoc()
	doEvent(mouseEvent(qCG.kCGEventRightMouseDown, mLoc))
	# eventually add in modifiers
	doEvent(mouseEvent(qCG.kCGEventRightMouseUp, mLoc))
	return True

def performDoubleLeftClick():
	mLoc = getMouseLoc()
	# left click once to bring to foreground
	clickMouse = mouseEvent(qCG.kCGEventLeftMouseDown, mLoc)
	CGEventSetIntegerValueField(clickMouse, qCG.kCGMouseEventClickState, 1)
	doEvent(clickMouse)
	releaseMouse = mouseEvent(qCG.kCGEventLeftMouseUp, mLoc)
	CGEventSetIntegerValueField(releaseMouse, qCG.kCGMouseEventClickState, 1)
	doEvent(releaseMouse)
	# perform actual double click
	clickMouse2 = mouseEvent(qCG.kCGEventLeftMouseDown, mLoc)
	CGEventSetIntegerValueField(clickMouse2, qCG.kCGMouseEventClickState, 2)
	doEvent(clickMouse2)
	releaseMouse2 = mouseEvent(qCG.kCGEventLeftMouseUp, mLoc)
	CGEventSetIntegerValueField(releaseMouse2, qCG.kCGMouseEventClickState, 1)
	doEvent(releaseMouse2)
	return True

def getModKeysValue(doShiftDown = False, doCommandDown = False, doOptionDown = False, doControlDown = False):
	modKeys = 0
	if (doShiftDown):
		modKeys |= qCG.kCGEventFlagMaskShift
	if (doCommandDown):
		modKeys |= qCG.kCGEventFlagMaskCommand
	if (doOptionDown):
		modKeys |= qCG.kCGEventFlagMaskAlternate
	if (doControlDown):
		modKeys |= qCG.kCGEventFlagMaskControl
	return modKeys

def allModifiersUp():
	try:
		os.system('/usr/bin/osascript -e "tell application \\"System Events\\" to key up {shift, command, option, control}"')
	finally:
		return True

# move mouse

def moveMouseToPoint(x, y):
	xFloat,yFloat = (0. + x), (0. + y)
	doEvent(mouseEvent(qCG.kCGEventMouseMoved, mouseLocation=CGPointMake(xFloat, yFloat)))
	return True

def stepMouseToPoint(x, y, numSteps=1):
	currentLoc = getMouseLoc()
	xFloat,yFloat = (0. + x), (0. + y)
	if (numSteps < 1):
		numSteps = 1
	xIncrement = (xFloat - currentLoc.x) / numSteps
	yIncrement = (yFloat - currentLoc.y) / numSteps
	xPrevious,yPrevious = (0. + currentLoc.x), (0. + currentLoc.y)
	for i in range(numSteps):
		xNew,yNew = (xPrevious + xIncrement), (yPrevious + yIncrement)
		moveMouseToPoint(xNew,yNew)
		xPrevious,yPrevious = xNew,yNew
		time.sleep(0.0008)
	moveMouseToPoint(x,y)

def mouseLocation(isTopCoordinates = True):
	if (isTopCoordinates):
		mLoc = getMouseLoc()
		return "%.0f\n%.0f" % (mLoc.x,mLoc.y)
	else:
		mLoc = NSEvent.mouseLocation()
		return "%.0f\n%.0f" % (mLoc.x,mLoc.y)

# helpers

def isPointOnAScreen(point):
	screens = NSScreen.screens()
	count = screens.count()
	for i in range(count):
		if (NSPointInRect(point, screens[i].frame())):
			return (True, screens[i])
	return (False, None)

# TODO:
# Work in flipping coordinates if requested between topleft and bottomleft
# Make use of isPointOnAScreen to verify the point is valid before moving there
# Can also pull details about the various screens and sizes that way
