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
from inputValidation import InputValidation
import win32api
"""macroHelpers is a module that contains many general helper methods and attributes for 
    the other classes to use."""
# The game can only register 1 input per frame, so the pause is ~1/60 
#pydirectinput.PAUSE = 0.017 
#pydirectinput.PAUSE = 1/59
fileNum = 0
scrollNum = 0

pydirectinput.PAUSE = 0 # handle pausing otherwise 
#lastInputTime = 0 
estimatedFPS = 60
ctypes.windll.user32.SetProcessDPIAware() # fix scaling issues
hwnd = None # represents the dark souls 3 menu 
ocrOpened = False # represents whether or not the onnx models have been prepared yet 
models = {} # holds the three onnx models 
gameScreen = None
# initialize these here instead of every method call 
sct = mss.mss() 
# region of the screenshot in terms of (x,y,w,h)
screenshotRegion = (.061,.149,.453,.705)
animDelay = .325
enterDelay = .3
clientRect = None
rectCoords = None
inputVal = InputValidation()


# This represents the in-game boundaries of each slider on slider menus, coords are in 
# terms of the entire window
sliderRegions = ((.3445,.203,.372,.226),
                     (.3445,.285,.372,.308),
                     (.3445,.366,.372,.389),
                     (.3445,.448,.372,.471),
                     (.3445,.529,.372,.552),
                     (.3445,.610,.372,.633),
                     (.3445,.692,.372,.715),
                     (.3445,.773,.372,.796))

sliderRegionsGameScreen = ((0.6258,0.0766,0.6865,0.1092),
                           (0.6258,0.1929,0.6865,0.2255),
                           (0.6258,0.3078,0.6865,0.3404),
                           (0.6258,0.4241,0.6865,0.4567),
                           (0.6258,0.5390,0.6865,0.5716),
                           (0.6258,0.6539,0.6865,0.6865),
                           (0.6258,0.7702,0.6865,0.8028),
                           (0.6258,0.8851,0.6865,0.9177))
buttonSelectRegions = ((0.1748,0.0930),(0.1748,0.1590),(0.1748,0.2240),(0.1748,0.2901),
                                    (0.1748,0.3560),(0.1748,0.4210),(0.1748,0.4871),(0.1748,0.5530),
                                    (0.1748,0.6180),(0.1748,0.6841),(0.1748,0.7501))

# This represents the in-game coordinates for each tile on the tile(image) menus, coords are in
# terms of the gameScreen screenshot.
tileCoords = [(0.4448,0.1078), (0.6219,0.1078), (0.8000,0.1078), 
              (0.4448,0.3074), (0.6219,0.3074), (0.8000,0.3074), 
              (0.4448,0.5006), (0.6219,0.5006), (0.8000,0.5006), 
              (0.4448,0.6949), (0.6219,0.6949), (0.8000,0.6949), 
              (0.4448,0.8852), (0.6219,0.8852), (0.8000,0.8852),]
sliderSelectRegions = ((0.1801,0.1128),(0.1801,0.2279),(0.1801,0.3443),(0.1801,0.4594),
                                    (0.1801,0.5748),(0.1801,0.6909),(0.1801,0.8052),(0.1801,0.9214))
safeMouseRange = None
startingMouseCoord = None

# This represents the in-game coordinates for the option box menus (such as age). The coordinates
# are specifically in a good place for the program to detect which is selected by color. Coords
# are in terms of the gameScreen screenshot 
optionBoxRegions = ((0.8344,0.2156), (0.8344,0.2809), (0.8344,0.3475)) 

# This is used for the tile (image) menus. This is used to figure out what tile is selected - 
# by seeing how far down the scroll bar is (different amount per each menu due to different sizes)
# you can ascertain which tile is currently selected. 
tileScrollAmounts = {"hair":.1184,"brow":.1582,"beard":0,"eyelashes":0,"tattoo":.0596, "pupil": 0} 
def inputKey(key, delay=0):
    """Presses the key specified by the arg as well as updates the screenshot"""
    #global lastInputTime
    #timeSinceInput = time.perf_counter() - lastInputTime
    #sleepLeft = (1/estimatedFPS) - timeSinceInput
    #print("sleep left:", sleepLeft)
    #if sleepLeft > 0:
    #    time.sleep(sleepLeft)
    if inputVal.menu == "NONE":
        updateGameScreen()
        inputVal.inputRegistered("0") # initialize values 
    print("key:", key)
    pydirectinput.keyDown(key)
    #time.sleep(.02)
    waitFrame()
    #time.sleep(.1)
    pydirectinput.keyUp(key)
    waitFrame()
    #waitFrame()
    #time.sleep(.01)
    
    time.sleep(delay)
    updateGameScreen()
    if not inputVal.inputRegistered(key):
        print("frame not updated")
        lowerEstimatedFps()
        waitFrame()
        waitFrame()
        waitFrame()
        waitFrame()
        waitFrame()
        waitFrame()
        updateGameScreen()
        if not inputVal.inputRegistered(key):
            print("INPUT MISSED")
            global estimatedFPS
            lowerEstimatedFps()
            print("CURRENT ESTIMATED FPS:", estimatedFPS)
            inputKey(key, delay)
    
    #lastInputTime = time.perf_counter()
    
