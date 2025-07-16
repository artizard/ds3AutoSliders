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
    time.sleep(.5)
def enterDelay():
    time.sleep(.3)
def isSelected(x,y,desiredColor,tolerance):
    """finds if box is selected (is orange), by pixel at ratio x and y"""
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))
    left = int(rectCoords[0] + x * clientRect[2])
    top = int(rectCoords[1] + y * clientRect[3])
    width = 1
    height = 1
    with mss.mss() as sct:
        mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
        screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
        # mss.tools.to_png(mssScreenshot.rgb, mssScreenshot.size, output="pixelScreenshot.png")
        r,g,b = screenshot.getpixel((0,0))
        print("desired:", desiredColor)
        print("actual:",r,g,b)
        return isColor(r,g,b,desiredColor,tolerance) 
def isColor(r,g,b, desiredColor, tolerance):
    """Returns whether the color matches the desired color or not, applies tolerance system"""
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
        logits = outputs[0]
        print("COLOR")
    else:
        outputs = sliderModel.run(None, {sliderInput_name: imageArray})
        logits = outputs[0]
        print("SLIDER")

    answer = np.argmax(logits)
    confidence = logits[0][answer]
    
    return answer, confidence
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
            if i not in ("menu", "options", "isLinked", "linkType", "numTiles", "folder") and menu[i] not in (-1, ""):
                return True # value is set 
        return False # no values set
    for i in menu:
        if i in "isLinked":
            continue
        if menuHasValues(menu[i]):
            return True # value was found 
    return False
def findSelectedTile(menu):
    page = findTilePage(menu)
    print("page:", page)
    tile = currentTileOnPage()
    print("tile:", tile)
    print("final:", (tile + (page-1)*3))
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