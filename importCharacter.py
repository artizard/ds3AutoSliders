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
    if (value > 255 or value < 0):
        print("error")
        return
    if (confidence < .5):
        print("LOW CONFIDENCE - BACKUP METHOD USED")
        time.sleep(2)
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
def threeSliders(a,b,c): 
    text,confidence = mh.processRegion(.343,.203,.372,.226, True)
    setVal(a,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.285,.372,.307, True)
    setVal(b,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.366,.372,.389, True)
    setVal(c,text,confidence)
    mh.enter()
    mh.back()
    mh.animDelay()
def fourSliders(a,b,c,d):
    text,confidence = mh.processRegion(.343,.203,.372,.226, True)
    setVal(a,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.285,.372,.307, True)
    setVal(b,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.366,.372,.389, True)
    setVal(c,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.448,.372,.470, True)
    setVal(d,text,confidence)
    mh.enter()
    mh.back()
    mh.animDelay()
def fiveSliders(a,b,c,d,e):
    text,confidence = mh.processRegion(.343,.203,.372,.226, True)
    setVal(a,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.285,.372,.307, True)
    setVal(b,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.366,.372,.389, True)
    setVal(c,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.448,.372,.470, True)
    setVal(d,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.529,.372,.552, True)
    setVal(e,text,confidence)
    mh.enter()
    mh.back()
    mh.animDelay()
def sixSliders(a,b,c,d,e,f):
    text,confidence = mh.processRegion(.343,.203,.372,.226, True)
    setVal(a,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.285,.372,.307, True)
    setVal(b,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.366,.372,.389, True)
    setVal(c,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.448,.372,.470, True)
    setVal(d,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.529,.372,.552, True)
    setVal(e,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.610,.372,.633, True)
    setVal(f,text,confidence)
    mh.enter()
    mh.back()
    mh.animDelay()
def sevenSliders(a,b,c,d,e,f,g):
    text,confidence = mh.processRegion(.343,.203,.372,.226, True)
    setVal(a,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.285,.372,.307, True)
    setVal(b,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.366,.372,.389, True)
    setVal(c,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.448,.372,.470, True)
    setVal(d,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.529,.372,.552, True)
    setVal(e,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.610,.372,.633, True)
    setVal(f,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.692,.372,.715, True)
    setVal(g,text,confidence)
    mh.enter()
    mh.back()
    mh.animDelay()
def eightSliders(a,b,c,d,e,f,g,h):
    text,confidence = mh.processRegion(.343,.203,.372,.226, True)
    setVal(a,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.285,.372,.307, True)
    setVal(b,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.366,.372,.389, True)
    setVal(c,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.448,.372,.470, True)
    setVal(d,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.529,.372,.552, True)
    setVal(e,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.610,.372,.633, True)
    setVal(f,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.692,.372,.715, True)
    setVal(g,text,confidence)
    mh.down()
    text,confidence = mh.processRegion(.343,.773,.372,.796, True)
    setVal(h,text,confidence)
    mh.enter()
    mh.back()
    mh.animDelay()
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
    if mh.isSelected(.439, .301):
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
    if mh.isSelected(.439, .301):
        current = 1
    elif mh.isSelected(.439, .347):
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
def tileSet(value,sleepTime):
    value -= 1
    pydirectinput.keyDown('left')
    time.sleep(sleepTime) # reset reset position 
    pydirectinput.keyUp('left')
    for i in range(int(value / 3)):
        mh.down()
    for i in range(value % 3):
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
    numSliders = len(menu) - 1 # subtract out menu key
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
    if menu["folder"] == "eyelashes": # extra delay for this particular page 
        sleepMultiplier = .125
    else:
        sleepMultiplier = .0918
    sleepTime = menu["numTiles"] * sleepMultiplier
    tileSet(menu["value"], sleepTime)
def importMacro(menu):
    time.sleep(.75)
    if "gender" not in menu: # don't do if main menu 
        mh.enter()
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
                return
    elif "isLinked" in menu:
        linkedImportMacro(menu, menu["isLinked"])
        mh.back()
    else:
        # recurse into next submenu 
        for nextMenu in menu:
            importMacro(menu[nextMenu])
            mh.down()
        mh.back()
            # down()
