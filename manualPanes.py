import customtkinter as ctk
import tkinter as tk
import re
from PIL import Image
import macroHelpers as mh
class Sliders:
    def __init__(self, manualFrame, w, h, font):
        # initialize frame
        self.manualSlidersPane = ctk.CTkFrame(manualFrame,width=w,height=h,fg_color="transparent")
        self.manualSlidersPane.place(relx=.525,rely=.15)
        self.manualSlidersPane.grid_propagate(False)
        # initialize widgets 
        #self.numSliders = 11
        self.numSliders = 10
        self.sliders = [None] * self.numSliders
        validateCommand = self.manualSlidersPane.register(validateEdit)
        for i in range(self.numSliders):
            self.sliders[i] = tk.Entry(self.manualSlidersPane, validate='key', validatecommand=(validateCommand, '%P'), font=font,
                                       fg="white",bg="#49473B",insertbackground="white", relief="flat")
            self.sliders[i].grid(row=i,column=0, pady=int(h/70)) # h/70 for resolution independent spacing 
        
    def load(self, menu):
        for i in range(len(menu)-2, self.numSliders): # hide unecessary buttons, compensate for menu
            self.sliders[i].grid_remove()
        for i in range(0,len(menu)-1):
            if not self.sliders[i].winfo_ismapped():
                self.sliders[i].grid()
        i = 0
        for key in menu:
            if key != "menu":
                self.sliders[i].delete(0,ctk.END)
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
                    dict[key] = int(self.sliders[i].get())  
                i += 1
class Colors:
    def __init__(self, manualFrame, w, h, font):
        # initialize frame
        self.manualColorsPane = ctk.CTkFrame(manualFrame,width=w,height=h,fg_color="transparent")
        # for column in range(3):
        #     self.manualColorsPane.grid_columnconfigure(column,weight=1, uniform="equal")
        self.manualColorsPane.grid_columnconfigure(0,weight=1, uniform="equal")
        self.manualColorsPane.grid_columnconfigure(1,weight=2, uniform="equal")
        self.manualColorsPane.grid_columnconfigure(1,weight=2, uniform="equal")
        self.manualColorsPane.grid_columnconfigure(3,weight=3, uniform="equal")
        self.manualColorsPane.place(relx=.05,rely=.15)
        self.manualColorsPane.grid_propagate(False)
        # initialize widgets 
        colors = ("Red", "Green", "Blue")
        self.shouldColorLog = False
        self.manualColors = [None] * 3
        self.colorLabels = [None] * 3
        self.colorValues = [0] * 3
        validateCommand = self.manualColorsPane.register(validateEdit)
        for i in range(3):
            self.colorValues[i] = ctk.StringVar()
            self.colorValues[i].trace_add("write", lambda *args, j = i: self.logColorValue(j))
            self.manualColors[i] = tk.Entry(self.manualColorsPane, validate='key', 
                                            validatecommand=(validateCommand, '%P'), textvariable=self.colorValues[i],
                                            font=font, fg="white",bg="#49473B",insertbackground="white", relief="flat",
                                            width=10)
            self.manualColors[i].grid(row=i,column=2, pady=int(h/31))
            self.colorLabels[i] = ctk.CTkLabel(self.manualColorsPane, text=colors[i], font=font)
            self.colorLabels[i].grid(row=i,column=1,pady=int(h/58))
        self.manualColorDisplay = ctk.CTkFrame(self.manualColorsPane, width=int(h/3), height=int(h/3), corner_radius=0)
        self.manualColorDisplay.grid(row=0,column=3,rowspan=3)
    def load(self, menu):
        self.currentMenu = menu
        hexCode = self.dictColorToHex()
        self.manualColorDisplay.configure(fg_color=hexCode)
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
        self.manualColorDisplay.configure(fg_color=hexCode)
class Labels:
    def __init__(self, manualFrame, w, h, font):
        # initialize frame
        self.manualLabelPane = ctk.CTkFrame(manualFrame,width=w,height=h,fg_color="transparent")
        self.manualLabelPane.place(relx=.15,rely=.15)
        self.manualLabelPane.grid_propagate(False)
        # initialize widgets 
        self.numLabels = 8
        self.labels = [None] * self.numLabels
        for i in range(self.numLabels):
            self.labels[i] = ctk.CTkLabel(self.manualLabelPane, text=f"label {i}", font=font)
            self.labels[i].grid(row=i,column=0, pady=int(h/58))
    def load(self, menu):
        i = 0
        for key in menu: 
            if key not in ("menu","linkType"):
                self.labels[i].configure(text=spaceFormat(key))
                i += 1
        for j in range(i, self.numLabels): # hide unecessary buttons, compensate for menu
            self.labels[j].grid_remove()
        for j in range(0,i):
            if not self.labels[j].winfo_ismapped():
                self.labels[j].grid()
        self.manualLabelPane.tkraise()
