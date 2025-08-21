import time
import pydirectinput
import macroHelpers as mh
import win32api
import threading

stopRecursion = threading.Event() # if called then the export will be stopped 

def exportCharacter(dict):
    """This method starts the chain of importing a character.
    
    Args:
        data (dict): The dictionary representing all of the values that need to be set. 
    
    Returns:
        bool or dict: If the export completed successfully then the completed dict will be returned. 
            Otherwise False will be returned.
    """
    openedCorrectly = mh.loadOCR()
    if not openedCorrectly:
        return False
    stopRecursion.clear() 
    mh.estimatedFPS = 60
    win32api.SetCursorPos(mh.startingMouseCoord)

    # the thread polls to make sure the user does not do anything that could mess up the export. 
    # If they do, it is caught by the try except statement and the export stops. 
    try:
        thread = threading.Thread(target=checkIfInvalidState)
        thread.start()
        mh.resetMainMenuPos()
        exportMacro(dict)
    except RuntimeError:
        return False
    stopRecursion.set() # ensure polling stops after import is done 
    return dict
def exportMacro(menu):
    """Carries out the macro portion of the export. Recursively goes through all parts of the dict
    and handles each submenu within. 

    Args:
        menu (dict): The current submenu.  
    """
    shouldContinue() 
    if "features" in menu: # if at face detail menu, skip 'similar face' option (not necessary for import)
        mh.inputKey("down")
    if "menu" in menu:
        match menu["menu"]:  # handle the menus where a value is to be set - stops recursion for this path 
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
            if nextMenu == "gender" or menu.get(nextMenu, {}).get("menu") == "sliders" :
                delay = mh.enterDelay
            else:
                delay = 0
            mh.inputKey("e", delay) # enter submenu in game 
            exportMacro(menu[nextMenu]) # handle submenu 
            mh.inputKey("down") # move down for next submenu 
        if "gender" not in menu: # don't go back on final recurse 
            mh.inputKey("q") # exit submenu when done 
def singleLinkedMacro(menu): 
    """ Helper method for exportMacro() - processes the linked menus that has only one linked attribute (only color - not tiles). 
    Reads all values from the page,then decides whether the menu is linked or not depending on whether 
    linked values differ. This means that unecessary values will be read, however the boolean colorsLinked 
    will prevent them from having an impact.

    Args:
        menu (dict): current submenu
    """
    for nextMenu in menu: # read in all values
        if nextMenu == "colorsLinked": # ignore this key as it does not represent a menu 
            continue
        mh.inputKey("e")
        exportMacro(menu[nextMenu]) # handle menu with normal export handling 
        mh.inputKey("down")
    
    # decide value of "colorsLinked"
    linkedValue = None 
    colorsLinked = True # starts as true, will change if not 
    for key in menu: # go through all menus 
        if key == "colorsLinked": # ignore key as it does not represent a menu 
            continue
        # check the unlinked menus only, and if any differ from one another, then it is unlinked. If all are the same, then 
        # it is okay to label this whole menu as linked. 
        if menu[key]["linkType"] == "unlinked": 
            if linkedValue is None: # no value to compare to 
                linkedValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
            else: # check if value matches 
                currentValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
                if currentValue != linkedValue:
                    colorsLinked = False
                    break
    menu["colorsLinked"] = colorsLinked # set value in dictionary 
