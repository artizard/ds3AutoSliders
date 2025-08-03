import time
import pydirectinput
import json
import macroHelpers as mh
import random
import threading
import win32api

stopRecursion = threading.Event()
optionBoxRegions = ((.439, .301),(.439, .347),(.439, .394)) 

def sliderMenu(menu):
    """Handles selecting the desired values for slider menus.
    
    Args:
        menu (dict): Specific menu for the current slider menu. Contains the values to set the sliders to. 
    """
    sliderValues = [] # turn the values from the dict into a list
    for i in menu: 
        if i != "menu":
            sliderValues.append(int(menu[i]))
    setSliders(sliderValues) # use helper method to actually set them
def setSliders(values):
    """Sets the in-game sliders to the argument values. The number of slider to set is variable.

    Args:
        values (list[int]): Each value in the list represents a slider to set to its respective value. 
    """
    mh.enterDelay()
    for i in range(len(values)): # for all sliders 
        if values[i] != -1: # ignore if user didn't set a value in json
            currentValue,confidence = mh.processRegion(*mh.sliderRegions[i], False)
            setVal(values[i],currentValue,confidence)

            # if game value does not match the desired one (something went wrong such as missed inputs), 
            # set the slider again till it is correct  
            while True: 
                shouldContinue() # avoid recursion if process is to be stopped 
                currentValue, confidence = mh.processRegion(*mh.sliderRegions[i], False)
                if currentValue != values[i]: 
                    print("ERROR")
                    setVal(values[i],currentValue,confidence)
                else:
                    break
        mh.down() # go down to next slider in game 
    # confirm changes and go back 
    mh.enter()
    mh.back()
    mh.animDelay() 
def setVal(value, startNum, confidence):
    """Sets the in-game slider to a specific value.
        
    Args:
        value (int): The value to set the slider to.
        startNum (int): The value that the slider starts at. 
        confidence (float): The confidence on the startNum from the model. 
    """
    print("text :", startNum, "| confidence :", confidence) # DEBUG
 
    slideAmount = value - startNum 
    # determine direction, and ensure slideAmount is positive 
    if (slideAmount < 0):
        direction = 'left'
        slideAmount *= -1
    else:
        direction = 'right'

    # SlideAmount is processed using shift+left/right then without shif. This is the fastest way to move the slider. 
    # set by 10's
    for i in range(int(slideAmount/10)):
        shouldContinue()
        adjust(direction, True)
    # set by 1's
    for i in range(slideAmount % 10):
        shouldContinue()
        adjust(direction, False)
def adjust(direction, isShift):
    """Adjusts the in-game slider by 1/10 in the desired direction (helper method for setVal).

    Args:
        direction (str): Can be either 'left' or 'right' representing the direction to move.
        isShift (bool): Represents whether to hold shift (increment by 10 or 1 (True is 10)). 
    """
    if (isShift):
        pydirectinput.keyDown('shift')
    pydirectinput.press(direction)
    if (isShift):
        pydirectinput.keyUp('shift')

def colorMenu(menu):
    """Handles selecting the desired values for color menus (rgb menus such as for base skin color).
    
    Args:
        menu (dict): Specific menu for the current color menu. Contains the values to set the sliders to. 
    """
    colorValues = [menu["red"],menu["green"],menu["blue"]]
    colorSliders(*colorValues)
    mh.enter()
def colorSliders(r,g,b):
    """Sets the in-game sliders to the argument values. This is done in reverse order due to the game ui (to make it faster).

    Args:
        r (int): The value to set the red slider to.
        g (int): The value to set the green slider to.
        b (int): The value to set the blue slider to.
    """
    setColorSlider(b, (.494,.784,.521,.807))
    setColorSlider(g, (.494,.738,.521,.761))
    setColorSlider(r, (.494,.691,.521,.715))
def setColorSlider(value, region):
    """Sets the in-game color slider to a particular value (helper method for colorSliders).

    Args:
        value (int): The value to set the slider to.
        region (tuple[float, float, float, float]): The part of the screen that represents where the 
            current slider is at. This is used for figuring out the slider's starting number. The coordinates
            are expressed as floats from 0 to 1 in order to be resolution independent. 
    """
    shouldContinue()
    mh.up() # move in-game cursor the correct slider 
    gameValue,confidence = mh.processRegion(*region, True)  # gameValue represents the slider's value in-game 
    setVal(value,gameValue,confidence)
    while True: # second check to ensure the number in game matches value
            shouldContinue()
            gameValue, confidence = mh.processRegion(*region, True) 
            if gameValue != value:
                print("ERROR")
                setVal(value,gameValue,confidence) 
            else:
                break