class Dropdown:
    def __init__(self, manualFrame, w, h, font):
        # initialize frame 
        self.manualDropdownPane = ctk.CTkFrame(manualFrame,width=w,height=h,fg_color="transparent")
        self.manualDropdownPane.place(relx=.5,rely=.2, anchor="center")
        #self.manualDropdownPane.grid_propagate(False)
        # initialize widgets 
        self.dropdownValue = ctk.StringVar()
        self.dropdownValue.trace_add("write", lambda *args: self.logDropboxValue())
        self.manualDropdown = ctk.CTkOptionMenu(self.manualDropdownPane, variable=self.dropdownValue, values=["placeholder"], 
                                                fg_color="#49473B", button_color="#49473B", button_hover_color="#38362A",
                                                font=font, dropdown_font=font, dropdown_fg_color="#49473B",
                                                anchor="center", width=w, height=h,dropdown_hover_color="#38362A")
        self.manualDropdown.place(relx=.5, rely=.5, anchor="center")
    def load(self, menu):
        self.currentMenu = menu
        self.manualDropdownPane.tkraise()
        newOptions = self.currentMenu["options"]
        self.manualDropdown.configure(values=newOptions)
        self.dropdownValue.set(self.currentMenu["value"])
    def logDropboxValue(self):
        """Logs the current dropbox value into the dictionary."""
        self.currentMenu["value"] = self.dropdownValue.get()
class Tiles:
    def __init__(self, manualFrame, w, h, font):
        # initiate frame 
        self.width = w
        self.height = h
        self.manualTilesPane = ctk.CTkFrame(manualFrame,width=w,height=h,fg_color="transparent")
        self.manualTilesPane.place(relx=.05,rely=.15)
        self.manualTilesPane.grid_propagate(False)
        # initiate widgets 
        self.tileImage = ctk.CTkLabel(self.manualTilesPane, text="")
        self.tileImage.place(relx=.65, rely=.4, anchor="center")

        tileValidateCommand = self.manualTilesPane.register(self.validateTileEdit)
        self.tileValue = tk.StringVar()
        self.shouldTileLog = False # ensure values aren't logged unintentionally
        self.tileSelector = tk.Spinbox(self.manualTilesPane, validate='key', validatecommand=(tileValidateCommand, '%P'), 
                                       command=lambda:self.logTile(int(self.tileValue.get())), textvariable=self.tileValue,
                                       from_=1, to=1, font=font, width=4, fg="white",
                                       relief="flat",
                                       bg="#49473B", buttonbackground="#38362A")
        self.tileSelector.place(relx=.25,rely=.4, anchor="center")

        self.tileImages = {"isLoaded": False, "noneSelected": None, "hair":[None] * 24, "brow": [None] * 17, 
                           "beard":[None] * 12, "eyelashes":[None] * 4, "pupil": [None] * 9, "tattoo": [None] * 50}
        self.loadImages()
    def load(self, menu):
        """Load and display the widgets for a tile type menu"""
        self.currentMenu = menu
        self.tileSelector.configure(to=self.currentMenu["numTiles"])
        loggedValue = self.currentMenu["value"]
        if loggedValue == -1:
            self.tileValue.set("") # dangerous with validation, potentially change 
            self.tileSelector.configure(validate='key')
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
        self.tileImages["noneSelected"] = ctk.CTkImage(Image.open("images/noneSelected.png"), size=(self.height//2,self.height//2))
        for key in self.tileImages:
            if key != "isLoaded" and key != "noneSelected":
                for i in range(len(self.tileImages[key])):
                    self.tileImages[key][i] = ctk.CTkImage(Image.open("images/"+ key + "/" + key +str(i+1)+".png"), 
                                                           size=(self.height//2,self.height//2))
    def showTileImage(self, value):
        """
        Display the corresponding tile image (noneSelected image for -1)
        arg: value
            value to match image to 
        """
        if value == -1: # no image selected 
            self.tileImage.configure(image=self.tileImages["noneSelected"])
        else:
            self.tileImage.configure(image=self.tileImages[self.currentMenu["folder"]][value-1])
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