def doubleLinkedMacro(menu):
    """ Helper method for exportMacro() - processes the linked menus that have two linked attributes (color and tiles). 
    Reads all values from the page,then decides whether the menu is linked or not depending on whether 
    linked values differ. This means that unecessary values will be read, however the boolean colorsLinked 
    will prevent them from having an impact.

    Args:
        menu (dict): current submenu
    """
    for nextMenu in menu: # read in all values 
        if nextMenu in ("tilesLinked","colorsLinked"): # ignore these keys as they do not represent menus 
            continue
        mh.inputKey("e")
        exportMacro(menu[nextMenu]) # handle menu with normal export handling 
        mh.inputKey("down")
    
    # decide value of "colorsLinked" and "tilesLinked"
    colorsValue = None 
    tilesValue = None
    tilesLinked = True
    colorsLinked = True
    for key in menu: # go through all menus 
        if key in ("tilesLinked","colorsLinked"): # ignore these keys as they do not represent menus 
            continue
        # check the unlinked menus only, and if any differ from one another, then it is unlinked. 
        # If all are the same, then it is okay to label this whole menu as linked. 
        if menu[key]["menu"] == "tiles":
            if menu[key]["linkType"] == "unlinked" and tilesLinked: 
                if tilesValue is None: # no value to compare to 
                    tilesValue = menu[key]["value"]
                else:
                    currentValue = menu[key]["value"]
                    if currentValue != tilesValue:
                        tilesLinked = False
        else: # colors menu 
            if menu[key]["linkType"] == "unlinked" and colorsLinked: 
                if colorsValue is None: # no value to compare to 
                    colorsValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
                else:
                    currentValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
                    if currentValue != colorsValue:
                        colorsLinked = False

    menu["tilesLinked"] = tilesLinked # set values in dictionary 
    menu["colorsLinked"] = colorsLinked

def sliderMenu(menu):
    """Reads the values from slider menus and sets them in the dictionary.
    
    Args:
        menu (dict): Specific menu for the current slider menu. The values from the game will be set in here. 
    """
    #mh.updateGameScreen(mh.enterDelay)

    j = 0 
    for i in menu:
        if i != "menu":
            currentNumber = mh.getGameRegion(*mh.sliderRegionsGameScreen[j])
            text = mh.runModel(currentNumber, False)
            menu[i] = text
            j += 1
    mh.inputKey("q", mh.animDelay)

def colorMenu(menu):
    """Reads the values from color menus (rgb menus such as for base skin color) and sets them in the dictionary.
    
    Args:
        menu (dict): Specific menu for the current color menu. The values from the game will be set in here. 
    """
    # similarly to isConfirmed() in inputValidation, I would rather this use the gameScreen capture instead of taking a 
    # screenshot for each, however these regions fall outside the regions of the gameScreen screenshot. I didn't bother
    # changing the bounds and left it here to save myself a lot of work, as the time difference is negligible. 
    menu["blue"] = mh.processRegion(.494,.784,.521,.807, True)
    menu["green"] = mh.processRegion(.494,.738,.521,.761, True)
    menu["red"] = mh.processRegion(.494,.691,.521,.715, True)
    
    mh.inputKey("q")

def dropdownMenu(menu): 
    """Handles reading the values from 'dropdown menus'(in game they are just a few boxes such as age and gender)
    
    Args:
        menu (dict): Specific menu for the current color menu. The values from the game will be set in here. 
    """
    # The gender menu has to be handled slightly differently because there is an additional animation that can 
    # cause missed inputs, as well as there are additional inputs that need to be pressed. 
    isGender = menu["options"][0] == "male" # shows whether or not the menu is the gender one

    if isGender:
        mh.inputKey("left")
        mh.inputKey("e", .05)
        #time.sleep(.1)
        mh.gameScreen.save("testGenderOptions.png")

    numOptions = len(menu["options"])
    menu["value"] = menu["options"][mh.readOptionBox(numOptions)]    
    mh.inputKey("q")


def tileMenu(menu):
    """Reads the value from tile menus (menu with the images such as hair styles) and writes it to dictionary. 
    
    Args: 
        menu (dict): Specific menu for the current tile menu. 
    """
    currentTile = mh.findSelectedTile(menu) - 1 
    menu["value"] = currentTile + 1
    mh.inputKey("q")

def checkIfInvalidState(): 
    """Runs on a separate thread and checks if either the mouse is moved or the game is tabbed out/closed. Both cases
        would mess up the macro, so recursion will stop. Otherwise the program will continue pressing buttons which makes
        it super hard to stop. """
    startPos = win32api.GetCursorPos()
    while not stopRecursion.is_set():
        if not mh.isCursorPosSafe():
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