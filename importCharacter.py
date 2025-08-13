import time
import pydirectinput
import macroHelpers as mh
import threading
import win32api

stopRecursion = threading.Event() # if called then the import will be stopped 


def importCharacter(data):
    """This method starts the chain of importing a character.
    
    Args:
        data (dict): The dictionary representing all of the values that need to be set. 
    
    Returns:
        bool: Whether or not the import was carried out successfully. 
    """
    openedCorrectly = mh.loadOCR() 
    if not openedCorrectly:
        return False
    stopRecursion.clear()

    # the thread polls to make sure the user does not do anything that could mess up the import. 
    # If they do, it is caught by the try except statement and the import stops. 
    try: 
        thread = threading.Thread(target=checkIfInvalidState)
        thread.start()
        mh.inputKey("q") # back then enter resets the position of the in-game cursor for the first menu 
        mh.inputKey("e")
        importMacro(data)
    except RuntimeError: 
        return False
    stopRecursion.set() # ensure polling stops after import is done 
    return True
def importMacro(menu):
    """Carries out the macro portion of the import. Recursively goes through all parts of the dict
    and handles each submenu within. 

    Args:
        menu (dict): The current submenu.  
    """
    shouldContinue()
    if "features" in menu: # if at face detail menu, skip 'similar face' option (not necessary for import)
        mh.inputKey("down")
    if "menu" in menu: # handle the menus where a value is to be set - stops recursion for this path 
        match menu["menu"]: 
            case "dropdown":
                dropdownMenu(menu)
            case "sliders":
                sliderMenu(menu)
            case "colors":
                colorMenu(menu)      
            case "tiles":
                tileMenu(menu)
    # linked menus are handled differently than the rest 
    elif "tilesLinked" in menu: # linked menu with two linked aspects
        doubleLinkedMacro(menu)
        mh.inputKey("q")
    elif "colorsLinked" in menu: # single linked menu 
        singleLinkedMacro(menu)
        mh.inputKey("q")

    else: # non linked button menu 
        # recurse into next submenu 
        for nextMenu in menu:
            if not mh.menuHasValues(menu[nextMenu]): # if there are no values that need to be set from this menu, skip to next 
                mh.inputKey("down")
                continue
            mh.inputKey("e") # enter submenu in game 
            importMacro(menu[nextMenu]) # handle submenu 
            mh.inputKey("down") # move down for next submenu 
        mh.inputKey("q") # exit submenu when done 
def singleLinkedMacro(menu):
    """Helper method for importMacro() - processes the linked menus that only have one linked attribute. 
    
    Args:
        menu (dict): current submenu
    """
    colorsLinked = menu["colorsLinked"] # find out whether menu is linked or not (boolean)
    for nextMenu in menu:
        if nextMenu == "colorsLinked": # ignore this key as it does not represent a menu 
            continue
        if not mh.menuHasValues(menu[nextMenu]): # if there are no values that need to be set from this submenu, skip to next 
                mh.inputKey("down")
                continue
        elif colorsLinked: # decide whether to import if the colors are linked 
            if menu[nextMenu]["linkType"] in ("all", "linked"): 
                mh.inputKey("e")
                importMacro(menu[nextMenu]) # use normal macro to handle
        elif not colorsLinked: # decide whether to import if the colors are not linked 
            if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                mh.inputKey("e")
                importMacro(menu[nextMenu]) 
        mh.inputKey("down") # move down for next submenu 
def doubleLinkedMacro(menu):
    """Helper method for importMacro() - processes the linked menus that have two linked attributes. (color and tiles)

    Args:
        menu (dict): current submenu
    """
    tilesLinked = menu["tilesLinked"] # find out if tiles are linked or not (boolean)
    colorsLinked = menu["colorsLinked"] # find out if colors are linked or not (boolean)
    for nextMenu in menu:
        if nextMenu in ("tilesLinked","colorsLinked"): # ignore these keys as they do not represent menus 
            continue
        if not mh.menuHasValues(menu[nextMenu]): # if there are no values that need to be set from this submenu, skip to next 
                mh.inputKey("down")
                continue
        if menu[nextMenu]["menu"] == "tiles":
            if tilesLinked:
                if menu[nextMenu]["linkType"] in ("all", "linked"): # decide if a value should be set 
                    mh.inputKey("e")
                    importMacro(menu[nextMenu]) # use normal macro to handle
            elif not tilesLinked:
                if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                    mh.inputKey("e")
                    importMacro(menu[nextMenu])
        else: # colors menu
            if colorsLinked:
                if menu[nextMenu]["linkType"] in ("all", "linked"):
                    mh.inputKey("e")
                    importMacro(menu[nextMenu]) 
            elif not colorsLinked:
                if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                    mh.inputKey("e")
                    importMacro(menu[nextMenu]) 
        mh.inputKey("down") # move down for next submenu 

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
    time.sleep(mh.enterDelay)
    for i in range(len(values)): # for all sliders 
        if values[i] != -1: # ignore if user didn't set a value in json
            currentValue = mh.processRegion(*mh.sliderRegions[i], False)
            setVal(values[i],currentValue)

            # if game value does not match the desired one (something went wrong such as missed inputs), 
            # set the slider again till it is correct  
            while True: 
                shouldContinue() # avoid recursion if process is to be stopped 
                currentValue = mh.processRegion(*mh.sliderRegions[i], False)
                if currentValue != values[i]: 
                    print("ERROR")
                    mh.estimatedFPS -= 2
                    setVal(values[i],currentValue)
                else:
                    break
        mh.inputKey("down") # go down to next slider in game 
    # confirm changes and go back 
    mh.inputKey("e")
    mh.inputKey("q", mh.animDelay) 
