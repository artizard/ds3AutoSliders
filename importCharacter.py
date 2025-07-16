import time
import pydirectinput
import json
import macroHelpers as mh

def adjust(direction, isShift):
    """
    direction: string (left or right),
    isShift: boolean representing whether to increment by 10 or 1 (True is 10) 
    """
    if (isShift):
        pydirectinput.keyDown('shift')
    pydirectinput.press(direction)
    if (isShift):
        pydirectinput.keyUp('shift')
def setVal(value, startNum, confidence):
    print("text :", startNum)
    print("confidence :", confidence)
    if (confidence < .8):
        print("LOW CONFIDENCE - BACKUP METHOD USED")
        time.sleep(10)
        # reset slider
        for i in range(26):
            adjust('left', True)
        startNum = 0
    slideAmount = value - int(startNum)
    print("slideAmount :", slideAmount)
    if (slideAmount < 0):
        direction = 'left'
        slideAmount *= -1
    else:
        direction = 'right'

    # set by 10's
    for i in range((int)(slideAmount/10)):
        adjust(direction, True)
    # set by 1's
    for i in range(slideAmount % 10):
        adjust(direction, False)
def colorSliders(r,g,b):
    mh.up()
    text,confidence = mh.processRegion(.494,.784,.521,.807, True)
    setVal(b,text,confidence)
    mh.up()
    text,confidence = mh.processRegion(.494,.738,.521,.761, True)
    setVal(g,text,confidence)
    mh.up()
    
    text,confidence = mh.processRegion(.494,.691,.521,.715, True)
    setVal(r,text,confidence)
    mh.enter()
def twoBoxes(option):
    """value 1 is the first box, 2 is second """
    time.sleep(.07)
    if mh.isSelected(.439, .301, (86,39,11),.05):
        current = 1
    else:
        current = 2
    print("current:", current)
    if (current == option):
        mh.enter()
    else:
        mh.down()
        mh.enter()
def threeBoxes(option):
    """value 1 is the first box, 2 is second, 3 is third """
    time.sleep(.05)
    if mh.isSelected(.439, .301, (86,39,11),.05):
        current = 1
    elif mh.isSelected(.439, .347, (86,39,11),.05):
        current = 2
    else:
        current = 3
    print("current:", current)
    if (current == option):
        mh.enter()
    else:
        steps = option - current 
        if steps > 0:
            for i in range(steps):
                mh.down()
        else:
            for i in range(abs(steps)):
                mh.up()
        mh.enter()
def tileSet(menu):
    value = menu["value"] - 1 
    currentTile = mh.findSelectedTile(menu) - 1 
    # print("current:",currentTile)
    # print("numTiles:",menu["numTiles"])
    if currentTile == (menu["numTiles"] - 1):
        print("last tile")
        pydirectinput.press('right')
        currentTile = 0

    valueX = value % 3
    valueY = int(value / 3)
    currentTileX = currentTile % 3
    currentTileY = int(currentTile / 3)
    xOffset = valueX - currentTileX
    yOffset = valueY - currentTileY

    if xOffset < 0:
        isxOffsetNegative = True
    else:
        isxOffsetNegative = False
    print("x :", xOffset)
    xOffset = abs(xOffset)
    
    if yOffset < 0:
        isyOffsetNegative = True
    else:
        isyOffsetNegative = False
    print("y :", yOffset)
    yOffset = abs(yOffset)

    for i in range(yOffset):
        #time.sleep(.1)
        if isyOffsetNegative:
            pydirectinput.press('up')
        else:
            pydirectinput.press('down')
    for i in range(xOffset):
        #time.sleep(.1)
        if isxOffsetNegative:
            pydirectinput.press('left')
        else:
            pydirectinput.press('right')

    mh.enter()
def dropdownMenu(menu):
    if menu["options"][0] == "male":
        isGender = True # the gender menu in particular has an animation delay, so we
        # need to only apply the extra delay to that menu. Additonally it requires extra inputs
    else:
        isGender = False
    if menu["value"] == "":
        if isGender:
            time.sleep(.3) # delay so input is not ignored 
        mh.enter() # exit menu  if no value is needed 
        if isGender:
            time.sleep(.2)
        return
    desiredValue = menu["options"].index(menu["value"]) + 1
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
def sliderMenu(menu):
    sliderValues = []
    for i in menu:
        if i != "menu":
            sliderValues.append(int(menu[i]))
    setSliders(sliderValues)
def colorMenu(menu):
    colorValues = [menu["red"],menu["green"],menu["blue"]]
    colorSliders(*colorValues)
def tileMenu(menu):
    if menu["value"] == -1:
        mh.back()
        return
    tileSet(menu)
def importMacro(menu):
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
    elif "isLinked" in menu: # linked button menu 
        linkedImportMacro(menu, menu["isLinked"])
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
def linkedImportMacro(menu, isLinked):
    """Helper method for importMacro() - processes the linked menus"""
    for nextMenu in menu:
        if nextMenu == "isLinked":
            continue
        if not mh.menuHasValues(menu[nextMenu]):
                mh.down()
                continue
        elif isLinked:
            if menu[nextMenu]["linkType"] in ("all", "linked"):
                mh.enter()
                importMacro(menu[nextMenu]) # use base case to deal with 
        elif not isLinked:
            if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                mh.enter()
                importMacro(menu[nextMenu]) # use base case to deal with 
        mh.down()
def importCharacter(jsonPath):
    with open(jsonPath) as f:
        data = json.load(f)
    openedCorrectly = mh.loadOCR()
    if not openedCorrectly:
        return False
    # reset position
    mh.back()
    mh.enter()
    importMacro(data)
    return True
def setSliders(values):
    mh.enterDelay()
    for i in range(len(values)):
        if values[i] != -1: # ignore if user didn't set a value in json
            text,confidence = mh.processRegion(*mh.sliderRegions[i], False)
            setVal(values[i],text,confidence)
        mh.down() # go down regardless 
    mh.enter()
    mh.back()
    mh.animDelay()