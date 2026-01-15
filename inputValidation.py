import macroHelpers as mh

class InputValidation:
    def __init__(self):
        self.menu = "NONE"
        self.selected = -1
        self.tileScrollStart = -1
        """Number of submenu icons on the buttons pages, which can arbitrarily be used to differentiate
        between different button menus. """
        self.numSubmenuIcons = [] 

        
        
        self.colorSelectRegions = (((0.6018,0.7923),(0.9501,.7923)),
                                   ((0.6018,0.8584),(0.9501,.8584)),
                                   ((0.6018,0.9244),(0.9501,.9244)))
    def inputRegistered(self, key):
        currentMenu = self.findMenu()
        newSelected = None
        match currentMenu:
            case "tiles":
                if currentMenu == self.menu and key == "e":
                    print("MISSED E PRESS TILE")
                    return False
                # we have to account for two success cases - the cases where the selection box 
                # moves on screen, and when only the scroll bar does 
                newSelected = mh.currentTileOnPage()
                newTileScrollStart = self.findScrollStart()
                if currentMenu == self.menu:
                    answer = self.selected != newSelected or self.tileScrollStart != newTileScrollStart
                else:
                    answer = True
                self.tileScrollStart = newTileScrollStart
            case "dropdown":
                newSelected = mh.readOptionBox(3) # assume 3 
                if self.menu == currentMenu:
                    answer = newSelected != self.selected
                else:
                    answer = True
            case "genderConfirm":
                newSelected = 2
                if mh.isSelected(0.5529,0.5491, (151,76,21), .025):
                    newSelected = 1
                if self.menu == currentMenu:
                    answer = newSelected != self.selected
                else:
                    answer = True
            case "sliders":
                if key == "e" and self.menu == "sliders":
                    if self.isConfirmed():
                        return True
                    else:
                        return False
                newSelected = mh.findSelectedSlider()
                if currentMenu == self.menu:
                    answer = newSelected != self.selected
                else:
                    answer = True
            case "buttons":
                newSelected = mh.findSelectedButton()
                if newSelected == -1:
                    newSelected = self.selected
                if self.menu == currentMenu:
                    answer = newSelected != self.selected
                else:
                    answer = True
            case "colors":
                if currentMenu == self.menu and key == "e":
                    print("MISSED E PRESS COLOR")
                    return False
                j = 1
                newSelected = 0
                for i in self.colorSelectRegions:
                    # We have to check two points, because the arrow that we are using to check which one is highlighted, will dissapear 
                    # if the slider is all the way to the left or right. This prevents that issue 
                    if mh.isSelected(*i[0], (139,131,110), .1) or mh.isSelected(*i[1], (139,131,110), .1):
                        newSelected = j
                        break
                    j += 1
                if currentMenu == self.menu:
                    answer = newSelected != self.selected
                else:
                    answer = True
            case _:
                answer = False
        self.menu = currentMenu
        if answer:
            self.selected = newSelected
        return answer

    def findMenu(self):
        if mh.isColor(mh.getGamePoint(.572,.7796), (182,67,70),.05):
            return "colors"
        elif mh.isColor(mh.getGamePoint(0.9501,0.0211), (105,85,61), .025):
           return "tiles"
        elif mh.isColor(mh.getGamePoint(0.7846,0.1147), (107,84,43), .05): 
            return "sliders"
        elif mh.isColor(mh.getGamePoint(0.9984,0.38), (158,157,140), .15):
            return "genderConfirm"
        elif mh.isColor(mh.getGamePoint(0.4871,0.9796), (13,11,16), .05):
            return "buttons"
        else:
            return "dropdown"
    def findScrollStart(self):
        sliderPos = 0.0258 # first possible scroll bar position 
        posNum = 1
        scrollBottom = .832 # position of the bottom of where the scroll bar can go 
        while sliderPos < scrollBottom:
            if mh.isSelected(.9764, sliderPos, (131,91,31), .05):
                return posNum
            sliderPos += .05
            posNum += 1
        # Menu with no scroll bar 
        return 0 
    def isConfirmed(self):
        # Ideally I wouldn't have to take a screenshot here, and instead just use mh.getGamePoint(), but this is outside
        # the region of the game screenshot. I thought about increasing the bounds of the screenshot to encompass this, but
        # that would mean I would have to translate all of the coordinates, so I figured it wasn't worth the time investment. 
        # This is a non-issue because this has a negligible performance impact, but worth noting. 
        left = int(mh.rectCoords[0] + .0875 * mh.clientRect[2])
        top = int(mh.rectCoords[1] + .9271 * mh.clientRect[3])
        screenshot = mh.sct.grab({'left': left, 'top': top, 'width': 1, 'height': 1})
        actualColor = (screenshot.pixel(0,0))[:3]
        if mh.isColor(actualColor,(202,202,202),.05, 1): 
            return False
        else:
            return True
