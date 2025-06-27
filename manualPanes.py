import tkinter as tk
import re
class Sliders:
    def __init__(self, manualFrame, w, h):
        # initialize frame
        self.manualSlidersPane = tk.Frame(manualFrame,width=w,height=h)
        self.manualSlidersPane.grid(row=1,column=1,sticky="nsew")
        # initialize widgets 
        self.numSliders = 11
        self.sliders = [None] * self.numSliders
        validateCommand = self.manualSlidersPane.register(validateEdit)
        for i in range(self.numSliders):
            self.sliders[i] = tk.Entry(self.manualSlidersPane, validate='key', validatecommand=(validateCommand, '%P'))
            self.sliders[i].grid(row=i,column=0)
        
    def load(self, menu):
        for i in range(len(menu)-2, self.numSliders): # hide unecessary buttons, compensate for menu
            self.sliders[i].grid_remove()
        for i in range(0,len(menu)-1):
            if not self.sliders[i].winfo_ismapped():
                self.sliders[i].grid()
        i = 0
        for key in menu:
            if key != "menu":
                self.sliders[i].delete(0,tk.END)
                self.sliders[i].insert(0,menu[key])
                i += 1
        self.manualSlidersPane.tkraise()
    def log(self, dict):
        i = 0 
        for key in dict:
            if key != "menu":
                if self.sliders[i].get() == "":
                    dict[key] = -1
                else:
                    dict[key] = int(self.sliders[i].get()) # HAVEN'T RETESTED AFTER CHANGE 
                i += 1
class Colors:
    def __init__(self, manualFrame, w, h):
        # initialize frame
        self.manualColorsPane = tk.Frame(manualFrame,width=w,height=h)
        self.manualColorsPane.grid(row=1,column=1,sticky="nsew")
        # initialize widgets 
        self.shouldColorLog = False
        self.manualColors = [None] * 3
        self.colorValues = [0] * 3
        validateCommand = self.manualColorsPane.register(validateEdit)
        for i in range(3):
            self.colorValues[i] = tk.StringVar()
            self.colorValues[i].trace_add("write", lambda *args, j = i: self.logColorValue(j))
            self.manualColors[i] = tk.Entry(self.manualColorsPane, validate='key', validatecommand=(validateCommand, '%P'), textvariable=self.colorValues[i])
            self.manualColors[i].grid(row=i,column=0)
        self.manualColorDisplay = tk.Frame(self.manualColorsPane, width=50, height=50)
        self.manualColorDisplay.grid(row=0,column=1)
    def load(self, menu):
        self.currentMenu = menu
        hexCode = self.dictColorToHex()
        self.manualColorDisplay.config(bg=hexCode)
        self.manualColorsPane.tkraise()
        i=0
        for key in menu: 
            if key not in ("menu", "linkType"):
                self.manualColors[i].delete(0,tk.END)
                self.manualColors[i].insert(0,menu[key])
                i += 1
        self.shouldColorLog = True
    def dictColorToHex(self):
        """Returns the hex value of the current menu's colors. This method is only called within a color menu, so the colors will always be present"""
        colors = [0,0,0]
        i = 0
        for key in self.currentMenu:
            if key not in ("menu", "linkType"):
                if self.currentMenu[key] != -1 and self.currentMenu[key] != '': # "" and -1 defaults to 0 for the display 
                    colors[i] = self.currentMenu[key]
                i += 1
        hexCode = "#" + format(colors[0], '02x') + format(colors[1], '02x') + format(colors[2], '02x')
        return hexCode
    def logColorValue(self, i):
        """Logs the changed color into the dictionary, then updates the color display to reflect that change"""
        if not self.shouldColorLog:
            return
        match i: # find name of color from number 
            case 0:
                color = "red"
            case 1:
                color = "green"
            case 2:
                color = "blue"
            case _:
                print("ERROR INVALID COLOR ID IN logColorValue()")
                quit()

        colorValue = self.colorValues[i].get()
        if colorValue: # if not ""
            colorValue = int(colorValue)
        else:
            colorValue = -1
        self.currentMenu[color] = colorValue

        hexCode = self.dictColorToHex()
        self.manualColorDisplay.config(bg=hexCode)
class Labels:
    def __init__(self, manualFrame, w, h):
        # initialize fram
        self.manualLabelPane = tk.Frame(manualFrame,width=w,height=h)
        self.manualLabelPane.grid(row=1,column=0,sticky="nsew")
        # initialize widgets 
        self.numLabels = 8
        self.labels = [None] * self.numLabels
        for i in range(self.numLabels):
            self.labels[i] = tk.Label(self.manualLabelPane, text=f"label {i}")
            self.labels[i].grid(row=i,column=0)
    def load(self, menu):
        i = 0
        for key in menu: 
            if key not in ("menu","linkType"):
                self.labels[i].config(text=spaceFormat(key))
                i += 1
        for j in range(i, self.numLabels): # hide unecessary buttons, compensate for menu
            self.labels[j].grid_remove()
        for j in range(0,i):
            if not self.labels[j].winfo_ismapped():
                self.labels[j].grid()
        self.manualLabelPane.tkraise()
