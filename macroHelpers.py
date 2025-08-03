import ctypes
import pydirectinput
import time
import win32gui
import mss
from PIL import Image, ImageOps
import json
import re
import colorsys
import onnxruntime as ort
import numpy as np
from tkinter import messagebox

# some things for import and export that need to be run before using. 
#pydirectinput.PAUSE = 0.0167 # The game can only register 1 input per frame, so the pause is ~1/60 
#pydirectinput.PAUSE = 0.017
pydirectinput.PAUSE = 0.017
ctypes.windll.user32.SetProcessDPIAware()
hwnd = None
reader = None
ocrOpened = False
sliderModel = None
sliderInput_name = None
colorModel = None
colorInput_name = None
gameOpenModel = None
gameOpenInput_name = None

sliderRegions = ((.3445,.203,.372,.226),
                     (.3445,.285,.372,.308),
                     (.3445,.366,.372,.389),
                     (.3445,.448,.372,.471),
                     (.3445,.529,.372,.552),
                     (.3445,.610,.372,.633),
                     (.3445,.692,.372,.715),
                     (.3445,.773,.372,.796))
tileCoords = [(.2625,.225),(.3427,.225),(.4234,.225),
              (.2625,.3657),(.3427,.3657),(.4234,.3657),
              (.2625,.5019),(.3427,.5019),(.4234,.5019),
              (.2625,.6389),(.3427,.6389),(.4234,.6389),
              (.2625,.7731),(.3427,.7731),(.4234,.7731),]
tileScrollAmounts = {"hair":.0835,"brow":.1115,"beard":0,"eyelashes":0,"tattoo":.042, "pupil": 0} # how much the scroll bar moves per page, used to find the tile selected 
def enter():
    pydirectinput.press('e')
def back():
    pydirectinput.press('q')
def down():
    pydirectinput.press('down')
def up():
    pydirectinput.press('up')
def scrollDown(times):
    for i in range(times):
        down()
def animDelay():
    time.sleep(.25) #.2 might be fine?
def enterDelay():
    time.sleep(.3)
def isSelected(x,y,desiredColor,tolerance):
    """Returns whether or not the box at the given coordinates is selected (is orange).

    Args:
        x (float): x coordinate represented as float from 0 to 1.
        y (float): y coordinate represented as float from 0 to 1.
        desiredColor (tuple[int, int, int]): The RGB color that represents a box being selecting. 
        tolerance (float): How close the in-game color has to be to desiredColor to be labeled as selected. 
    
    Returns:
        bool: Represents whether or not the box at the coordinate is selected. 
    """
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))
    left = int(rectCoords[0] + x * clientRect[2]) # convert to pixel coordinates 
    top = int(rectCoords[1] + y * clientRect[3])
    with mss.mss() as sct:
        mssScreenshot = sct.grab({'left': left, 'top': top, 'width': 1, 'height': 1})
        screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
        # mss.tools.to_png(mssScreenshot.rgb, mssScreenshot.size, output="pixelScreenshot.png")
        r,g,b = screenshot.getpixel((0,0))
        # print("desired:", desiredColor)
        # print("actual:",r,g,b)
        print("color difference :", desiredColor[0]-r,desiredColor[1]-g,desiredColor[2]-b) # DEBUG
        return isColor(r,g,b,desiredColor,tolerance) 
def isColor(r,g,b, desiredColor, tolerance):
    """This is a helper method for isSelected that checks whether the game's color is close enough to the desired color.
    
    Args:
        x (float): x coordinate represented as float from 0 to 1.
        y (float): y coordinate represented as float from 0 to 1.
        desiredColor (tuple[int, int, int]): The RGB color that represents a box being selecting. 
        tolerance (float): How close the in-game color has to be to desiredColor to be labeled as selected. 
    
    Returns:
        bool: Represents whether or not the box at the coordinate is selected. 
    """
    # Checking difference in hue works better than rgb because the color's brightness is variable due to the animation in-game. 
    actualHue = colorsys.rgb_to_hls(r/255,g/255,b/255)[0] 
    desiredHue = colorsys.rgb_to_hls(desiredColor[0]/255,desiredColor[1]/255,desiredColor[2]/255)[0]
    if abs(desiredHue - actualHue) < tolerance:
        return True
    else:
        return False
def loadOCR():
    global ocrOpened
    if ocrOpened:
        print("OCR already opened")
        time.sleep(3)
        if not checkIfGameIsOpen():
            notOpenedMessage()
            return False
        return True
    
    startFullscreenWait = time.time()
    print("starting fullscreen wait")

    global sliderModel
    global sliderInput_name
    sliderModel = ort.InferenceSession("models/sliderValueDetect.onnx")
    sliderInput_name = sliderModel.get_inputs()[0].name
    global colorModel
    global colorInput_name
    colorModel = ort.InferenceSession("models/colorValueDetect.onnx")
    colorInput_name = colorModel.get_inputs()[0].name
    global gameOpenModel
    global gameOpenInput_name
    gameOpenModel = ort.InferenceSession("models/gameOpenDetect.onnx")
    gameOpenInput_name = gameOpenModel.get_inputs()[0].name

    global hwnd
    hwnd = win32gui.FindWindow(None, "DARK SOULS III")
    if (hwnd == 0):
        print("error")
        quit()  

    endFullscreenWait = time.time()

    timeLeftToWait = 3 - (endFullscreenWait-startFullscreenWait)
    if (timeLeftToWait > 0):
        time.sleep(timeLeftToWait)
    if not checkIfGameIsOpen() or hwnd == 0:
        notOpenedMessage()
        return False
    ocrOpened = True
    return True