def dropdownMenu(menu):
    """Handles selecting the desired option for 'dropdown menus'(in game they are just a few boxes such as age and gender)
    
    Args:
        menu (dict): Specific menu for the current dropdown menu. Contains not only the desired value, but the 
            dropdown options - this is important becuase it is used to determine whether to handle it like a page 
            with two or three pages. 
    """
    # The gender menu has to be handled slightly differently because there is an additional animation that can 
    # cause missed inputs as well as additional inputs that need to be pressed. 
    isGender = menu["options"][0] == "male" # shows whether or not the menu is the gender one

    if menu["value"] == "": # this means the user did not select an option for the json file, so exit out 
        if isGender:
            time.sleep(.3) # delay so input is not ignored 
        mh.enter() # exit menu 
        if isGender:
            time.sleep(.2)
        return
    
    desiredValue = menu["options"].index(menu["value"]) + 1 # convert value (originally string) to a number 
    numOptions = len(menu["options"])

    if isGender:
        time.sleep(.3)
        pydirectinput.press('left')
        mh.enter()
        time.sleep(.2)
    match numOptions:
        case 2:
            twoBoxes(desiredValue)
        case 3:
            threeBoxes(desiredValue)
def twoBoxes(option):
    """Selects a specific option for a box menu with two options. There are two versions (two and three boxes) of this instead of
        one more generic version because it allows for simpler logic in twoBoxes.
    
    Args:
        option (int): The option to select - 1 is the first box, 2 is second box
    """
    time.sleep(.07) # delay for animation to finish 
    while True: 
        if mh.isSelected(*optionBoxRegions[0], (86,39,11), .05):
            current = 1
            break
        elif mh.isSelected(*optionBoxRegions[1], (86,39,11), .05):
            current = 2
            break
        else: 
            shouldContinue()
            time.sleep(5) # DEBUG VERY SLOW RIGHT NOW ON PURPOSE 
    if (current != option):
        mh.down()
    mh.enter()
def threeBoxes(option):
    """Selects a specific option for a box menu with three options.'
    
    Args:
        option (int): The option to select - 1 is the first box, 2 is second box, 3 is third box
    """
    time.sleep(.05)
    # if none of the options are selected, then try again, this could 
    # possibly be caused from animation where the highlight fades in and out
    while True: 
        if mh.isSelected(*optionBoxRegions[0], (86,39,11), .05):
            current = 1
            break
        elif mh.isSelected(*optionBoxRegions[1], (86,39,11), .05):
            current = 2
            break
        elif mh.isSelected(*optionBoxRegions[2], (86,39,11), .05):
            current = 3
            break
        else: 
            shouldContinue()
            time.sleep(5) # DEBUG VERY SLOW RIGHT NOW ON PURPOSE 

    print("current:", current)
    if (current != option):
        steps = option - current 
        if steps > 0:
            for i in range(steps):
                mh.down()
        else:
            for i in range(abs(steps)):
                mh.up()
    mh.enter()

def tileMenu(menu):
    """Selects the desired value for a tile menu in game (menu with the images such as hair styles)
    
    Args: 
        menu (dict): Specific menu for the current tile menu. This is used because the other values (folder name) 
            is used for figuring out which tile is selected. 
    """
    if menu["value"] == -1: # if value was not set in json, then ignore 
        mh.back()
        return
    tileSet(menu) # set tile 
    mh.enter() # complete tile selection in game
def tileSet(menu): 
    """Sets the in-game tile (menu with images) to a specific value

    Args:
        menu (dict): Specific menu for the current tile menu. This is used because the other values (folder name) 
            is used for figuring out which tile is selected. 
    """
    value = menu["value"] - 1 # value to set to 
    currentTile = mh.findSelectedTile(menu) - 1 # current in-game tile selected
    print("current:", currentTile)
    print("desired:", value)
    # if currentTile == (menu["numTiles"] - 1): NOT NECESSARY??? 
    #     print("last tile")
    #     pydirectinput.press('right')
    #     currentTile = 0
    valueX = value % 3 # find column of desired
    valueY = int(value / 3) # find row 
    currentTileX = currentTile % 3 # find column of current
    currentTileY = int(currentTile / 3)
    xOffset = valueX - currentTileX # find how much x and y should change by to get to desired value 
    yOffset = valueY - currentTileY

    if xOffset < 0: # find which direction to shift 
        xDirection = "left"
    else:
        xDirection = "right"
    xOffset = abs(xOffset)
    
    if yOffset < 0:
        yDirection = "up"
    else:
        yDirection = "down"
    yOffset = abs(yOffset)

    for i in range(yOffset): # set value in game 
        pydirectinput.press(yDirection) 
    for i in range(xOffset):
        pydirectinput.press(xDirection)

    if stopRecursion.is_set(): # avoid recursion if process is to be stopped 
        return
    if mh.findSelectedTile(menu) - 1 != value: # if game value does not match desired (sign of an error) then attempt to set it again 
        tileSet(menu)