def scrollDown(times):
    """Simulates scrolling down in game a specified amount of times.
    
    Args:
        times (int): Number of times to scroll down. 
    """
    for i in range(times):
        inputKey("down")
# def animDelay():
#     """Stalls program to allow for certain animations in game to finish. Without this, inputs
#     during the animation will be ignored, causing massive issues."""
#     time.sleep(.25) #.2 might be fine?
# def enterDelay():
#     """Stalls program to allow for certain animations in game to finish. Without this, inputs
#     during the animation will be ignored, causing massive issues."""
#     time.sleep(.3)
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
    # w,h = gameScreen.size
    # x = int(x * w) # convert to pixel coordinates 
    # y = int(y * h)

    #point = getGamePoint(x,y)
    r,g,b = getGamePoint(x,y)
    # for all pixels in point 
    # for i in range(3):
    #     for j in range(3):
    #         r,g,b = point.getpixel((i,j))
    #         current = isColor(r,g,b,desiredColor,tolerance) 
    #         print(current)
    #         if current:
    #             print("FINAL : TRUE")
    #             return True

    #print("FINAL : FALSE")
    return isColor((r,g,b),desiredColor,tolerance) 
def isColor(color, desiredColor, tolerance, mode=0):
    """This is a helper method for isSelected that checks whether the game's color is close enough to the desired color. It checks
    this using different metrics - hue, saturation, and lightness.
    
    Args:
        x (float): x coordinate represented as float from 0 to 1.
        y (float): y coordinate represented as float from 0 to 1.
        desiredColor (tuple[int, int, int]): The RGB color that represents a box being selecting. 
        tolerance (float): How close the in-game color has to be to desiredColor to be labeled as selected.
        mode (int): Which mode to compare with. 0 = hue, 1 = lightness, 2 = saturation
    
    Returns:
        bool: Represents whether or not the box at the coordinate is selected. 
    """
    # Checking difference in hue works better than rgb because the color's brightness is variable due to the animation in-game. 
    #print("actual color:", color)
    actualAttribute = colorsys.rgb_to_hls(color[0]/255,color[1]/255,color[2]/255)[mode] 
    desiredAttribute = colorsys.rgb_to_hls(desiredColor[0]/255,desiredColor[1]/255,desiredColor[2]/255)[mode]
    #print("actual:", actualAttribute, "| desired:", desiredAttribute)
    if abs(desiredAttribute - actualAttribute) < tolerance:
        return True
    else:
        return False

def loadModel(key, path):
    """Loads the models and stores them in the models dictionary to avoid an unecessary
    number of variables.
    
    Args:
        key (str): name used to access particular model
        path (str): path to the model
    """
    model = ort.InferenceSession(path)
    input_name = model.get_inputs()[0].name
    models[key] = {"model":model,
                  "input_name":input_name}
def loadOCR():
    """Loads certain things and does some checks before starting an import or export. 
    Loads the onnx ocr models as well as ensures the game is correctly opened. This method
    also waits a few seconds, allowing the user time to open up the game. 
    
    Returns:
        bool: Whether or not the everything was loaded correctly. 
    """
    # This is done regardless of whether ocr has already been opened because if ocr is opened then the game is closed and reopened,
    # then the hwnd will no longer be correct. By doing it every time you avoid that scenario. 
    # Additionally make sure the window location updates if necessary. 
    
    waitTime = 3
    global ocrOpened
    if ocrOpened:
        time.sleep(waitTime)
        initializeDimensions() # important to do after sleep in case user moves window during sleep 
        if not checkIfGameIsOpen():
            notOpenedMessage()
            return False
        return True
    
    startFullscreenWait = time.time()
    print("starting fullscreen wait")

    loadModel("slider","assets/models/sliderValueDetect.onnx")
    loadModel("color","assets/models/colorValueDetect.onnx")
    loadModel("gameOpen","assets/models/gameOpenDetect.onnx")

    endFullscreenWait = time.time()
    timeLeftToWait = waitTime - (endFullscreenWait-startFullscreenWait)
    if (timeLeftToWait > 0):
        time.sleep(timeLeftToWait)
    initializeDimensions()
    if not checkIfGameIsOpen() or hwnd == 0:
        notOpenedMessage()
        return False
    ocrOpened = True
    return True
