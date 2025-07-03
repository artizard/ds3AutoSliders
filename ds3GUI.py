import tkinter as tk
from tkinter import filedialog
import importCharacter
import exportCharacter
from manualPanes import Sliders, Colors, Labels, Dropdown, Tiles, spaceFormat
import macroHelpers as mh
import time
class GUI:
    def __init__(self):
        # mh.loadOCR()
        # while True:
        #     print("start")
        #     time.sleep(.2242)
        #     mh.findSelectedTile({
        #             "numTiles": 4,
        #             "folder": "hair",
        #             "value": -1})
        # quit()
        # sliderRegions = ((.3445,.203,.372,.226),
        #              (.3445,.285,.372,.308),
        #              (.3445,.366,.372,.389),
        #              (.3445,.448,.372,.471),
        #              (.3445,.529,.372,.552),
        #              (.3445,.610,.372,.633),
        #              (.3445,.692,.372,.715),
        #              (.3445,.773,.372,.796))
        # mh.loadOCR()
        # while True:
        #     input()
        #     #time.sleep(2)
        #     for i in sliderRegions:
        #         mh.processRegion(*i)
            
        # quit()
        self.window = tk.Tk()
        self.window.resizable(False,False)
        self.window.title("DS3 AutoSliders")

        self.initWindowSize()
        self.buttonsWidth = int(self.windowWidth / 3)
        self.selectWidth = int((2 * self.windowWidth) / 3)
        self.paneHeight = int(self.windowHeight * .6)
        self.dictionary = mh.getDictTemplate()
        self.backDictionary = [self.dictionary]

        """keeps track of the key names of the different menus so you can traverse backwards and still know
        the name of the parent key. """
        self.backMenuName = ["main menu"] 
        self.currentMenu = self.dictionary

        self.pages = {}
        self.pages["main"] = self.createMainPage()
        self.pages["import"] = self.createImportPage()
        self.pages["export"] = self.createExportPage()
        self.pages["manual"] = self.createManualPage()
        self.pages["complete"] = self.createCompletePage()
        for i in self.pages.values():
            i.grid(row=0, column=0, sticky="nsew")

        self.manualButtonPane = tk.Frame(self.pages["manual"],width=self.buttonsWidth,height=self.paneHeight)
        self.manualButtonPane.grid(row=1,column=0,sticky="nsew")
        self.manualBlankPane = tk.Frame(self.pages["manual"],width=self.selectWidth,height=self.paneHeight)
        self.manualBlankPane.grid(row=1,column=1,sticky="nsew") 

        self.initButtons()
        self.sliders = Sliders(self.pages["manual"], self.selectWidth, self.paneHeight)
        self.colors = Colors(self.pages["manual"], self.selectWidth, self.paneHeight)
        self.labels = Labels(self.pages["manual"], self.selectWidth, self.paneHeight)
        self.dropdown = Dropdown(self.pages["manual"], self.selectWidth, self.paneHeight)
        self.tiles = Tiles(self.pages["manual"], self.selectWidth, self.paneHeight)

        self.pages["main"].tkraise()

        self.pages["manual"].grid_columnconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.window.mainloop()

    def initWindowSize(self):
        """"Sets the scale and position of the window"""
        self.screenWidth = self.window.winfo_screenwidth()
        self.screenHeight = self.window.winfo_screenheight()
        self.windowWidth = self.screenWidth // 4
        self.windowHeight = int(self.screenWidth / 3.5)
        windowX = self.screenWidth // 2
        windowY = self.screenHeight // 3
        self.window.geometry(str(self.windowWidth) + "x" + str(self.windowHeight) + "+" + str(windowX) + "+" + str(windowY))
    def createMainPage(self):
        """Create the frame and widgets for the main page"""
        mainPage = tk.Frame(self.window)
        title = tk.Label(mainPage, text="DS3 AutoSliders").pack()
        importButton = tk.Button(mainPage, text="Import from file to game", command=lambda:self.pages["import"].tkraise()).pack()
        exportButton = tk.Button(mainPage, text="Export from game to file", command=lambda:self.pages["export"].tkraise()).pack()
        manualButton = tk.Button(mainPage, text="Create file manually", command=self.manualCommand).pack()
        return mainPage
    def createImportPage(self):
        """Create the frame and widgets for the import page"""
        importPage = tk.Frame(self.window)
        tk.Label(importPage, text="Import page").pack() # page title
        tk.Label(importPage, text="First, open a json file. Next you should click the \"start\" button " \
        "then quickly open up your game to the appearance menu of the character creation menu. Do not close the game or tab" \
        " out until it is completed.", wraplength=500).pack() # instructions 
        self.importFilePath = None # initialize location where path of json will go
        tk.Button(importPage, text="open json", command=self.openFile).pack() # open json button
        self.importStartButton = tk.Button(importPage, text="start", command=self.importCommand, state="disabled")
        self.importStartButton.pack()
        tk.Button(importPage, text=("Back to menu"), command=lambda:self.pages["main"].tkraise()).pack() # back button 
        return importPage
    def createExportPage(self):
        """Create the frame and widgets for the export page"""
        exportPage = tk.Frame(self.window)
        tk.Label(exportPage, text="Export page").pack() # page title
        tk.Button(exportPage, text="choose where to save to", command=self.openExportSaveLocation).pack() # open file location button 
        self.exportFilePath = None
        self.exportStartButton = tk.Button(exportPage, text="start", command=self.exportCommand, state="disabled")
        self.exportStartButton.pack()
        tk.Button(exportPage, text=("Back to menu"), command=lambda:self.pages["main"].tkraise()).pack() # back button 
        return exportPage
    def createManualPage(self):
        """Create the frame and widgets for the manual page"""
        manualPage = tk.Frame(self.window)
        self.manualPageTitle = tk.Label(manualPage, text="Manually Create JSON File")
        self.manualPageTitle.grid(row=0,column=0,columnspan=2,pady=(0,5))
        self.manualBackButton = tk.Button(manualPage, text="Back", command=self.backCommand)
        self.manualBackButton.grid(row=2,column=0,columnspan=2) 
        tk.Button(manualPage, text="Reset to menu", command=lambda:self.pages["main"].tkraise()).grid(row=3,column=0,columnspan=2) # back to menu button 
        self.isLinked = tk.BooleanVar()
        self.linkedCheckbox = tk.Checkbutton(manualPage, text="Link features", variable=self.isLinked, command=self.changeLinkedStatus)
        self.linkedCheckbox.grid(row=2,column=0)
        self.linkedCheckbox.grid_remove() # hidden by default 
        self.manualSaveButton = tk.Button(manualPage, text="save", command=self.saveFile) 
        self.manualSaveButton.grid(row=2,column=0, columnspan=2)
        return manualPage
    def createCompletePage(self):
        """Create the frame and widgets for the import/export complete page"""
        completePage = tk.Frame(self.window)
        self.completeLabel = tk.Label(completePage, text=("placeholder"))
        self.completeLabel.pack()
        tk.Button(completePage, text=("Back to menu"), command=lambda:self.pages["main"].tkraise()).pack() # back button
        return completePage
    def initButtons(self):
        """Initializes the widgets for the button pages"""
        self.numberButtons = 11
        self.manualButtons = [None] * self.numberButtons
        for i in range(self.numberButtons):
            self.manualButtons[i] = tk.Button(self.manualButtonPane, text=f"button {i}")
            self.manualButtons[i].grid(row=i,column=0)
    def openFile(self):
        """opens a file and sets the path to the field"""
        self.importFilePath = filedialog.askopenfilename(filetypes=[("AutoSlider file", "*.json")])
        if (self.importFilePath):
            self.importStartButton.config(state="active")
        else:
            self.importStartButton.config(state="disabled")
    def importCommand(self):
        """called by the start button on the import page - starts the import process then shows the complete page"""
        importCharacter.importCharacter(self.importFilePath) # import character into game 
        self.completeLabel.config(text="Your import is complete!")
        self.pages["complete"].tkraise()
    def validateEdit(self, P):
        """Validation command for text boxes. Limits from 0 to 255, but also allows the field to be cleared"""
        if (P.isdigit()):
            text = int(P)
            if(text >= 0 and text <= 255):
                return True
        elif (P == ""): # let user clear field
            return True

        return False
    def manualCommand(self):
        """Switches to the manual character creation menu"""
        self.loadButtons() # load first buttons 
        self.pages["manual"].tkraise() # display page
    def loadButtons(self):
        """Configures and displays the buttons for the current menu"""
        titleText = spaceFormat(self.backMenuName[-1])
        self.manualPageTitle.config(text=titleText)
        if self.backMenuName[-1] == "main menu":
            self.manualSaveButton.grid()
            self.manualBackButton.grid_remove()
        else:
            self.manualSaveButton.grid_remove()
            self.manualBackButton.grid()

        if "menu" in self.currentMenu: # if menu type page then handle accordingly 
            if self.currentMenu["menu"] == "sliders":
                self.labels.load(self.currentMenu)
                self.sliders.load(self.currentMenu)
            elif self.currentMenu["menu"] == "colors":
                self.labels.load(self.currentMenu)
                self.colors.load(self.currentMenu)
            elif self.currentMenu["menu"] == "tiles":
                self.tiles.load(self.currentMenu)
            elif self.currentMenu["menu"] == "dropdown":
                self.dropdown.load(self.currentMenu)
            return
        
        # if not menu type

        if "isLinked" in self.currentMenu: # handle linked menus
            isLinked = self.currentMenu["isLinked"] # load checkbox choice
            self.isLinked.set(isLinked) # set checkbox choice 
            self.linkedCheckbox.grid() # display checkbox 
            i=0
            for key in self.currentMenu:
                if key == "isLinked": # dont display isLinked as button
                    continue
                if isLinked: # configure button parameters for linked
                    if self.currentMenu[key]["linkType"] in ("linked", "all"):
                        self.manualButtons[i].config(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                        i += 1 # count number of buttons 
                else: # configure correct buttons for unlinked
                    if self.currentMenu[key]["linkType"] in ("unlinked", "all"):
                        self.manualButtons[i].config(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                        i += 1 # count number of buttons 
        else: # if not a linked menu, then configure buttons 
            i = 0 
            for key in self.currentMenu: 
                self.manualButtons[i].config(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                i += 1 # count number of buttons, and used 

        # used by both linked and non linked menus 

        for j in range(i-1, self.numberButtons): # hide unecessary buttons 
                self.manualButtons[j].grid_remove()
        for j in range(0,i): # display necessary buttons if not already displayed 
                if not self.manualButtons[j].winfo_ismapped():
                    self.manualButtons[j].grid()
        self.manualButtonPane.tkraise() # display button pane
        self.manualBlankPane.tkraise() # display blank pane to hide anything on the left side such as text boxes  
    def clickButton(self, option): 
        self.linkedCheckbox.grid_remove()
        self.backDictionary.append(self.currentMenu)
        self.backMenuName.append(option)
        self.currentMenu = self.currentMenu[option]
        self.lastKey = option
        self.loadButtons()
    def backCommand(self):
        if (len(self.backDictionary) <= 1):
            print("can't go back any more")
            return 
        self.colors.shouldColorLog = False
        self.tiles.shouldTileLog = False
        self.linkedCheckbox.grid_remove()
        if "menu" in self.currentMenu:
            if self.currentMenu["menu"] in ("sliders", "colors", "tiles"):
                self.manualBlankPane.focus()
            if self.currentMenu["menu"] == "sliders":
                self.sliders.log(self.currentMenu)
                
        self.currentMenu = self.backDictionary[len(self.backDictionary)-1]
        self.backMenuName.pop()
        self.backDictionary.pop()
        self.loadButtons()
    def changeLinkedStatus(self):
        """Logs the current linked status into the dictionary, and loads the corresponding buttons"""
        self.currentMenu["isLinked"] = self.isLinked.get()
        self.loadButtons()
    def saveFile(self): 
        savePath = filedialog.asksaveasfilename(defaultextension=".json", 
                                                filetypes=[("JSON files", "*.json")], 
                                                title="Save Character File")
        if not savePath:
            print("INVALID PATH")
            return
        mh.saveFile(savePath, self.dictionary)
    def openExportSaveLocation(self):
        self.exportFilePath = filedialog.asksaveasfilename(defaultextension=".json", 
                                                filetypes=[("JSON files", "*.json")], 
                                                title="Save Character File")
        if (self.exportFilePath):
            self.exportStartButton.config(state="active")
        else:
            self.exportStartButton.config(state="disabled")
    def exportCommand(self):
        dict = exportCharacter.exportCharacter()
        mh.saveFile(self.exportFilePath, dict)