class Dropdown:
    def __init__(self, manualFrame, w, h):
        # initialize frame 
        self.manualDropdownPane = tk.Frame(manualFrame,width=w,height=h)
        self.manualDropdownPane.grid(row=1,column=0,sticky="nsew")
        # initialize widgets 
        self.dropdownValue = tk.StringVar()
        self.dropdownValue.trace_add("write", lambda *args: self.logDropboxValue())
        self.manualDropdown = tk.OptionMenu(self.manualDropdownPane, self.dropdownValue, *["placeholder"])
        self.manualDropdown.grid(row=0,column=0)
    def load(self, menu):
        self.currentMenu = menu
        self.manualDropdownPane.tkraise()
        newOptions = self.currentMenu["options"]
        self.manualDropdown['menu'].delete(0,'end')
        self.dropdownValue.set(self.currentMenu["value"])
        for i in newOptions: # add dropdown options 
            self.manualDropdown['menu'].add_command(label=i, command=tk._setit(self.dropdownValue,i))
    def logDropboxValue(self):
        """Logs the current dropbox value into the dictionary."""
        self.currentMenu["value"] = self.dropdownValue.get()
class Tiles:
    def __init__(self, manualFrame, w, h):
        # initiate frame 
        self.manualTilesPane = tk.Frame(manualFrame,width=w,height=h)
        self.manualTilesPane.grid(row=1,column=0,sticky="nsew",columnspan=2)
        # initiate widgets 
        self.tileImage = tk.Label(self.manualTilesPane)
        self.tileImage.grid(row=0,column=1)

        tileValidateCommand = self.manualTilesPane.register(self.validateTileEdit)
        self.tileValue = tk.StringVar()
        self.shouldTileLog = False # ensure values aren't logged unintentionally
        self.tileSelector = tk.Spinbox(self.manualTilesPane, validate='key', validatecommand=(tileValidateCommand, '%P'), 
                                       command=lambda:self.logTile(int(self.tileValue.get())), textvariable=self.tileValue,
                                       from_=1, to=1)
        self.tileSelector.grid(row=0,column=0)

        self.tileImages = {"isLoaded": False, "noneSelected": None, "hair":[None] * 24, "brow": [None] * 17, 
                           "beard":[None] * 12, "eyelashes":[None] * 4, "pupil": [None] * 9, "tattoo": [None] * 50}
        self.loadImages()
    def load(self, menu):
        """Load and display the widgets for a tile type menu"""
        self.currentMenu = menu
        self.tileSelector.config(to=self.currentMenu["numTiles"])
        loggedValue = self.currentMenu["value"]
        if loggedValue == -1:
            self.tileValue.set("") # dangerous with validation, potentially change 
            self.tileSelector.config(validate='key')
        else:
            self.tileValue.set(loggedValue)
        self.showTileImage(loggedValue) # ensure image changes
        self.shouldTileLog = True
        self.manualTilesPane.tkraise()
    def logTile(self, value):
        """Shows the now selected image and logs it into the dictionary"""
        if not self.shouldTileLog: # only log if shouldTileLog == True
            return
        self.currentMenu["value"] = value
        self.showTileImage(value)
    def validateTileEdit(self, P):
        """Validation command for the tile spinboxes. Limits from 0 to the specific tile's number of tiles, but also allows the field to be cleared"""
        if not self.shouldTileLog:
            return False
        if (P.isdigit()):
            number = int(P)
            if (number > 0 and number <= self.currentMenu["numTiles"]):
                self.logTile(number)
                return True
        if (P == ""):
            self.showTileImage(-1)
            return True
        return False
    def loadImages(self):
        """Loads the tile images into the dictionary to be used later"""
        self.tileImages["noneSelected"] = tk.PhotoImage(file="images/noneSelected.png")
        for key in self.tileImages:
            if key != "isLoaded" and key != "noneSelected":
                for i in range(len(self.tileImages[key])):
                    self.tileImages[key][i] = tk.PhotoImage(file=("images/"+ key + "/" + key +str(i+1)+".png"))
    def showTileImage(self, value):
        """
        Display the corresponding tile image (noneSelected image for -1)
        arg: value
            value to match image to 
        """
        if value == -1: # no image selected 
            self.tileImage.config(image=self.tileImages["noneSelected"])
        else:
            self.tileImage.config(image=self.tileImages[self.currentMenu["folder"]][value-1])
def validateEdit(P):
    """Validation command for text boxes. Limits from 0 to 255, but also allows the field to be cleared"""
    if (P.isdigit()):
        text = int(P)
        if(text >= 0 and text <= 255):
            return True
    elif (P == ""): # let user clear field
        return True

    return False
def spaceFormat(text):
        """Converts camel case to normal uppercase format (wordsLikeThis -> Words Like This)"""
        formatted = re.sub(r"([a-z])([A-Z])", r"\1 \2", text) # space between camel case
        formatted = re.sub(r"([a-z])([0-9])", r"\1 \2", formatted) # space between letters and numbers
        formatted = re.sub(r"([a-z])(\()", r"\1 \2", formatted) # space between letters and parenthesis 
        formatted = re.sub(r"(\.)([a-z])", r"\1 \2", formatted) # space after . 
        return formatted.title()