def initializeDimensions():
    global hwnd 
    global clientRect
    global rectCoords 
    global safeMouseRange
    global startingMouseCoord
    hwnd = win32gui.FindWindow(None, "DARK SOULS III")
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))
    safeMouseRange = (int(clientRect[2] * .043 + rectCoords[0]), 
                      int(clientRect[3] * .135 + rectCoords[1]), 
                      int(clientRect[2] * .742 + rectCoords[0]), 
                      int(clientRect[3] * .86 + rectCoords[1]))
    startingMouseCoord = (int(clientRect[2] * .888 + rectCoords[0]),int(clientRect[3] * .492 + rectCoords[1]))
def checkIfGameIsOpen():
    """Checks if not only if the game window is open and focused, but uses an onnx
    model to ensure that the game is opened to the correct menu.
    
    Returns:
        bool: Whether or not the game is open correctly."""
    if not isGameFocused():
        return False
    
    # Get the correct coordinates, adjusting for windowposition on screen 
    x,y,x2,y2 = (.0469,.1333,.4992,.7153)
    left = int(rectCoords[0] + x * clientRect[2])
    top = int(rectCoords[1] + y * clientRect[3])
    width = int((x2-x) * clientRect[2])
    height = int((y2-y) * clientRect[3])

    mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
    screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
    resized = ImageOps.fit(screenshot, (290, 210), method=Image.LANCZOS, centering=(0.5, 0.5))
    imageArray = np.array(resized).astype(np.float32)
    imageArray = imageArray.reshape(1, 210, 290, 3)

    outputs = models["gameOpen"]["model"].run(None, {models["gameOpen"]["input_name"]: imageArray})
    prob = outputs[0][0]
    if prob != 0 or prob != 1:
        print("GAME OPEN PROB:", prob)
    if prob > .5:
        return True # correct menu open
    else:
        return False # game not open/focused or incorrect menu 
def processRegion(x,y,x2,y2, isColor):
    """Uses an onnx model to detect the number at the specified coordinates. This uses
    two different but similar models for the color slider page, and the normal slider pages.
    These models were created with tensorflow (keras) and have 256 classes each, 1 per number.
      
    Args:
        x (float): the coordinate (from 0 to 1 to be resolution independent) 
            of the left side of the box
        y (float): the coordinate of the top side of the box
        x2 (float): the coordinate of the right side of the box
        y2 (float): the coordinate of the bottom side of the box
        isColor (bool): represents whether to use slider or color onnx model 
    
    Returns:
        int: the number detected
    """

    # Get the correct coordinates, adjusting for window position on screen 
    left = int(rectCoords[0] + x * clientRect[2])
    top = int(rectCoords[1] + y * clientRect[3])
    width = int((x2-x) * clientRect[2])
    height = int((y2-y) * clientRect[3])

    mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
    screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
    return runModel(screenshot, isColor)
    
def runModel(screenshot, isColor):
    screenshot = ImageOps.grayscale(screenshot)

    resized = ImageOps.fit(screenshot, (35, 17), method=Image.LANCZOS, centering=(0.5, 0.5))
    imageArray = np.array(resized).astype(np.float32)
    imageArray = imageArray.reshape(1, 17, 35, 1)

    if isColor:
        outputs = models["color"]["model"].run(None, {models["color"]["input_name"]: imageArray})
        probs = outputs[0]
    else:
        outputs = models["slider"]["model"].run(None, {models["slider"]["input_name"]: imageArray})
        probs = outputs[0]

    answer = np.argmax(probs[0])
    return int(answer)

def saveFile(filePath, data):
    """Saves dict to file path as json.
    
    Args:
        filePath: The path to save to.
        data (dict): The data to save. 
    """
    def stripNewLine(m):
        """Gets rid of \n characters as well as the extra spaces - formatting for readability"""
        values = m.group(1)
        strippedValues = re.sub(r'\n\s*', '', values)
        return f'"options": [{strippedValues}],'
    jsonString = json.dumps(data, indent=3)
    jsonString = re.sub(r'"options":\s\[(.*?)\],', stripNewLine, jsonString, flags=re.DOTALL)
    with open(filePath, "w") as f:
        f.write(jsonString)
