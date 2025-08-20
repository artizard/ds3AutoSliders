import macroHelpers as mh

class InputValidation:
    def __init__(self):
        self.menu = "NONE"
        self.selected = -1
        self.tileScrollStart = -1
        """Number of submenu icons on the buttons pages, which can arbitrarily be used to differentiate
        between different button menus. """
        self.numSubmenuIcons = [] 

        self.sliderSelectRegions = ((0.1801,0.1128),(0.1801,0.2279),(0.1801,0.3443),(0.1801,0.4594),
                                    (0.1801,0.5748),(0.1801,0.6909),(0.1801,0.8052),(0.1801,0.9214))
        
        self.colorSelectRegions = (((0.6018,0.7923),(0.9501,.7923)),
                                   ((0.6018,0.8584),(0.9501,.8584)),
                                   ((0.6018,0.9244),(0.9501,.9244)))
    def inputRegistered(self, key):
        currentMenu = self.findMenu()
        print("Menu:", currentMenu)
        match currentMenu:
            case "tiles":
                newSelected = mh.currentTileOnPage()
                newTileScrollStart = self.findScrollStart()
                if self.menu == currentMenu:
                    #print(f"OLD: {self.selected}, {self.tileScrollStart}")
                    #print(f"New: {newSelected}, {newTileScrollStart}")
                    if self.selected != newSelected or self.tileScrollStart != newTileScrollStart:
                        answer = True
                    else:
                        answer = False
                else:
                    answer = True
                self.selected = newSelected
                self.tileScrollStart = newTileScrollStart
            case "dropdown":
                newSelected = mh.readOptionBox(3) # assume 3 
                if self.menu == currentMenu:
                    #print(f"OLD: {self.selected}")
                    #print(f"New: {newSelected}")
                    if newSelected != self.selected:
                        answer = True
                    else: 
                        answer = False
                else:
                    answer = True
                self.selected = newSelected
            case "genderConfirm":
                newSelected = 2
                if mh.isSelected(0.5529,0.5491, (151,76,21), .025):
                    newSelected = 1
                if self.menu == currentMenu:
                    if newSelected != self.selected:
                        answer = True
                    else:
                        answer = False
                else:
                    answer = True
                self.selected = newSelected
            case "backMenu":
                if self.menu != currentMenu:
                    answer = True
                else:
                    answer = False # you should never have the backMenu twice 
            case "sliders":
                if key in ("e","6") and self.menu == "sliders":
                    if self.isConfirmed():
                        return True
                    else:
                        return False
                newSelected = mh.findSelectedSlider()
                if self.menu == currentMenu:
                    if newSelected != self.selected:
                        answer = True
                    else:
                        answer = False
                else:
                    answer = True
                self.selected = newSelected
            case "buttons":
                newSelected = mh.findSelectedSlider()
                if self.menu == currentMenu:
                    if newSelected != self.selected:
                        answer = True
                    else:
                        answer = False
                else:
                    answer = True
                self.selected = newSelected
            case "colors":
                j = 1
                newSelected = 0
                for i in self.colorSelectRegions:
                    # We have to check to points, because the arrow that we are using to check which one is highlighted, will dissapear 
                    # if the slider is all the way to the left or right. This prevents that issue 
                    if mh.isSelected(*i[0], (139,131,110), .1) or mh.isSelected(*i[1], (139,131,110), .1):
                        newSelected = j
                        break
                    j += 1
                if self.menu == currentMenu:
                    if newSelected != self.selected:
                        answer = True
                    else:
                        answer = False
                else:
                    answer = True
                self.selected = newSelected
            case _:
                answer = False
        self.menu = currentMenu
        print("Selected:", self.selected)
        return answer

    def findMenu(self):
        if mh.isColor(mh.getGamePoint(.572,.7796), (182,67,70),.05):
            return "colors"
        elif mh.isColor(mh.getGamePoint(0.9501,0.0211), (105,85,61), .025):
           return "tiles"
        elif mh.isColor(mh.getGamePoint(0.7846,0.1147), (107,84,43), .05): 
            return "sliders"
        elif mh.isColor(mh.getGamePoint(0.3776,0.7165), (132,112,79), .05):
            return "backMenu"
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
        # (0.6293,0.6819)
        # pos = .6293
        # while pos <= .6819:
        #     if mh.isSelected(pos,.094,(202,24,20),.025): # if red
        #         print("FALSE")
        #         return False
        #     pos += .00527 #.0526 / 10
        # print("TRUE")
        # return True

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
