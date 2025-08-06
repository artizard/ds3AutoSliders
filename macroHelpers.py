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
"""macroHelpers is a module that contains many general helper methods and attributes for 
    the other classes to use."""
# The game can only register 1 input per frame, so the pause is ~1/60 
pydirectinput.PAUSE = 0.017 
ctypes.windll.user32.SetProcessDPIAware() # fix scaling issues
hwnd = None # represents the dark souls 3 menu 
ocrOpened = False # represents whether or not the onnx models have been prepared yet 
models = {} # holds the three onnx models 

# This represents the in-game boundaries of each slider on slider menus 
sliderRegions = ((.3445,.203,.372,.226),
                     (.3445,.285,.372,.308),
                     (.3445,.366,.372,.389),
                     (.3445,.448,.372,.471),
                     (.3445,.529,.372,.552),
                     (.3445,.610,.372,.633),
                     (.3445,.692,.372,.715),
                     (.3445,.773,.372,.796))

# This represents the in-game coordinates for each tile on the tile(image) menus
tileCoords = [(.2625,.225),(.3427,.225),(.4234,.225),
              (.2625,.3657),(.3427,.3657),(.4234,.3657),
              (.2625,.5019),(.3427,.5019),(.4234,.5019),
              (.2625,.6389),(.3427,.6389),(.4234,.6389),
              (.2625,.7731),(.3427,.7731),(.4234,.7731),]

# This represents the in-game coordinates for the option box menus (such as age). The coordinates
# are specifically in a good place for the program to detect which is selected by color. 
optionBoxRegions = ((.439, .301),(.439, .347),(.439, .394)) 

# This is used for the tile (image) menus. This is used to figure out what tile is selected - 
# by seeing how far down the scroll bar is (different amount per each menu due to different sizes)
# you can ascertain which tile is currently selected. 
tileScrollAmounts = {"hair":.0835,"brow":.1115,"beard":0,"eyelashes":0,"tattoo":.042, "pupil": 0} 

def enter():
    """Presses the 'e' key to simulate entering a menu in game."""
    pydirectinput.press('e')
def back():
    """Presses the 'q' key to simulate going back a menu in game."""
    pydirectinput.press('q')
def down():
    """Presses the 'down' key to simulate moving the selection down in game."""
    pydirectinput.press('down')
def up():
    """Presses the 'up' key to simulate moving the selection up in game."""
    pydirectinput.press('up')
def scrollDown(times):
    """Simulates scrolling down in game a specified amount of times.
    
    Args:
        times (int): Number of times to scroll down. 
    """
    for i in range(times):
        down()
def animDelay():
    """Stalls program to allow for certain animations in game to finish. Without this, inputs
    during the animation will be ignored, causing massive issues."""
    time.sleep(.25) #.2 might be fine?
def enterDelay():
    """Stalls program to allow for certain animations in game to finish. Without this, inputs
    during the animation will be ignored, causing massive issues."""
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
def loadModel(key, path):
    """Loads the models and stores them in the models dictionary to avoid an unecessary
    number of variables.
    
    Args:
        key (str): name used to access particular model
        path (str): path to the model
    """
    model = ort.InferenceSession(path)
    input_name = model.get_inputs()[0].name
    model[key] = {"model":model,
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
    global hwnd 
    hwnd = win32gui.FindWindow(None, "DARK SOULS III")

    global ocrOpened
    if ocrOpened:
        print("OCR already opened")
        
        time.sleep(5)
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
    timeLeftToWait = 5 - (endFullscreenWait-startFullscreenWait)
    if (timeLeftToWait > 0):
        time.sleep(timeLeftToWait)

    if not checkIfGameIsOpen() or hwnd == 0:
        notOpenedMessage()
        return False
    ocrOpened = True
    return True
def checkIfGameIsOpen():
    """Checks if not only if the game window is open and focused, but uses an onnx
    model to ensure that the game is opened to the correct menu.
    
    Returns:
        bool: Whether or not the game is open correctly."""
    if not isGameFocused():
        return False
    
    # Get the correct coordinates, adjusting for windowposition on screen 
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
        float: the confidence value for the answer (0 to 1)
    """

    # Get the correct coordinates, adjusting for window position on screen 
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

    if isColor:
        outputs = models["color"]["model"].run(None, {models["color"]["input_name"]: imageArray})
        probs = outputs[0]
    else:
        outputs = models["slider"]["model"].run(None, {models["slider"]["input_name"]: imageArray})
        probs = outputs[0]

    answer = np.argmax(probs[0])
    confidence = probs[0][answer]
    
    return int(answer), confidence
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
    
    sliderPos = .167 # first possible scroll bar position 
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
    return findTilePage(menu) # recurse and try again 
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