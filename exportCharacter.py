import time
import pydirectinput
import macroHelpers as mh
import win32api
import threading

stopRecursion = threading.Event()

def twoBoxes():
    """value 1 is the first box, 2 is second """
    time.sleep(.07)
    if mh.isSelected(.439, .301, (86,39,11),.05):
        current = 1
    else:
        current = 2
    mh.back()
    return current
def threeBoxes():
    """value 1 is the first box, 2 is second, 3 is third """
    time.sleep(.05)
    if mh.isSelected(.439, .301, (86,39,11),.05):
        current = 1
    elif mh.isSelected(.439, .347, (86,39,11),.05):
        current = 2
    else:
        current = 3
    mh.back()
    return current
def dropdownMenu(menu): # NOT DONE
    if menu["options"][0] == "male":
        isGender = True # the gender menu in particular has an animation delay, so we
        # need to only apply the extra delay to that menu. Additonally it requires extra inputs
    else:
        isGender = False
    numOptions = len(menu["options"])
    if isGender:
        time.sleep(.3)
        pydirectinput.press('left')
        mh.enter()
        time.sleep(.2)
    match numOptions:
        case 2:
            menu["value"] = menu["options"][twoBoxes()-1]
        case 3:
            menu["value"] = menu["options"][threeBoxes()-1]
def sliderMenu(menu):
    mh.enterDelay()
    j = 0 
    confidence = 0
    for i in menu:
        if i != "menu":
            confidence = 0
            while confidence < .2:
                text, confidence = mh.processRegion(*mh.sliderRegions[j], False)
            menu[i] = int(text)
            j += 1
    mh.back()
    mh.animDelay()
def colorMenu(menu):
    confidence = 0
    while confidence < .75: # ensure confiddence is good 
        text,confidence = mh.processRegion(.494,.784,.521,.807, True)
    menu["blue"] = int(text)
    confidence = 0
    while confidence < .75:
        text,confidence = mh.processRegion(.494,.738,.521,.761, True)
    menu["green"] = int(text)
    confidence = 0
    while confidence < .75:
        text,confidence = mh.processRegion(.494,.691,.521,.715, True)
    menu["red"] = int(text)
    
    mh.back()
def tileMenu(menu):
    currentTile = mh.findSelectedTile(menu) - 1 
    menu["value"] = currentTile + 1
    mh.back()
def exportMacro(menu):
    #time.sleep(1)
    if stopRecursion.is_set():
        mh.mouseMovedMessage()
        raise RuntimeError("Mouse moved")
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
        # if not mh.checkIfGameIsOpen():
        #     raise RuntimeError("Game is no longer open, recursion stopped.")
        if not mh.isGameFocused():
            mh.gameClosedMesage()
            stopRecursion.set()
            raise RuntimeError("Game is no longer open, recursion stopped.")
    elif "tilesLinked" in menu: # linked menu with two linked aspects
        doubleLinkedMacro(menu)
        mh.back()
    elif "colorsLinked" in menu: # single linked menu 
        singleLinkedMacro(menu)
        mh.back()

    else: # non linked button menu 
        # recurse into next submenu 
        for nextMenu in menu:
            mh.enter()
            exportMacro(menu[nextMenu])
            mh.down()
        mh.back()
            # down()
def singleLinkedMacro(menu): 
    """ Helper method for exportMacro() - processes the linked menus that has only one linked aspect (hair). 
        Reads all values from the page,then decides whether the menu is linked or not depending on whether 
        linked values differ. This means that unecessary values will be read, however the boolean colorsLinked 
        will prevent them from having an impact, so I think it's a worthwhile tradeoff for simplicity's sake."""
    for nextMenu in menu: # read in all values 
        if nextMenu == "colorsLinked": # ignore key as it does not represent a menu 
            continue
        mh.enter()
        exportMacro(menu[nextMenu]) # handle menu with normal export handling 
        mh.down()
    
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
            else:
                currentValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
                if currentValue != linkedValue:
                    colorsLinked = False
                    break
    menu["colorsLinked"] = colorsLinked # set value in dictionary 
def doubleLinkedMacro(menu):
    """Works simlarly to singleLinkedMacro(), however it has extra checks to accommodate two link types"""
    for nextMenu in menu: # read in all values 
        if nextMenu in ("tilesLinked","colorsLinked"): # ignore these keys as they do not represent menus 
            continue
        mh.enter()
        exportMacro(menu[nextMenu]) # handle menu with normal export handling 
        mh.down()
    
    colorsValue = None 
    tilesValue = None
    tilesLinked = True
    colorsLinked = True
    for key in menu: # go through all menus 
        if key in ("tilesLinked","colorsLinked"): # ignore these keys as they do not represent menus 
            continue
        # check the unlinked menus only, and if any differ from one another, then it is unlinked. If all are the same, then 
        # it is okay to label this whole menu as linked. 
        if menu[key]["menu"] == "tiles":
            if menu[key]["linkType"] == "unlinked": 
                if tilesValue is None: # no value to compare to 
                    tilesValue = menu[key]["value"]
                else:
                    currentValue = menu[key]["value"]
                    if currentValue != tilesValue:
                        tilesLinked = False
        else: # colors menu 
            if menu[key]["linkType"] == "unlinked": 
                if colorsValue is None: # no value to compare to 
                    colorsValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
                else:
                    currentValue = (menu[key]["red"], menu[key]["green"], menu[key]["blue"])
                    if currentValue != colorsValue:
                        colorsLinked = False
    menu["tilesLinked"] = tilesLinked
    menu["colorsLinked"] = colorsLinked
def exportCharacter(dict):
    openedCorrectly = mh.loadOCR()
    if not openedCorrectly:
        return False
    # reset position
    stopRecursion.clear()

    try:
        thread = threading.Thread(target=checkIfMouseMoves)
        thread.start()
        mh.back()
        mh.enter()
        exportMacro(dict)
    except RuntimeError:
        return False
    stopRecursion.set()
    return dict
def checkIfMouseMoves():
    startPos = win32api.GetCursorPos()
    while not stopRecursion.is_set():
        if win32api.GetCursorPos() != startPos:
            stopRecursion.set()
        time.sleep(.5)
