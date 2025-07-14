import time
import pydirectinput
import macroHelpers as mh

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
        linkedExportMacro(menu, menu["isLinked"])
        mh.back()
    else: # non linked button menu 
        # recurse into next submenu 
        for nextMenu in menu:
            mh.enter()
            exportMacro(menu[nextMenu])
            mh.down()
        mh.back()
            # down()
def linkedExportMacro(menu, isLinked): 
    """Helper method for exportMacro() - processes the linked menus"""
    for nextMenu in menu:
        if nextMenu == "isLinked":
            continue
        elif isLinked:
            if menu[nextMenu]["linkType"] in ("all", "linked"):
                mh.enter()
                exportMacro(menu[nextMenu]) # use base case to deal with 
        elif not isLinked:
            if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                mh.enter()
                exportMacro(menu[nextMenu]) # use base case to deal with 
        mh.down()
def exportCharacter():
    dict = mh.getDictTemplate()
    openedCorrectly = mh.loadOCR()
    if not openedCorrectly:
        return False
    # reset position
    mh.back()
    mh.enter()
    exportMacro(dict)
    return dict