def importCharacter(data):
    openedCorrectly = mh.loadOCR()
    if not openedCorrectly:
        return False
    # reset position
    stopRecursion.clear()

    try:
        thread = threading.Thread(target=checkIfInvalidState)
        thread.start()
        mh.back()
        mh.enter()
        importMacro(data)
    except RuntimeError:
        return False
    stopRecursion.set() # ensure mouse polling stops 
    return True
def importMacro(menu):
    if stopRecursion.is_set():
        raise RuntimeError("Invalid game state")
    if "features" in menu: # if at face detail menu, skip similar face option
        mh.down()
    if "menu" in menu:
        match menu["menu"]: # acts as base case/ end of recursion per each path 
            case "dropdown":
                dropdownMenu(menu)
            case "sliders":
                sliderMenu(menu)
            case "colors":
                colorMenu(menu)      
            case "tiles":
                tileMenu(menu)
            case _:
                print("invalid json error")
                quit()
    elif "tilesLinked" in menu: # linked menu with two linked aspects
        doubleLinkedMacro(menu)
        mh.back()
    elif "colorsLinked" in menu: # single linked menu 
        singleLinkedMacro(menu)
        mh.back()
    else: # non linked button menu 
        # recurse into next submenu 
        for nextMenu in menu:
            if not mh.menuHasValues(menu[nextMenu]):
                mh.down()
                continue
            mh.enter()
            importMacro(menu[nextMenu])
            mh.down()
        mh.back()
        
            # down()
def singleLinkedMacro(menu):
    """Helper method for importMacro() - processes the linked menus"""
    colorsLinked = menu["colorsLinked"]
    for nextMenu in menu:
        if nextMenu == "colorsLinked": # ignore this key as it does not represent a menu 
            continue
        if not mh.menuHasValues(menu[nextMenu]):
                mh.down()
                continue
        elif colorsLinked:
            if menu[nextMenu]["linkType"] in ("all", "linked"):
                mh.enter()
                importMacro(menu[nextMenu]) # use base case to deal with 
        elif not colorsLinked:
            if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                mh.enter()
                importMacro(menu[nextMenu]) # use base case to deal with 
        mh.down()
def doubleLinkedMacro(menu):
    """Works simlarly to singleLinkedMacro(), however it has extra checks to accommodate two link types"""
    tilesLinked = menu["tilesLinked"]
    colorsLinked = menu["colorsLinked"]
    for nextMenu in menu:
        if nextMenu in ("tilesLinked","colorsLinked"): # ignore these keys as they do not represent menus 
            continue
        if not mh.menuHasValues(menu[nextMenu]):
                mh.down()
                continue
        if menu[nextMenu]["menu"] == "tiles":
            if tilesLinked:
                if menu[nextMenu]["linkType"] in ("all", "linked"):
                    mh.enter()
                    importMacro(menu[nextMenu]) # use base case to deal with 
            elif not tilesLinked:
                if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                    mh.enter()
                    importMacro(menu[nextMenu]) # use base case to deal with 
        else: # colors menu
            if colorsLinked:
                if menu[nextMenu]["linkType"] in ("all", "linked"):
                    mh.enter()
                    importMacro(menu[nextMenu]) # use base case to deal with 
            elif not colorsLinked:
                if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                    mh.enter()
                    importMacro(menu[nextMenu]) # use base case to deal with 
        mh.down()


def checkIfInvalidState(): 
    """Runs on a separate thread and checks if either the mouse is moved or the game is tabbed out/closed. Both cases
        would mess up the macro, so recursion will stop. Otherwise the program will continue pressing buttons which makes
        it super hard to stop. """
    startPos = win32api.GetCursorPos()
    while not stopRecursion.is_set():
        if win32api.GetCursorPos() != startPos:
            stopRecursion.set()
            mh.mouseMovedMessage()
        elif not mh.isGameFocused():
            stopRecursion.set()
            mh.gameClosedMesage()
        time.sleep(.1)
def shouldContinue():
    """Raises a runtime error if stopRecursion is set. This will be set in scenarios where 
    the user does something that will mess up the import so the import will be stopped early. 

    Raises: 
        RuntimeError: Used as a way to exit the importMacro altogether.
    """
    if stopRecursion.is_set(): # end early if told to
        raise RuntimeError("Invalid game state")