def menuHasValues(menu):
    """Recursive method that determines whether or not the children of the dict have any
    values set by the user. -1 and '' represent an unset value. This is used to avoid going 
    through unecessary menus when importing. 
    
    Args:
        menu (dict): The dictionary to check.

    Returns:
        bool: If the dictionary contains user set values. 
    """
    if "menu" in menu: # if page with values (not a buttons page)
        for i in menu:
            if i not in ("menu", "options", "colorsLinked", 
                         "linkType", "numTiles", "folder", "tilesLinked"
                         ) and menu[i] not in (-1, ""): # ignore keys that don't represent values
                return True # value is set 
        return False # since it wasn't returned, then no value is set 
    for i in menu: # if buttons page (not a page with values) then recurse 
        if i in ("colorsLinked","tilesLinked"): # ignore keys that don't represent values 
            continue
        if menuHasValues(menu[i]): # traverse into next submenu 
            return True # value was found 
    return False
def findSelectedTile(menu):
    """Finds the selected tile on a tile menu (such as hair or tattoo). 
    
    Args:
        menu (dict): Contains information on which particular tile menu it is.

    Returns:
        int: The currently selected title. 
    """
    page = findTilePage(menu)
    tile = currentTileOnPage()
    print(f"page:{page} tile:{tile}")
    if page and tile: # if not null 
        return tile + (page-1)*3  
def findTilePage(menu):
    """Finds which page the current tile menu is on. What I mean by this, is when you
    scroll down and the tiles shift up, that is the next 'page'. So with the scroll bar
    all the way up it is the 1st page, and the scroll bar at the bottom it is the last page.
    This is used to ascertain the tile selected.
    
    Args:
        menu (dict): Contains information on which particular tile menu it is.

    Returns:
        int: The current page number of the tile menu. 
    """
    specificMenu = menu["folder"]
    scrollAmount = tileScrollAmounts[specificMenu]
    if scrollAmount == 0: # page without scrollbar, so there is only 1 page
        return 1
    sliderPos = 0.0258 # first possible scroll bar position 
    pageNum = 1
    scrollBottom = .832 # position of the bottom of where the scroll bar can go 
    while sliderPos < scrollBottom:
        if isSelected(.9764, sliderPos, (131,91,31), .05):
            return pageNum
        sliderPos += scrollAmount
        pageNum += 1
    # failsafe
    # print("ERROR: no slider found")
    # time.sleep(.1)
    # return findTilePage(menu) # recurse and try again 
    fatalErrorMessage()
    return -1
def currentTileOnPage():
    """Finds which tile is currently selected on the current page (1-15), does 
    not account for the scroll bar pages - so if it is in the 3rd position, it will return 3 
    regardless of page number.  
    
    Returns: 
        int: Current tile on page. 
    """
    j = 1
    for i in tileCoords:
        if isSelected(*i, (86,39,11),.05):
            return j
        j +=1
    # call again if none found - this could cause an infinite loop but that shouldn't be a real issue 
    time.sleep(.1)
    print("none found")
    updateGameScreen()
    return currentTileOnPage()
def notOpenedMessage():
    """Shows dialog box message for the scenario where the game was not 
    opened/was opened to wrong menu"""
    messagebox.showwarning("ERROR", "The game was either not opened, or was opened to the wrong menu.")
def invalidJsonMessage():
    """Shows dialog box message for the scenario where the json file chosen was invalid."""
    messagebox.showwarning("ERROR", "The file you chose is invalid. This is likely due to it not being a json file, or it having invalid json syntax.")
def gameClosedMesage():
    """Shows dialog box message for the scenario where the user closes the game mid import/export."""
    messagebox.showwarning("ERROR", "The game was closed or tabbed out of during the process, the game needs to stay open for it to work.")
def fatalErrorMessage():
    """Shows dialog box message for errors such as when a method is unable to read part of the game screen."""
    messagebox.showwarning("FATAL ERROR", "Something went wrong, try changing your resolution or brightness in game.")
def mouseMovedMessage():
    """Shows dialog box message for the scenario where the user moves the mouse mid import/export."""
    messagebox.showwarning("ERROR", "The mouse was moved so the process was canceled because that could cause errors. Please do not move your mouse till the process is done.")
def loadJSON(path):
    """Loads a json as a dictionary, then returns it.
    
    Args:
        path (str): The path to the json file that will be opened. 

    Returns:
        dict or None: Returns the dictionary version of the json, or None if the json was invalid. 
    """
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except:
        invalidJsonMessage()
        return None