def linkedImportMacro(menu, isLinked):
    """Helper method for importMacro() - processes the linked menus"""
    for nextMenu in menu:
        if nextMenu == "isLinked":
            continue
        elif isLinked:
            if menu[nextMenu]["linkType"] in ("all", "linked"):
                importMacro(menu[nextMenu]) # use base case to deal with 
        elif not isLinked:
            if menu[nextMenu]["linkType"] in ("all", "unlinked"):
                importMacro(menu[nextMenu]) # use base case to deal with 
        mh.down()
def importCharacter(jsonPath):
    with open(jsonPath) as f:
        data = json.load(f)
    mh.loadOCR()
    # reset position
    mh.back()
    mh.enter()
    importMacro(data)
def getDictTemplate():
    DROPDOWN = "dropdown"
    SLIDERS = "sliders"
    TILES = "tiles"
    COLORS = "colors"
    MENU = "menu"
    LINKTYPE = "linkType"
    template = {
        "gender": {
            MENU: DROPDOWN,
            "options": ("male", "female"),
            "value": ""
        },
        "age": {
            MENU: DROPDOWN,
            "options": ("young", "mature", "aged"),
            "value": ""
        },
        "voice": {
            MENU: DROPDOWN,
            "options": ("youngVoice", "matureVoice", "agedVoice"),
            "value": ""
        },
        "physique": {
            "musculature": {
                MENU: DROPDOWN,
                "options": ("standard", "muscular"),
                "value": ""
            },
            "bodyHair": {
                MENU: DROPDOWN,
                "options": ("standard", "thick"),
                "value": ""
            }
        },
        "buildDetail": {
            MENU: SLIDERS,
            "head": -1,
            "chest": -1,
            "abdomen": -1,
            "arms": -1,
            "legs": -1
        },
        "baseSkinColor": {
            MENU: COLORS,
            "red": -1,
            "green": -1,
            "blue": -1
        },
        "skinColor": {
            MENU: SLIDERS,
            "skinTone": -1,
            "skinColorLayer1": -1,
            "skinColorLayer2": -1,
            "skinColorLayer3": -1,
            "skinColorLayer4": -1,
            "noseBridgeColor": -1,
            "cheekColor": -1,
            "laughLines": -1
        },
        "faceDetail": {
            "features": {
                MENU: SLIDERS,
                "apparentAge": -1,
                "facialAesthetic": -1,
                "formEmphasis": -1
            },
            "faceShape": {
                "facialBalance": {
                    MENU: SLIDERS,
                    "noseSize" : -1,
                    "nose/foreheadRatio": -1,
                    "faceProtrusion": -1,
                    "vert.FacialSpacing": -1,
                    "facialFeatureSlant": -1,
                    "horiz.Facial": -1
                },
                "forehead/glabella": {
                    MENU: SLIDERS,
                    "foreheadDepth": -1,
                    "foreheadProtrusion": -1,
                    "noseBridgeHeight": -1,
                    "bridgeProtrusion1": -1,
                    "bridgeProtrusion2": -1,
                    "noseBridgeWidth": -1
                },
                "browRidge": {
                    MENU: SLIDERS,
                    "browRidgeHeight": -1,
                    "innerBrowRidge": -1,
                    "outerBrowRidge": -1
                },
                "eyes": {
                    MENU: SLIDERS,
                    "eyePosition": -1,
                    "eyeSize": -1,
                    "eyeSlant": -1,
                    "eyeSpacing": -1
                },
                "noseRidge": {
                    MENU: SLIDERS,
                    "noseRidgeDepth": -1,
                    "noseRidgeLength": -1,
                    "nosePosition": -1,
                    "noseTipHeight": -1,
                    "noseProtrusion": -1,
                    "noseHeight": -1,
                    "noseSlant": -1
                },
                "nostrils": {
                    MENU: SLIDERS,
                    "nostrilSlant": -1,
                    "nostrilSize": -1,
                    "nostrilWidth": -1,
                    "nasalSize": -1
                },
                "cheeks": {
                    MENU: SLIDERS,
                    "cheekboneHeight": -1,
                    "cheekboneDepth": -1,
                    "cheekboneWidth": -1,
                    "cheekbone": -1,
                    "cheeks": -1
                },
                "lips": {
                    MENU: SLIDERS,
                    "lipShape": -1,
                    "mouthExpression": -1,
                    "lipFullness": -1,
                    "lipSize": -1,
                    "lipProtrusion": -1,
                    "lipThickness": -1
                },
                "mouth": {
                    MENU: SLIDERS,
                    "mouthProtrusion": -1,
                    "mouthSlant": -1,
                    "occlusion": -1,
                    "mouthPosition": -1,
                    "mouthWidth": -1,
                    "mouth-chinDistance": -1
                },
                "chin": {
                    MENU: SLIDERS,
                    "chinTipPosition": -1,
                    "chinLength": -1,
                    "chinProtrusion": -1,
                    "chinDepth": -1,
                    "chinSize": -1,
                    "chinHeight": -1,
                    "chinWidth": -1
                },
                "jaw": {
                    MENU: SLIDERS,
                    "jawProtrusion": -1,
                    "jawWidth": -1,
                    "lowerJaw": -1,
                    "jawContour": -1
                }
            },
            "hair/facialHair": {
                "isLinked": True,
                "hair/brow/beard": {
                    MENU: COLORS,
                    LINKTYPE: "linked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "hair": {
                    MENU: TILES,
                    LINKTYPE: "all",
                    "numTiles": 24,
                    "folder": "hair",
                    "value": -1
                },
                "hairColor": {
                    MENU: COLORS,
                    LINKTYPE: "unlinked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "brow": {
                    MENU: TILES,
                    LINKTYPE: "all",
                    "numTiles": 17,
                    "folder": "brow",
                    "value": -1
                },
                "browColor": {
                    MENU: COLORS,
                    LINKTYPE: "unlinked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "beard": {
                    MENU: TILES,
                    LINKTYPE: "all",
                    "numTiles": 12,
                    "folder": "beard",
                    "value": -1
                },
                "beardColor": {
                    MENU: COLORS,
                    LINKTYPE: "unlinked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "eyelashes": {
                    MENU: TILES,
                    LINKTYPE: "all",
                    "numTiles": 4,
                    "folder": "eyelashes",
                    "value": -1
                },
                "eyelashColor": {
                    MENU: COLORS,
                    LINKTYPE: "all",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                }
            },
            "pupils": {
                "isLinked": True,
                "pupils": {
                    MENU: TILES,
                    LINKTYPE: "linked",
                    "numTiles": 9,
                    "folder": "pupil",
                    "value": -1
                },
                "colorOfPupils": {
                    MENU: COLORS,
                    LINKTYPE: "linked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "rightPupil": {
                    MENU: TILES,
                    LINKTYPE: "unlinked",
                    "numTiles": 9,
                    "folder": "pupil",
                    "value": -1
                },
                "rightPupilColor": {
                    MENU: COLORS,
                    LINKTYPE: "unlinked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "leftPupil": {
                    MENU: TILES,
                    LINKTYPE: "unlinked",
                    "numTiles": 9,
                    "folder": "pupil",
                    "value": -1
                },
                "leftPupilColor": {
                    MENU: COLORS,
                    LINKTYPE: "unlinked",
                    "red": -1,
                    "green": -1,
                    "blue": -1
                }
            },
            "cosmetics": {
                MENU:SLIDERS,
                "toneAroundEyes": -1,
                "eyeSocket": -1,
                "eyelidBrightness": -1,
                "eyelidColor": -1,
                "eyeliner": -1,
                "eyeShadow": -1,
                "lipstick1": -1,
                "lipstick2": -1
            },
            "tattoo/mark": {
                "tattoo/mark": {
                    MENU: TILES,
                    "numTiles": 50,
                    "folder": "tattoo",
                    "value": -1
                },
                "tattoo/markColor": {
                    MENU: COLORS,
                    "red": -1,
                    "green": -1,
                    "blue": -1
                },
                "tweakTattoo/mark": {
                    MENU: SLIDERS,
                    "position(Vertical)": -1,
                    "position(Horizontal)": -1,
                    "angle": -1,
                    "expansion": -1
                }
            }
                
        }
    }
    return template
def setSliders(values):
    for i in range(len(values)):
        if values[i] != -1: # ignore if user didn't set a value in json
            text,confidence = mh.processRegion(*mh.sliderRegions[i], True)
            setVal(values[i],text,confidence)
        mh.down() # go down regardless 
    mh.enter()
    mh.back()
    mh.animDelay()