def checkIfGameIsOpen():
    if not isGameFocused():
        return False
    x,y,x2,y2 = (.0469,.1333,.4992,.7153)
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))

    left = int(rectCoords[0] + x * clientRect[2])
    top = int(rectCoords[1] + y * clientRect[3])
    width = int((x2-x) * clientRect[2])
    height = int((y2-y) * clientRect[3])

    with mss.mss() as sct:
        mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
        screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
    resized = ImageOps.fit(screenshot, (290, 210), method=Image.LANCZOS, centering=(0.5, 0.5))
    imageArray = np.array(resized).astype(np.float32)
    imageArray = imageArray.reshape(1, 210, 290, 3)

    resized.save("testOpenDetection.png") # DEBUG

    outputs = gameOpenModel.run(None, {gameOpenInput_name: imageArray})
    prob = outputs[0][0]
    print(prob)
    if prob > .5:
        return True # correct menu open
    else:
        return False # game not open or incorrect menu 
def processRegion(x,y,x2,y2, isColor):
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))

    left = int(rectCoords[0] + x * clientRect[2])
    top = int(rectCoords[1] + y * clientRect[3])
    width = int((x2-x) * clientRect[2])
    height = int((y2-y) * clientRect[3])

    with mss.mss() as sct:
        mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
        screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
        screenshot = ImageOps.grayscale(screenshot)

    resized = ImageOps.fit(screenshot, (35, 17), method=Image.LANCZOS, centering=(0.5, 0.5))
    imageArray = np.array(resized).astype(np.float32)
    imageArray = imageArray.reshape(1, 17, 35, 1)

    resized.save("testInput.png") # DEBUG

    if isColor:
        outputs = colorModel.run(None, {colorInput_name: imageArray})
        probs = outputs[0]
    else:
        outputs = sliderModel.run(None, {sliderInput_name: imageArray})
        probs = outputs[0]

    answer = np.argmax(probs[0])
    confidence = probs[0][answer]
    
    return int(answer), confidence
def saveFile(filePath, dict):
    def stripNewLine(m):
        """gets rid of \n characters as well as the extra spaces"""
        values = m.group(1)
        strippedValues = re.sub(r'\n\s*', '', values)
        return f'"options": [{strippedValues}],'
    jsonString = json.dumps(dict, indent=3)
    #formatting
    jsonString = re.sub(r'"options":\s\[(.*?)\],', stripNewLine, jsonString, flags=re.DOTALL)
    with open(filePath, "w") as f:
        f.write(jsonString)
        print("saved")
def menuHasValues(menu):
    if "menu" in menu: # if page with values (not a buttons page)
        for i in menu:
            if i not in ("menu", "options", "colorsLinked", "linkType", "numTiles", "folder","tilesLinked") and menu[i] not in (-1, ""):
                return True # value is set 
        return False # no values set
    for i in menu:
        if i in ("colorsLinked","tilesLinked"):
            continue
        if menuHasValues(menu[i]):
            return True # value was found 
    return False
def findSelectedTile(menu):
    page = findTilePage(menu)
    #print("page:", page)
    tile = currentTileOnPage()
    #print("tile:", tile)
    #print("final:", (tile + (page-1)*3))
    if page and tile: # if not null 
        return tile + (page-1)*3  
def findTilePage(menu):
    specificMenu = menu["folder"]
    scrollAmount = tileScrollAmounts[specificMenu]
    if scrollAmount == 0: # page without scrollbar 
        return 1
    sliderPos = .167
    pageNum = 1
    scrollBottom = .832 # position of the bottom of where the scroll bar can go 
    while sliderPos < scrollBottom:
        if isSelected(.5026, sliderPos, (131,91,31), .05):
            return pageNum
        sliderPos += scrollAmount
        pageNum += 1
    # failsafe
    print("ERROR: no slider found")
    time.sleep(.1)
    return findTilePage(menu)
def currentTileOnPage():
    """finds which tile is currently selected on the current page (1-15), does not account for the scroll bar """
    j = 1
    for i in tileCoords:
        if isSelected(*i, (86,39,11),.05):
            return j
        j +=1
    # call again if none found - this could cause an infinite loop but that shouldn't be a real issue 
    time.sleep(.1)
    print("none found")
    return currentTileOnPage()
def notOpenedMessage():
    messagebox.showwarning("ERROR", "The game was either not opened, or was opened to the wrong menu.")
def invalidJsonMessage():
    messagebox.showwarning("ERROR", "The file you chose is invalid. This is likely due to it not being a json file, or it having invalid json syntax.")
def gameClosedMesage():
    messagebox.showwarning("ERROR", "The game was closed or tabbed out of during the process, the game needs to stay open for it to work.")
def mouseMovedMessage():
    messagebox.showwarning("ERROR", "The mouse was moved so the process was canceled because that could cause errors. Please do not move your mouse till the process is done.")
def loadJSON(path):
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except:
        invalidJsonMessage()
        return None
def isDictValid(reference, dictionary):
    if not isinstance(reference, dict) or not isinstance(dictionary, dict):
        return True # exit out since you can't recurse further into this path 
    if reference.keys() != dictionary.keys():
        return False
    for i in reference:
        if i in ("colorsLinked","tilesLinked"):
            continue
        if not isDictValid(reference[i], dictionary[i]):
            return False # value was found 
    return True
def isGameFocused():
    return win32gui.GetForegroundWindow() == hwnd