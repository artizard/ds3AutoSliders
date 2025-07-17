import customtkinter as ctk
from tkinter import filedialog
import importCharacter
from tkinter import font

import exportCharacter
from manualPanes import Sliders, Colors, Labels, Dropdown, Tiles, spaceFormat
import macroHelpers as mh
import time
from PIL import Image
class GUI:
    def __init__(self):
        self.window = ctk.CTk()
        # fonts = list(font.families())
        # fonts.sort()
        # print(fonts)
        # if "" in fonts:
        #     print("font available")
        # else:
        #     print("font NOT available")
        # quit()
        
        self.window.resizable(False,False)
        self.window.title("DS3 AutoSliders")
        self.window.configure(fg_color="#0D0D0F")
    
        self.initWindowSize()
        
        self.font = ("OptimusPrincepsSemiBold",int(self.windowHeight/34),"normal")
        self.instructionsFont = ("OptimusPrinceps",int(self.windowHeight/34),"normal")
        self.bigFont = ("OptimusPrincepsSemiBold",int(self.windowHeight/17),"normal")
        self.smallButtonAttributes = {"fg_color":"#49473B","corner_radius":self.windowHeight/48, 
                                 "hover_color":"#38362A","font":self.font, "width":self.windowHeight/3.36, 
                                 "height":self.windowHeight/16.8} 
        self.buttonAttributes = {"fg_color":"#49473B","corner_radius":self.windowHeight/48, 
                                 "hover_color":"#38362A","font":self.font, "width":self.windowHeight/2.4, 
                                 "height":self.windowHeight/16.8}
        self.bigButtonAttributes = {"fg_color":"#49473B","corner_radius":self.windowHeight/48, 
                                 "hover_color":"#38362A","font":("OptimusPrincepsSemiBold",self.windowHeight/28,"normal"), 
                                 "width":self.windowHeight/1.92, "height":self.windowHeight/8.64}
        self.paneWidth = int(self.windowWidth / 1.11)
        self.paneHeight = int(self.windowHeight / 1.5)
        self.dictionary = mh.getDictTemplate()

        """keeps track of the previous menus you were in so you can use the back button"""
        self.backDictionary = [self.dictionary]
        """keeps track of the key names of the different menus so you can traverse backwards and still know
        the name of the parent key. """
        self.backMenuName = ["main menu"] 
        """keeps track of the current menu"""
        self.currentMenu = self.dictionary

        self.background = ctk.CTkImage(Image.open("images/ui/background.png"), size=(self.windowWidth,self.windowHeight))
        ctk.CTkLabel(self.window, text="", image=self.background).grid(row=0,column=0,sticky="nsew")
        #self.backgroundLabel

        self.pages = {}
        self.pages["main"] = self.createMainPage()
        self.pages["import"] = self.createImportPage()
        self.pages["export"] = self.createExportPage()
        self.pages["manual"] = self.createManualPage()
        self.pages["complete"] = self.createCompletePage()
        for i in self.pages.values():
            i.grid(row=0, column=0, sticky="nsew")
            i.grid_columnconfigure(0, weight=1)
            i.grid_rowconfigure(0, weight=1)

        self.manualButtonPane = ctk.CTkFrame(self.pages["manual"],width=int(self.windowWidth / 2.2),
                                             height=int(self.windowHeight / 1.5), fg_color="transparent")
        self.manualButtonPane.place(relx=.5,rely=.48, anchor="center")
        self.manualButtonPane.grid_propagate(False)
        self.manualBlankPane = ctk.CTkFrame(self.pages["manual"],width=int(self.windowWidth / 1.11),
                                            height=int(self.windowHeight / 1.5), fg_color="transparent")
        self.manualBlankPane.place(relx=.05,rely=.14)

        self.initButtons()
        self.sliders = Sliders(self.pages["manual"], int(self.windowWidth / 3.5), int(self.windowHeight / 1.5), self.font)
        self.colors = Colors(self.pages["manual"], int(self.windowWidth / 1.11), int(self.windowHeight / 3), self.font)
        self.labels = Labels(self.pages["manual"], int(self.windowWidth / 2.75), int(self.windowHeight / 1.5), self.font)
        self.dropdown = Dropdown(self.pages["manual"], int(self.windowWidth / 3), int(self.windowHeight / 20), self.font)
        self.tiles = Tiles(self.pages["manual"], int(self.windowWidth / 1.11), int(self.windowHeight / 2), self.bigFont)

        self.pages["main"].tkraise() 

        self.window.mainloop()
    def initWindowSize(self):
        """"Sets the scale and position of the window"""
        self.screenWidth = self.window.winfo_screenwidth()
        self.screenHeight = self.window.winfo_screenheight()
        self.windowWidth = self.screenHeight // (1.5 * 1.5)
        self.windowHeight = int(self.screenHeight / (1.3886 * 1.5))
        windowX = self.screenWidth // 2
        windowY = self.screenHeight // 3
        self.window.geometry(str(self.windowWidth) + "x" + str(self.windowHeight) + "+" + str(windowX) + "+" + str(windowY))
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
    def createMainPage(self):
        """Create the frame and widgets for the main page"""
        mainPage = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(mainPage, text="", image=self.background).place(x=0, y=0, relwidth=1, relheight=1)
        ctk.CTkLabel(mainPage, text="DS3 AutoSliders", 
                     fg_color="transparent", 
                     font=self.bigFont).place(relx=.5,rely=.08, anchor="center")
        ctk.CTkButton(mainPage, text="Import from file to game", 
                      command=lambda:self.pages["import"].tkraise(), 
                      **self.bigButtonAttributes).place(relx=.5,rely=.3, anchor="center")
        ctk.CTkButton(mainPage, text="Export from game to file", 
                      command=lambda:self.pages["export"].tkraise(), 
                      **self.bigButtonAttributes).place(relx=.5,rely=.45, anchor="center")
        ctk.CTkButton(mainPage, text="Create file manually", command=self.manualCommand, 
                      **self.bigButtonAttributes).place(relx=.5,rely=.6, anchor="center")
        return mainPage
    def createImportPage(self):
        """Create the frame and widgets for the import page"""
        importPage = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(importPage, text="", image=self.background).place(x=0, y=0, relwidth=1, relheight=1)
        ctk.CTkLabel(importPage, text="Import Character", font=self.bigFont).place(relx=.5, rely=.08, anchor="center") # page title
        ctk.CTkLabel(importPage, font=self.instructionsFont, text="First, open your character file. Next, click the \"start\" button " \
        "then quickly open up your game to the appearance menu of the character creation menu. The import will start after a few seconds. " \
        "Leave the game open and do not move your mouse until the menus stop changing.", 
        wraplength=int(self.windowWidth*.9)).place(relx=.5, rely=.25, anchor="center") # instructions 
        self.importFilePath = None # initialize location where path of json will go
        ctk.CTkButton(importPage, text="open json", command=self.openFile, 
                      **self.bigButtonAttributes).place(relx=.5, rely=.5, anchor="center") # open json button
        self.importStartButton = ctk.CTkButton(importPage, text="start", command=self.importCommand, 
                                            state="disabled", 
                                            **self.bigButtonAttributes)
        self.importStartButton.place(relx=.5, rely=.65, anchor="center")
        ctk.CTkButton(importPage, text=("back to menu"), 
                      command=lambda:self.pages["main"].tkraise(), 
                      **self.bigButtonAttributes).place(relx=.5, rely=.8, anchor="center") # back button 
        return importPage
    def createExportPage(self):
        """Create the frame and widgets for the export page"""
        exportPage = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(exportPage, text="", image=self.background).place(x=0, y=0, relwidth=1, relheight=1)
        ctk.CTkLabel(exportPage, text="Export From Game", font=self.bigFont).place(relx=.5, rely=.08, anchor="center") # page title
        ctk.CTkLabel(exportPage, font=self.instructionsFont, text="First, choose the desired filename and location. Next, click the \"start\" button " \
        "then quickly open up your game to the appearance menu of the character creation menu. The export will start after a few seconds. " \
        "Leave the game open and do not move your mouse until the menus stop changing.", wraplength=500).place(relx=.5, rely=.25, anchor="center") # instructions 
        ctk.CTkButton(exportPage, text="choose save location", 
                      command=self.openExportSaveLocation, 
                      **self.bigButtonAttributes).place(relx=.5, rely=.5, anchor="center") # open file location button 
        self.exportFilePath = None
        self.exportStartButton = ctk.CTkButton(exportPage, text="start", 
                                               command=self.exportCommand, 
                                               state="disabled", **self.bigButtonAttributes)
        self.exportStartButton.place(relx=.5, rely=.65, anchor="center")
        ctk.CTkButton(exportPage, text=("back to menu"), command=lambda:self.pages["main"].tkraise(), 
                      **self.bigButtonAttributes).place(relx=.5, rely=.8, anchor="center") # back button 
        return exportPage
    def createManualPage(self):
        """Create the frame and widgets for the manual page"""
        manualPage = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(manualPage, text="", image=self.background).place(x=0, y=0, relwidth=1, relheight=1)
        self.manualPageTitle = ctk.CTkLabel(manualPage, text="PLACEHOLDER", font=self.bigFont)
        self.manualPageTitle.place(relx=.5, rely=.08, anchor="center")
        self.backSavePlacement = {"relx":.675, "rely":.85, "anchor":"center"} # need to save placement to remove and replace 
        self.manualBackButton = ctk.CTkButton(manualPage, text="Back", command=self.backCommand, 
                      **self.smallButtonAttributes)
        self.manualBackButton.place(**self.backSavePlacement)
        ctk.CTkButton(manualPage, text="Reset to menu", command=self.resetToMenu, 
                      **self.smallButtonAttributes).place(relx=.325, rely=.85, anchor="center") # back to menu button 
        
        self.areColorsLinked = ctk.BooleanVar()
        self.colorsLinkedCheckbox = ctk.CTkCheckBox(manualPage, text="Link colors", variable=self.areColorsLinked, 
                                                    command=lambda: self.changeLinkedStatus(True),
                                              font = self.font, fg_color="#49473B", hover_color="#38362A")
        self.colorsLinkedCheckboxPlacement = {"relx":.35, "rely":.925, "anchor":"center"} # need to save placement to remove and replace 

        self.areTilesLinked = ctk.BooleanVar()
        self.tilesLinkedCheckbox = ctk.CTkCheckBox(manualPage, text="Link pupilis", variable=self.areTilesLinked, 
                                                   command=lambda: self.changeLinkedStatus(False),
                                              font = self.font, fg_color="#49473B", hover_color="#38362A")
        self.tilesLinkedCheckboxPlacement = {"relx":.65, "rely":.925, "anchor":"center"} # need to save placement to remove and replace 

        self.singleLinkedCheckboxPlacement = {"relx":.5, "rely":.925, "anchor":"center"} # need to save placement to remove and replace 
        
        self.manualSaveButton = ctk.CTkButton(manualPage, text="Save", command=self.saveFile, 
                      **self.smallButtonAttributes)
        self.manualSaveButton.place(**self.backSavePlacement)
        return manualPage
    def createCompletePage(self):
        """Create the frame and widgets for the import/export complete page"""
        completePage = ctk.CTkFrame(self.window, fg_color="transparent")
        ctk.CTkLabel(completePage, text="", image=self.background).place(x=0, y=0, relwidth=1, relheight=1)
        self.completeLabel = ctk.CTkLabel(completePage, text=("placeholder"), font=self.bigFont)
        self.completeLabel.place(relx=.5, rely=.25, anchor="center")
        ctk.CTkButton(completePage, text=("Back to menu"), command=lambda:self.pages["main"].tkraise(),
                      **self.bigButtonAttributes).place(relx=.5, rely=.65, anchor="center") # back button
        return completePage
    def initButtons(self):
        """Initializes the widgets for the button pages"""
        self.numberButtons = 11
        self.manualButtons = [None] * self.numberButtons
        for i in range(self.numberButtons):
            self.manualButtons[i] = ctk.CTkButton(self.manualButtonPane, text=f"button {i}", 
                      **self.buttonAttributes)
            self.manualButtons[i].grid(row=i,column=0)
    def openFile(self):
        """opens a file and sets the path to the field"""
        self.importFilePath = filedialog.askopenfilename(filetypes=[("AutoSlider file", "*.json")])
        if (self.importFilePath):
            self.importStartButton.configure(state="normal")
        else:
            self.importStartButton.configure(state="disabled")
    def importCommand(self):
        """called by the start button on the import page - starts the import process then shows the complete page"""
        isCompleted = importCharacter.importCharacter(self.importFilePath) # import character into game 
        if not isCompleted:
            return
        self.completeLabel.configure(text="Your import is complete!")
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
        self.manualBlankPane.tkraise() # hide things behind main button frame 
        if self.backMenuName[-1] == "main menu":
            self.manualPageTitle.configure(text="General")
        else:
            titleText = spaceFormat(self.backMenuName[-1])
            self.manualPageTitle.configure(text=titleText)
        if self.backMenuName[-1] == "main menu":
            self.manualSaveButton.place(**self.backSavePlacement)
            self.manualBackButton.place_forget()
        else:
            self.manualSaveButton.place_forget()
            self.manualBackButton.place(**self.backSavePlacement)

        if "menu" in self.currentMenu: # if menu type page then handle accordingly 
            if self.currentMenu["menu"] == "sliders":
                self.labels.load(self.currentMenu)
                self.sliders.load(self.currentMenu)
            elif self.currentMenu["menu"] == "colors":
                self.colors.load(self.currentMenu)
            elif self.currentMenu["menu"] == "tiles":
                self.tiles.load(self.currentMenu)
            elif self.currentMenu["menu"] == "dropdown":
                self.dropdown.load(self.currentMenu)
            return
        
        # if not menu type

        if "colorsLinked" in self.currentMenu: # handle linked menus
            if "tilesLinked" in self.currentMenu: # handle additional checkbox if in double linked menu 
                self.areTilesLinked.set(self.currentMenu["tilesLinked"]) # set checkbox choice to dictionary value 
                self.tilesLinkedCheckbox.place(**self.tilesLinkedCheckboxPlacement) # display checkbox 
                self.areColorsLinked.set(self.currentMenu["colorsLinked"]) # set checkbox choice to dictionary value
                self.colorsLinkedCheckbox.place(**self.colorsLinkedCheckboxPlacement) # display checkbox 
            else:
                self.areColorsLinked.set(self.currentMenu["colorsLinked"]) # set checkbox choice to dictionary value
                self.colorsLinkedCheckbox.place(**self.singleLinkedCheckboxPlacement) # display checkbox 
            

            i=0
            for key in self.currentMenu:
                if key in ("colorsLinked","tilesLinked"): # dont display booleans as buttons
                    continue
                if "tilesLinked" in self.currentMenu: # handle double menu
                    if self.currentMenu[key]["menu"] == "tiles":
                        if self.currentMenu["tilesLinked"]:
                            if self.currentMenu[key]["linkType"] in ("linked", "all"):
                                self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                                i += 1 # count number of buttons 
                        else: # configure correct buttons for unlinked
                            if self.currentMenu[key]["linkType"] in ("unlinked", "all"):
                                self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                                i += 1 # count number of buttons 
                        
                    else: # colors menu
                        if self.currentMenu["colorsLinked"]:
                            if self.currentMenu[key]["linkType"] in ("linked", "all"):
                                self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                                i += 1 # count number of buttons 
                        else: # configure correct buttons for unlinked
                            if self.currentMenu[key]["linkType"] in ("unlinked", "all"):
                                self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                                i += 1 # count number of buttons 

                else: # configure button parameters for single linked menu
                    if self.currentMenu["colorsLinked"]: 
                        if self.currentMenu[key]["linkType"] in ("linked", "all"):
                            self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                            i += 1 # count number of buttons 
                    else: # configure correct buttons for unlinked
                        if self.currentMenu[key]["linkType"] in ("unlinked", "all"):
                            self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                            i += 1 # count number of buttons 
        else: # if not a linked menu, then configure buttons 
            i = 0 
            for key in self.currentMenu: 
                self.manualButtons[i].configure(text=spaceFormat(key), command=lambda o=key:self.clickButton(o))
                i += 1 # count number of buttons, and used 

        # used by both linked and non linked menus 

        for j in range(i-1, self.numberButtons): # hide unecessary buttons 
                self.manualButtons[j].grid_remove()
        for j in range(0,i): # display necessary buttons if not already displayed 
                if not self.manualButtons[j].winfo_ismapped():
                    self.manualButtons[j].grid()
        
        self.manualButtonPane.tkraise() # display button pane
    def clickButton(self, option): 
        self.colorsLinkedCheckbox.place_forget()
        self.tilesLinkedCheckbox.place_forget()
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
        self.colorsLinkedCheckbox.place_forget()
        self.tilesLinkedCheckbox.place_forget()
        if "menu" in self.currentMenu:
            #self.manualBlankPane.focus()
            if self.currentMenu["menu"] == "sliders":
                self.sliders.log(self.currentMenu)
                
        self.currentMenu = self.backDictionary[len(self.backDictionary)-1]
        self.backMenuName.pop()
        self.backDictionary.pop()
        self.loadButtons()
    def changeLinkedStatus(self, isColor):
        """Logs the current linked status into the dictionary, and loads the corresponding buttons"""
        if isColor:
            self.currentMenu["colorsLinked"] = self.areColorsLinked.get()
        else:
            self.currentMenu["tilesLinked"] = self.areTilesLinked.get()
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
            self.exportStartButton.configure(state="normal")
        else:
            self.exportStartButton.configure(state="disabled")
    def exportCommand(self):
        dict = exportCharacter.exportCharacter()
        if not dict: # don't do anything if export wasn't carried out 
            return
        mh.saveFile(self.exportFilePath, dict)
        self.completeLabel.configure(text="Your export is complete!")
        self.pages["complete"].tkraise()
    def resetToMenu(self):
        self.pages["main"].tkraise()
        self.backDictionary[1:] = []
        self.backMenuName[1:] = []
        self.currentMenu = self.dictionary