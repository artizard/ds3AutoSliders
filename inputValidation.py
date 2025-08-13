import macroHelpers as mh
class InputValidation:
    def __init__(self):
        self.menu = "NONE"
        self.selected = 0
        """Number of submenu icons on the buttons pages, which can arbitrarily be used to differentiate
        between different button menus. """
        self.numSubmenuIcons = [] 
    def inputRegistered(self):
        currentMenu = self.findMenu()
    def findMenu(self):
        if mh.isColor(mh.getGamePoint(.572,.7796), (182,67,70),.05):
            return "colors"
        elif mh.isColor(mh.getGamePoint(0.9501,0.0211), (105,85,61), .025):
           return "tiles"
        elif mh.isColor(mh.getGamePoint(0.9984,0.38), (158,157,140), .025):
            return "genderConfirm"
        elif mh.isColor(mh.getGamePoint(0.7846,0.1147), (107,84,43), .025): 
            return "sliders"
        elif mh.isColor(mh.getGamePoint(0.3776,0.7165), (132,112,79), .025):
            return "backMenu"
        elif mh.isColor(mh.getGamePoint(0.4871,0.9796), (13,11,16), .05):
            return "buttons"
        else:
            return "dropdown"