def setVal(value, startNum):
    """Sets the in-game slider to a specific value.
        
    Args:
        value (int): The value to set the slider to.
        startNum (int): The value that the slider starts at. 
    """
    print("text :", startNum) # DEBUG
 
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
    mh.inputNoScreenshot(direction)
    if (isShift):
        pydirectinput.keyUp('shift')
    mh.waitFrame() # prevent from going so fast you get missed inputs 

def colorMenu(menu):
    """Handles selecting the desired values for color menus (rgb menus such as for base skin color).
    
    Args:
        menu (dict): Specific menu for the current color menu. Contains the values to set the sliders to. 
    """
    colorValues = [menu["red"],menu["green"],menu["blue"]]
    colorSliders(*colorValues)
    mh.inputKey("e")
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
    mh.inputKey("up") # move in-game cursor the correct slider 
    gameValue = mh.processRegion(*region, True)  # gameValue represents the slider's value in-game 
    setVal(value,gameValue)
    while True: # second check to ensure the number in game matches value
            shouldContinue()
            gameValue = mh.processRegion(*region, True) 
            if gameValue != value:
                print("ERROR")
                mh.estimatedFPS -= 2
                setVal(value,gameValue) 
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

    # if menu["value"] == "": # this means the user did not select an option for the json file, so exit out 
    #     if isGender:
    #         time.sleep(.3) # delay so input is not ignored 
    #     mh.inputKey("e") # exit menu 
    #     if isGender:
    #         time.sleep(.2)
    #     return
    
    desiredValue = menu["options"].index(menu["value"]) + 1 # convert value (originally string) to a number 
    numOptions = len(menu["options"])

    if isGender:
        time.sleep(.3)
        mh.inputKey('left')
        mh.inputKey("e", .05)
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
    time.sleep(mh.animDelay) # delay for animation to finish 
    while True: 
        if mh.isSelected(*mh.optionBoxRegions[0], (86,39,11), .05):
            current = 1
            break
        elif mh.isSelected(*mh.optionBoxRegions[1], (86,39,11), .05):
            current = 2
            break
        else: 
            shouldContinue()
            print("DROPDOWN ERROR")
            time.sleep(3) # DEBUG VERY SLOW RIGHT NOW ON PURPOSE 
            twoBoxes(option)
            return
    if (current != option):
        mh.inputKey("down")
    mh.inputKey("e")
def threeBoxes(option):
    """Selects a specific option for a box menu with three options.'
    
    Args:
        option (int): The option to select - 1 is the first box, 2 is second box, 3 is third box
    """
    time.sleep(.05)
    # if none of the options are selected, then try again, this could 
    # possibly be caused from animation where the highlight fades in and out
    while True: 
        if mh.isSelected(*mh.optionBoxRegions[0], (86,39,11), .05):
            current = 1
            break
        elif mh.isSelected(*mh.optionBoxRegions[1], (86,39,11), .05):
            current = 2
            break
        elif mh.isSelected(*mh.optionBoxRegions[2], (86,39,11), .05):
            current = 3
            break
        else: 
            shouldContinue()
            time.sleep(3) # DEBUG VERY SLOW RIGHT NOW ON PURPOSE 
            threeBoxes(option)
            return

    print("current:", current)
    if (current != option):
        steps = option - current 
        if steps > 0:
            for i in range(steps):
                mh.inputKey("down")
        else:
            for i in range(abs(steps)):
                mh.inputKey("up")
    mh.inputKey("e")

def tileMenu(menu):
    """Selects the desired value for a tile menu in game (menu with the images such as hair styles)
    
    Args: 
        menu (dict): Specific menu for the current tile menu. This is used because the other values (folder name) 
            is used for figuring out which tile is selected. 
    """
    if menu["value"] == -1: # if value was not set in json, then ignore 
        mh.inputKey("q")
        return
    tileSet(menu) # set tile 
    mh.inputKey("e") # complete tile selection in game
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
    #time.sleep(5)
    # fix for issue with odd number menus at the bottom 
    if menu["numTiles"] % 2 == 1:
        if int(currentTile/3) == int(menu["numTiles"]/3):
            row = currentTile % 3
            if row == 1:
                mh.inputNoScreenshot("left")
            elif row == 2:
                mh.inputNoScreenshot("left")
                mh.inputNoScreenshot("left")

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

    for i in range(xOffset):
        mh.inputNoScreenshot(xDirection)
    for i in range(yOffset): # set value in game 
        mh.inputNoScreenshot(yDirection)
    

    if stopRecursion.is_set(): # avoid recursion if process is to be stopped 
        return
    mh.waitFrame()
    mh.updateGameScreen()
    if mh.findSelectedTile(menu) - 1 != value: # if game value does not match desired (sign of an error) then attempt to set it again 
        print("ERROR")
        time.sleep(3)
        tileSet(menu)

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