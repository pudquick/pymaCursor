import time, os
from objc import NULL
from Quartz.CoreGraphics import CGEventCreate, CGEventCreateMouseEvent, \
	CGEventGetLocation, CGEventPost, CGEventSetFlags, CGEventSetIntegerValueField,   \
	CGEventSourceCreate, CGPointMake, kCGEventFlagMaskAlternate,                     \
	kCGEventFlagMaskCommand, kCGEventFlagMaskControl, kCGEventFlagMaskShift,         \
	kCGEventLeftMouseDown, kCGEventLeftMouseUp, kCGEventMouseMoved,                  \
	kCGEventRightMouseDown, kCGEventRightMouseUp, kCGEventSourceStateHIDSystemState, \
	kCGHIDEventTap, kCGMouseEventClickState
from AppKit import NSEvent, NSScreen, NSPointInRect

PYMAC_SOURCE_REF = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)

def getMouseLoc():
	mouseEvent = CGEventCreate(NULL)
	mouseLoc = CGEventGetLocation(mouseEvent)
	return mouseLoc

def mouseEvent(eventVal, mouseLocation = False):
	if (mouseLocation == False): mouseLocation = getMouseLoc()
	return CGEventCreateMouseEvent(PYMAC_SOURCE_REF, eventVal, mouseLocation, 0)

def doEvent(eventObj):
	CGEventPost(kCGHIDEventTap, eventObj)

# mouse clicks

def performLeftClick(modKeys = 0):
	mLoc = getMouseLoc()
	clickMouse = mouseEvent(kCGEventLeftMouseDown, mLoc)
	if (modKeys != 0): CGEventSetFlags(clickMouse, modKeys)
	doEvent(clickMouse)
	doEvent(mouseEvent(kCGEventLeftMouseUp, mLoc))

def performRightClick():
	mLoc = getMouseLoc()
	doEvent(mouseEvent(kCGEventRightMouseDown, mLoc))
	doEvent(mouseEvent(kCGEventRightMouseUp, mLoc))

def performDoubleLeftClick():
	mLoc = getMouseLoc()
	# left click once to bring to foreground
	clickMouse = mouseEvent(kCGEventLeftMouseDown, mLoc)
	CGEventSetIntegerValueField(clickMouse, kCGMouseEventClickState, 1)
	doEvent(clickMouse)
	releaseMouse = mouseEvent(kCGEventLeftMouseUp, mLoc)
	CGEventSetIntegerValueField(releaseMouse, kCGMouseEventClickState, 1)
	doEvent(releaseMouse)
	# perform actual double click
	clickMouse2 = mouseEvent(kCGEventLeftMouseDown, mLoc)
	CGEventSetIntegerValueField(clickMouse2, kCGMouseEventClickState, 2)
	doEvent(clickMouse2)
	releaseMouse2 = mouseEvent(kCGEventLeftMouseUp, mLoc)
	CGEventSetIntegerValueField(releaseMouse2, kCGMouseEventClickState, 1)
	doEvent(releaseMouse2)

def getModKeysValue(doShiftDown = False, doCommandDown = False, doOptionDown = False, doControlDown = False):
	modKeys = 0
	if (doShiftDown):   modKeys |= kCGEventFlagMaskShift
	if (doCommandDown): modKeys |= kCGEventFlagMaskCommand
	if (doOptionDown):  modKeys |= kCGEventFlagMaskAlternate
	if (doControlDown): modKeys |= kCGEventFlagMaskControl
	return modKeys

def allModifiersUp():
	try: os.system('/usr/bin/osascript -e "tell application \\"System Events\\" to key up {shift, command, option, control}"')
	finally: return

# move mouse

def moveMouseToPoint(x, y):
	xFloat,yFloat = (0. + x), (0. + y)
	doEvent(mouseEvent(kCGEventMouseMoved, mouseLocation=CGPointMake(xFloat, yFloat)))

def stepMouseToPoint(x, y, numSteps=1):
	currentLoc = getMouseLoc()
	xFloat,yFloat = (0. + x), (0. + y)
	if (numSteps < 1): numSteps = 1
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
		return (mLoc.x,mLoc.y)
	else:
		mLoc = NSEvent.mouseLocation()
		return (mLoc.x,mLoc.y)

# helpers

def isPointOnAScreen(point):
	screens = NSScreen.screens()
	count = screens.count()
	for i in range(count):
		if (NSPointInRect(point, screens[i].frame())): return screens[i]
	return None