def isDictValid(reference, dictionary):
    """Recursive method that checks if a dictionary has all of the same keys as the template
    dictionary. If the keys are different then the structure of the menus will be messed up,
    so this ensures that the JSON file is valid for this program. 
    
    Args:
        reference (dict) or (other): Either a dictionary representing how the keys should be,
            or another data type representing the current value in the traversal  (end of this path). 
        dictionary (dict) or (other): The dictionary to check the validity of, or the current value
            in the traversal (end of this path). 
    
    Returns: 
        bool: Whether or not the dictionary is valid. 
    """
    # If the 
    if not isinstance(reference, dict) or not isinstance(dictionary, dict):
        return True 
    if reference.keys() != dictionary.keys(): # mismatch between dicts 
        return False
    for i in reference:
        # Ignore these keys as they are not dictionaries so they can't be traversed 
        if i in ("colorsLinked","tilesLinked"): 
            continue
        if not isDictValid(reference[i], dictionary[i]): # recurse further 
            return False 
    return True # returns true if False didn't get return before 
def isGameFocused():
    """Checks whether the game is focused or not.
    
    Returns:
        bool: Whether or not the window is focused. 
    """
    return win32gui.GetForegroundWindow() == hwnd
def getGameRegion(x,y,x2,y2):
    w,h = gameScreen.size
    x = int(x * w) 
    y = int(y * h)
    x2 = int(x2 * w) 
    y2 = int(y2 * h)
    return gameScreen.crop((x,y,x2,y2))
def getGamePoint(x,y):
    """Returns the pixels closest to that point."""
    w,h = gameScreen.size
    x = int(x*w)
    y = int(y*h)

    # global scrollNum
    # gameScreen.crop((x-10,y-10,x+11,y+11)).save(f"scrollImages/scroll{scrollNum}.png")
    # scrollNum += 1

    return gameScreen.getpixel((x,y))
def updateGameScreen(delay=0):

    left = int(rectCoords[0] + screenshotRegion[0] * clientRect[2])
    top = int(rectCoords[1] + screenshotRegion[1] * clientRect[3])
    width = int(screenshotRegion[2] * clientRect[2])
    height = int(screenshotRegion[3] * clientRect[3])

    time.sleep(delay)
    mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
    global gameScreen
    gameScreen = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
    global fileNum
    fileNum += 1
    #gameScreen.save(f"debugImages/debug{fileNum}.png")
def waitFrame():
    time.sleep(1/estimatedFPS)
def inputNoScreenshot(key):
    pydirectinput.keyDown(key)
    waitFrame()
    pydirectinput.keyUp(key)
    waitFrame()
def readOptionBox(numOptions):
    """Reads the value of 
    
    Args:
        numOption (int): Number of options in the menu. 

    Returns:
        int: the index of the option selected (zero-indexed)
    """
    #time.sleep(mh.enterDelay())
    #mh.waitFrame()
    # if none of the options are selected, then try again, this could 
    # possibly happen from animation where the highlight fades in and out
    # while True: 
    current = None
    for i in range(numOptions): # check each option box and see which is selected 
        if isSelected(*optionBoxRegions[i], (86,39,11), .05):
            current = i
            break
    # if current is not None: # end if selected option has been found 
    #     break
    # else:
    # loops because it didn't detect any selected boxes 
        # shouldContinue()
        # mh.updateGameScreen()
        # print("NONE DETECTED")
        # time.sleep(1) # DEBUG VERY SLOW RIGHT NOW ON PURPOSE 
        # current = -1
        #print("ERROR ERROR ERROR")
    if current is None:
        fatalErrorMessage()
    return current
def lowerEstimatedFps():
    global estimatedFPS
    if estimatedFPS < 10:
        print("CANNOT DECREMENT FPS FURTHER")
        return
    estimatedFPS -= 3
def findSelectedSlider():
    selected = -1
    j = 1
    for i in sliderSelectRegions:
        if isSelected(*i, (240,96,0), .1):
            selected = j
            break
        j += 1
    if selected == -1:
        fatalErrorMessage()
    return selected
def findSelectedButton():
    selected = -1
    j = 1
    for i in buttonSelectRegions:
        if isSelected(*i, (240,96,0), .1):
            selected = j
            break
        j += 1
    return selected
def resetMainMenuPos():
    updateGameScreen()
    currentSelection = findSelectedButton()
    print("CURRENT :", currentSelection)
    if currentSelection < 7:
        for _ in range(currentSelection - 1):
            inputKey("up")
    else:
        for _ in range(12 - currentSelection):
            inputKey("down")
def isCursorPosSafe():
    x,y = win32api.GetCursorPos()
    return (
        x < safeMouseRange[0] or 
        x > safeMouseRange[2] or 
        y < safeMouseRange[1] or 
        y > safeMouseRange[3]
    )
