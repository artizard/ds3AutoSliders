import ctypes
import pydirectinput
import time
import win32gui
import mss
from PIL import Image, ImageOps, ImageEnhance
import numpy
import easyocr
import json
import re
# some things for import and export that need to be run before using. 
#pydirectinput.PAUSE = 0.0167 # The game can only register 1 input per frame, so the pause is ~1/60 
#pydirectinput.PAUSE = 0.017
pydirectinput.PAUSE = 0.017
ctypes.windll.user32.SetProcessDPIAware()
hwnd = None
reader = None
ocrOpened = False
sliderRegions = ((.343,.203,.372,.226),
                     (.343,.285,.372,.307),
                     (.343,.366,.372,.389),
                     (.343,.448,.372,.470),
                     (.343,.529,.372,.552),
                     (.343,.610,.372,.633),
                     (.343,.692,.372,.715),
                     (.343,.773,.372,.796))
def enter():
    pydirectinput.press('e')
def back():
    pydirectinput.press('q')
def down():
    print("down")
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
def isSelected(x, y):
    """finds if box is selected (is orange), by pixel at ratio x and y"""
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))
    left = int(rectCoords[0] + x * clientRect[2])
    top = int(rectCoords[1] + y * clientRect[3])
    width = 1
    height = 1
    desiredColor = (86,39,11)
    tolerance = 40
    with mss.mss() as sct:
        mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
        screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
        # mss.tools.to_png(mssScreenshot.rgb, mssScreenshot.size, output="pixelScreenshot.png")
        r,g,b = screenshot.getpixel((0,0))
        if abs(desiredColor[0] - r) > tolerance:
            return False
        if abs(desiredColor[1] - g) > tolerance:
            return False
        if abs(desiredColor[2] - b) > tolerance:
            return False
        return True
def loadOCR():
    global ocrOpened
    if ocrOpened:
        print("OCR already opened")
        time.sleep(3)
        return
    startFullscreenWait = time.time()
    print("memory load easyocr")
    global reader
    reader = easyocr.Reader(['ch_tra', 'en'], gpu=False)
    print("ocr loaded")
    global hwnd
    hwnd = win32gui.FindWindow(None, "DARK SOULS III")
    if (hwnd == 0):
        print("error")
        quit()  
    endFullscreenWait = time.time()
    timeLeftToWait = 3 - (endFullscreenWait-startFullscreenWait)
    if (timeLeftToWait > 0):
        time.sleep(timeLeftToWait)
    checkIfGameIsOpen() # check if open 
    ocrOpened = True
    return reader
def checkIfGameIsOpen():
    try:
        ageText,ageConfidence = processRegion(.156, .230, .206, .274, False)
        defaultsText,defaultsConfidence = processRegion(.133, .644, .200, .691, False)
    except: 
        print("GAME NOT OPEN")
        quit()
    if (ageText != "Age" and defaultsText != "Defaults"):
        print("WRONG MENU")
        quit()
def processRegion(x,y,x2,y2, isNum):
    clientRect = win32gui.GetClientRect(hwnd)
    rectCoords = win32gui.ClientToScreen(hwnd, (0, 0))
    #print(rectCoords)
    left = int(rectCoords[0] + x * clientRect[2])
    #print("left:", left)
    top = int(rectCoords[1] + y * clientRect[3])
    #print("top", top)
    width = int((x2-x) * clientRect[2])
    #print("width", width)
    height = int((y2-y) * clientRect[3])
    #print("height", height)
    with mss.mss() as sct:
        mssScreenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
        screenshot = Image.frombytes("RGB", mssScreenshot.size, mssScreenshot.rgb)
        screenshot = ImageOps.grayscale(screenshot)
        contraster = ImageEnhance.Contrast(screenshot)
        screenshot = contraster.enhance(3.5)
        # mss.tools.to_png(mssScreenshot.rgb, mssScreenshot.size, output="uneditedScreenshot.png")
        # screenshot.save("testScreenshot.png", format="PNG")

    results = reader.readtext(numpy.array(screenshot))
    for _, text, confidence in results:
        print(f"Text: {text} | Confidence: {confidence:.2f}")
    # return 0 when text is not detected (main case where that happens)
    if not results:
        print("NOT DETECTED 0")
        return 0, 1
    # in case of low confidence 0
    if results[0][1] == 0:
        print("LOW CONFIDENCE 0")
        return 0, 1
    # return text, confidence 
    # get rid of whitespace, avoid l vs 1 confusion
    result = (results[0][1]).replace(" ", "")
    if (isNum):
        result = result.replace("l", "1")
        result = result.replace("O", "0")
    else:
        result = result.replace("1", "l")
        result = result.replace("0", "O")

    return result, results[0][2]
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